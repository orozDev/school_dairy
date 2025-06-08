from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from core.decorators import is_teacher
from core.forms import LoginForm, RegistrationForm, TeacherForm, ScheduleForm, TestForm, TaskForm, AnnouncementForm
from core.models import Group, User, Student, Subject, Schedule, Test, Task, DayOfWeek, Announcement, Attedance, \
    Teacher, Mark


def entrance(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    if request.user.is_authenticated:
        if not request.user.is_superuser:
            return user_profile(request)
        else:
            return redirect('/admin/')


def login_profile(request):
    if request.user.is_authenticated:
        return redirect('/')

    form_login = LoginForm()
    if request.method == 'POST':
        form_login = LoginForm(request.POST)
        if form_login.is_valid():
            username = form_login.cleaned_data['username']
            password = form_login.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('/')
            messages.error(request, 'Не существует пользователь или неправильный пароль')

    return render(request, 'auth/login.html', {'form_login': form_login})


def logout_profile(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('/')


def list_status(request):
    if not request.user.is_authenticated:
        return render(request, 'auth/list_status.html', {})
    else:
        return redirect('/')


def registration_student(request):
    if request.user.is_authenticated:
        return redirect('/')

    form = RegistrationForm()
    group = Group.objects.all()

    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.STUDENT
            user.save()
            group = Group.objects.get(id=request.POST.get('group'))
            Student.objects.create(user=user, group=group)

            login(request, user)
            return redirect('/')

        messages.error(request, form.errors)

    return render(request, 'auth/registration_student.html', {'form': form, 'groups': group})


def registration_teacher(request):
    if request.user.is_authenticated:
        return redirect('/')

    form = RegistrationForm()
    form_teacher = TeacherForm()

    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.role = User.TEACHER
            instance.save()

            form2 = TeacherForm(request.POST)
            if form2.is_valid():

                instance2 = form2.save(commit=False)
                instance2.teacher = instance
                instance2.save()
                for subject in request.POST.getlist('subject'):
                    instance2.subjects.add(Subject.objects.get(id=subject))
                for group in request.POST.getlist('group'):
                    instance2.group.add(Group.objects.get(id=group))
                instance2.save()

                username = form.cleaned_data['username']
                password = form.cleaned_data['password2']
                user = authenticate(username=username, password=password)
                if user:
                    login(request, user)
                    return redirect('/')

                messages.error(request, 'Что-то не так!')
            messages.error(request, form.errors)

    return render(request, 'auth/registration_teacher.html', {'form': form, 'form2': form_teacher})


def user_profile(request):
    if request.user.is_authenticated:
        if request.user.role == User.STUDENT:
            person = Student.objects.get(user=request.user)
            template = 'student/user_profile_for_students.html'
        else:
            person = Teacher.objects.get(user=request.user)
            template = 'teacher/user_profile_for_teachers.html'
        return render(request, template, {'user': request.user, 'person': person})
    else:
        return redirect('/')


def schedule_for_students(request):
    if request.user.is_authenticated and request.user.role == User.STUDENT:
        student = Student.objects.get(user=request.user)
        schedule = Schedule.objects.filter(group__id=student.group.id).order_by('hour')
        day_of_week = DayOfWeek.objects.all()
        return render(request, 'student/schedule/schedule_for_students.html',
                      {'user': request.user, 'schedules': schedule, 'day_of_week': day_of_week})
    else:
        return redirect('/')


def attedance_of_student(request):
    if request.user.is_authenticated and request.user.role == User.STUDENT:
        student = Student.objects.get(user=request.user)
        subject = student.group.subjects.all()
        return render(request, 'student/attedance/attedance_of_student.html',
                      {'students': student, 'subjects': subject, 'user': request.user})
    else:
        return redirect('/')


def attedance_of_student_with_subject(request, subject_id):
    if request.user.is_authenticated and request.user.role == User.STUDENT:
        attedance = Attedance.objects.filter(subject__id=subject_id, student__user=request.user).order_by('-date')
        pagin = Paginator(attedance, 10)
        page = request.GET.get('page', None)
        if page is None:
            combine_pagin_news = pagin.get_page(1)
        else:
            combine_pagin_news = pagin.get_page(page)
        return render(request, 'student/attedance/attedance_of_student_with_subject.html',
                      {'user': request.user, 'attedances': combine_pagin_news})
    else:
        return redirect('/')


def attedance_of_student_with_date(request):
    if request.user.is_authenticated and request.user.role == User.STUDENT:
        if request.method == 'POST':
            date = request.POST.get('date')
            attedance = Attedance.objects.filter(date=date, student__user=request.user).order_by(
                '-date')
            date = correct_date(date)
            return render(request, 'student/attedance/attedance_of_student_with_date.html',
                          {'user': request.user, 'attedances': attedance, 'date': date})
    else:
        return redirect('/')


def correct_date(date):
    date = date.split('-')
    month = [
        'Январь',
        'Февраль',
        'Март',
        'Апрель',
        'Май',
        'Июнь',
        'Июль',
        'Август',
        'Сентябрь',
        'Октябрь',
        'Ноябрь',
        'Декабрь',

    ]
    new_date = date[2] + ' ' + month[int(date[1]) - 1] + ' ' + date[0] + ' г.'
    return new_date


def mark_for_students(request):
    if request.user.is_authenticated and request.user.role == User.STUDENT:
        student = Student.objects.get(user=request.user)
        mark = Mark.objects.filter(student=student, group=student.group).order_by('-date')
        pagin = Paginator(mark, 15)
        page = request.GET.get('page', None)
        if page is None:
            combine_pagin_news = pagin.get_page(1)
        else:
            combine_pagin_news = pagin.get_page(page)

        return render(request, 'student/mark/mark_for_students.html',
                      {'user': request.user, 'marks': combine_pagin_news})

    else:
        return redirect('/')


def mark_for_students_subject(request, subject_id):
    if request.user.is_authenticated and request.user.role == User.STUDENT:
        student = Student.objects.get(user=request.user)
        mark = Mark.objects.filter(student=student, subject__id=subject_id, group=student.group)
        return render(request, 'mark_for_students_subject.html', {'user': request.user, 'marks': mark})
    else:
        return redirect('/')


def test_for_students(request):
    if request.method == 'POST':
        if request.user.is_authenticated and request.user.role == User.STUDENT:
            student = Student.objects.get(user=request.user)
            date = request.POST.get('date')
            subject = request.POST.get('subject')
            subjects = student.group.subjects.all()
            if date == '' and subject is not None:
                test = Test.objects.filter(group=student.group, subject__id=subject).order_by('-date')
            elif date != '' and subject is None:
                test = Test.objects.filter(group=student.group, date__date=date).order_by('-date')
            elif date != '' and subject is not None:
                test = Test.objects.filter(group=student.group, date__date=date, subject__id=subject).order_by('-date')
            elif date == '' and subject is None:
                messages.error(request, 'Вы должны задать фильтрацию')
                return redirect('/test_for_students/')
            pagin = Paginator(test, 10)
            page = request.GET.get('page', None)
            if page is None:
                combine_pagin_news = pagin.get_page(1)
            else:
                combine_pagin_news = pagin.get_page(page)
            return render(request, 'student/test/test_for_students.html',
                          {'user': request.user, 'tests': combine_pagin_news, 'subjects': subjects})

    if request.user.is_authenticated and request.user.role == User.STUDENT:
        student = Student.objects.get(user=request.user)
        subjects = student.group.subjects.all()
        test = Test.objects.filter(group=student.group).order_by('-date')
        pagin = Paginator(test, 10)
        page = request.GET.get('page', None)
        if page is None:
            combine_pagin_news = pagin.get_page(1)
        else:
            combine_pagin_news = pagin.get_page(page)
        return render(request, 'student/test/test_for_students.html',
                      {'user': request.user, 'tests': combine_pagin_news, 'subjects': subjects})
    else:
        return redirect('/')


@login_required(login_url='/login/')
def homework_for_students(request):
    if request.method == 'POST':
        student = Student.objects.get(user=request.user)
        date = request.POST.get('date')
        subject = request.POST.get('subject')
        subjects = student.group.subjects.all()
        if date == '' and subject is not None:
            task = Task.objects.filter(group=student.group, subject__id=subject).order_by('-date')
        elif date != '' and subject is None:
            task = Task.objects.filter(group=student.group, date__date=date).order_by('-date')
        elif date != '' and subject is not None:
            task = Task.objects.filter(group=student.group, date__date=date, subject__id=subject).order_by('-date')
        elif date == '' and subject is None:
            messages.error(request, 'Вы должны задать фильтрацию')
            return redirect('/homework/')
        pagin = Paginator(task, 10)
        page = request.GET.get('page', None)
        if page is None:
            combine_pagin_news = pagin.get_page(1)
        else:
            combine_pagin_news = pagin.get_page(page)
        return render(request, 'student/task/homework_for_students.html',
                      {'user': request.user, 'tasks': combine_pagin_news, 'subjects': subjects})

    student = Student.objects.get(user=request.user)
    subject = student.group.subjects.all()
    task = Task.objects.filter(group=student.group).order_by('-date')
    pagin = Paginator(task, 10)
    page = request.GET.get('page', None)
    if page is None:
        combine_pagin_news = pagin.get_page(1)
    else:
        combine_pagin_news = pagin.get_page(page)
    return render(request, 'student/task/homework_for_students.html',
                  {'user': request.user, 'tasks': combine_pagin_news, 'subjects': subject})


@login_required(login_url='/login/')
def announcement_for_students(request):
    announcement = Announcement.objects.all().order_by('-date')
    pagin = Paginator(announcement, 10)
    page = request.GET.get('page', None)
    if page is None:
        combine_pagin_news = pagin.get_page(1)
    else:
        combine_pagin_news = pagin.get_page(page)
    return render(request, 'student/announcement/announcement_for_students.html',
                  {'user': request.user, 'announcements': combine_pagin_news})


@login_required(login_url='/login/')
@is_teacher
def schedule_for_teachers(request):
    teacher = Teacher.objects.get(user=request.user)
    schedule = Schedule.objects.filter(teacher=teacher).order_by('hour')
    day_of_week = DayOfWeek.objects.all()
    return render(request, 'teacher/schedule/schedule_for_teachers.html',
                  {'user': request.user, 'schedules': schedule, 'day_of_week': day_of_week})


@login_required(login_url='/login/')
@is_teacher
def create_schedule(request):
    form = ScheduleForm(teacher=request.user.teacher)
    if request.method == 'POST':
        form = ScheduleForm(teacher=request.user.teacher, data=request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.teacher = request.user.teacher
            item.save()
            messages.success(request, 'Успешно добавлено!')
            return redirect('/schedule_for_teachers/')

    return render(request, 'teacher/schedule/create_schedule.html', {'form': form})


@login_required(login_url='/login/')
@is_teacher
def delete_schedule(request, schedule_id):
    Schedule.objects.get(id=schedule_id).delete()
    messages.success(request, 'Успешно удалено!')
    return schedule_for_teachers(request)


@login_required(login_url='/login/')
@is_teacher
def attedance_for_teachers(request):
    teacher = Teacher.objects.get(user=request.user)
    return render(request, 'teacher/attedance/attedance_for_teachers.html', {'user': request.user, 'teacher': teacher})


@login_required(login_url='/login/')
@is_teacher
def show_attedance_group_for_teachers(request, group_id):
    teacher = Teacher.objects.get(user=request.user)
    attedance = Attedance.objects.filter(group__id=group_id, teacher=teacher).order_by('-date')
    group = Group.objects.get(id=group_id)
    if request.method == 'POST':
        date = request.POST.get('date', None)
        subject = request.POST.get('subject', None)
        teacher = Teacher.objects.get(user=request.user)
        if date != '' and subject is None:
            attedance = Attedance.objects.filter(group__id=group_id, teacher=teacher, date=date).order_by('-date')
        elif date == '' and subject is not None:
            attedance = Attedance.objects.filter(group__id=group_id, teacher=teacher, subject__id=subject).order_by(
                '-date')

        elif date != '' and subject is not None:
            attedance = Attedance.objects.filter(group__id=group_id, teacher=teacher, date=date,
                                                 subject__id=subject).order_by('-date')

    pagin = Paginator(attedance, 20)
    page = request.GET.get('page', None)
    if page is None:
        combine_pagin_attedance = pagin.get_page(1)
    else:
        combine_pagin_attedance = pagin.get_page(page)
    return render(request, 'teacher/attedance/show_attedance_group_for_teachers.html',
                  {'user': request.user, 'teacher': teacher, 'attedances': combine_pagin_attedance,
                   'group': group})


@login_required(login_url='/login/')
@is_teacher
def create_attedance(request, group_id):
    teacher = Teacher.objects.get(user=request.user)
    subject = teacher.subjects.all()
    request.session['group_id'] = group_id
    return render(request, 'teacher/announcement/create_attedance.html', {'user': request.user, 'subjects': subject})


def is_clean(date, subject, teacher, group):
    attedance = Attedance.objects.filter(date=date, subject=subject, teacher=teacher, group=group)
    if attedance.exists():
        return False
    else:
        return True


@login_required(login_url='/login/')
@is_teacher
def create_attedance_with_subject(request, subject_id):
    group_id = request.session['group_id']
    student = Student.objects.filter(group__id=group_id)
    subject = Subject.objects.get(id=subject_id)
    date = timezone.now().date()
    return render(request, 'teacher/announcement/create_attedance_2.html',
                  {'user': request.user, 'subject': subject, 'students': student, 'date': date})


@login_required(login_url='/login/')
@is_teacher
def create_attedance_2(request):
    if request.method == 'POST':
        date = timezone.now().date()
        group = Group.objects.get(id=request.POST.get('group'))
        teacher = Teacher.objects.get(user=request.user)
        subject = Subject.objects.get(id=request.POST.get('subject'))
        attedance = Attedance.objects.filter(date=date, subject=subject, teacher=teacher, group=group)
        if not attedance.exists():
            for student in Student.objects.filter(group=group):
                attedance_date = bool(request.POST.get('attedace_date_' + str(student.id)))
                Attedance.objects.create(date=date, subject=subject, teacher=teacher, group=group, student=student,
                                         attedance_date=attedance_date)
            messages.success(request, 'Посещаемость успешно сохранено!!')
            return redirect('/attedance_for_teachers/' + str(group.id) + '/filter_attedance_for_teacher/')
        else:
            messages.error(request, 'Вы не можете записать данные, так как данные уже записаны на сегодня')
            return redirect('/attedance_for_teachers/' + str(group.id) + '/filter_attedance_for_teacher/')


@login_required(login_url='/login/')
@is_teacher
def test_for_teachers(request):
    teacher = Teacher.objects.get(user=request.user)
    test = Test.objects.filter(teacher=teacher).order_by('-date')
    if request.method == 'POST':
        date = request.POST.get('date', None)
        subject = request.POST.get('subject', None)
        group_id = request.POST.get('group')

        if date != '' and subject is None:
            test = Test.objects.filter(group__id=group_id, teacher=teacher, date__date=date).order_by('-date')
        elif date == '' and subject is not None:
            test = Test.objects.filter(group__id=group_id, teacher=teacher, subject__id=subject).order_by('-date')

        elif date != '' and subject is not None:
            test = Test.objects.filter(group__id=group_id, teacher=teacher, date__date=date,
                                       subject__id=subject).order_by('-date')

        elif date == '' and subject is None:
            test = Test.objects.filter(group__id=group_id, teacher=teacher).order_by('-date')

    pagin = Paginator(test, 10)
    page = request.GET.get('page', None)
    if page is None:
        combine_pagin_test = pagin.get_page(1)
    else:
        combine_pagin_test = pagin.get_page(page)
    return render(request, 'teacher/test/test_for_teachers.html',
                  {'user': request.user, 'tests': combine_pagin_test, 'teacher': teacher})


@login_required(login_url='/login/')
@is_teacher
def create_test(request):
    form = TestForm(teacher=request.user.teacher)
    if request.method == 'POST':
        form = TestForm(teacher=request.user.teacher, data=request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.teacher = request.user.teacher
            item.save()
            messages.success(request, 'Тест успешно опубликовано!')
            return redirect('/test_for_teachers/')

    return render(request, 'teacher/test/create_test.html', {'form': form})


@login_required(login_url='/login/')
@is_teacher
def delete_test(request, test_id):
    Test.objects.get(id=test_id).delete()
    messages.success(request, 'Тест успешно удалено!')
    return redirect('/test_for_teachers/')


@login_required(login_url='/login/')
@is_teacher
def update_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    form = TestForm(teacher=request.user.teacher, instance=test)

    if request.method == 'POST':
        form = TestForm(teacher=request.user.teacher, instance=test, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, ' Тест успешно изменено!!')
            return redirect('/test_for_teachers/')

    return render(request, 'teacher/test/update_test.html', {'form': form, 'test': test})


@login_required(login_url='/login/')
@is_teacher
def homework_for_teachers(request):
    teacher = Teacher.objects.get(user=request.user)
    task = Task.objects.filter(teacher=teacher).order_by('-date')
    if request.method == 'POST':
        date = request.POST.get('date', None)
        subject = request.POST.get('subject', None)
        group_id = request.POST.get('group')

        if date != '' and subject is None:
            task = Task.objects.filter(group__id=group_id, teacher=teacher, date__date=date).order_by('-date')
        elif date == '' and subject is not None:
            task = Task.objects.filter(group__id=group_id, teacher=teacher, subject__id=subject).order_by('-date')

        elif date != '' and subject is not None:
            task = Task.objects.filter(group__id=group_id, teacher=teacher, date__date=date,
                                       subject__id=subject).order_by('-date')

        elif date == '' and subject is None:
            task = Task.objects.filter(group__id=group_id, teacher=teacher).order_by('-date')

    pagin = Paginator(task, 10)
    page = request.GET.get('page', None)
    if page is None:
        combine_pagin_task = pagin.get_page(1)
    else:
        combine_pagin_task = pagin.get_page(page)
    return render(request, 'teacher/task/homework_for_teachers.html',
                  {'user': request.user, 'tasks': combine_pagin_task, 'teacher': teacher})



@login_required(login_url='/login/')
@is_teacher
def create_homework(request):
    form = TaskForm(teacher=request.user.teacher)

    if request.method == 'POST':
        form = TaskForm(teacher=request.user.teacher, data=request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.teacher = request.user.teacher
            item.save()
            messages.success(request, 'Задание успешно опубликовано!')
            return redirect('/homework_for_teachers/')

    return render(request, 'teacher/task/create_task.html', {'form': form})


@login_required(login_url='/login/')
@is_teacher
def delete_homework(request, task_id):
    Task.objects.get(id=task_id).delete()
    messages.success(request, 'Задание успешно удалено!')
    return redirect('/homework_for_teachers/')


@login_required(login_url='/login/')
@is_teacher
def update_homework(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    form = TaskForm(teacher=request.user.teacher, instance=task)

    if request.method == 'POST':
        form = TaskForm(teacher=request.user.teacher, data=request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, ' Задание успешно изменено!!')
            return redirect('/homework_for_teachers/')

    return render(request, 'teacher/task/update_task.html', {'task': task, 'form': form})


def announcement_for_teachers(request):
    if request.user.is_authenticated and request.user.role == User.TEACHER:
        teachers = Teacher.objects.all()
        announcement = Announcement.objects.all().order_by('-date')
        if request.method == 'POST':
            date = request.POST.get('date', None)
            teacher = request.POST.get('teacher', None)

            if date != '' and teacher is None:
                announcement = Announcement.objects.filter(date__date=date).order_by('-date')
            elif date == '' and teacher is not None:
                announcement = Announcement.objects.filter(teacher__id=teacher).order_by('-date')

            elif date != '' and teacher is not None:
                announcement = Announcement.objects.filter(teacher__id=teacher, date__date=date).order_by('-date')

        pagin = Paginator(announcement, 10)
        page = request.GET.get('page', None)
        if page is None:
            combine_pagin_announcement = pagin.get_page(1)
        else:
            combine_pagin_announcement = pagin.get_page(page)
        return render(request, 'teacher/announcement/announcement_for_teachers.html',
                      {'user': request.user, 'announcements': combine_pagin_announcement, 'teachers': teachers})
    else:
        return redirect('/')


@login_required(login_url='/login/')
@is_teacher
def create_announcement(request):
    form = AnnouncementForm()

    if request.method == 'POST':
        form = AnnouncementForm(data=request.POST)

        if form.is_valid():
            item = form.save(commit=False)
            item.teacher = request.user.teacher
            item.save()

            messages.success(request, 'Объявление успешно опубликовано!')
            return redirect('/announcement_for_teachers/')

    return render(request, 'teacher/announcement/create_announcement.html', {'form': form})


@login_required(login_url='/login/')
@is_teacher
def delete_announcement(request, ann_id):
    Announcement.objects.get(id=ann_id).delete()
    messages.success(request, 'Объявление успешно удалено!')
    return redirect('/announcement_for_teachers/')


@login_required(login_url='/login/')
@is_teacher
def update_announcement(request, ann_id):
    announcement = get_object_or_404(Announcement, id=ann_id)

    if request.user.id == announcement.teacher.user.id:
        form = AnnouncementForm(instance=announcement)

        if request.method == 'POST':
            form = AnnouncementForm(instance=announcement, data=request.POST)

            if form.is_valid():
                form.save()
                messages.success(request, ' Объявление успешно изменено!!')
                return redirect('/announcement_for_teachers/')

        return render(request, 'teacher/announcement/update_announcement.html', {'announcement': announcement, 'form': form})

    messages.warning(request, 'У вас нет досту к этому объявлению')
    return redirect('/announcement_for_teachers/')


@login_required(login_url='/login/')
@is_teacher
def mark_for_teachers(request):
    teacher = Teacher.objects.get(user=request.user)
    mark = Mark.objects.filter(teacher__user=request.user)
    if request.method == 'POST':
        date = request.POST.get('date', None)
        subject = request.POST.get('subject', None)
        group_id = request.POST.get('group')

        if date != '' and subject is None:
            mark = Mark.objects.filter(group__id=group_id, teacher=teacher, date=date).order_by('-date')
        elif date == '' and subject is not None:
            mark = Mark.objects.filter(group__id=group_id, teacher=teacher, subject__id=subject).order_by('-date')

        elif date != '' and subject is not None:
            mark = Mark.objects.filter(group__id=group_id, teacher=teacher, date=date,
                                       subject__id=subject).order_by('-date')

        elif date == '' and subject is None:
            mark = Task.objects.filter(group__id=group_id, teacher=teacher).order_by('-date')
    pagin = Paginator(mark, 20)
    page = request.GET.get('page', None)
    if page is None:
        combine_pagin_mark = pagin.get_page(1)
    else:
        combine_pagin_mark = pagin.get_page(page)
    return render(request, 'teacher/mark/mark_for_teachers.html',
                  {'user': request.user, 'marks': combine_pagin_mark, 'teacher': teacher})


@login_required(login_url='/login/')
@is_teacher
def create_mark_group(request):
    teacher = Teacher.objects.get(user=request.user)
    return render(request, 'teacher/mark/create_mark_group.html', {'user': request.user, 'teacher': teacher, })


@login_required(login_url='/login/')
@is_teacher
def create_mark_subject(request, group_id):
    request.session['group_id'] = group_id
    teacher = Teacher.objects.get(user=request.user)
    return render(request, 'teacher/mark/create_mark_subject.html', {'user': request.user, 'teacher': teacher, })


@login_required(login_url='/login/')
@is_teacher
def create_mark(request, subject_id):
    if request.method == 'POST':
        subject = Subject.objects.get(id=subject_id)
        group = Group.objects.get(id=request.session['group_id'])
        date = timezone.now().date()
        teacher = Teacher.objects.get(user=request.user)
        students = Student.objects.filter(group=group)

        for student in students:
            mark = request.POST.get('mark_' + str(student.id))
            if mark is not None and mark != '':

                if int(mark) < 2 or int(mark) > 5:
                    messages.error(request, 'Оценка задана не корректно!')
                    return render(request, 'teacher/mark/create_mark.html',
                                  {'user': request.user, 'subject': subject, 'group': group, 'date': date,
                                   'teacher': teacher, 'students': students, })

                Mark.objects.create(student=student, group=group, teacher=teacher, subject=subject, date=date,
                                    mark=mark)

        messages.success(request, 'Оценки успешно сохранены!')
        return redirect('/mark_for_teachers/')

    subject = Subject.objects.get(id=subject_id)
    group = Group.objects.get(id=request.session['group_id'])
    date = timezone.now().date()
    teacher = Teacher.objects.get(user=request.user)
    students = Student.objects.filter(group=group)

    return render(request, 'teacher/mark/create_mark.html',
                  {'user': request.user, 'subject': subject, 'group': group, 'date': date, 'teacher': teacher,
                   'students': students, })


# Create your views here.
