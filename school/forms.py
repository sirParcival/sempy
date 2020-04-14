from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from school.models import SignUpRequestModel, SchoolUser, SchoolingGroup


class SignUpRequestForm(forms.ModelForm):
    class Meta:
        model = SignUpRequestModel
        fields = ['name', 'surname', 'email']


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = SchoolUser
        fields = ('username', 'first_name', 'last_name',)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = SchoolUser
        fields = ('username', 'password', 'first_name', 'last_name', 'is_headteacher', 'is_student', 'is_teacher',
                  'is_active',)

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class FileUploadForm(forms.Form):
    choices = [
        ('teacher', 'Teacher'),
        ('student', 'Student')
    ]
    file_field = forms.FileField()
    radio = forms.ChoiceField(choices=choices, widget=forms.RadioSelect, initial='teacher')


class GroupForm(forms.ModelForm):
    class Meta:
        model = SchoolingGroup
        fields = ('name', )
