from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.post_list, name='post_list'),
    url(r'^index$', views.post_list, name='index'),
    url(r'^register/$', views.RegisterFormView.as_view(), name='register'),
    url(r'^singin/$', views.LoginFormView.as_view(), name='singin'),
    url(r'ˆlogout/$', views.LogoutView.as_view(), name='logout'),
]


# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)