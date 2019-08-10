#!/user/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url

from .views import *

app_name = 'df_user'

urlpatterns = [
    url(r'^register/$', register, name="register"),
    url(r'^register_handle/$', register_handle, name="register_handle"),
    url(r'^register_exist/$', register_exist, name="register_exist"),
    url(r'^login/$', login, name="login"),
    url(r'^login_handle/$', login_handle, name="login_handle"),
    url(r'^info/$', info, name="info"),
    url(r'^order/(\d+)$', order, name="order"),
    url(r'^site/$', site, name="site"),
    # url(r'^place_order/$', views.place_order),
    url(r'^logout/$', logout, name="logout"),
    # 登录页面验证码图片请求
    url(r'^get_valid_img/', GetValidImg, name='get_valid_img'),
    url(r'^download/(.*)/',download, name="download"),
    # url(r'^email/$', send_my_email, name="email"),
    url(r'^user_info/$', user_info, name="user_info"),
    url(r'^change_nickname/$', change_nickname, name="change_nickname"),
]