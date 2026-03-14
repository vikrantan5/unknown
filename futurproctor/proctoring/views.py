# Django Core Imports
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404  # Rendering templates, redirecting, and fetching objects
from django.http import JsonResponse, StreamingHttpResponse, HttpResponse, HttpResponseRedirect  # Handling HTTP responses
from django.contrib import messages  # Displaying success/error messages
from django.contrib.auth.decorators import login_required, user_passes_test  # Restricting views to logged-in users
from django.contrib.auth.models import User  # Accessing Django's built-in User model
from django.contrib.auth.hashers import make_password  # Hashing passwords securely
from django.contrib.auth import authenticate, login as auth_login  # Handling user authentication
from django.urls import reverse  # Generating dynamic URLs
from django.views.decorators.csrf import csrf_exempt  # Disabling CSRF protection for certain views (Use cautiously)
from django.utils.timezone import now  # Getting timezone-aware current time
from django.core.files.base import ContentFile  # Handling in-memory file storage
# import cv2
# import io
# from PIL import Image

# Models
from .models import Student, Exam, CheatingEvent, CheatingImage, CheatingAudio  # Importing custom models

# External Library Imports
import os  # Operating system utilities (e.g., file handling)
import json  # JSON handling (e.g., parsing request data)
import threading  # Running concurrent tasks (e.g., real-time monitoring)
import base64  # Encoding and decoding base64 (used for image handling)
# import numpy as np  # Numerical operations, especially for image processing
# import cv2  # OpenCV for computer vision tasks (e.g., face recognition)
import logging  # Logging errors and system activity
import time  # Time-based operations (e.g., timestamps)
# from PIL import Image  # Image processing using the Pillow library
import io  # Handling in-memory file operations


# Import optional dependencies
try:
    import cv2  # OpenCV for computer vision tasks
    import numpy as np  # Numerical operations, especially for image processing
    from PIL import Image  # Image processing using the Pillow library
    CV2_AVAILABLE = True
except ImportError as e:
    print(f"Warning: OpenCV/NumPy/PIL not installed - {e}. Camera features may not work.")
    CV2_AVAILABLE = False

# Machine Learning Imports (Custom AI Models for Proctoring)
try:
    from .ml_models.object_detection import detectObject  # Detecting objects in the exam environment
    from .ml_models.audio_detection import audio_detection  # Detecting external sounds for cheating detection
    from .ml_models.gaze_tracking import gaze_tracking # Tracking eye gaze to detect focus and distractions
    ML_MODELS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ML models import failed - {e}. Proctoring features may not work.")
    ML_MODELS_AVAILABLE = False

# Fix: Import face_recognition (Previously missing)
try:
    import face_recognition  # Used for facial recognition, comparing student faces with stored images
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    print("Warning: face_recognition not installed. Face recognition features may not work.")
    FACE_RECOGNITION_AVAILABLE = False

# Fix: Proper datetime handling for Nepal Time Zone (Asia/Kathmandu)
import pytz  # For timezone handling
from datetime import datetime  # Standard date and time handling

# Define Nepal Time Zone
# Fix: Proper datetime handling for Indian Standard Time Zone (Asia/Kolkata)
import pytz  # For timezone handling
from datetime import datetime  # Standard date and time handling

# Define Indian Standard Time Zone
IST_TZ = pytz.timezone('Asia/Kolkata')

# Function to get IST current time
def get_ist_time():
    """
    Returns the current time in IST timezone.
    This ensures all timestamps are consistent with the local time.
    """
    return datetime.now(IST_TZ)

# Backward compatibility alias for old code/migrations
get_nepal_time = get_ist_time


# Home page view
def home(request):
    """
    Renders the home page of the application.
    This is the entry point for users visiting the site.
    """
    return render(request, 'home.html')  # Render the home page


