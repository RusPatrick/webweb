from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import timezone
from .models import Post, UserProfile
from django.views.generic.edit import FormView
from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect
from django.views.generic.base import View
from .forms import UserProfForm
from django.core.urlresolvers import reverse


def post_list(request):
    posts = Post.objects.filter(created_date__lte=timezone.now()).order_by('created_date')
    return render(request, 'blog/post_list.html', {'posts': posts} )


# class MyRegistrationView(FormView):
#     form_class = UserProfForm
#
#     success_url = "/singin/"
#
#     template_name = "blog/register.html"
#
#     def post(self, request, *args, **kwargs):
#         form = self.form_class(request.POST, request.FILES)
#         if form.is_valid():
#             instance = form.save(commit=False)
#             instance.save()
#             # user = UserProfile.objects.create_user(username=form.cleaned_data['username'],
#             #                                 email=form.cleaned_data['email'],
#             #                                 password=form.cleaned_data['password'],
#             #                                 first_name=form.cleaned_data['firstname'],
#             #                                 last_name=form.cleaned_data['surname'])
#             # ...
#             return HttpResponseRedirect(reverse("singin"))
#         return super(MyRegistrationView, self).get(request)


class RegisterFormView(FormView):
    form_class = UserCreationForm

    # Ссылка, на которую будет перенаправляться пользователь в случае успешной регистрации.
    # В данном случае указана ссылка на страницу входа для зарегистрированных пользователей.
    success_url = "/singin/"

    # Шаблон, который будет использоваться при отображении представления.
    template_name = "blog/register.html"

    def form_valid(self, form):
        # Создаём пользователя, если данные в форму были введены корректно.
        form.save()

        # Вызываем метод базового класса
        return super(RegisterFormView, self).form_valid(form)


class LoginFormView(FormView):
    form_class = AuthenticationForm

    # Аналогично регистрации, только используем шаблон аутентификации.
    template_name = "blog/singin.html"

    # В случае успеха перенаправим на главную.
    success_url = "/"

    def form_valid(self, form):
        # Получаем объект пользователя на основе введённых в форму данных.
        self.user = form.get_user()

        # Выполняем аутентификацию пользователя.
        login(self.request, self.user)
        return super(LoginFormView, self).form_valid(form)


class LogoutView(View):
    def get(self, request):
        # Выполняем выход для пользователя, запросившего данное представление.
        logout(request)

        # После чего, перенаправляем пользователя на главную страницу.
        return HttpResponseRedirect("/")