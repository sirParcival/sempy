from django.contrib import admin
from django.contrib.auth.models import Group

from .forms import UserChangeForm, UserCreationForm

# Register your models here.
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from school.models import School, SchoolUser, SignUpRequestModel, SchoolingGroup, AddToGroupRequest, Lecture


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('username', 'is_teacher', 'is_student', 'is_headteacher', )
    list_filter = ('is_admin', 'is_teacher', 'is_student', 'is_headteacher')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('is_headteacher', 'is_teacher', 'is_student', 'first_name',
                                      'last_name', 'school', 'groups')}),

    )
    search_fields = ('username',)
    ordering = ('username',)
    filter_horizontal = ()


admin.site.register(SchoolUser, UserAdmin)

admin.site.register(
    (
        School,
        SignUpRequestModel,
        SchoolingGroup,
        AddToGroupRequest,
        Lecture,
    )
)
admin.site.unregister(Group)
