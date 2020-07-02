from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


# Create your models here.


class School(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class SchoolUserManager(BaseUserManager):
    def create_user(self, username, name, surname, school, is_headteacher, is_teacher, is_student, password=None):
        user = self.model(
            first_name=name,
            last_name=surname,
            username=username,
            school=school,
            is_headteacher=is_headteacher,
            is_student=is_student,
            is_teacher=is_teacher
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(
            username,
            school=None,
            name='',
            surname='',
            is_headteacher=False,
            is_student=False,
            is_teacher=False,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class SchoolingGroup(models.Model):
    name = models.CharField(max_length=50)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    creator = models.ForeignKey('SchoolUser', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class SchoolUser(AbstractBaseUser):
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50, default="")
    last_name = models.CharField(max_length=50, default="")
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    is_headteacher = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    were_logged_in = models.BooleanField(default=False)

    groups = models.ManyToManyField(SchoolingGroup, blank=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = SchoolUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        if self.is_student:
            return "Student " + self.username
        else:
            return "Teacher " + self.username

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        # Simplest possible answer: All admins are staff
        return self.is_admin


class SignUpRequestModel(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    email = models.EmailField()

    def __str__(self):
        return "Request from " + self.name


class AddToGroupRequest(models.Model):
    full_name = models.CharField(max_length=150)
    user = models.CharField(max_length=150)
    to_user = models.ForeignKey(SchoolUser, on_delete=models.CASCADE, null=True, blank=True)
    to_group = models.ForeignKey(SchoolingGroup, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'Got new request from {self.full_name}'


class LectureOrTask(models.Model):
    creator = models.ForeignKey(SchoolUser, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=1000, null=True, blank=True)
    subject = models.CharField(max_length=50)
    group = models.ForeignKey(SchoolingGroup, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    link = models.URLField(blank=True, null=True)
    is_lecture = models.BooleanField(default=True)


class CommentToLectureOrTask(models.Model):
    comment = models.TextField()
    full_name = models.CharField(max_length=150)
    commenting_object = models.ForeignKey(LectureOrTask, on_delete=models.CASCADE)


class Post(models.Model):
    post_title = models.CharField(max_length=50)
    post_description = models.TextField(null=True, blank=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    author = models.ForeignKey(SchoolUser, on_delete=models.CASCADE)
    group = models.ForeignKey(SchoolingGroup, on_delete=models.CASCADE, null=True, blank=True)
    for_teachers = models.BooleanField(default=False)
    for_students = models.BooleanField(default=False)
    files = models.FileField(null=True, blank=True)


class Question(models.Model):
    question = models.TextField()
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    author = models.CharField(max_length=50)
    group = models.ForeignKey(SchoolingGroup, on_delete=models.CASCADE, null=True, blank=True)
    users_voted = models.ManyToManyField(SchoolUser, blank=True)
    for_teachers = models.BooleanField(default=False)
    for_students = models.BooleanField(default=False)

    def __str__(self):
        return self.question


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=50)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


class CommentToPost(models.Model):
    comment = models.TextField()
    author = models.CharField(max_length=150)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)