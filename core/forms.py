from django import forms
from django.contrib.auth.forms import UserCreationForm

from core.models import Teacher, Schedule, User, Test, Task, Announcement


class LoginForm(forms.Form):
    username = forms.CharField(max_length=155,
                               widget=forms.TextInput(attrs={'class': 'text-center', 'placeholder': 'Username'}))

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'text-center', 'placeholder': 'Password'}))


class RegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={'placeholder': 'Пароль', 'class': 'form-control'})
        self.fields['password2'].widget = forms.PasswordInput(
            attrs={'placeholder': 'Подтвердите пароль', 'class': 'form-control'})

    class Meta:
        model = User
        fields = ('avatar', 'username', 'name', 'password1', 'password2')

        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Фамилия и имя', 'class': 'form-control', 'required': ''}),
            'username': forms.TextInput(attrs={'placeholder': 'Логин', 'class': 'form-control'}),
            'avatar': forms.FileInput(
                attrs={'id': 'upload_file', 'onchange': 'getImagePreview(event)', 'class': 'form-control'}),
        }


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ('subjects', 'group')

        widgets = {
            'subjects': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'group': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


class ScheduleForm(forms.ModelForm):
    def __init__(self, teacher, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        self.teacher = teacher
        self.fields['group'].queryset = teacher.group.all()
        self.fields['subject'].queryset = teacher.subjects.all()

        self.fields['group'].empty_label = 'Выберите группу'
        self.fields['subject'].empty_label = 'Выберите предмет'
        self.fields['types'].empty_label = 'Выберите тип'
        self.fields['day'].empty_label = 'Выберите день'

    def clean(self):
        if self.is_valid():
            hour = self.cleaned_data.get('hour')
            day = self.cleaned_data.get('day')
            group = self.cleaned_data.get('group')
            schedule = Schedule.objects.filter(hour=hour, day=day, group=group)
            schedule2 = Schedule.objects.filter(hour=hour, day=day, teacher=self.teacher)

            if schedule.exists() or schedule2.exists():
                raise forms.ValidationError({'day': ['Расписание занято']})

    class Meta:
        model = Schedule
        fields = ('subject', 'group', 'hour', 'types', 'day')

        widgets = {
            'day': forms.Select(attrs={'class': 'form-select'}),
            'hour': forms.NumberInput(attrs={'placeholder': 'Время', 'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'group': forms.Select(attrs={'class': 'form-select'}),
            'types': forms.Select(attrs={'class': 'form-select'}),

        }


class TestForm(forms.ModelForm):
    def __init__(self, teacher, *args, **kwargs):
        super(TestForm, self).__init__(*args, **kwargs)
        self.teacher = teacher
        self.fields['group'].queryset = self.teacher.group.all()
        self.fields['subject'].queryset = self.teacher.subjects.all()

        self.fields['group'].empty_label = 'Выберите группу'
        self.fields['subject'].empty_label = 'Выберите предмет'

    class Meta:
        model = Test
        fields = ('subject', 'group', 'link', 'about')
        widgets = {
            'link': forms.TextInput(attrs={'placeholder': 'Ссылка на тест', 'class': 'form-control'}),
            'about': forms.Textarea(
                attrs={'rows': '5', 'cols': '44', 'placeholder': 'Информация о тесте (Необязательно)',
                       'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'group': forms.Select(attrs={'class': 'form-select'}),
        }


class TaskForm(forms.ModelForm):
    def __init__(self, teacher, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)

        self.teacher = teacher

        self.fields['group'].queryset = self.teacher.group.all()
        self.fields['subject'].queryset = self.teacher.subjects.all()

        self.fields['group'].empty_label = 'Выберите группу'
        self.fields['subject'].empty_label = 'Выберите предмет'
        self.fields['types'].empty_label = 'Выберите тип'

    class Meta:
        model = Task
        fields = ('subject', 'group', 'link', 'about', 'types')
        widgets = {
            'link': forms.TextInput(attrs={'placeholder': 'Ссылка (Необязательно)', 'class': 'form-control'}),
            'about': forms.Textarea(
                attrs={'rows': '5', 'cols': '44', 'placeholder': 'Информация о д/з', 'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'group': forms.Select(attrs={'class': 'form-select'}),
            'types': forms.Select(attrs={'class': 'form-select'}),
        }


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ('theme', 'link', 'about')
        widgets = {
            'theme': forms.TextInput(attrs={'placeholder': 'Тема', 'class': 'form-control'}),
            'link': forms.TextInput(attrs={'placeholder': 'Ссылка (Необязательно)', 'class': 'form-control'}),
            'about': forms.Textarea(
                attrs={'rows': '5', 'cols': '44', 'placeholder': 'Объявление', 'class': 'form-control'})
        }
