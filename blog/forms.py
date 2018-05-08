from blog.models import Profile, Question, Answer, Tag
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
import re
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class New_answer_form(ModelForm):
    class Meta:
        model = Answer
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Write your answer here'
            })
        }


class AskForm(ModelForm):
    tagsInput = forms.CharField(
        required=False,
        help_text='Input 0 to 3 tags separated by space each less than 15 characters.',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tags'
        })
    )

    class Meta:
        model = Question
        fields = ['title', 'text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Write your question here'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Title'
            })
        }

    def clean_tagsInput(self):
        data = self.cleaned_data.get('tagsInput')
        data = data.strip()
        data = re.sub("\s{2,}", " ",  data)
        pattern = "^\s*(\w+,?\s*){0,3}$"
        if re.match(pattern, data):
            tags = re.split(",+\s*|\s+", data)
        else:
            raise ValidationError('Invalid format.')

        for tag in tags:
            if len(tag) >= 15:
                raise ValidationError('Tag is too long.')

        return tags

    def save(self, commit=True):
        tags = self.cleaned_data.get('tagsInput')
        super(AskForm, self).save(commit=True)
        for tag in tags:
            obj, created = Tag.objects.get_or_create(name=tag)
            self.instance.tags.add(obj)
        return super(AskForm, self).save(commit=commit)


class ProfileForm(forms.Form):
    fieldClass = 'form-control'
    login = forms.CharField(label='Your login', max_length=20, widget=forms.TextInput(attrs={'class': fieldClass}))
    nick = forms.CharField(label='Your nick', max_length=20, widget=forms.TextInput(attrs={'class': fieldClass}))
    email = forms.EmailField(label="Your email", max_length=255, widget=forms.TextInput(attrs={'class': fieldClass}))
    password = forms.CharField(label="Your password", widget=forms.PasswordInput(attrs={'class': fieldClass}))
    repPassword = forms.CharField(label="Repeat password", widget=forms.PasswordInput(attrs={'class': fieldClass}))
    avatar = forms.ImageField(
        label='Your avatar',
        widget=forms.FileInput(
            attrs={'class': 'form-control-file'}
        )
    )


class SignInForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Login'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))

    def clean_username(self):
        data = self.cleaned_data.get('username')
        if Profile.objects.filter(username=data).first() is None:
            raise ValidationError('User does not exist.')
        else:
            return data;



class RegistrationForm(UserCreationForm):
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm password'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email == '':
            return ''
        else:
            if Profile.objects.filter(email=email).first() is None:
                return email
            else:
                raise ValidationError('User with this email already exists.')

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data.get('email')
        return super(RegistrationForm, self).save(commit=commit)

    class Meta:
        model = Profile
        fields = ('username', 'password1', 'password2', 'avatar', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Login'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'Password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'Confirm password'}),
            'email': forms.EmailInput(attrs={'class': 'form-control','placeholder': 'Email'}),
        }


class EditProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['username', 'email', 'avatar']
        widgets = {
            'username': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Login'
        }),
        'email': forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        }),
        }

    def clean_email(self):
    email = self.cleaned_data.get('email')
    if email == '':
    return None
    else:
    u = Profile.objects.filter(email=email).first()
    if u is None or u.username == self.cleaned_data.get('username'):
    return email
    else:
    raise ValidationError('User with this email already exists.')
