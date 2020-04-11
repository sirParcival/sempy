from django.shortcuts import render
from django.urls import reverse_lazy
from .forms import SignUpRequestForm, FileUploadForm
from django.views import generic
import csv
import secrets
import string

# Create your views here.
from .models import SchoolUser


class HomeView(generic.TemplateView):
    template_name = 'index.html'


class SignUpRequestView(generic.CreateView):
    form_class = SignUpRequestForm
    success_url = reverse_lazy('thanks')
    template_name = 'signup.html'


class ThanksView(generic.TemplateView):
    template_name = 'thanks.html'


class ProfileView(generic.TemplateView):
    template_name = 'profile.html'


class FileField(generic.FormView):
    form_class = FileUploadForm
    success_url = reverse_lazy('checkout')
    template_name = 'upload_users.html'

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        file = self.request.FILES['file_field']
        if form.is_valid():
            with open('files/generated_for_{}.csv'.format(self.request.user.username), 'wb') as new_file:
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
                for line, row in enumerate(csv_reader):

                    if line == 0:
                        first_name_index = row.index('first_name')
                        last_name_index = row.index('last_name')
                    else:
                        first_name = row[first_name_index]
                        last_name = row[last_name_index]
                        username = gen_username(row[first_name_index], row[last_name_index])
                        alphabet = string.ascii_letters + string.digits
                        password = ''.join(secrets.choice(alphabet) for i in range(16))
                        school = self.request.user.school
                        new_user = SchoolUser.objects.create_user(username=username, name=first_name, surname=last_name,
                                                                  school=school, is_teacher=True, is_headteacher=False,
                                                                  is_student=False,
                                                                  password=password)
                        new_user.save()
                        user_writer.writerow([first_name, last_name, username, password])
        return render(request, 'checkout.html')