# Registration View
def registration(request):
    """
    Handles user registration, including:
    - Capturing form data (name, address, email, password, and photo)
    - Decoding and processing a base64-encoded image
    - Extracting face encoding using face recognition
    - Creating a new User and Student instance
    - Handling errors and displaying messages
    """
    if request.method == 'POST':  # Check if form is submitted
        # Retrieve form data
        name = request.POST['name']
        address = request.POST['address']
        email = request.POST['email']
        password = request.POST['password']
        captured_photo = request.POST.get('photo_data')  # Base64 image data

        try:
            # Decode the base64 image (photo_data comes in "data:image/png;base64,ENCODED_DATA")
            img_data = base64.b64decode(captured_photo.split(',')[1])
            nparr = np.frombuffer(img_data, np.uint8)  # Convert to numpy array
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # Convert to OpenCV image

            # Extract face encoding from the image
            face_encoding = get_face_encoding(image)  # Function should return a list or None
            if face_encoding is None:  # No face detected
                messages.error(request, "No face detected. Please try again.")
                return redirect('registration')
        except Exception as e:
            messages.error(request, f"Error processing image: {e}")
            return redirect('registration')

        # Check if the email is already registered
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('registration')

        try:
            # Create a new User instance
            user = User.objects.create(
                username=email,  # Use email as username for uniqueness
                email=email,
                first_name=name.split(' ')[0],  # Extract first name
                last_name=' '.join(name.split(' ')[1:]) if ' ' in name else '',  # Extract last name if available
                password=make_password(password),  # Hash password for security
            )

            # Create a linked Student instance
            student = Student(
                user=user,
                name=name,
                address=address,
                email=email,
                photo=ContentFile(img_data, name=f"{name}_photo.jpg"),  # Save the uploaded image
                face_encoding=face_encoding.tolist(),  # Convert NumPy array to list
            )
            student.save()

            # Store user session data
            request.session['user_id'] = user.id
            request.session['user_name'] = user.first_name

            messages.success(request, "Registration successful!")
            return redirect('login')  # Redirect to login page
        except Exception as e:
            messages.error(request, f"Error creating user: {e}")
            return redirect('registration')

    return render(request, 'registration.html')  # Render the registration page


# Helper function to extract face encoding
def get_face_encoding(image):
    """
    Extracts face encoding from an image using the face_recognition library.
    - Detects faces in the image.
    - Returns the encoding of the first face found.
    
    - Returns None if no faces are detected or if face_recognition is not available.
    """
    if not FACE_RECOGNITION_AVAILABLE:
        print("Warning: face_recognition not available")
        return None
    
    face_locations = face_recognition.face_locations(image)  # Detect faces in the image
    if not face_locations:
        return None  # Return None if no faces are detected
    return face_recognition.face_encodings(image, face_locations)[0]  # Return the first face encoding

# Helper function to match face encodings
def match_face_encodings(captured_encoding, stored_encoding):
    if not FACE_RECOGNITION_AVAILABLE:
        return False
    return face_recognition.compare_faces([stored_encoding], captured_encoding)[0]  # Compare encodings


