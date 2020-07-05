import datetime
import os

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .forms import SignUpRequestForm, FileUploadForm, GroupForm, CreateLectureForm, CommentForm, CreateHomeTask, \
    ChoiceForm, QuestionForm, CommentPost
from django.views import generic
import csv
import secrets
import string

# Create your views here.
from .models import SchoolUser, SchoolingGroup, AddToGroupRequest, LectureOrTask, CommentToLectureOrTask, Post, \
    Question, Choice, CommentToPost


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change_password.html', {'form': form})


def add_user_to_group(request, **kwargs):
    data = {
        'is_ok': True
    }
    if request.is_ajax():
        group_request_id = kwargs['pk']
        group_request = AddToGroupRequest.objects.get(id=group_request_id)
        group = SchoolingGroup.objects.get(id=group_request.to_group.pk)
        user = SchoolUser.objects.get(username=group_request.user)
        user.groups.add(group)
        user.save()

        group_request.delete()
    return JsonResponse(data)


def decline_request(request, **kwargs):
    group_request_id = kwargs['pk']
    group_request = AddToGroupRequest.objects.get(id=group_request_id)
    group_request.delete()
    return JsonResponse({"is_ok": True})


def delete_group(request, **kwargs):
    group_id = kwargs['pk']
    group = SchoolingGroup.objects.get(id=group_id)
    group.delete()
    return JsonResponse({'is_rename': False})


def edit_group_name(request, **kwargs):
    data = {
        "is_rename": True
    }

    if request.is_ajax():
        new_name = request.GET.get('new_name', None)
        group = SchoolingGroup.objects.get(pk=kwargs['pk'])
        group.name = new_name
        group.save()
        data.update(text=new_name)

    return JsonResponse(data)


class HomeView(generic.TemplateView):
    template_name = 'index.html'


def iterate_over_structure(structure, count, groups, type_of_structure):
    structure_list = []
    if type_of_structure == "lecture_or_task":
        for struct, index in zip(reversed(structure), range(count)):
            if struct.group in groups or struct.group is None:
                if struct.is_lecture:
                    structure_list.append({
                        'type': 'lecture',
                        'struct': struct
                    })
                else:
                    structure_list.append({
                        'type': 'task',
                        'struct': struct
                    })
    else:
        for struct, index in zip(reversed(structure), range(count)):
            if struct.group in groups or struct.group is None:
                structure_list.append({
                    'type': type_of_structure,
                    'struct': struct
                })

    return structure_list


class ProfileView(generic.View):
    template_name = 'profile.html'

    def get(self, request, *args, **kwargs):
        if not self.request.user.were_logged_in:
            self.request.user.were_logged_in = True
            self.request.user.save()
            return redirect('change_password')

        else:
            lectures_and_tasks = LectureOrTask.objects.filter(school=self.request.user.school).exclude(
                creator=self.request.user
            )
            if self.request.user.is_teacher:
                posts = Post.objects.filter(school=self.request.user.school).exclude(
                    author=self.request.user, for_students=True
                )
                polls = Question.objects.filter(school=self.request.user.school).exclude(
                    author=self.request.user.username, for_students=True
                )
            else:
                posts = Post.objects.filter(school=self.request.user.school).exclude(
                    author=self.request.user, for_teachers=True
                )
                polls = Question.objects.filter(school=self.request.user.school).exclude(
                    author=self.request.user.username, for_teachers=True
                )

            user_groups = self.request.user.groups.all()
            lectures_and_task_list = iterate_over_structure(lectures_and_tasks, 3, user_groups, 'lecture_or_task')
            posts_list = iterate_over_structure(posts, 3, user_groups, 'post')
            polls_list = iterate_over_structure(polls, 3, user_groups, 'poll')

            dashboard_elements = lectures_and_task_list[:] + posts_list[:] + polls_list[:]

            context = {
                'list': dashboard_elements
            }
            return render(self.request, self.template_name, context)


class AllGroupsView(generic.View):
    def get(self, request, *args, **kwargs):
        all_groups = SchoolingGroup.objects.filter(school=self.request.user.school)
        context = {
            'school_groups': all_groups,
        }
        return render(self.request, 'all_groups.html', context)


class SignUpRequestView(generic.CreateView):
    form_class = SignUpRequestForm
    success_url = reverse_lazy('thanks')
    template_name = 'signup.html'


class ThanksView(generic.TemplateView):
    template_name = 'thanks.html'


