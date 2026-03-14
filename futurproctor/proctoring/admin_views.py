# admin_views.py - Admin-specific views
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    Student, ExamPaper, Question, StudentExamAttempt, 
    StudentAnswer, Result, CheatingEvent
)
from django.contrib.auth.models import User
import json
import logging

# Import email and Groq services
from .email_service import send_result_published_email, send_approval_email, send_rejection_email
from .groq_service import get_groq_service

logger = logging.getLogger(__name__)


@staff_member_required(login_url='/admin/login/')
def admin_dashboard_enhanced(request):
    """Enhanced admin dashboard with comprehensive analytics"""
    
    # Get counts
    total_students = Student.objects.count()
    approved_students = Student.objects.filter(approval_status='approved').count()
    pending_approvals = Student.objects.filter(approval_status='pending').count()
    rejected_students = Student.objects.filter(approval_status='rejected').count()
    
    total_exams = ExamPaper.objects.count()
    active_exams = ExamPaper.objects.filter(is_active=True).count()
    published_exams = ExamPaper.objects.filter(published=True).count()
    draft_exams = ExamPaper.objects.filter(published=False).count()
    
    total_attempts = StudentExamAttempt.objects.count()
    pending_evaluations = StudentExamAttempt.objects.filter(status='submitted').count()
    evaluated_attempts = StudentExamAttempt.objects.filter(status='evaluated').count()
    
     # Classify exams by status
    now = timezone.now()
    all_published_exams = ExamPaper.objects.filter(published=True)
    
    upcoming_exams = []
    live_exams = []
    closed_exams = []
    
    for exam in all_published_exams:
        exam_end_time = exam.exam_date + timezone.timedelta(minutes=exam.duration_minutes)
        if now < exam.exam_date:
            upcoming_exams.append(exam)
        elif exam.exam_date <= now <= exam_end_time:
            live_exams.append(exam)
        else:
            closed_exams.append(exam)
    
    # Sort by date
    upcoming_exams = sorted(upcoming_exams, key=lambda x: x.exam_date)[:5]
    live_exams = sorted(live_exams, key=lambda x: x.exam_date, reverse=True)[:5]
    closed_exams = sorted(closed_exams, key=lambda x: x.exam_date, reverse=True)[:5]
    
    # Recent submissions needing evaluation
    pending_subjective = StudentExamAttempt.objects.filter(
        status='submitted'
    ).select_related('student', 'exam_paper').order_by('-submitted_at')[:10]
    
    # Students pending approval
    pending_students = Student.objects.filter(
        approval_status='pending'
    ).order_by('-timestamp')[:10]


     # ML Proctoring Reports - Get students with exam attempts and their proctoring data
    from .models import CheatingImage, CheatingAudio
    from django.db.models import Prefetch
    
    # Get all students who have taken exams with their cheating events
    proctoring_reports = []
    students_with_attempts = Student.objects.filter(
        exam_attempts__isnull=False
    ).distinct().prefetch_related(
        Prefetch('cheating_events', queryset=CheatingEvent.objects.all()),
        'exam_attempts__exam_paper'
    )[:20]  # Limit to 20 most recent
    
    for student in students_with_attempts:
        cheating_events = student.cheating_events.all()
        
        # Get tab switch count
        tab_switches = cheating_events.aggregate(total=Sum('tab_switch_count'))['total'] or 0
        
        # Get detected objects
        detected_objects = []
        for event in cheating_events:
            if event.detected_objects:
                if isinstance(event.detected_objects, str):
                    import json
                    try:
                        objs = json.loads(event.detected_objects)
                        if isinstance(objs, list):
                            detected_objects.extend(objs)
                    except:
                        pass
                elif isinstance(event.detected_objects, list):
                    detected_objects.extend(event.detected_objects)
        detected_objects = list(set(detected_objects))  # Remove duplicates
        detected_objects_str = ", ".join(detected_objects) if detected_objects else "None"
        
        # Check if cheating detected
        cheating_detected = any(
            event.cheating_flag or event.tab_switch_count > 0
            for event in cheating_events
        )
        
        # Get latest exam attempt
        latest_attempt = student.exam_attempts.order_by('-submitted_at').first()
        
        proctoring_reports.append({
            'student': student,
            'latest_exam': latest_attempt.exam_paper.title if latest_attempt else 'N/A',
            'tab_switches': tab_switches,
            'detected_objects': detected_objects_str,
            'cheating_detected': cheating_detected,
            'has_images': CheatingImage.objects.filter(event__student=student).exists(),
            'has_audio': CheatingAudio.objects.filter(event__student=student).exists(),
        })
    
    
    context = {
        'total_students': total_students,
        'approved_students': approved_students,
        'pending_approvals': pending_approvals,
        'rejected_students': rejected_students,
        'total_exams': total_exams,
        'active_exams': active_exams,
        'published_exams': published_exams,
        'draft_exams': draft_exams,
        'total_attempts': total_attempts,
        'pending_evaluations': pending_evaluations,
        'evaluated_attempts': evaluated_attempts,
        'upcoming_exams': upcoming_exams,
        'live_exams': live_exams,
        'closed_exams': closed_exams,
        'pending_subjective': pending_subjective,
        'pending_students': pending_students,
        'proctoring_reports': proctoring_reports,  # ML Proctoring data
    }
    
    return render(request, 'admin/dashboard_enhanced.html', context)


