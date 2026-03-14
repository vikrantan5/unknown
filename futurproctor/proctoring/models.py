# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import pytz
from django.core.files.base import ContentFile
from django.utils import timezone
import pytz
from datetime import datetime  

# Define Indian Standard Time Zone
IST_TZ = pytz.timezone('Asia/Kolkata')

# Helper function to get IST time
def get_ist_time():
    return timezone.now().astimezone(IST_TZ)

def get_ist_time_str():
    return get_ist_time().strftime('%Y-%m-%d %I:%M:%S %p %Z')

# Backward compatibility alias for old migrations
# Old migrations reference get_nepal_time, so we keep it as an alias
get_nepal_time = get_ist_time
get_nepal_time_str = get_ist_time_str

class Student(models.Model):
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student', null=True, blank=True)
    name = models.CharField(max_length=255)
    address = models.TextField(null=True, blank=True)
    email = models.EmailField(unique=True)
    photo = models.ImageField(upload_to='student_photos/')
    face_encoding = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(default=datetime.now())
    feedback = models.TextField(null=True, blank=True, max_length=1000)
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_students')
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

class Exam(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exams', null=True, blank=True)
    exam_name = models.CharField(max_length=255, default='Default Exam Name')
    total_questions = models.IntegerField(null=True, blank=True)
    correct_answers = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(default=datetime.now())
    status = models.CharField(
        max_length=50,
        choices=[('ongoing', 'Ongoing'), ('completed', 'Completed'), ('cancelled', 'Cancelled')],
        default='ongoing'
    )
    percentage_score = models.FloatField(null=True, blank=True)

    def calculate_percentage(self):
        if self.total_questions and self.total_questions > 0:
            self.percentage_score = round((self.correct_answers / self.total_questions) * 100, 2)
        else:
            self.percentage_score = 0.0
        self.save()

    def __str__(self):
        return f"{self.exam_name} - {self.student.name}"

class CheatingEvent(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='cheating_events',  # Added related_name for easier reverse lookups
        blank=True,
        null=True
    )
    cheating_flag = models.BooleanField(default=False)
    event_type = models.CharField(max_length=50, blank=True, null=True)
    # Use a single timestamp field. Here we use Nepal time.
    timestamp = models.DateTimeField(default=datetime.now())
    detected_objects = models.JSONField(default=list)
    tab_switch_count = models.IntegerField(default=0)

class CheatingImage(models.Model):
    event = models.ForeignKey(CheatingEvent, on_delete=models.CASCADE, related_name='cheating_images')
    image = models.ImageField(upload_to='cheating_images/')
    timestamp = models.DateTimeField(default=datetime.now())

class CheatingAudio(models.Model):
    event = models.ForeignKey(CheatingEvent, on_delete=models.CASCADE, related_name='cheating_audios')
    audio = models.FileField(upload_to='cheating_audios/', blank=True, null=True)
    timestamp = models.DateTimeField(default=datetime.now())













class ExamPaper(models.Model):
    """Exam paper with multi-subject support"""
    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    duration_minutes = models.IntegerField(help_text="Exam duration in minutes")
    exam_date = models.DateTimeField(help_text="Scheduled exam date and time")
    instructions = models.TextField(blank=True, null=True, help_text="Exam instructions for students")
    total_marks = models.IntegerField(default=0, help_text="Total marks for the exam")
    passing_marks = models.IntegerField(default=0, help_text="Minimum marks to pass")
    is_active = models.BooleanField(default=True, help_text="Is exam available for students")
    published = models.BooleanField(default=False, help_text="Is exam published and visible to students")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_exams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.subject}"
    @property
    def exam_status(self):
        """Get current exam status based on date and time"""
        now = timezone.now()
        exam_end_time = self.exam_date + timezone.timedelta(minutes=self.duration_minutes)
        
        if not self.published:
            return 'draft'
        elif now < self.exam_date:
            return 'upcoming'
        elif self.exam_date <= now <= exam_end_time:
            return 'live'
        else:
            return 'closed'
    
    @property
    def exam_status_display(self):
        """Get human-readable exam status"""
        status_map = {
            'draft': 'Draft',
            'upcoming': 'Upcoming',
            'live': 'Live',
            'closed': 'Closed'
        }
        return status_map.get(self.exam_status, 'Unknown')

    class Meta:
        ordering = ['-created_at']


