from django.urls import re_path
from users import views

urlpatterns = [
    # 用户注册验证用户是否已经存在
    re_path(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
    # 验证注册是用户手机是否存在
    re_path(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    # 用户注册逻辑接口完成注册
    re_path(r'^register/$', views.RegisterView.as_view()),
    # 用户登录接口
    re_path(r'^login/$', views.LoginView.as_view()),
    # 用户登出接口
    re_path(r'^logout/$', views.LogoutView.as_view()),
    # 用户个人中心页
    re_path(r'^info/$', views.UserInfoView.as_view()),
    # 用户中心页添加邮箱接口
    re_path(r'^emails/$', views.EmailView.as_view()),
    # 接收用户邮箱认证链接并激活用户邮箱接口
    re_path(r'^emails/verification/$', views.VerifyEmailView.as_view()),
]