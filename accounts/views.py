from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from .forms import CustomUserCreationForm
from .models import CustomUser, Profile


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/signup.html'

    def post(self, request, *args, **kwargs):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            signup_user = CustomUser.objects.get(username=username)
            user_group = form.cleaned_data.get('group')
            user_group.user_set.add(signup_user)
            
            return redirect('login')
        else:
            return render(
                request,
                self.template_name,
                {'form': form}
            )


class ProfilePageView(LoginRequiredMixin, DetailView):
    model = Profile
    slug_field = 'user__username'
    slug_url_kwarg = 'username'
    template_name = 'registration/user_profile.html'


class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Profile
    slug_field = 'user__username'
    slug_url_kwarg = 'username'
    template_name = 'registration/edit_profile.html'
    fields = [
        'email',
        'first_name',
        'last_name',
        'image',
    ]

    def get_success_url(self):
        return reverse_lazy('view_profile', kwargs={'username': self.object.user.username})
    
    def test_func(self):
        profile = self.get_object()
        if self.request.user == profile.user:
            return True
        return False


class AccountDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = CustomUser
    template_name = 'account_delete.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        return CustomUser.objects.get(username=self.request.user.username)