@staff_member_required(login_url='/admin/login/')
def student_approval_list(request):
    """List all students with approval actions"""
    students = Student.objects.all().order_by('-timestamp')
    
    context = {
        'students': students,
    }
    
    return render(request, 'admin/student_approval_list.html', context)


@staff_member_required(login_url='/admin/login/')
def approve_student(request, student_id):
    """Approve a student"""
    student = get_object_or_404(Student, id=student_id)
    
    student.approval_status = 'approved'
    student.approved_by = request.user
    student.approved_at = timezone.now()
    student.save()

    # Send approval email using email service
    email_sent = send_approval_email(student, request.user)
    if email_sent:
        messages.success(request, f"Student {student.name} has been approved and notified via email!")
    else:
        messages.success(request, f"Student {student.name} has been approved! (Email notification failed)")
    
    return redirect('student_approval_list')


@staff_member_required(login_url='/admin/login/')
def reject_student(request, student_id):
    """Reject a student"""
    student = get_object_or_404(Student, id=student_id)
    
    student.approval_status = 'rejected'
    student.approved_by = request.user
    student.approved_at = timezone.now()
    student.save()

       # Send rejection email using email service
    rejection_reason = request.POST.get('rejection_reason', None)
    email_sent = send_rejection_email(student, rejection_reason)
    if email_sent:
        messages.warning(request, f"Student {student.name} has been rejected and notified via email!")
    else:
        messages.warning(request, f"Student {student.name} has been rejected! (Email notification failed)")
    return redirect('student_approval_list')


@staff_member_required(login_url='/admin/login/')
def exam_paper_list(request):
    """List all exam papers"""
    exam_papers = ExamPaper.objects.all().order_by('-created_at')
    
    context = {
        'exam_papers': exam_papers,
    }
    
    return render(request, 'admin/exam_paper_list.html', context)


@staff_member_required(login_url='/admin/login/')
def exam_paper_create(request):
    """Create a new exam paper"""
    if request.method == 'POST':
        title = request.POST.get('title')
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        duration_minutes = request.POST.get('duration_minutes')
        exam_date = request.POST.get('exam_date')
        instructions = request.POST.get('instructions')
        total_marks = request.POST.get('total_marks', 0)
        passing_marks = request.POST.get('passing_marks', 0)
        
        exam_paper = ExamPaper.objects.create(
            title=title,
            subject=subject,
            description=description,
            duration_minutes=duration_minutes,
            exam_date=exam_date,
            instructions=instructions,
            total_marks=total_marks,
            passing_marks=passing_marks,
            created_by=request.user
        )
        
        messages.success(request, f"Exam paper '{title}' created successfully!")
        return redirect('exam_paper_detail', exam_id=exam_paper.id)
    
    return render(request, 'admin/exam_paper_create.html')


@staff_member_required(login_url='/admin/login/')
def exam_paper_edit(request, exam_id):
    """Edit an exam paper"""
    exam_paper = get_object_or_404(ExamPaper, id=exam_id)
    
    if request.method == 'POST':
        exam_paper.title = request.POST.get('title')
        exam_paper.subject = request.POST.get('subject')
        exam_paper.description = request.POST.get('description')
        exam_paper.duration_minutes = request.POST.get('duration_minutes')
        exam_paper.exam_date = request.POST.get('exam_date')
        exam_paper.instructions = request.POST.get('instructions')
        exam_paper.total_marks = request.POST.get('total_marks', 0)
        exam_paper.passing_marks = request.POST.get('passing_marks', 0)
        exam_paper.is_active = request.POST.get('is_active') == 'on'
        exam_paper.save()
        
        messages.success(request, f"Exam paper '{exam_paper.title}' updated successfully!")
        return redirect('exam_paper_detail', exam_id=exam_paper.id)
    
    context = {
        'exam_paper': exam_paper,
    }
    
    return render(request, 'admin/exam_paper_edit.html', context)


