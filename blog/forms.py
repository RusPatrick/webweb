from blog.models import User, Question, Answer, Tag
from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm


class New_question_Form(ModelForm):
	class Meta:
		fieldClass = 'form-control'
		model = Question
		fields = ['title', 'text']
		widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'input question here', 'class': 'new-q-input ' + fieldClass}),
            'text': forms.Textarea(attrs={'placeholder': 'input question\'s text here', 'class': 'new-q-input ' + fieldClass}),
            # 'tags': forms.TextInput(attrs={'placeholder': 'input tag\'s here', 'class': fieldClass}),
        }
	def clean_tags(self):
		return [Tag.objects.get(pk=41),]

	# def __init__(self, *args, **kwargs):
	# 	if args:
	# 		print ("we are inside 1")
	# 		print ("args:")
	# 		print (args)
	# 		print ("kwargs:")
	# 		print (kwargs)
	# 		QueryDict = args[0].copy()
	# 		QueryDict['tags'] = 40
	# 		print ("QueryDict")
	# 		print (QueryDict)
	# 		MultiValueDict = args[1].copy()
	# 		print ("MultiValueDict")
	# 		print (MultiValueDict)
	# 		NewTuple = (QueryDict, MultiValueDict)
	# 		print ("NewTuple")
	# 		print (NewTuple)
	# 		super(ModelForm, self).__init__(*args, **kwargs)
	# 	else:
	# 		print ("we are inside 2")
	# 		super(ModelForm, self).__init__(*args, **kwargs)

	def save(self, user):
		data = self.cleaned_data
		question = Question()
		question.title = data['title']
		question.text = data['text']
		question.ratin = 0
		question.asking = user
		question.save()
		# for tag in data['tags']:
		# 	question.tags.add(tag)
		question.save()
		return question


class ProfileForm(forms.Form):
	fieldClass = 'form-control'
	login = forms.CharField(label = 'Your login', max_length=20, widget = forms.TextInput(attrs={'class': fieldClass}))
	nick = forms.CharField(label = 'Your nick', max_length=20, widget = forms.TextInput(attrs={'class': fieldClass}))
	email = forms.EmailField(label = "Your email", max_length=255, widget = forms.TextInput(attrs={'class': fieldClass}))
	password = forms.CharField(label = "Your password", widget = forms.PasswordInput(attrs={'class': fieldClass}))
	repPassword = forms.CharField(label = "Repeat password", widget = forms.PasswordInput(attrs={'class': fieldClass}))
	avatar = forms.ImageField(
		label = 'Your avatar',
		widget = forms.FileInput (
			attrs={'class':'form-control-file'}
			)
		)


class RegistrationForm(ModelForm):
    fieldClass = 'form-control'
    email = forms.EmailField(label="Your email", max_length=255, widget=forms.TextInput(attrs={'class': fieldClass}))
    login = forms.CharField(label='Your login', max_length=20, widget=forms.TextInput(attrs={'class': fieldClass}))
    password = forms.CharField(label="Your password", widget=forms.PasswordInput(attrs={'class': fieldClass}))
    repPassword = forms.CharField(label="Repeat password", widget=forms.PasswordInput(attrs={'class': fieldClass}))
    nick = forms.CharField(label='Your nick', max_length=20, widget=forms.TextInput(attrs={'class': fieldClass}))
    # avatar = forms.ImageField(label='Your avatar', widget=forms.FileInput(attrs={'class': 'form-control-file'}))

    class Meta:
        model = User
        fields = ('login', 'nick', 'email', 'password')

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data['login'],
            email=data['email'],
            password=data['password'],
            nick=data['nick'],
            # avatar=data['avatar']
        )
        return user

    def authorization_conditions_are_complete(self):
        if self.passwords_match() and self.login_is_unique() and self.email_is_unique():
            return True
        else:
            return False

    def login_is_unique(self):
        if User.objects.filter(username=self.cleaned_data['login']):
            return False
        else:
            return True

    def email_is_unique(self):
        if User.objects.filter(email=self.cleaned_data['email']):
            return False
        else:
            return True

    def passwords_match(self):
        data = self.cleaned_data
        if data['password'] == data['repPassword']:
            return True
        else:
            return False


class LoginForm(forms.Form):
    fieldClass = 'form-control'
    login = forms.CharField(label='Your login', max_length=20, widget=forms.TextInput(attrs={'class': fieldClass}))
    password = forms.CharField(label="Your password", max_length=20,
                               widget=forms.PasswordInput(attrs={'class': fieldClass}))

    def login_is_valid(self):
        if User.objects.filter(username=self.cleaned_data['login']):
            print("username found")
            return True
        else:
            print("username NOT found")
            return False

    def password_is_valid(self):
        user = User.objects.get(username=self.cleaned_data['login'])
        if user.check_password(self.cleaned_data['password']):
            print("passwod valid")
            return True
        else:
            print("passwod not valid")
            return False

    def log_in(self):
        data = self.cleaned_data
        if self.login_is_valid() and self.password_is_valid():
            # authenticate(username = self.cleaned_data['login'], password=self.cleaned_data['password'])
            print("success login")
            return True
        else:
            print("NOT success login")
            return False
