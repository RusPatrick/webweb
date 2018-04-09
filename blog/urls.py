from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.question_list, name='question_list'),
    url(r'^signup/$', views.RegistForm.as_view(), name='signup'),
    url(r'^signin/$', views.login, name='signin'),
    url(r'^signout/$', views.logout, name='signout'),
    url(r'^question/(?P<qid>\d+)/$', views.question_detail, name='question_detail'),
    url(r'^ask/$', views.ask, name='ask'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^hot/$', views.hot, name='hot'),
    # url(r'^tag/$', views.searchByTag, name='SBT'),
]