@staff_member_required(login_url='/admin/login/')
def exam_paper_detail(request, exam_id):
    """View exam paper details with questions"""
    exam_paper = get_object_or_404(ExamPaper, id=exam_id)
    questions = exam_paper.questions.all().order_by('order')
    
    context = {
        'exam_paper': exam_paper,
        'questions': questions,
    }
    
    return render(request, 'admin/exam_paper_detail.html', context)


@staff_member_required(login_url='/admin/login/')
def question_create(request, exam_id):
    """Create a new question for an exam"""
    exam_paper = get_object_or_404(ExamPaper, id=exam_id)
    
    if request.method == 'POST':
        question_type = request.POST.get('question_type')
        question_text = request.POST.get('question_text')
        marks = request.POST.get('marks', 1)
        order = request.POST.get('order', 0)
        
        question = Question(
            exam_paper=exam_paper,
            question_text=question_text,
            question_type=question_type,
            marks=marks,
            order=order
        )
        
        if question_type == 'mcq':
            question.option_a = request.POST.get('option_a')
            question.option_b = request.POST.get('option_b')
            question.option_c = request.POST.get('option_c')
            question.option_d = request.POST.get('option_d')
            question.correct_answer = request.POST.get('correct_answer')
        else:  # subjective
            question.model_answer = request.POST.get('model_answer')
        
        question.save()
        
        # Update total marks
        total_marks = exam_paper.questions.aggregate(Sum('marks'))['marks__sum'] or 0
        exam_paper.total_marks = total_marks
        exam_paper.save()
        
        messages.success(request, "Question added successfully!")
        return redirect('exam_paper_detail', exam_id=exam_id)
    
    # Get next order number
    last_question = exam_paper.questions.order_by('-order').first()
    next_order = (last_question.order + 1) if last_question else 1
    
    context = {
        'exam_paper': exam_paper,
        'next_order': next_order,
    }
    
    return render(request, 'admin/question_create.html', context)


@staff_member_required(login_url='/admin/login/')
def question_edit(request, question_id):
    """Edit a question"""
    question = get_object_or_404(Question, id=question_id)
    exam_paper = question.exam_paper
    
    if request.method == 'POST':
        question.question_text = request.POST.get('question_text')
        question.marks = request.POST.get('marks', 1)
        question.order = request.POST.get('order', 0)
        
        if question.question_type == 'mcq':
            question.option_a = request.POST.get('option_a')
            question.option_b = request.POST.get('option_b')
            question.option_c = request.POST.get('option_c')
            question.option_d = request.POST.get('option_d')
            question.correct_answer = request.POST.get('correct_answer')
        else:
            question.model_answer = request.POST.get('model_answer')
        
        question.save()
        
        # Update total marks
        total_marks = exam_paper.questions.aggregate(Sum('marks'))['marks__sum'] or 0
        exam_paper.total_marks = total_marks
        exam_paper.save()
        
        messages.success(request, "Question updated successfully!")
        return redirect('exam_paper_detail', exam_id=exam_paper.id)
    
    context = {
        'question': question,
        'exam_paper': exam_paper,
    }
    
    return render(request, 'admin/question_edit.html', context)


@staff_member_required(login_url='/admin/login/')
def question_delete(request, question_id):
    """Delete a question"""
    question = get_object_or_404(Question, id=question_id)
    exam_id = question.exam_paper.id
    exam_paper = question.exam_paper
    
    question.delete()
    
    # Update total marks
    total_marks = exam_paper.questions.aggregate(Sum('marks'))['marks__sum'] or 0
    exam_paper.total_marks = total_marks
    exam_paper.save()
    
    messages.success(request, "Question deleted successfully!")
    return redirect('exam_paper_detail', exam_id=exam_id)


