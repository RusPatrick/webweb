from django.conf.urls import url
from . import views
from django.urls import path


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^signin/$', views.signin, name='signin'),
    url(r'^signout/$', views.logout, name='signout'),
    url(r'^question/<int:questionId>$', views.question, name='question'),
    url(r'^ask/$', views.ask, name='ask'),
    url(r'^profile/$', views.profile, name='profile'),
    path('profile/<int:userId>', views.profile, name='profile'),
    url(r'^profile/edit$', views.editProfile, name='editProfile'),
    url(r'^tag/<str:tagName>$', views.tag, name='tag'),
    url(r'^like$', views.like, name='like'),
    # url(r'^tag/$', views.searchByTag, name='SBT'),
]
