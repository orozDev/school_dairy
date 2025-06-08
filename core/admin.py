from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from core.models import Student, Teacher, User, DayOfWeek, TypesOfSubject, Schedule, Mark, Task, Group, Attedance, Test, \
    Announcement, Subject


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


class StudentTabularInline(admin.TabularInline):
    model = Student
    extra = 0


class TeacherTabularInline(admin.TabularInline):
    model = Teacher
    extra = 0


class UserAdminConfig(BaseUserAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'name',
        'role',
        'get_avatar',
    )
    list_display_links = ('id', 'username',)
    search_fields = ('name', 'email', 'username', 'group')
    filter_horizontal = ('groups', 'user_permissions')
    list_filter = ('role', 'student__group', 'teacher__subjects')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': (
            'username',
            'email',
            'password',
        )}),
        (_('Personal info'), {'fields': (
            'avatar',
            'get_avatar',
            'name',
            'role',
        )}),
        (_('Permissions'), {'fields': (
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions',
        )}),
        (_('Important dates'), {'fields': (
            'date_joined',
            'last_login',
        )}),
    )
    readonly_fields = (
        'get_avatar',
        'date_joined',
        'last_login',
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'avatar',
                'username',
                'email',
                'name',
                'role',
                'password1',
                'password2',
            ),
        }),
    )

    inlines = [StudentTabularInline, TeacherTabularInline]

    @admin.display(description=_('Аватарка'))
    def get_avatar(self, user):
        if user.avatar:
            return mark_safe(
                f'<img src="{user.avatar.url}" alt="{user.get_full_name}" width="100px" />')
        return '-'


admin.site.register(User, UserAdminConfig)
admin.site.register(DayOfWeek)
admin.site.register(TypesOfSubject)


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('subject', 'group', 'hour', 'day', 'teacher', 'types')
    list_filter = ('subject', 'group', 'hour', 'day', 'types')
    search_fields = ('teacher__icontains',)


@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = ('student', 'group', 'mark', 'subject', 'teacher', 'date')
    search_fields = ('user__icontains', 'date', 'teacher')
    list_filter = ('group', 'mark', 'subject')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'group', 'subject', 'date', 'types')
    search_fields = ('teacher', 'date',)
    list_filter = ('group', 'types', 'subject')


# @admin.register(Student)
# class StudentAdmin(admin.ModelAdmin):
#     list_display = ('show_user', 'group', 'get_photo')
#
#     def show_user(self, obj):
#         return f'{obj.user.name} - {obj.user.username}'
#
#     search_fields = ('user__icontains',)
#     list_filter = ['group']
#
#     readonly_fields = ('get_photo', 'start_date')
#
#     def start_date(self, obj):
#         date = str(obj.user.start_date)
#         date = list(date.split(' '))
#         new_date = correct_date(date[0])
#         return f'{new_date}'
#
#     def get_photo(self, obj):
#         return mark_safe(f'<img src="{obj.user.avatar.url}" alt="" width="75" class="avatars">')
#
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == "user":
#             kwargs["queryset"] = User.objects.filter(role=User.STUDENT)
#
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ('title__icontains',)


# @admin.register(Teacher)
# class TeacherAdmin(admin.ModelAdmin):
#     list_display = ('name', 'get_photo')
#     search_fields = ('user__icontains',)
#
#     readonly_fields = ['get_photo', 'start_date']
#
#     def name(self, obj):
#         return f'{obj.user.name} - {obj.user.username}'
#
#     def start_date(self, obj):
#         date = str(obj.user.start_date)
#         date = list(date.split(' '))
#         new_date = correct_date(date[0])
#         return f'{new_date}'
#
#     def get_photo(self, obj):
#         return mark_safe(f'<img src="{obj.user.avatar.url}" alt="" width="75" class="avatars">')
#
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == "user":
#             kwargs["queryset"] = User.objects.filter(role=User.TEACHER)
#
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title__icontains',)


@admin.register(Attedance)
class AttedanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'group', 'subject', 'date', 'teacher')
    list_filter = ('group', 'subject')
    search_fields = ['student__icontains', 'date', 'teacher__icontains']


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'group', 'subject', 'date',)
    list_filter = ('group', 'subject', 'teacher',)
    search_fields = ['date', 'teacher__icontains']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'theme', 'date',)
    list_filter = ('teacher',)


admin.site.site_title = 'Администрация'
admin.site.site_header = 'Администрация и контроль данных'

# Register your models here.
