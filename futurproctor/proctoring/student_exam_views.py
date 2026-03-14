# student_exam_views.py - Student exam-related views
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Q
from .models import (
    Student, ExamPaper, Question, StudentExamAttempt, 
    StudentAnswer, Result
)
import json


def student_approval_check(view_func):
    """Decorator to check if student is approved"""
    def wrapper(request, *args, **kwargs):
        try:
            student = request.user.student
            if student.approval_status != 'approved':
                messages.error(request, "Your account is pending admin approval. Please wait for approval to access exams.")
                return redirect('dashboard')
        except:
            messages.error(request, "Student profile not found.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@student_approval_check
def available_exams(request):
    """Show all available exams categorized by status: Upcoming, Live, Completed"""
    student = request.user.student
    now = timezone.now()
    
    # Get all active and published exams
    all_exams = ExamPaper.objects.filter(is_active=True, published=True).order_by('exam_date')
    
    # Get student's attempts
    attempted_exam_ids = StudentExamAttempt.objects.filter(
        student=student
    ).values_list('exam_paper_id', flat=True).distinct()
    
    # Categorize exams into upcoming, live, and completed
    upcoming_exams = []
    live_exams = []
    completed_exams = []
    
    for exam in all_exams:
        exam_end_time = exam.exam_date + timezone.timedelta(minutes=exam.duration_minutes)
        
        # Check if student has already attempted
        has_attempted = exam.id in attempted_exam_ids
        
        # Add exam status info
        exam.has_attempted = has_attempted
        exam.end_time = exam_end_time
        
        if now < exam.exam_date:
            # Exam hasn't started yet - UPCOMING
            exam.time_until_start = exam.exam_date - now
            upcoming_exams.append(exam)
        elif exam.exam_date <= now <= exam_end_time:
            # Exam is currently active - LIVE
            exam.time_remaining = exam_end_time - now
            live_exams.append(exam)
        else:
            # Exam has ended - COMPLETED
            completed_exams.append(exam)
    
    context = {
        'upcoming_exams': upcoming_exams,
        'live_exams': live_exams,
        'completed_exams': completed_exams,
        'attempted_exam_ids': attempted_exam_ids,
        'student': student,
        'now': now,
    }
    
    return render(request, 'student/available_exams.html', context)


@login_required
@student_approval_check
def start_exam(request, exam_id):
    """Start a new exam attempt with time-based validation"""
    student = request.user.student
    exam_paper = get_object_or_404(ExamPaper, id=exam_id, is_active=True, published=True)
    
    # TIME-BASED VALIDATION - Critical Security Check
    now = timezone.now()
    exam_end_time = exam_paper.exam_date + timezone.timedelta(minutes=exam_paper.duration_minutes)
    
    # Check if exam is in valid time window
    if now < exam_paper.exam_date:
        # Exam hasn't started yet
        time_until_start = exam_paper.exam_date - now
        days = time_until_start.days
        hours, remainder = divmod(time_until_start.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        messages.error(
            request, 
            f"This exam is scheduled for {exam_paper.exam_date.strftime('%B %d, %Y at %I:%M %p')}. "
            f"You can attempt it only when it becomes active. "
            f"Time remaining: {days}d {hours}h {minutes}m {seconds}s"
        )
        return redirect('available_exams')
    
    if now > exam_end_time:
        # Exam has already ended
        messages.error(
            request, 
            f"This exam ended on {exam_end_time.strftime('%B %d, %Y at %I:%M %p')}. "
            "You can no longer attempt this exam."
        )
        return redirect('available_exams')
    
    # Check if student has already attempted this exam
    existing_attempt = StudentExamAttempt.objects.filter(
        student=student,
        exam_paper=exam_paper
    ).first()
    
    if existing_attempt:
        messages.warning(request, "You have already attempted this exam.")
        return redirect('available_exams')
    
    # All checks passed - Create new attempt
    attempt = StudentExamAttempt.objects.create(
        student=student,
        exam_paper=exam_paper,
        status='ongoing'
    )
    
    messages.success(request, f"Exam '{exam_paper.title}' started successfully!")
    return redirect('take_exam', attempt_id=attempt.id)


@login_required
@student_approval_check
def take_exam(request, attempt_id):
    """Take exam with proctoring - dynamic questions from database"""
    attempt = get_object_or_404(StudentExamAttempt, id=attempt_id)
    
    # Check if student owns this attempt
    if attempt.student != request.user.student:
        messages.error(request, "Unauthorized access!")
        return redirect('available_exams')
    
    # Check if already submitted
    if attempt.status != 'ongoing':
        messages.warning(request, "This exam has already been submitted!")
        return redirect('student_results')
    
    # Get all questions for this exam
    questions = attempt.exam_paper.questions.all().order_by('order')
    
    # Convert questions to format similar to old ai.json
    questions_data = []
    for q in questions:
        question_dict = {
            'id': q.id,
            'text': q.question_text,
            'type': q.question_type,
            'marks': q.marks,
        }
        
        if q.question_type == 'mcq':
            question_dict.update({
                'option_a': q.option_a,
                'option_b': q.option_b,
                'option_c': q.option_c,
                'option_d': q.option_d,
            })
        
        questions_data.append(question_dict)
    
    # Get tab switch count from CheatingEvent
    from .models import CheatingEvent
    violations = CheatingEvent.objects.filter(student=request.user.student).first()
    tab_count = violations.tab_switch_count if violations else 0

      
    # Start background processing threads for video and audio monitoring (ML Proctoring)
    import threading
    from .views import stop_event, background_processing, process_audio, warning
    stop_event.clear()  # Reset the stop event flag
    threading.Thread(target=background_processing, args=(request,), daemon=True).start()
    threading.Thread(target=process_audio, args=(request,), daemon=True).start()
    
    context = {
        'attempt': attempt,
        'exam_paper': attempt.exam_paper,
        'questions': questions_data,
        'tab_count': tab_count,
        # 'warning': None,
        'warning': warning,
    }
    
    return render(request, 'student/take_exam.html', context)


@login_required
@student_approval_check
def submit_exam_new(request, attempt_id):
    """Submit exam answers - handles both MCQ and subjective"""
    if request.method != 'POST':
        return HttpResponse("Invalid request method.", status=400)
    
    attempt = get_object_or_404(StudentExamAttempt, id=attempt_id)
    
    # Check if student owns this attempt
    if attempt.student != request.user.student:
        messages.error(request, "Unauthorized access!")
        return redirect('available_exams')
    
    # Get all questions
    questions = attempt.exam_paper.questions.all()
    
    total_marks_obtained = 0
    
    for question in questions:
        if question.question_type == 'mcq':
            # MCQ answer
            user_answer = request.POST.get(f'answer_{question.id}')
            
            if user_answer:
                is_correct = (user_answer.upper() == question.correct_answer.upper())
                marks = question.marks if is_correct else 0
                
                StudentAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_option=user_answer.upper(),
                    is_correct=is_correct,
                    marks_obtained=marks
                )
                
                total_marks_obtained += marks
        
        else:  # subjective
            # Subjective answer
            answer_text = request.POST.get(f'answer_{question.id}', '').strip()
            
            StudentAnswer.objects.create(
                attempt=attempt,
                question=question,
                answer_text=answer_text,
                marks_obtained=0  # Will be evaluated later
            )
    
    # Update attempt
    attempt.submitted_at = timezone.now()
    attempt.status = 'submitted'  # Needs evaluation for subjective questions
    attempt.total_marks_obtained = total_marks_obtained  # Only MCQ marks for now
    attempt.save()
    
    # Stop background proctoring threads
    import threading
    from .views import stop_event
    stop_event.set()
    
    messages.success(request, 'Exam submitted successfully! Results will be published after evaluation.')
    return redirect('exam_submission_success_new')


@login_required
def exam_submission_success_new(request):
    """Exam submission success page"""
    return render(request, 'student/exam_submission_success.html')


@login_required
def student_results(request):
    """View all results for the student"""
    student = request.user.student
    
    # Get all published results
    published_results = Result.objects.filter(
        attempt__student=student,
        published=True
    ).select_related('attempt__exam_paper').order_by('-published_at')
    
    # Get pending evaluations
    pending_attempts = StudentExamAttempt.objects.filter(
        student=student,
        status__in=['submitted', 'evaluated'],
        result__isnull=True
    ).select_related('exam_paper').order_by('-submitted_at')
    
    context = {
        'published_results': published_results,
        'pending_attempts': pending_attempts,
        'student': student,
    }
    
    return render(request, 'student/results.html', context)


@login_required
def result_detail(request, result_id):
    """View detailed result with answers and feedback"""
    result = get_object_or_404(Result, id=result_id)
    
    # Check if student owns this result
    if result.attempt.student != request.user.student:
        messages.error(request, "Unauthorized access!")
        return redirect('student_results')
    
    # Get all answers with questions
    answers = result.attempt.answers.all().select_related('question').order_by('question__order')
    
    context = {
        'result': result,
        'answers': answers,
    }
    
    return render(request, 'student/result_detail.html', context)


@login_required
def student_dashboard_enhanced(request):
    """Enhanced student dashboard with approval status, categorized exams, and results"""
    student = request.user.student
    now = timezone.now()
    
    # Get approval status
    approval_status = student.approval_status
    
    # Get stats
    total_attempts = StudentExamAttempt.objects.filter(student=student).count()
    completed_exams = StudentExamAttempt.objects.filter(
        student=student, 
        status__in=['submitted', 'evaluated']
    ).count()
    
    # Get recent results
    recent_results = Result.objects.filter(
        attempt__student=student,
        published=True
    ).select_related('attempt__exam_paper').order_by('-published_at')[:5]
    
    # Get categorized exams (Upcoming, Live, Completed)
    all_exams = ExamPaper.objects.filter(
        is_active=True,
        published=True
    ).order_by('exam_date')
    
    attempted_exam_ids = StudentExamAttempt.objects.filter(
        student=student
    ).values_list('exam_paper_id', flat=True).distinct()
    
    upcoming_exams = []
    live_exams = []
    
    for exam in all_exams:
        exam_end_time = exam.exam_date + timezone.timedelta(minutes=exam.duration_minutes)
        has_attempted = exam.id in attempted_exam_ids
        
        if now < exam.exam_date and not has_attempted:
            # Upcoming exam
            exam.time_until_start = exam.exam_date - now
            upcoming_exams.append(exam)
        elif exam.exam_date <= now <= exam_end_time and not has_attempted:
            # Live exam
            exam.time_remaining = exam_end_time - now
            live_exams.append(exam)
    
    upcoming_exams_count = len(upcoming_exams)
    live_exams_count = len(live_exams)
    
    context = {
        'student': student,
        'approval_status': approval_status,
        'total_attempts': total_attempts,
        'completed_exams': completed_exams,
        'recent_results': recent_results,
        'upcoming_exams_count': upcoming_exams_count,
        'live_exams_count': live_exams_count,
        'upcoming_exams': upcoming_exams[:3],  # Show top 3
        'live_exams': live_exams[:3],  # Show top 3
        'now': now,
    }
    
    return render(request, 'student/dashboard_enhanced.html', context)