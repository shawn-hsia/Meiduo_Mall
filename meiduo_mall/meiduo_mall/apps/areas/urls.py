from django.urls import re_path

from areas import views





urlpatterns = [
    # 第一级行政区划理由
    re_path(r'^areas/$', views.ProvinceAreasView.as_view()),
    re_path(r'^areas/(?P<pk>[1-9]\d+)/$', views.SubAreasView.as_view()),

]