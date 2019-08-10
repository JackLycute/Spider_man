#!/user/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

app_name = 'df_order'

urlpatterns = [
    url(r'^$', views.order, name="order"),
    url(r'^push/$', views.order_handle, name="push"),
    url(r'^orderpay/$', views.orderpay, name="orderpay"),#订单支付
    url(r'^checkorder/$', views.checkorder, name='checkorder'),
    # url(r'^order/(\d+)$', views.order, name="order"),
]