class GroupDetail(generic.View):
    school_users = SchoolUser.objects.all()

    def get(self, request, *args, **kwargs):
        users = self.school_users.filter(groups=kwargs['pk'])
        context = {
            'school_users': users,
            'group_name': kwargs['name']
        }
        return render(request, 'group.html', context)

    def post(self, request, *args, **kwargs):
        new_request = AddToGroupRequest.objects.create(
            full_name=f'{self.request.user.first_name} {self.request.user.last_name}',
            user=self.request.user.username,
            to_user=SchoolUser.objects.get(id=kwargs['creator_id']),
            to_group=SchoolingGroup.objects.get(id=kwargs['pk'])
        )
        new_request.save()
        return redirect('profile')


class MyGroupsView(generic.View):
    form_class = GroupForm

    def get(self, request, *args, **kwargs):
        group_request = AddToGroupRequest.objects.filter(to_user=self.request.user)
        context = {
            'form': self.form_class,
            'groups': self.request.user.groups.all(),
        }
        if group_request:
            context['group_requests'] = group_request
        return render(request, 'my_groups.html', context)

    def post(self, request, *args, **kwargs):
        if self.request.POST['name']:
            group_name = self.request.POST['name']
            form = self.form_class(request.POST)
            if form.is_valid():
                new_group = SchoolingGroup.objects.create(name=group_name, school=self.request.user.school,
                                                          creator=self.request.user)
                new_group.save()
                self.request.user.groups.add(new_group)
                self.request.user.save()
                return redirect('my_groups')
            else:
                return redirect('my_groups')
        else:
            return redirect('my_groups')


class FileField(generic.FormView):
    form_class = FileUploadForm
    success_url = reverse_lazy('checkout')
    template_name = 'upload_users.html'

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        file = self.request.FILES['file_field']
        choice = self.request.POST['radio']
        if form.is_valid():
            with open('files/generated_for_{}.csv'.format(self.request.user.username), 'w') as des_file:
                des_file.write(choice + ',')
            with open('files/generated_for_{}.csv'.format(self.request.user.username), 'ab') as new_file:
                for chunk in file.chunks():
                    new_file.write(chunk)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


def gen_username(first_name, last_name):
    count = 0
    while True:
        username = first_name[0].lower() + last_name[:len(last_name) - 2].lower() + str(count)
        if SchoolUser.objects.filter(username=username).exists():
            count += 1
        else:
            return username


class Checkout(generic.CreateView):
    def get(self, request, *args, **kwargs):
        with open('files/generated_for_{}.csv'.format(self.request.user.username)) as csv_file:
            with open('files/result_for_{}.csv'.format(self.request.user.username), mode='w') as result_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                user_writer = csv.writer(result_file, delimiter=',')
                first_name_index = 0
                last_name_index = 0
                is_teacher = False
                is_student = False
                for line, row in enumerate(csv_reader):

                    if line == 0:
                        first_name_index = row.index('first_name') - 1
                        last_name_index = row.index('last_name') - 1
                        if 'student' in row:
                            is_student = True
                        else:
                            is_teacher = True
                    else:
                        first_name = row[first_name_index]
                        last_name = row[last_name_index]
                        username = gen_username(row[first_name_index], row[last_name_index])
                        alphabet = string.ascii_letters + string.digits
                        password = ''.join(secrets.choice(alphabet) for i in range(16))
                        school = self.request.user.school
                        new_user = SchoolUser.objects.create_user(username=username,
                                                                  name=first_name, surname=last_name,
                                                                  school=school,
                                                                  is_teacher=is_teacher,
                                                                  is_headteacher=False,
                                                                  is_student=is_student,
                                                                  password=password)
                        new_user.save()
                        user_writer.writerow([first_name, last_name, username, password])
        return render(request, 'checkout.html')