@staff_member_required(login_url='/admin/login/')
def pending_evaluations_list(request):
    """List all pending subjective evaluations"""
    pending_attempts = StudentExamAttempt.objects.filter(
        status='submitted'
    ).select_related('student', 'exam_paper').order_by('-submitted_at')
    
    context = {
        'pending_attempts': pending_attempts,
    }
    
    return render(request, 'admin/pending_evaluations_list.html', context)


@staff_member_required(login_url='/admin/login/')
def evaluate_subjective_answers(request, attempt_id):
    """Evaluate subjective answers for a student attempt"""
    attempt = get_object_or_404(StudentExamAttempt, id=attempt_id)
    
    # Get all subjective answers
    subjective_answers = attempt.answers.filter(
        question__question_type='subjective'
    ).select_related('question')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        logger.info(f"Evaluation action triggered: {action} for attempt {attempt_id}")
        
        if action == 'auto_evaluate':
            # Auto-evaluate using Groq AI service
            try:
                groq_service = get_groq_service()
                logger.info(f"Groq service initialized successfully")
                
                evaluated_count = 0
                error_count = 0
                
                for answer in subjective_answers:
                    if not answer.answer_text:
                        answer.marks_obtained = 0
                        answer.ai_feedback = "No answer provided"
                        answer.evaluated_by = request.user
                        answer.evaluated_at = timezone.now()
                        answer.save()
                        logger.info(f"Answer {answer.id}: No text provided")
                        continue
                    
                    try:
                        logger.info(f"Evaluating answer {answer.id} for question: {answer.question.question_text[:50]}...")
                        
                        # Call Groq service for evaluation
                        evaluation = groq_service.evaluate_subjective_answer(
                            question_text=answer.question.question_text,
                            model_answer=answer.question.model_answer,
                            student_answer=answer.answer_text,
                            max_marks=answer.question.marks
                        )
                        
                        logger.info(f"Groq evaluation result: marks={evaluation['marks']}, feedback_length={len(evaluation['feedback'])}")
                        
                        answer.marks_obtained = evaluation['marks']
                        answer.ai_feedback = evaluation['feedback']
                        answer.evaluated_by = request.user
                        answer.evaluated_at = timezone.now()
                        answer.save()
                        
                        evaluated_count += 1
                        logger.info(f"Answer {answer.id} evaluated successfully: {evaluation['marks']}/{answer.question.marks} marks")
                        
                    except Exception as e:
                        error_count += 1
                        error_msg = f"Error during AI evaluation: {str(e)}"
                        logger.error(f"Answer {answer.id} evaluation failed: {error_msg}")
                        answer.ai_feedback = error_msg
                        answer.marks_obtained = 0
                        answer.evaluated_by = request.user
                        answer.evaluated_at = timezone.now()
                        answer.save()
                
                if error_count > 0:
                    messages.warning(request, f"⚠️ {evaluated_count} answers evaluated successfully, {error_count} failed. Check console for errors.")
                else:
                    messages.success(request, f"✅ Subjective answers auto-evaluated successfully using Groq AI! ({evaluated_count} answers)")
                    
            except Exception as e:
                logger.error(f"Failed to initialize Groq service: {str(e)}")
                messages.error(request, f"❌ Failed to initialize Groq AI service: {str(e)}")
            
        elif action == 'manual_save':
            # Manual override
            saved_count = 0
            for answer in subjective_answers:
                marks_key = f'marks_{answer.id}'
                feedback_key = f'feedback_{answer.id}'
                
                if marks_key in request.POST:
                    answer.marks_obtained = float(request.POST.get(marks_key, 0))
                    answer.ai_feedback = request.POST.get(feedback_key, '')
                    answer.manually_overridden = True
                    answer.evaluated_by = request.user
                    answer.evaluated_at = timezone.now()
                    answer.save()
                    saved_count += 1
            
            messages.success(request, f"✅ Manual evaluation saved successfully! ({saved_count} answers)")
        
        # Calculate total marks (include both MCQ and subjective)
        total_marks_obtained = attempt.answers.aggregate(Sum('marks_obtained'))['marks_obtained__sum'] or 0
        attempt.total_marks_obtained = total_marks_obtained
        attempt.percentage = (total_marks_obtained / attempt.exam_paper.total_marks * 100) if attempt.exam_paper.total_marks > 0 else 0
        attempt.status = 'evaluated'
        attempt.save()
        
        logger.info(f"Attempt {attempt_id} total marks: {total_marks_obtained}/{attempt.exam_paper.total_marks} ({attempt.percentage}%)")
        
        return redirect('publish_result', attempt_id=attempt.id)
    
    context = {
        'attempt': attempt,
        'subjective_answers': subjective_answers,
    }
    
    return render(request, 'admin/evaluate_subjective_answers.html', context)







