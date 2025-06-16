from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


def max_limit_size_upload(file):
    if file.size > 10485760:
        raise ValueError('Размер файла превышает ограниченный размер')
    else:
        return file


def ValueValidator(mark):
    if mark > 5:
        raise ValueError(f'Значение не соответствует, оценка не может быть больше 5-ти. Вы написали {mark}')
    elif mark < 2 and mark != 0:
        raise ValueError(f'Значение не соответствует, оценка не может быть меньше 2-х. Вы написали {mark}')
    else:
        return mark


def is_teacher(user):
    if type(user) in [int, float]:
        user = User.objects.get(id=user)

    if user.role != User.TEACHER:
        raise ValidationError(f'Пользователь должен быть преподователем.')

    return user


def is_student(user):
    if type(user) in [int, float]:
        user = User.objects.get(id=user)

    if user.role != User.STUDENT:
        raise ValidationError(f'Пользователь должен быть студентом.')

    return user


class CustomAccountManager(BaseUserManager):

    def create_superuser(self, username, name, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(username, name, password, **other_fields)

    def create_user(self, username, name, password, **other_fields):

        user = self.model(username=username,
                          name=name, **other_fields)
        user.set_password(password)
        user.save()
        return user


class User(AbstractUser):
    STUDENT = 'student'
    TEACHER = 'teacher'

    ROLES = (
        (STUDENT, 'Студент'),
        (TEACHER, 'Преподователь'),
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = 'Пользователи'

    first_name = None
    last_name = None

    avatar = models.ImageField(upload_to='avatars/', verbose_name='Аватарка', validators=[max_limit_size_upload],
                               null=True)
    name = models.CharField('ФИО', max_length=150, blank=True)
    role = models.CharField('роль', choices=ROLES, default=STUDENT)
    objects = CustomAccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f'{self.name} .... {self.username}'


class Subject(models.Model):
    class Meta:
        verbose_name_plural = 'Предметы'
        verbose_name = 'Предмет'

    title = models.CharField(verbose_name='Название предмета', max_length=250)

    def __str__(self):
        return f'{self.title}'


class Group(models.Model):
    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    title = models.CharField(max_length=100, verbose_name='Название группы')
    subjects = models.ManyToManyField('Subject', 'Предмет')

    def __str__(self):
        return f'{self.title}'


class Student(models.Model):
    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'

    user = models.OneToOneField('core.User', verbose_name='Cтудент', on_delete=models.CASCADE,
                                related_name='student', validators=[is_student])
    group = models.ForeignKey('Group', verbose_name='Группу студента', on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f'{self.user.name}'


class Teacher(models.Model):
    class Meta:
        verbose_name = 'Преподователь'
        verbose_name_plural = 'Преподователи'

    user = models.OneToOneField('core.User', verbose_name='Преподователь', on_delete=models.CASCADE,
                                related_name='teacher', validators=[is_teacher])
    group = models.ManyToManyField('Group', verbose_name='Группу которые обучает')
    subjects = models.ManyToManyField('Subject', verbose_name='Предметы')

    def __str__(self):
        return f'{self.user.name}'


class DayOfWeek(models.Model):
    class Meta:
        verbose_name = 'Дни-недели'
        verbose_name_plural = 'Дни-недели'

    day = models.CharField(max_length=50, verbose_name='День (дни-недели)')

    def __str__(self) -> str:
        return f'{self.day}'


class TypesOfSubject(models.Model):
    class Meta:
        verbose_name = 'Тип предмета'
        verbose_name_plural = 'Тип предмета'

    title = models.CharField(max_length=50, verbose_name='Тип предмета')

    def __str__(self):
        return f'{self.title}'


class Schedule(models.Model):
    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписание'

    subject = models.ForeignKey('Subject', on_delete=models.PROTECT, null=True, verbose_name='Предмет')
    group = models.ForeignKey('Group', on_delete=models.PROTECT, null=True, verbose_name='группа')
    hour = models.IntegerField(verbose_name='Время')
    types = models.ForeignKey('TypesOfSubject', on_delete=models.PROTECT, null=True, verbose_name='Тип предмета')
    day = models.ForeignKey('DayOfWeek', on_delete=models.PROTECT, null=True, verbose_name='День (дни-недели)')
    teacher = models.ForeignKey('Teacher', on_delete=models.PROTECT, null=True, verbose_name='Преподаватель')

    def __str__(self):
        return f'{self.subject} - {self.group}'


class Mark(models.Model):
    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'

    student = models.ForeignKey('Student', on_delete=models.PROTECT, null=True, verbose_name='Студент')
    group = models.ForeignKey('Group', on_delete=models.PROTECT, null=True, verbose_name='Предмет')
    teacher = models.ForeignKey('Teacher', on_delete=models.PROTECT, null=True, verbose_name='Преподаватель')
    subject = models.ForeignKey('Subject', on_delete=models.PROTECT, null=True, verbose_name='Предмет')
    date = models.DateField(default=timezone.datetime.now, verbose_name='Дата добавления оценки')
    mark = models.IntegerField(validators=[ValueValidator], verbose_name='Оценка')

    def __str__(self):
        return f'{self.student.user.name} - {self.subject}'


class Attedance(models.Model):
    class Meta:
        verbose_name = 'Посещаемость'
        verbose_name_plural = 'Посещаемость'

    student = models.ForeignKey('Student', on_delete=models.PROTECT, null=True, verbose_name='Студент')
    subject = models.ForeignKey('Subject', on_delete=models.PROTECT, null=True, verbose_name='Предмет')
    teacher = models.ForeignKey('Teacher', on_delete=models.PROTECT, null=True, verbose_name='Преподаватель')
    group = models.ForeignKey('Group', on_delete=models.PROTECT, null=True, verbose_name='группа')
    date = models.DateField(verbose_name='Дата', default=timezone.datetime.now)
    attedance_date = models.BooleanField(default=False, null=True, verbose_name='Отметка')

    def __str__(self):
        return f'{self.teacher} - {self.group}'


class Task(models.Model):
    class Meta:
        verbose_name = 'задание'
        verbose_name_plural = 'задании'

    teacher = models.ForeignKey('Teacher', on_delete=models.PROTECT, null=True, verbose_name='Преподаватль')
    group = models.ForeignKey('Group', on_delete=models.PROTECT, null=True, verbose_name='группа')
    about = models.TextField(verbose_name='Задание')
    subject = models.ForeignKey('Subject', on_delete=models.PROTECT, null=True, verbose_name='Предмет')
    types = models.ForeignKey('TypesOfSubject', on_delete=models.PROTECT, null=True, verbose_name='Тип предмета')
    date = models.DateTimeField(verbose_name='Дата и время выдачи задания', default=timezone.now)
    link = models.TextField(verbose_name='Ссылка', blank=True, null=True)

    def __str__(self):
        return f'{self.teacher} - {self.group}'


class Test(models.Model):
    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'

    teacher = models.ForeignKey('Teacher', on_delete=models.PROTECT, null=True, verbose_name='Преподаватель')
    group = models.ForeignKey('Group', on_delete=models.PROTECT, null=True, verbose_name='группа')
    subject = models.ForeignKey('Subject', on_delete=models.PROTECT, null=True, verbose_name='Предмет')
    about = models.TextField(verbose_name='Текс', null=True, blank=True)
    date = models.DateTimeField(verbose_name='Дата и время выдачи теста', default=timezone.now)
    link = models.TextField(verbose_name='Ссылка', null=True)

    def __str__(self):
        return f'{self.teacher} - {self.group}'


class Announcement(models.Model):
    class Meta:
        verbose_name = 'Объявления'
        verbose_name_plural = 'Объявлении'

    theme = models.CharField(max_length=200, verbose_name='Тема')
    teacher = models.ForeignKey('Teacher', on_delete=models.PROTECT, null=True, verbose_name='Преподаватель')
    about = models.TextField(verbose_name='Объявление')
    date = models.DateTimeField(verbose_name='Дата и время выдачи теста', default=timezone.now)
    link = models.TextField(verbose_name='Ссылка', blank=True, null=True)

    def __str__(self):
        return f'{self.teacher}'

# Create your models here.
