from django.contrib import admin
from .models import Question, Profile, Tag


admin.site.register(Question)
admin.site.register(Profile)
admin.site.register(Tag)
