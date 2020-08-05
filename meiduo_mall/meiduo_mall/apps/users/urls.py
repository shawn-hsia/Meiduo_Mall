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
    # 接收用户添加收货地址的接口路由映射
    re_path(r'^addresses/create/$', views.CreateAddressView.as_view()),
    # 展示当前用户的所有收货地址路由映射
    re_path(r'^addresses/$', views.AddressView.as_view()),
    # 展示当前用户修改收货地址的路由映射
    re_path(r'^addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view()),
    # 删除当前登录用户的收货地址
    re_path(r'^addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view()),
    # 设置登录用户的默认地址
    re_path(r'^addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view()),
    # 设置修改用户收货地址的标题接口映射
    re_path(r'^addresses/(?P<address_id>\d+)/title/$', views.UpdateTitleAddressView.as_view()),
    # 修改密码接口路由映射
    re_path(r'^password/$', views.ChangePasswordView.as_view()),
]