class LectureCreatorView(generic.View):
    template_name = 'lecture_creator.html'

    def get(self, request, *args, **kwargs):
        form = CreateLectureForm()
        context = {
            'form': form,
            'groups': SchoolingGroup.objects.filter(school=self.request.user.school)
        }
        return render(self.request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        lecture_title = self.request.POST.get('title')
        lecture_description = self.request.POST.get('description')
        lecture_subject = self.request.POST.get('subject')
        lecture_link = self.request.POST.get('link')
        lecture_group = self.request.POST.get('dropdown')
        link = lecture_link.replace('watch?v=', 'embed/')
        files = self.request.FILES.getlist('files')
        lecture = LectureOrTask.objects.create(
            title=lecture_title, description=lecture_description, subject=lecture_subject, link=link,
            school=self.request.user.school, creator=self.request.user, date=datetime.datetime.now()
        )
        if lecture_group != '0':
            group = SchoolingGroup.objects.get(pk=lecture_group)
            lecture.group = group
        lecture.save()
        file_path = f'files/lecture{lecture.id}/'
        os.makedirs(file_path, 0o777)
        for file in files:
            with open(file_path + str(file), 'wb+') as file_for_lecture:
                for chunk in file.chunks():
                    file_for_lecture.write(chunk)

        return redirect('profile')


class LecturesListView(generic.View):
    def get(self, request, *args, **kwargs):
        context = {
            'lectures': LectureOrTask.objects.filter(school=self.request.user.school, is_lecture=True),
            'user_groups': self.request.user.groups.all()
        }
        return render(self.request, 'all_lectures.html', context)


class LectureDetailView(generic.View):
    def get(self, request, *args, **kwargs):
        filelinks = []
        lecture = LectureOrTask.objects.get(id=kwargs['pk'])
        comments = CommentToLectureOrTask.objects.filter(commenting_object=lecture)
        directory = f'files/lecture{lecture.id}/'
        comments_form = CommentForm
        for file in os.listdir(directory):
            filelinks.append(
                {
                    'file_path': directory + file,
                    'filename': file
                }
            )
        context = {
            'lecture': lecture,
            'files': filelinks,
            'comments': comments,
            'comment_form': comments_form
        }
        return render(self.request, 'lecture_detail.html', context)

    def post(self, request, *args, **kwargs):
        data = {}
        comment = CommentToLectureOrTask(
            comment=self.request.POST['comment'],
            full_name=self.request.user.first_name + " " + self.request.user.last_name,
            commenting_object=LectureOrTask.objects.get(id=kwargs['pk'])
        )
        comment.save()
        data.update(comment=comment.comment, name=comment.full_name)
        return JsonResponse(data)


class HomeTaskCreatorView(generic.View):
    template_name = 'home_task_creator.html'

    def get(self, request, *args, **kwargs):
        form = CreateHomeTask()
        context = {
            'form': form,
            'groups': SchoolingGroup.objects.filter(school=self.request.user.school)
        }
        return render(self.request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        home_task_title = self.request.POST.get('title')
        home_task_date = self.request.POST.get('date')
        home_task_description = self.request.POST.get('description')
        home_task_subject = self.request.POST.get('subject')
        home_task_link = self.request.POST.get('link')
        home_task_group = self.request.POST.get('dropdown')
        home_task = home_task_link.replace('watch?v=', 'embed/')
        files = self.request.FILES.getlist('files')
        task = LectureOrTask.objects.create(
            title=home_task_title, description=home_task_description, subject=home_task_subject, link=home_task,
            school=self.request.user.school, creator=self.request.user, date=home_task_date, is_lecture=False,
        )
        if home_task_group != '0':
            group = SchoolingGroup.objects.get(pk=home_task_group)
            task.group = group
        task.save()
        file_path = f'files/hometask{task.id}/'
        os.makedirs(file_path, 0o777)
        for file in files:
            with open(file_path + str(file), 'wb+') as file_for_lecture:
                for chunk in file.chunks():
                    file_for_lecture.write(chunk)

        return redirect('profile')


class TaskListView(generic.View):
    def get(self, request, *args, **kwargs):
        context = {
            'tasks': LectureOrTask.objects.filter(school=self.request.user.school, is_lecture=False),
            'user_groups': self.request.user.groups.all()
        }
        return render(self.request, 'all_tasks.html', context)


class TaskDetailView(generic.View):
    def get(self, request, *args, **kwargs):
        filelinks = []
        home_task = LectureOrTask.objects.get(id=kwargs['pk'])
        comments = CommentToLectureOrTask.objects.filter(commenting_object=home_task)
        directory = f'files/hometask{home_task.id}/'
        comments_form = CommentForm
        for file in os.listdir(directory):
            filelinks.append(
                {
                    'file_path': directory + file,
                    'filename': file
                }
            )
        context = {
            'home_task': home_task,
            'files': filelinks,
            'comments': comments,
            'comment_form': comments_form
        }
        return render(self.request, 'task_detail.html', context)

    def post(self, request, *args, **kwargs):
        data = {}
        comment = CommentToLectureOrTask(
            comment=self.request.POST['comment'],
            full_name=self.request.user.first_name + " " + self.request.user.last_name,
            commenting_object=LectureOrTask.objects.get(id=kwargs['pk'])
        )
        comment.save()
        data.update(comment=comment.comment, name=comment.full_name)
        return JsonResponse(data)


class PostCreator(generic.View):
    template_name = 'post_creator.html'
    success_url = 'profile'

    def get(self, request, *args, **kwargs):
        context = {
            'groups': SchoolingGroup.objects.filter(school=self.request.user.school)
        }
        return render(self.request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        post_title = self.request.POST['title']
        post_description = self.request.POST['description']
        post_school = self.request.user.school
        post_author = self.request.user
        post_group = self.request.POST['dropdown']
        post_files = self.request.FILES.getlist('file')
        post_for_students = False
        post_for_teachers = False
        if 'teacher' in self.request.POST:
            post_for_teachers = True
        if 'student' in self.request.POST:
            post_for_students = True

        post = Post(
            post_title=post_title, post_description=post_description, school=post_school, author=post_author,
            for_students=post_for_students, for_teachers=post_for_teachers,
        )

        if post_group != '0':
            post.group = SchoolingGroup.objects.get(pk=post_group)
        post.save()
        file_path = f'files/post{post.id}/'
        os.makedirs(file_path, 0o777)
        for post_file in post_files:
            with open(file_path + str(post_file), 'wb+') as file:
                for chunk in post_file.chunks():
                    file.write(chunk)

        post.files = file_path
        post.save()

        return redirect(self.success_url)


class QuestionView(generic.View):
    form_class = QuestionForm

    def get(self, request, *args, **kwargs):
        context = {
            'question': self.form_class,
            'choice': ChoiceForm,
            'groups': SchoolingGroup.objects.filter(school=self.request.user.school)
        }
        return render(self.request, 'poll_creator.html', context)

    def post(self, request, *args, **kwargs):
        user = self.request.user.username
        question_text = self.request.POST.get('question')
        poll_for_students = False
        poll_for_teachers = False
        poll_group = self.request.POST['dropdown']

        if 'teacher' in self.request.POST:
            poll_for_teachers = True
        if 'student' in self.request.POST:
            poll_for_students = True
        question = Question(
            question=question_text, author=user, school=self.request.user.school, for_teachers=poll_for_teachers,
            for_students=poll_for_students)
        if poll_group != '0':
            question.group = SchoolingGroup.objects.get(pk=poll_group)
        question.save()
        choices = self.request.POST.getlist('choice_text')
        for choice in choices:
            new_choice = Choice(question=question, choice_text=choice, votes=0)
            new_choice.save()
        return redirect('profile')


class News(generic.View):
    template_name = 'news.html'

    def get(self, request, *args, **kwargs):

        if self.request.user.is_teacher:
            posts = Post.objects.filter(school=self.request.user.school).exclude(for_students=True)
            polls = Question.objects.filter(school=self.request.user.school).exclude(for_students=True)
        else:
            posts = Post.objects.filter(school=self.request.user.school).exclude(for_teachers=True)
            polls = Question.objects.filter(school=self.request.user.school).exclude(for_teachers=True)
        poll_list = []
        for poll in polls:
            choice_list = []
            choices = Choice.objects.filter(question=poll)
            for choice in choices:
                choice_list.append(choice)
            poll_list.append({
                'question': poll,
                'choice': choice_list,
                'id': poll.id,
                'users_voted': poll.users_voted.all(),
                'author': SchoolUser.objects.get(username=poll.author)
            })
        context = {
            'posts': posts,
            'polls': polls,
            'poll_list': poll_list,
        }
        return render(self.request, self.template_name, context)


def voting(request):
    choice_id = request.GET.get('choice', None)
    user = request.user
    choice = Choice.objects.get(pk=choice_id)
    question = Question.objects.get(pk=choice.question.pk)
    question.users_voted.add(user)
    choice.votes += 1
    choice.save()
    return JsonResponse({'': ''})


class PostDetailedView(generic.View):
    template_name = 'post.html'

    def get(self, request, *args, **kwargs):
        post = Post.objects.get(pk=kwargs['pk'])
        post_files_dir = f'files/post{post.id}/'
        file_links = []
        for file in os.listdir(post_files_dir):
            file_links.append(
                {
                    'file_path': post_files_dir + file,
                    'filename': file
                }
            )
        context = {
            'post': post,
            'files': file_links,
            'comment_form': CommentPost
        }
        return render(self.request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        data = {}
        comment = CommentToPost(
            comment=self.request.POST['comment'],
            author=self.request.user.first_name + " " + self.request.user.last_name,
            post=Post.objects.get(id=kwargs['pk'])
        )
        comment.save()
        data.update(comment=comment.comment, name=comment.author)
        return JsonResponse(data)
