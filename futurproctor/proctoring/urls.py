# from django.urls import path
# from . import views
# from django.conf import settings
# from django.conf.urls.static import static
# from .views import home, registration,login,video_feed,dashboard,exam_submission_success,exam,submit_exam,result,record_tab_switch,get_warning,add_question
# from django.conf import settings
# from django.conf.urls.static import static

# urlpatterns = [
#     path('', views.home, name='home'),  # Home page
#     path('registration/', views.registration, name='registration'),
#     path('login/', views.login, name='login'),
#     path('video_feed/', views.video_feed, name='video_feed'),  # For video feed
#     # path('stop_event /', views.stop_event , name='stop_event'),
#     path('dashboard/', views.dashboard, name='dashboard'),
#     path('exam/', views.exam, name='exam'),
#     path('submit_exam/', views.submit_exam, name='submit_exam'),
#     path('exam_submission_success/', views.exam_submission_success, name='exam_submission_success'),
#     path('result/', views.result, name='result'),
#     path('get_warning/', views.get_warning, name='get_warning'),
#     path('proctor_notifications/', views.proctor_notifications, name='proctor_notifications'),
#     path('record_tab_switch/', views.record_tab_switch, name='record_tab_switch'),
#     path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
#     path('report_page/<int:student_id>/', views.report_page, name='report_page'),
#     path('logout/',views.logout, name='logout'),
#     path('download_report/<int:student_id>/', views.download_report, name='download_report'),
#     path('admin_dashboard/add_question/', add_question, name='add_question'),

    
#     # path("proctoring_report/", views.proctoring_report, name="proctoring_report")

    
    
# ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



























from django.urls import path
from . import views
from . import admin_views
from . import student_exam_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Original URLs
    path('', views.home, name='home'),
    path('registration/', views.registration, name='registration'),
    path('login/', views.login, name='login'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('exam/', views.exam, name='exam'),  # Old exam (for backward compatibility)
    path('submit_exam/', views.submit_exam, name='submit_exam'),  # Old submit
    path('exam_submission_success/', views.exam_submission_success, name='exam_submission_success'),
    path('result/', views.result, name='result'),  # Old result
    path('get_warning/', views.get_warning, name='get_warning'),
    path('proctor_notifications/', views.proctor_notifications, name='proctor_notifications'),
    path('record_tab_switch/', views.record_tab_switch, name='record_tab_switch'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),  # Old admin dashboard
    path('admin_dashboard/add_question/', views.add_question, name='add_question'),
    path('report_page/<int:student_id>/', views.report_page, name='report_page'),
    path('logout/', views.logout, name='logout'),
    path('download_report/<int:student_id>/', views.download_report, name='download_report'),
    
    # ========== NEW ADMIN URLS ==========
    path('admin/dashboard-enhanced/', admin_views.admin_dashboard_enhanced, name='admin_dashboard_enhanced'),
    
    # Student Approval URLs
    path('admin/students/approval/', admin_views.student_approval_list, name='student_approval_list'),
    path('admin/students/<int:student_id>/approve/', admin_views.approve_student, name='approve_student'),
    path('admin/students/<int:student_id>/reject/', admin_views.reject_student, name='reject_student'),
    
    # Exam Paper Management URLs
    path('admin/exams/', admin_views.exam_paper_list, name='exam_paper_list'),
    path('admin/exams/create/', admin_views.exam_paper_create, name='exam_paper_create'),
    path('admin/exams/<int:exam_id>/', admin_views.exam_paper_detail, name='exam_paper_detail'),
    path('admin/exams/<int:exam_id>/edit/', admin_views.exam_paper_edit, name='exam_paper_edit'),
    path('admin/exams/<int:exam_id>/publish/', admin_views.publish_exam, name='publish_exam'),
    path('admin/exams/<int:exam_id>/unpublish/', admin_views.unpublish_exam, name='unpublish_exam'),
    
    # Question Management URLs
    path('admin/exams/<int:exam_id>/questions/create/', admin_views.question_create, name='question_create'),
    path('admin/questions/<int:question_id>/edit/', admin_views.question_edit, name='question_edit'),
    path('admin/questions/<int:question_id>/delete/', admin_views.question_delete, name='question_delete'),
    
    # Evaluation & Results URLs
    path('admin/evaluations/pending/', admin_views.pending_evaluations_list, name='pending_evaluations_list'),
    path('admin/evaluations/<int:attempt_id>/evaluate/', admin_views.evaluate_subjective_answers, name='evaluate_subjective_answers'),
    path('admin/evaluations/<int:attempt_id>/publish/', admin_views.publish_result, name='publish_result'),
    path('admin/results/', admin_views.results_management, name='results_management'),
    
    # ========== NEW STUDENT URLS ==========
    path('student/dashboard-enhanced/', student_exam_views.student_dashboard_enhanced, name='student_dashboard_enhanced'),
    path('student/exams/available/', student_exam_views.available_exams, name='available_exams'),
    path('student/exams/<int:exam_id>/start/', student_exam_views.start_exam, name='start_exam'),
    path('student/exams/attempt/<int:attempt_id>/', student_exam_views.take_exam, name='take_exam'),
    path('student/exams/attempt/<int:attempt_id>/submit/', student_exam_views.submit_exam_new, name='submit_exam_new'),

    path('student/exams/submission-success/', student_exam_views.exam_submission_success_new, name='exam_submission_success_new'),
    path('student/results/', student_exam_views.student_results, name='student_results'),
    path('student/results/<int:result_id>/', student_exam_views.result_detail, name='result_detail'),
    
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)