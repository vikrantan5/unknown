#!/usr/bin/env python
"""
Test SendGrid email configuration
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/app/temp_repo/futurproctor')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'futurproctor.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email_config():
    """Test if SendGrid is configured correctly"""
    print("=" * 60)
    print("SendGrid Email Configuration Test")
    print("=" * 60)
    
    # Display current settings
    print(f"📧 Email Settings:")
    print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    # Check if API key is set
    api_key = settings.EMAIL_HOST_PASSWORD
    if api_key and api_key.startswith('SG.'):
        print(f"   ✅ SendGrid API Key: {api_key[:10]}...{api_key[-10:]}")
    else:
        print(f"   ❌ SendGrid API Key: Not configured properly")
        return False
    
    # Test email send
    print(f"📨 Sending test email to: {settings.DEFAULT_FROM_EMAIL}")
    
    try:
        result = send_mail(
            subject='Test Email - FuturProctor System',
            message='This is a test email from your FuturProctor exam system. If you receive this, SendGrid is configured correctly!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        
        if result == 1:
            print("   ✅ Test email sent successfully!")
            print(f"   📬 Check your inbox at: {settings.DEFAULT_FROM_EMAIL}")
            return True
        else:
            print("   ❌ Email failed to send (no error but result=0)")
            return False
            
    except Exception as e:
        print(f"   ❌ Error sending email: {str(e)}")
        return False

if __name__ == '__main__':
    success = test_email_config()
    print("" + "=" * 60)
    if success:
        print("✅ SendGrid is configured correctly!")
    else:
        print("❌ SendGrid configuration failed. Please check your API key.")
    print("=" * 60)
