"""school_dairy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from core import views

urlpatterns = [
    # public
    path('admin/', admin.site.urls),
    path('login/', views.login_profile, name='login_profile'),
    path('logout/', views.logout_profile, name='logout_profile'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('list_status/', views.list_status, name='list_status'),
    path('registration_student/', views.registration_student, name='registration_student'),
    path('registration_teacher/', views.registration_teacher, name='registration_teacher'),
    # for students
    path('announcemet/', views.announcement_for_students, name="announcement_for_students"),
    path('schedule_for_students/', views.schedule_for_students, name='schedule_for_students'),
    path('attedance_of_student/', views.attedance_of_student, name='attedance_of_student'),
    path('attedance_of_student/subject/<int:subject_id>/', views.attedance_of_student_with_subject,
         name='attedance_of_student_with_subject'),
    path('attedance_of_student/date/', views.attedance_of_student_with_date, name='attedance_of_student_with_date'),
    path('mark/', views.mark_for_students, name='mark_for_students'),
    path('test_for_students/', views.test_for_students, name='test_for_students'),
    path('homework/', views.homework_for_students, name='homework_for_students'),
    # for teachers
    path('schedule_for_teachers/', views.schedule_for_teachers, name='schedule_for_teachers'),
    path('schedule_for_teachers/create_schedule/', views.create_schedule, name='create_schedule'),
    path('schedule_for_teachers/delete_schedule/<int:schedule_id>/', views.delete_schedule, name='delete_schedule'),
    # path('schedule_for_teachers/update_schedule/<int:schedule_id>/', views.update_schedule, name='update_schedule'),
    path('attedance_for_teachers/', views.attedance_for_teachers, name='attedance_for_teachers'),
    path('attedance_for_teachers/<int:group_id>/', views.show_attedance_group_for_teachers,
         name='show_attedance_group_for_teachers'),
    path('attedance_for_teachers/<int:group_id>/filter_attedance_for_teacher/', views.show_attedance_group_for_teachers,
         name='filter_attedance_for_teachers'),
    path('attedance_for_teachers/<int:group_id>/create_attedance/', views.create_attedance, name='create_attedance'),
    path('attedance_for_teachers/<int:subject_id>/create_attedance_with_subject/', views.create_attedance_with_subject,
         name='create_attedance_with_subject'),
    path('attedance_for_teachers/create_attedance_with_subject/create_attedance_2/', views.create_attedance_2,
         name='create_attedance_2'),
    path('test_for_teachers/', views.test_for_teachers, name='test_for_teachers'),
    path('test_for_teachers/create_test/', views.create_test, name='create_test'),
    path('test_for_teachers/delete_test/<int:test_id>/', views.delete_test, name='delete_test'),
    path('test_for_teachers/update_test/<int:test_id>/', views.update_test, name='update_test'),
    path('homework_for_teachers/', views.homework_for_teachers, name='homework_for_teachers'),
    path('homework_for_teachers/create_homework/', views.create_homework, name='create_homework'),
    path('homework_for_teachers/delete_homework/<int:task_id>/', views.delete_homework, name='delete_homework'),
    path('homework_for_teachers/update_homework/<int:task_id>/', views.update_homework, name='update_homework'),
    path('announcement_for_teachers/', views.announcement_for_teachers, name='announcement_for_teachers'),
    path('announcement_for_teachers/create_announcement/', views.create_announcement, name='create_announcement'),
    path('announcement_for_teachers/delete_announcement/<int:ann_id>/', views.delete_announcement,
         name='delete_announcement'),
    path('announcement_for_teachers/update_announcement/<int:ann_id>/', views.update_announcement,
         name='update_announcement'),
    path('mark_for_teachers/', views.mark_for_teachers, name='mark_for_teachers'),
    path('mark_for_teachers/create_mark_group/', views.create_mark_group, name='create_mark_group'),
    path('mark_for_teachers/create_mark_group/<int:group_id>/', views.create_mark_subject, name='create_mark_subject'),
    path('mark_for_teachers/create_mark_group/subject/<int:subject_id>', views.create_mark, name='create_mark'),
    path('', views.entrance, name='entrance'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
