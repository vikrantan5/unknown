"""
Email Service for sending notifications via SendGrid
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


def send_result_published_email(student, result, attempt):
    """
    Send email notification when exam result is published
    
    Args:
        student: Student instance
        result: Result instance
        attempt: StudentExamAttempt instance
    """
    try:
        subject = f"Exam Result Published - {attempt.exam_paper.title}"
        
        # Create HTML message
        html_message = f"""
        <html>
        <body>
            <h2>Dear {student.name},</h2>
            <p>Your exam result for <strong>{attempt.exam_paper.title}</strong> ({attempt.exam_paper.subject}) has been published.</p>
            
            <h3>Result Summary:</h3>
            <ul>
                <li><strong>Total Marks:</strong> {result.total_marks}</li>
                <li><strong>Marks Obtained:</strong> {result.marks_obtained}</li>
                <li><strong>Percentage:</strong> {result.percentage}%</li>
                <li><strong>Grade:</strong> {result.grade}</li>
            </ul>
            
            {f'<p><strong>Remarks:</strong> {result.remarks}</p>' if result.remarks else ''}
            
            <p>Please login to your dashboard to view detailed results.</p>
            
            <p>Best regards,<br>
            Exam Proctoring Team</p>
        </body>
        </html>
        """
        
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Result published email sent to {student.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send result email to {student.email}: {str(e)}")
        return False


def send_approval_email(student, approved_by):
    """
    Send email notification when student account is approved
    
    Args:
        student: Student instance
        approved_by: User who approved the account
    """
    try:
        subject = "Account Approved - Online Exam Proctoring System"
        
        html_message = f"""
        <html>
        <body>
            <h2>Dear {student.name},</h2>
            <p>Congratulations! Your account has been <strong>approved</strong>.</p>
            
            <p>You can now login and access available exams.</p>
            
            <h3>Account Details:</h3>
            <ul>
                <li><strong>Name:</strong> {student.name}</li>
                <li><strong>Email:</strong> {student.email}</li>
                <li><strong>Status:</strong> Approved</li>
            </ul>
            
            <p>Please login to your dashboard to view available exams.</p>
            
            <p>Best regards,<br>
            Exam Proctoring Team</p>
        </body>
        </html>
        """
        
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Approval email sent to {student.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send approval email to {student.email}: {str(e)}")
        return False


def send_rejection_email(student, rejection_reason=None):
    """
    Send email notification when student account is rejected
    
    Args:
        student: Student instance
        rejection_reason: Optional reason for rejection
    """
    try:
        subject = "Account Status - Online Exam Proctoring System"
        
        html_message = f"""
        <html>
        <body>
            <h2>Dear {student.name},</h2>
            <p>We regret to inform you that your account registration could not be approved at this time.</p>
            
            {f'<p><strong>Reason:</strong> {rejection_reason}</p>' if rejection_reason else ''}
            
            <p>If you believe this is an error or need further assistance, please contact the administration.</p>
            
            <p>Best regards,<br>
            Exam Proctoring Team</p>
        </body>
        </html>
        """
        
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Rejection email sent to {student.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send rejection email to {student.email}: {str(e)}")
        return False
