from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Article, Comment, UserProfile


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class LoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False)


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "body", "category", "status"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 10}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 3}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["bio"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }


class PreferenceForm(forms.Form):
    results_per_page = forms.IntegerField(min_value=3, max_value=20, initial=5)
    compact_mode = forms.BooleanField(required=False)