class Question(models.Model):
    """Questions for exam papers - supports MCQ and Subjective"""
    QUESTION_TYPES = [
        ('mcq', 'Multiple Choice Question'),
        ('subjective', 'Subjective Question'),
    ]
    
    exam_paper = models.ForeignKey(ExamPaper, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField(help_text="The question text")
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='mcq')
    
    # For MCQ questions
    option_a = models.CharField(max_length=500, blank=True, null=True)
    option_b = models.CharField(max_length=500, blank=True, null=True)
    option_c = models.CharField(max_length=500, blank=True, null=True)
    option_d = models.CharField(max_length=500, blank=True, null=True)
    correct_answer = models.CharField(max_length=1, blank=True, null=True, help_text="A, B, C, or D")
    
    # For subjective questions
    model_answer = models.TextField(blank=True, null=True, help_text="Model answer for subjective questions")
    
    marks = models.IntegerField(default=1, help_text="Marks for this question")
    order = models.IntegerField(default=0, help_text="Order of question in exam")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.exam_paper.title} - Q{self.order}: {self.question_text[:50]}"

    class Meta:
        ordering = ['order']


class StudentExamAttempt(models.Model):
    """Track student's exam attempts"""
    STATUS_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('submitted', 'Submitted'),
        ('evaluated', 'Evaluated'),
        ('cancelled', 'Cancelled'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_attempts')
    exam_paper = models.ForeignKey(ExamPaper, on_delete=models.CASCADE, related_name='attempts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ongoing')
    
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    total_marks_obtained = models.FloatField(default=0.0)
    percentage = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.name} - {self.exam_paper.title} ({self.status})"

    class Meta:
        ordering = ['-started_at']


class StudentAnswer(models.Model):
    """Store student's answers for each question"""
    attempt = models.ForeignKey(StudentExamAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='student_answers')
    
    # For MCQ
    selected_option = models.CharField(max_length=1, blank=True, null=True, help_text="A, B, C, or D")
    is_correct = models.BooleanField(default=False)
    
    # For Subjective
    answer_text = models.TextField(blank=True, null=True, help_text="Student's subjective answer")
    
    # Evaluation
    marks_obtained = models.FloatField(default=0.0)
    ai_feedback = models.TextField(blank=True, null=True, help_text="AI-generated feedback for subjective answers")
    manually_overridden = models.BooleanField(default=False, help_text="Was this manually graded by admin?")
    evaluated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='evaluated_answers')
    evaluated_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.attempt.student.name} - {self.question.question_text[:30]}"


class Result(models.Model):
    """Published exam results"""
    GRADE_CHOICES = [
        ('A+', 'A+ (90-100%)'),
        ('A', 'A (80-89%)'),
        ('B+', 'B+ (70-79%)'),
        ('B', 'B (60-69%)'),
        ('C+', 'C+ (50-59%)'),
        ('C', 'C (40-49%)'),
        ('F', 'F (Below 40%)'),
    ]
    
    attempt = models.OneToOneField(StudentExamAttempt, on_delete=models.CASCADE, related_name='result')
    
    total_marks = models.FloatField()
    marks_obtained = models.FloatField()
    percentage = models.FloatField()
    grade = models.CharField(max_length=5, choices=GRADE_CHOICES)
    
    remarks = models.TextField(blank=True, null=True, help_text="Admin remarks")
    
    published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    published_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='published_results')
    
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.attempt.student.name} - {self.attempt.exam_paper.title} - {self.grade}"

    def calculate_grade(self):
        """Calculate grade based on percentage"""
        if self.percentage >= 90:
            return 'A+'
        elif self.percentage >= 80:
            return 'A'
        elif self.percentage >= 70:
            return 'B+'
        elif self.percentage >= 60:
            return 'B'
        elif self.percentage >= 50:
            return 'C+'
        elif self.percentage >= 40:
            return 'C'
        else:
            return 'F'

    class Meta:
        ordering = ['-published_at']