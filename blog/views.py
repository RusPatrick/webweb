from django.shortcuts import render, get_object_or_404, render_to_response
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
import re
from .models import *
from .forms import *
from django.template import RequestContext
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.generic.base import View
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
import datetime
from django.views.generic.edit import FormView

def paginate(request, objects_list, limit):
  page = request.GET.get('page') or 1

  try:
    page = int(page)
  except ValueError:
    page = 1

  paginator = Paginator(objects_list, limit)
  try:
    page = paginator.get_page(page)
  except EmptyPage:
    page = paginator.get_page(paginator.num_pages)

  return page


def index(request):
  if request.path == '/hot':
    tab = 'hot'
    questions = Question.objects.hottest()
  else:
    tab = 'new'
    questions = Question.objects.newest()
  page = paginate(request, questions, 20)
  context = {'questions': page.object_list, 'tab': tab, 'page': page}
  return render(request, 'blog/index.html', context)


@login_required(login_url='/blog/signin')
def ask(request):
  form = AskForm(request.POST or None)
  if request.method == "POST":
    if form.is_valid():
      form.instance.author = request.user
      question = form.save()
      return redirect('question', question.id)
  context = {'form': form}
  return render(request, 'blog/ask.html', context)


def question(request, questionId):
  question = Question.objects.by_id(questionId)
  answers = Answer.objects.hottest(questionId)
  page = paginate(request, answers, 30)
  form = AnswerForm(request.POST or None)

  if request.method == "POST":
    if form.is_valid():
      answer = form.save(commit=False)
      answer.author = request.user
      answer.question = question
      answer.save()
      page_number = answer.get_page()
      return redirect('/question/' + str(questionId) + '?page=' + str(page_number) + '#answer' + str(answer.id))

  if request.method == "GET" and request.user.is_authenticated:
    if question.is_answered_by(request.user):
      form = None

  context = {'question': question, 'answers': page.object_list, 'page': page, 'form': form}
  return render(request, 'blog/question.html', context)


def signin(request):
  if request.user.is_authenticated:
    return redirect(request.GET.get('next', 'index'))
  else:
    return auth_views.login(request, template_name='blog/signin.html', authentication_form=SignInForm)


def signup(request):
  if request.method == "GET" and request.user.is_authenticated:
    return redirect('index')
  form = SignUpForm(request.POST or None, request.FILES or None)
  if request.method == 'POST':
    if form.is_valid():
      form.save()
      user = authenticate(
        request,
        username=form.cleaned_data.get('username'),
        password=form.cleaned_data.get('password1')
      )
      login(request, user)
      return redirect('index')
  context = {'form': form}
  return render(request, 'blog/signup.html', context)


def signout(request):
  logout(request)
  return redirect(request.META.get('HTTP_REFERER'))


def tag(request, tagName):
  questions = Tag.objects.by_tag_newest(tagName)
  page = paginate(request, questions, 20)
  context = {'questions': page.object_list, 'tag': tagName, 'page': page}
  return render(request, 'blog/tag.html', context)


def profile(request, userId):
  profile = Profile.objects.by_id(userId)
  questions = profile.get_questions()
  answers = profile.get_answers()
  context = {'profile': profile, 'questions': questions, 'answers': answers}
  return render(request, 'blog/profile.html', context)


@login_required(login_url='/signin')
def editProfile(request):
  if request.method == "POST":
    form = EditProfileForm(request.POST, request.FILES, instance=request.user)
    if form.is_valid():
      form.save()
      return redirect('profile', request.user.id)
  else:
    form = EditProfileForm(instance=request.user)
  context = {'form': form}
  return render(request, 'blog/editProfile.html', context)


@require_POST
def like(request):
  content_type = request.POST.get('content_type')
  if content_type is None:
    return JsonResponse({'status': 'error'})

  try:
    value = int(request.POST.get('value'))
  except ValueError:
    return JsonResponse({'status': 'error'})

  try:
    object_id = int(request.POST.get('object_id'))
  except ValueError:
    return JsonResponse({'status': 'error'})

  if content_type == 'Question':
    content_object = Question.objects.filter(pk=object_id)
  elif content_type == 'Answer':
    content_object = Answer.objects.filter(pk=object_id)
  else:
    content_object = Profile.objects.filter(pk=object_id)

  if not content_object.exists():
    return JsonResponse({'status': 'error'})

  author = request.user
  kwargs = {'author': author, 'content_type__model': content_type, 'object_id': object_id}

  newLike = Like.objects.filter(**kwargs)
  if newLike.exists():
    return JsonResponse({'status': 'error'})
  else:
    Like.objects.create(value=value, author=author, content_object=content_object.first())

  content_object.update(rating=F('rating') + value)

  return JsonResponse({'status': 'ok', 'likes_count': content_object.first().rating})


@require_POST
def correct(request):
  try:
    answer_id = int(request.POST.get('answer_id'))
  except ValueError:
    return JsonResponse({'status': 'error'})

  answer = Answer.objects.get(pk=answer_id)
  state = answer.is_correct
  answer.is_correct = not state
  answer.save()
  return JsonResponse({'status': 'ok', 'is_correct': answer.is_correct})


def search(request):
  q = request.GET.get('q')
  if q == '':
    return redirect(request.GET.get('back_path'))
  tags = Tag.objects.search(q)
  users = Profile.objects.search(q)
  questions = Question.objects.search(q)
  context = {'q': q, 'tags': tags, 'users': users, 'questions': questions}
  return render(request, 'blog/search_list.html', context)
