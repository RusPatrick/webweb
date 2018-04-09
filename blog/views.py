from django.shortcuts import render, get_object_or_404, render_to_response
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import re
from .models import User, UserManager, Question, Answer
from django.template import RequestContext
from django.contrib.auth import authenticate
from django.contrib.auth import login as authorization
from django.contrib.auth import logout as deAuthorization
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from django.views.generic.base import View
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import New_question_Form, New_answer_form, ProfileForm, LoginForm, RegistrationForm
from django.shortcuts import redirect
import datetime
from django.views.generic.edit import FormView

def paginate(objects_list, request):
	paginator = Paginator(objects_list, 5)
	page = request.GET.get('page')
	try:
		questions = paginator.page(page)
	except PageNotAnInteger:
		questions = paginator.page(1)
	except EmptyPage:
		questions = paginator.page(paginator.num_pages)
	return questions


def question_list(request):
	objects_list = Question.objects.sortByDate()
	questions = paginate(objects_list, request)
	context = {'questions' : questions,}
	return render(request, "blog/post_list.html", context)


def hot(request):
	objects_list = Question.objects.bestQuestions()
	questions = paginate(objects_list, request)
	context = {'questions' : questions}
	return(render(request, "blog/hot.html", context))


def question_detail(request, qid):
    if request.method == "POST":
        form = New_answer_form(request.POST, request.FILES)
        if form.is_valid():
            print ("Correct answer")
            answer = form.make_answer(request.user, qid)
            question = Question.objects.get(pk=qid)
            context = {'answerer': request.user, 'question': question, "answer": answer}
            # requests.post('http://localhost:8888/publish/', data=dict(uid=qid, msg="New message created"))
            return render(request, "blog/answer.html", context)
        else:
            print ("not correct answer")
            HttpResponse("not correct answer")
    else:
        result = re.search(r'(\d)+', request.path_info)
        if result != None:
            id = result.group(0)
        else:
            id = str(1)
        question = Question.objects.get(pk=id)
        objects_list = Answer.objects.answersOnQuestion(id)
        answers = paginate(objects_list, request)
        form = New_answer_form()
        # if request.user.is_authenticated():
        #     chanal = question.id + "new_questions"
        # else:
        #     chanal = datetime.datetime.now()
        context = {'answers': answers, 'question': question, "form": form,
                   "user": request.user}
        return render(request, "blog/post_detail.html", context)


def ask(request):
	if request.method=="POST":
		form = New_question_Form(request.POST)
		if form.is_valid():
			question = form.save(request.user)
			print ('success new question add')
			return redirect('question_detail', question.id)
		print ('not success add new question')
		print (form.errors)
	else:
		form = New_question_Form()
	context = {'form' : form}
	return render(request, "blog/ask.html", context)


def signup(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST, request.FILES)
        print(form)
        if form.is_valid():
            # TODO: create user
            user = form.save()
            authorization(request, user)
            print('register success')
            return redirect('profile')
        print('Save not success')
        print(form.errors)
    else:
        form = RegistrationForm()
    context = {'title': 'Ask Rodya', 'form': form}
    return render(request, "blog/register.html", context)


def login(request):
    # if request.user.is_authenticated():
    # return redirect('personal_page')
    if request.method == "POST":
        form = LoginForm(request.POST, request.FILES)
        print(form)
        if form.is_valid() and form.log_in():
            user = User.objects.get(username=form.cleaned_data['login'])
            print("login success")
            authorization(request, user)
            return redirect('profile')
        else:
            print(form.errors)
    form = LoginForm()
    context = {'title': 'Ask Rodya', 'form': form}
    return render(request, "blog/signin.html", context)


@login_required(login_url='signin')
def profile(request):
    user = request.user
    print(user.username)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user.avatar = form.cleaned_data['avatar']
            user.save()
            print('Save success')
        else:
            print('Save not success')
    form = ProfileForm()
    form.fields['login'].initial = user.username
    form.fields['nick'].initial = user.nick
    form.fields['email'].initial = user.email
    context = {'title': 'Ask_Rodya', 'user': user, 'form': form}
    return (render(request, "blog/profile.html", context))


def logout(request):
	print ('user logut')
	deAuthorization(request)
	return HttpResponseRedirect('/')


def searchByTag(request):
    tag = request.GET.get('tag')
    objects_list = Question.objects.questionsByTag(tag)
    questions = paginate(objects_list, request)
    context = {'questions': questions, 'searchTag': tag}
    return (render(request, "listByTag.html", context))


def vote(request):
    try:
        qid = int(request.POST.get('qid'))
    except:
        return JsonResponse(dict(error='bad question id'))
    vote = request.POST.get('vote')
    question = Question.objects.get(pk=qid)
    if not Like.objects.filter(question__id=qid, user__id=request.user.id):
        like = Like()
        like.user = request.user
        like.question = question
        like.assessment = 0
    else:
        like = Like.objects.get(question__id=qid, user__id=request.user.id)
    print
    like
    if vote == 'inc':
        if like.assessment <= 0:
            question.ratin += 1
            like.assessment += 2
            like.save()
            question.save()
        else:
            return JsonResponse(dict(error="already inc"))
    if vote == 'dec':
        if like.assessment >= 0:
            question.ratin -= 1
            like.assessment -= 2
            like.save()
            question.save()
        else:
            return JsonResponse(dict(error="already dec"))
    return JsonResponse(dict(ok=1, rating=question.ratin))


def correct(request):
    try:
        qid = int(request.POST.get('qid'))
    except:
        return JsonResponse(dict(error='bad question id'))
    try:
        aid = int(request.POST.get('aid'))
    except:
        return JsonResponse(dict(error='bad answer id'))


class RegistForm(FormView):
    form_class = RegistrationForm
    success_url = "/signin/"
    template_name = "blog/register.html"

    def form_valid(self, form):
         user = form.save()
         return super(RegistForm, self).form_valid(form)
