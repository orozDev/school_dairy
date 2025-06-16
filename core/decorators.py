from core.models import User
from django.shortcuts import redirect
from django.contrib import messages


def is_teacher(func):

    def inner(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == User.TEACHER:
            return func(request, *args, **kwargs)

        messages.warning(request, 'Пользователь должен быть преподователем.')
        return redirect('/')

    return inner