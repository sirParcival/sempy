from django.urls import reverse_lazy
from .forms import SignUpRequestForm
from django.views import generic


# Create your views here.


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
