from django.urls import re_path
from oauth import views

urlpatterns = [
    re_path(r'^qq/authorization/$', views.QQFirstView.as_view())
]