@staff_member_required(login_url='/admin/login/')
def results_management(request):
    """Manage all published and unpublished results"""
    published_results = Result.objects.filter(published=True).select_related(
        'attempt__student', 'attempt__exam_paper'
    ).order_by('-published_at')
    
    unpublished_attempts = StudentExamAttempt.objects.filter(
        status='evaluated',
        result__isnull=True
    ).select_related('student', 'exam_paper').order_by('-submitted_at')
    
    context = {
        'published_results': published_results,
        'unpublished_attempts': unpublished_attempts,
    }
    
    return render(request, 'admin/results_management.html', context)





@staff_member_required(login_url='/admin/login/')
def publish_result(request, attempt_id):
    """Publish a single result for a student attempt"""
    attempt = get_object_or_404(StudentExamAttempt, id=attempt_id)
    
    if request.method == 'POST':
        # Calculate grade based on percentage
        percentage = attempt.percentage or 0
        if percentage >= 90:
            grade = 'A+'
        elif percentage >= 80:
            grade = 'A'
        elif percentage >= 70:
            grade = 'B+'
        elif percentage >= 60:
            grade = 'B'
        elif percentage >= 50:
            grade = 'C+'
        elif percentage >= 40:
            grade = 'C'
        else:
            grade = 'F'
        
        # Check if result already exists
        result, created = Result.objects.get_or_create(
            attempt=attempt,
            defaults={
                'total_marks': attempt.exam_paper.total_marks,
                'marks_obtained': attempt.total_marks_obtained or 0,
                'percentage': percentage,
                'grade': grade,
                'published_by': request.user,
                'published_at': timezone.now(),
                'published': True
            }
        )
        
        if not created:
            # Update existing result
            result.total_marks = attempt.exam_paper.total_marks
            result.marks_obtained = attempt.total_marks_obtained or 0
            result.percentage = percentage
            result.grade = grade
            result.published_by = request.user
            result.published_at = timezone.now()
            result.published = True
            result.save()
        
        # Send email notification if email service is available
        try:
            from .email_service import send_result_published_email
            email_sent = send_result_published_email(attempt.student, result, attempt)
            if email_sent:
                result.email_sent = True
                result.email_sent_at = timezone.now()
                result.save()
                messages.success(request, f"Result for {attempt.student.name} published and email notification sent!")
            else:
                messages.success(request, f"Result for {attempt.student.name} published! (Email notification failed)")
        except Exception as e:
            logger.error(f"Email sending failed: {str(e)}")
            messages.success(request, f"Result for {attempt.student.name} published successfully!")
        
        return redirect('results_management')
    
    # GET request - show confirmation page
    context = {
        'attempt': attempt,
        'student': attempt.student,
        'exam': attempt.exam_paper,
        'total_obtained': attempt.total_marks_obtained or 0,
        'percentage': attempt.percentage or 0,
        'passed': (attempt.percentage or 0) >= (attempt.exam_paper.passing_marks or 40)
    }
    
    return render(request, 'admin/publish_result_confirm.html', context)




@staff_member_required(login_url='/admin/login/')
def publish_exam(request, exam_id):
    """Publish an exam to make it visible to students"""
    exam_paper = get_object_or_404(ExamPaper, id=exam_id)
    
    # Check if exam has questions
    if exam_paper.questions.count() == 0:
        messages.error(request, "Cannot publish exam without questions!")
        return redirect('exam_paper_detail', exam_id=exam_id)
    
    exam_paper.published = True
    exam_paper.save()
    
    messages.success(request, f"Exam '{exam_paper.title}' has been published! Students can now see it.")
    return redirect('exam_paper_detail', exam_id=exam_id)


@staff_member_required(login_url='/admin/login/')
def unpublish_exam(request, exam_id):
    """Unpublish an exam to hide it from students"""
    exam_paper = get_object_or_404(ExamPaper, id=exam_id)
    
    exam_paper.published = False
    exam_paper.save()
    
    messages.warning(request, f"Exam '{exam_paper.title}' has been unpublished. Students cannot see it now.")
    return redirect('exam_paper_detail', exam_id=exam_id)