#Login View
@csrf_exempt  # Allow POST requests without CSRF token (for simplicity, use proper CSRF handling in production)
def login(request):
    """
    Handles user login with email, password, and facial recognition.
    - Authenticates the user using email and password.
    - Compares the captured photo with the stored face encoding.
    - Logs the user in if all checks pass.
    - Returns JSON responses for success or failure.
    """
    if request.method == "POST":
        # Retrieve form data
        email = request.POST.get('email')
        password = request.POST.get('password')
        captured_photo_data = request.POST.get('captured_photo')

        # Validate required fields
        if not email or not password or not captured_photo_data:
            return JsonResponse({"success": False, "error": "Missing email, password, or captured photo."})

        try:
            # Decode the base64 image (remove the "data:image/png;base64," prefix)
            captured_photo_data = captured_photo_data.split(',')[1]
            captured_photo = base64.b64decode(captured_photo_data)

            # Convert the image to a NumPy array and decode it using OpenCV
            nparr = np.frombuffer(captured_photo, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Extract face encoding from the captured image
            captured_encoding = get_face_encoding(image)
            if captured_encoding is None:
                return JsonResponse({"success": False, "error": "No face detected in the captured photo."})

            # Authenticate the user using email and password
            user = authenticate(request, username=email, password=password)
            if user is None:
                return JsonResponse({"success": False, "error": "Invalid email or password."})

            try:
                # Fetch the associated student record
                student = user.student
                stored_encoding = np.array(student.face_encoding)

                # Compare the captured face encoding with the stored encoding
                if match_face_encodings(captured_encoding, stored_encoding):
                    # Log the user in
                    auth_login(request, user)

                    # Store student data in the session for future use
                    request.session['student_id'] = student.id
                    request.session['student_name'] = student.name


                       # Redirect to appropriate dashboard based on user role
                    if user.is_staff or user.is_superuser:
                        redirect_url = "/admin/dashboard-enhanced/"
                    else:
                        redirect_url = "/student/dashboard-enhanced/"

                    # Return a success response with redirect URL and student name
                    return JsonResponse({
                        "success": True,
                        # "redirect_url": "/dashboard/",
                        "redirect_url": redirect_url,
                        "student_name": student.name
                    })
                else:
                    return JsonResponse({"success": False, "error": "Face does not match our records."})

            except Student.DoesNotExist:
                return JsonResponse({"success": False, "error": "No student record associated with this account."})

        except Exception as e:
            # Handle any unexpected errors during the login process
            return JsonResponse({"success": False, "error": f"Error processing image: {str(e)}"})

    # Render the login page for GET requests
    return render(request, "login.html")

# Logout View 
def logout_view(request):
    """
    Handles user logout.
    - Clears all session data.
    - Displays a success message.
    - Redirects the user to the home page.
    """
    request.session.flush()  # Clear all session data
    messages.success(request, "You have been logged out.")  # Display a success message
    return redirect('home')  # Redirect to the home page

# Video feed generation for the webcam
def gen_frames():
    """
    Generates a live video feed from the webcam.
    - Captures frames from the webcam using OpenCV.
    - Encodes each frame as a JPEG image.
    - Yields the frames as a streaming response for real-time display in the browser.
    """
    camera = cv2.VideoCapture(0)  # Open the default webcam (index 0)
    if not camera.isOpened():  # Check if the webcam was successfully opened
        raise RuntimeError("Could not open webcam.")

    while True:
        success, frame = camera.read()  # Read a frame from the webcam
        if not success:
            break  # Exit the loop if the frame cannot be read

        # Encode the frame as a JPEG image
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()  # Convert the frame to bytes

        # Yield the frame as part of a streaming response
        yield (b'--framern'
               b'Content-Type: image/jpegrnrn' + frame + b'rn')

    # Release the webcam when the loop ends
    camera.release()


# Video feed view
def video_feed(request):
    """
    Streams the live video feed to the browser.
    - Uses the `gen_frames` generator to fetch frames from the webcam.
    - Returns a `StreamingHttpResponse` with the appropriate content type for real-time video streaming.
    """
    return StreamingHttpResponse(
        gen_frames(),  # Use the generator to stream frames
        content_type='multipart/x-mixed-replace; boundary=frame'  # Required for live video streaming
    )


# Stop video feed view
def stop_event(request):
    """
    Dummy endpoint for stopping the video feed.
    - Can be extended to handle cleanup or other actions when the video feed is stopped.
    - Returns a JSON response indicating success.
    """
    return JsonResponse({'status': 'success'})  # Simple response for stopping the video feed

#Dashboard View
@login_required
def dashboard(request):
    """
    Redirects to appropriate enhanced dashboard based on user role.
    - Admin/Staff users → admin/dashboard-enhanced/
    - Regular students → student/dashboard-enhanced/
    """
    user = request.user
    
    # Redirect to appropriate dashboard based on user role
    if user.is_staff or user.is_superuser:
        return redirect('admin_dashboard_enhanced')
    else:
        return redirect('student_dashboard_enhanced')



# -------------------------Video Detection Thread----------------------------------
from django.utils import timezone
import pytz

# Define Indian Standard Time Zone
IST_TZ = pytz.timezone('Asia/Kolkata')
# Backward compatibility: Keep old timezone variable name for migrations
NEPAL_TZ = IST_TZ  # Now points to IST instead of Nepal time

# Helper function to get IST time
def get_ist_time():
    return timezone.now().astimezone(IST_TZ)

def get_ist_time_str():
    return get_ist_time().strftime('%Y-%m-%d %I:%M:%S %p %Z')

# Backward compatibility alias for old code
get_nepal_time = get_ist_time
get_nepal_time_str = get_ist_time_str


logger = logging.getLogger(__name__)

# Global variables for warnings and background processes
warning = None
last_audio_detected_time = time.time()
stop_event = threading.Event()  # To stop background threads

# Function to process each frame
def process_frame(frame, request):
    """Process a single frame for cheating detection."""
    global warning
    labels, processed_frame, person_count, detected_objects = detectObject(frame)
    cheating_event = None

    # Extract object names
    detected_labels = [label for label, _ in labels]
    # Check for cheating conditions
    if any(label in ["cell phone", "book"] for label in detected_labels):
        warning = f"ALERT: {', '.join(detected_labels)} detected!"  # Corrected formatting
        cheating_event, _ = CheatingEvent.objects.get_or_create(
            student=request.user.student,
            cheating_flag=True,
            event_type="object_detected"
        )
        save_cheating_event(frame, request, cheating_event, detected_objects)

    if person_count > 1:
        warning = "ALERT: Multiple persons detected!"
        cheating_event, _ = CheatingEvent.objects.get_or_create(
            student=request.user.student,
            cheating_flag=True,
            event_type="multiple_persons"
        )
        save_cheating_event(frame, request, cheating_event, detected_objects)

    gaze = gaze_tracking(frame)
    if gaze["gaze"] != "center":
        warning = "ALERT: Candidate not looking at the screen!"
        cheating_event, _ = CheatingEvent.objects.get_or_create(
            student=request.user.student,
            cheating_flag=True,
            event_type="gaze_detected"
        )
        save_cheating_event(frame, request, cheating_event, detected_objects)

# Function to process audio
def process_audio(request):
    """Continuously process audio for cheating detection."""
    global last_audio_detected_time, warning

    while not stop_event.is_set():  # Check if stop_event is triggered
        audio = audio_detection()
        if audio["audio_detected"]:
            warning = "ALERT: Suspicious audio detected!"
            cheating_event, _ = CheatingEvent.objects.get_or_create(
                student=request.user.student,
                cheating_flag=True,
                event_type="audio_detected"
            )
            save_cheating_event(None, request, cheating_event, audio_data=audio["audio_data"])
            last_audio_detected_time = time.time()

        if time.time() - last_audio_detected_time > 5:
            warning = None

        time.sleep(2)  # Avoid excessive CPU usage

    print("Audio processing stopped.")  # Debugging to confirm the thread exits



# Background processing for video
def background_processing(request):
    """Runs video processing in the background."""
    cap = cv2.VideoCapture(0)
    frame_count = 0

    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % 2 == 0:
            process_frame(frame, request)
        
        frame_count += 1
        time.sleep(0.5)
    
    cap.release()


# Helper function to create a WAV file from raw audio bytes
import io
import wave

def create_wav_bytes(raw_audio, channels=1, sampwidth=2, framerate=48000):
    """
    Wrap raw PCM audio bytes with a WAV header.
    
    :param raw_audio: The raw audio bytes (concatenated frames)
    :param channels: Number of audio channels (1 for mono)
    :param sampwidth: Sample width in bytes (2 for 16-bit audio)
    :param framerate: Frame rate (sample rate)
    :return: Audio data in WAV format as bytes
    """
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(framerate)
        wf.writeframes(raw_audio)
    return wav_buffer.getvalue()

## Function to save cheating event
def save_cheating_event(frame, request, cheating_event, detected_objects=None, audio_data=None):
    """Save cheating event along with images and audio in the database."""
    try:
        
        # Save detected objects
        if detected_objects:
            cheating_event.detected_objects = detected_objects  # Save as JSON
            cheating_event.save()
        # Save up to 10 sample images per event
        if frame is not None and cheating_event.cheating_images.count() < 10:
            try:
                image_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                image_io = io.BytesIO()
                image_pil.save(image_io, format="JPEG", quality=85)
                image_content = image_io.getvalue()
                
                cheating_image = CheatingImage(event=cheating_event)
                cheating_image.image.save(
                    f"cheating_{time.time()}.jpg", 
                    ContentFile(image_content), 
                    save=True
                )
            except Exception as e:
                logger.error(f"Error processing image: {e}")
        
        # Save audio data
        if audio_data:
            try:
                # Convert raw audio bytes to a proper WAV file bytes.
                wav_data = create_wav_bytes(audio_data, channels=1, sampwidth=2, framerate=48000)
                cheating_audio = CheatingAudio(event=cheating_event)
                cheating_audio.audio.save(
                    f"cheating_audio_{time.time()}.wav", 
                    ContentFile(wav_data), 
                    save=True
                )
            except Exception as e:
                logger.error(f"Error processing audio: {e}")

        logger.info(f"Cheating event saved for student {request.user.student.id}")
    
    except Exception as e:
        logger.error(f"Error saving cheating event: {e}")

## Exam Page View
@login_required
def exam(request):
    """Start the exam and initialize proctoring."""
    try:
        # Get the Student instance associated with the logged-in user
        student = request.user.student
    except Student.DoesNotExist:
        # Handle the case where the user does not have a linked Student instance
        return HttpResponse("Student profile not found. Please contact support.", status=404)

    # Get the tab switch count from the CheatingEvent model
    violations = CheatingEvent.objects.filter(student=student).first()
    tab_count = violations.tab_switch_count if violations else 0

    # Load exam questions from the JSON file
    try:
        with open("C://Users//ASUS//Downloads//AI-Based-online-exam-proctoring-System//futurproctor//proctoring//dummy_data//ai.json") as file:
            data = json.load(file)
        questions = data.get("questions", [])
    except FileNotFoundError:
        return HttpResponse("Error: Questions file not found!", status=404)
    except json.JSONDecodeError:
        return HttpResponse("Error: Failed to parse the questions file!", status=400)

    # Start background processing threads for video and audio monitoring
    global stop_event
    stop_event.clear()  # Reset the stop event flag
    threading.Thread(target=background_processing, args=(request,), daemon=True).start()
    threading.Thread(target=process_audio, args=(request,), daemon=True).start()

    # Render the exam template with questions and tab count
    return render(request, 'exam.html', {
        'questions': questions,
        
        'warning': warning,
        'tab_count': tab_count,
    })

# Submit exam
@login_required
def submit_exam(request):
    if request.method == 'POST':
        # Stop the background threads
        global stop_event
        stop_event.set()
        user = request.user

        # Load questions from ai.json
        try:
            with open('C://Users//ASUS//Downloads//AI-Based-online-exam-proctoring-System//futurproctor//proctoring//dummy_data//ai.json', 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            return HttpResponse("Error: Questions file not found!", status=404)
        except json.JSONDecodeError:
            return HttpResponse("Error: Failed to parse the questions file!", status=400)

        questions = data.get('questions', [])
        total_questions = len(questions)
        correct_answers = 0

        # Check answers
        for question in questions:
            question_id = question['id']
            user_answer = request.POST.get(f'answer_{question_id}')
            if user_answer == question['correct_answer']:
                correct_answers += 1

        # Save exam result
        exam = Exam(
            student=user.student,
            total_questions=total_questions,
            correct_answers=correct_answers,
            timestamp=timezone.now()
        )
        exam.save()

        # Redirect to success page
        messages.success(request, 'You have successfully completed the exam!')
        return redirect('exam_submission_success')

    return HttpResponse("Invalid request method.", status=400)

# Tab switch tracking
stop_event = threading.Event()


# Set up logging
logger = logging.getLogger(__name__)

# Tab switch tracking View
@login_required
def record_tab_switch(request):
    if request.method == "POST":
        # Get the current student
        student = request.user.student
        logger.info(f"Student: {student}")

        # # Get the active exam for the student
        # active_exam = Exam.objects.filter(student=student, status='ongoing').first()
        # if not active_exam:
        #     logger.error("No active exam found for the student")
        #     return JsonResponse({"error": "No active exam found for the student"}, status=400)

        # logger.info(f"Active Exam: {active_exam}")

        # Get or create a CheatingEvent for the student and exam
        cheating_event, created = CheatingEvent.objects.get_or_create(
            student=student,
            # exam=active_exam,
            event_type='tab_switch',  # Specify the event type
            defaults={
                'cheating_flag': False,
                'tab_switch_count': 0,
            }
        )

        logger.info(f"Cheating Event: {cheating_event}, Created: {created}")

        # Increment the tab switch count
        cheating_event.tab_switch_count += 1
        logger.info(f"Updated Tab Switch Count: {cheating_event.tab_switch_count}")

        # Set cheating_flag based on tab_switch_count
        cheating_event.cheating_flag = cheating_event.tab_switch_count >= 1
        logger.info(f"Cheating Flag: {cheating_event.cheating_flag}")

        # Save the updated CheatingEvent
        cheating_event.save()
        logger.info("Cheating Event saved successfully")

        # If tab switches exceed 5, take action
        if cheating_event.tab_switch_count > 5:
            stop_event.set()  # Stop background threads (ensure stop_event is defined)
            logger.info("Tab switches exceeded 5, terminated from the exam")
            return JsonResponse({
                "status": "terminated",
                "message": "You have exceeded the allowed tab switches. Your exam is terminated."
            }, status=200)
        # Return a JSON response with the updated count and flag
        return JsonResponse({
            "status": "updated",
            "count": cheating_event.tab_switch_count,
            "cheating_flag": cheating_event.cheating_flag,
            "message": f"Tab switch detected! Total switches: {cheating_event.tab_switch_count}"
        }, status=200)

    return JsonResponse({"error": "Invalid request"}, status=400)


# Exam submission success page
def exam_submission_success(request):
    return render(request, 'exam_submission_success.html')

# Result page
@login_required
def result(request):
    user = request.user
    try:
        exam = Exam.objects.filter(student=user.student).latest('timestamp')
    except Exam.DoesNotExist:
        return HttpResponse("No exam found for this user", status=404)

    total_questions = exam.total_questions
    correct_answers = exam.correct_answers
    percentage = (correct_answers / total_questions) * 100

    context = {
        'user_name': user.username,
        'score': correct_answers,
        'total_questions': total_questions,
        'percentage': round(percentage, 2),
    }

    return render(request, 'result.html', context)



from django.http import JsonResponse

# Fetch warnings
@csrf_exempt
def get_warning(request):
    """Fetch real-time warnings for the exam page."""
    global warning
    return JsonResponse({'warning': warning})

# Streaming notifications to the proctor
def proctor_notifications(request):
    """Stream real-time cheating events to the proctor."""
    def event_stream():
        while True:
            events = CheatingEvent.objects.filter(cheating_flag=True).order_by('-timestamp')[:5]
            if events:
                yield f"data: {json.dumps([str(event) for event in events])}nn"
            time.sleep(5)
    
    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')


## Logout
def logout(request):
    return render(request,'home.html')

# ----------------------Admin Plus Report Page ---------------------------------------

# Admin views
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Sum
from django.contrib.admin.views.decorators import staff_member_required
from .models import Student, Exam, CheatingEvent, CheatingImage, CheatingAudio
@staff_member_required(login_url='/admin/login/')
def admin_dashboard(request):
        """Redirect old admin dashboard to new enhanced version"""
        return redirect('admin_dashboard_enhanced')

## exam score
def calculate_exam_score(exam):
    """Calculate the exam score as a percentage."""
    if exam.total_questions and exam.total_questions > 0:
        return round((exam.correct_answers / exam.total_questions) * 100, 2)
    return 0.0


## Helper Function for aggregated detected objects
import json
def get_detected_objects_string(cheating_events):
    """Aggregate and convert the detected objects from all events into a list."""
    detected_objects_set = set()
    for event in cheating_events:
        # If detected_objects is not already a list, try converting it.
        objs = event.detected_objects
        if isinstance(objs, str):
            try:
                objs = json.loads(objs)
            except json.JSONDecodeError:
                objs = []
        # Now, objs should be a list so add each one to our set.
        if isinstance(objs, list):
            detected_objects_set.update(objs)
    return list(detected_objects_set)

### Report view
def report_page(request, student_id):

    student = get_object_or_404(Student, id=student_id)

    # Try to get data from the NEW exam system first (StudentExamAttempt + Result)
    from .models import StudentExamAttempt, Result
    
    latest_attempt = StudentExamAttempt.objects.filter(student=student).order_by('-submitted_at').first()
    
    # Initialize exam data variables
    exam_name = "Not Available"
    total_questions = 0
    correct_answers = 0
    percentage_score = 0
    
    if latest_attempt:
        # NEW SYSTEM: Use data from StudentExamAttempt and Result
        exam_name = latest_attempt.exam_paper.title
        
        # Get total questions from the exam paper
        total_questions = latest_attempt.exam_paper.questions.count()
        
        # Get correct MCQ answers count
        from .models import StudentAnswer
        correct_answers = StudentAnswer.objects.filter(
            attempt=latest_attempt,
            is_correct=True
        ).count()
        
        # Get percentage from attempt or result
        try:
            result = Result.objects.get(attempt=latest_attempt)
            percentage_score = result.percentage
        except Result.DoesNotExist:
            percentage_score = latest_attempt.percentage if latest_attempt.percentage else 0
    else:
        # OLD SYSTEM: Fallback to old Exam model
        exam = Exam.objects.filter(student=student).order_by('-timestamp').first()
        if exam:
            exam_name = exam.exam_name
            total_questions = exam.total_questions if exam.total_questions else 0
            correct_answers = exam.correct_answers if exam.correct_answers else 0
            percentage_score = exam.percentage_score if exam.percentage_score else 0

    # Create a mock exam object to pass to template (for backward compatibility)
    class ExamData:
        pass
    
    exam_obj = ExamData()
    exam_obj.exam_name = exam_name
    exam_obj.total_questions = total_questions
    exam_obj.correct_answers = correct_answers
    exam_obj.percentage_score = percentage_score

    cheating_events = CheatingEvent.objects.filter(student=student)

    detected_objects_list = get_detected_objects_string(cheating_events)
    detected_objects_str = ", ".join(detected_objects_list) if detected_objects_list else "No objects detected"

    total_tab_switch_count = cheating_events.aggregate(total=Sum('tab_switch_count'))['total'] or 0

    cheating_images_data = [
        {
            'url': img.image.url,
            'event_type': img.event.event_type,
            'timestamp': img.timestamp
        }
        for img in CheatingImage.objects.filter(event__student=student)
    ]

    # Get cheating audios
    cheating_audios = CheatingAudio.objects.filter(event__student=student)
    audio_urls = [audio.audio.url for audio in cheating_audios if audio.audio]


    context = {
        'student': student,
        'exam': exam_obj,

        'correct_answers': correct_answers,
        'total_questions': total_questions,

        'detected_objects': detected_objects_str,
        'total_tab_switch_count': total_tab_switch_count,
        'cheating_status': any(
            event.event_type in ['object_detected', 'multiple_persons', 'tab_switch']
            for event in cheating_events
        ),

        'cheating_images': cheating_images_data,
        'audio_urls': audio_urls,
        'cheating_events': cheating_events
    }

    return render(request, 'report_page.html', context)



from django.template.loader import get_template
try:
    from xhtml2pdf import pisa
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: xhtml2pdf not installed. PDF download feature will be disabled.")

def download_report(request, student_id):

    # Get student
    student = get_object_or_404(Student, id=student_id)

    # Try to get data from the NEW exam system first (StudentExamAttempt + Result)
    from .models import StudentExamAttempt, Result
    
    latest_attempt = StudentExamAttempt.objects.filter(student=student).order_by('-submitted_at').first()
    
    # Initialize exam data variables
    exam_name = "Not Available"
    total_questions = 0
    correct_answers = 0
    percentage_score = 0
    
    if latest_attempt:
        # NEW SYSTEM: Use data from StudentExamAttempt and Result
        exam_name = latest_attempt.exam_paper.title
        
        # Get total questions from the exam paper
        total_questions = latest_attempt.exam_paper.questions.count()
        
        # Get correct MCQ answers count
        from .models import StudentAnswer
        correct_answers = StudentAnswer.objects.filter(
            attempt=latest_attempt,
            is_correct=True
        ).count()
        
        # Get percentage from attempt or result
        try:
            result = Result.objects.get(attempt=latest_attempt)
            percentage_score = result.percentage
        except Result.DoesNotExist:
            percentage_score = latest_attempt.percentage if latest_attempt.percentage else 0
    else:
        # OLD SYSTEM: Fallback to old Exam model
        exam = student.exams.first()
        if exam:
            exam_name = exam.exam_name
            total_questions = exam.total_questions if exam.total_questions else 0
            correct_answers = exam.correct_answers if exam.correct_answers else 0
            percentage_score = exam.percentage_score if exam.percentage_score else 0

    # Create a mock exam object to pass to template (for backward compatibility)
    class ExamData:
        pass
    
    exam_obj = ExamData()
    exam_obj.exam_name = exam_name
    exam_obj.total_questions = total_questions
    exam_obj.correct_answers = correct_answers
    exam_obj.percentage_score = percentage_score

    # Get cheating events
    cheating_events = CheatingEvent.objects.filter(student=student)

    # Get detected objects
    detected_objects_list = get_detected_objects_string(cheating_events)
    detected_objects_str = ", ".join(detected_objects_list) if detected_objects_list else "No objects detected"

    # Tab switch count
    total_tab_switch_count = cheating_events.aggregate(total=Sum('tab_switch_count'))['total'] or 0

    # Get cheating images
    cheating_images = CheatingImage.objects.filter(event__student=student)

    cheating_images_data = []
    for img in cheating_images:
        image_path = os.path.join(settings.MEDIA_ROOT, str(img.image))
        cheating_images_data.append({
            "url": image_path,
            "event_type": img.event.event_type,
            "timestamp": img.timestamp
        })

    # Get cheating audios
    cheating_audios = CheatingAudio.objects.filter(event__student=student)
    audio_urls = [audio.audio.url for audio in cheating_audios if audio.audio]

    # Context
    context = {
        "student": student,
        "exam": exam_obj,
        "detected_objects": detected_objects_str,
        "score": percentage_score,
        "total_tab_switch_count": total_tab_switch_count,

        "correct_answers": correct_answers,
        "total_questions": total_questions,

        "cheating_status": any(
            event.event_type in ['object_detected', 'multiple_persons', 'tab_switch']
            for event in cheating_events
        ),

        "cheating_images": cheating_images_data,
        "audio_urls": audio_urls,
        "cheating_events": cheating_events,
    }

    # Render HTML
    template = get_template("report_page.html")
    html = template.render(context)

    # PDF response
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="report_{student.id}.pdf"'

    # Generate PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)

    return response

def add_question(request):
    return render(request, 'add_question.html')  # Ensure you have this template