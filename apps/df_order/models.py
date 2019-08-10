from django.db import models

from df_goods.models import GoodsInfo
from df_user.models import UserInfo

class OrderInfo(models.Model):  # 大订单
    PAY_METHOD = (
        (1, '货到付款'),
        (2, '微信支付'),
        (3, '支付宝'),
        (4, '银联支付')
    )
    PAY_METHOD_DIC = {
        '1': '货到付款',
        '2': '微信支付',
        '3': '支付宝',
        '4': '银联支付'
    }
    ORDER_status = (
        (1, '待支付'),
        (2, '代发货'),
        (3, '待收货'),
        (4, '待评价'),
        (5, '已完成'),
    )
    ORDER_status_dic = {
        '1': '待支付',
        '2': '代发货',
        '3': '待收货',
        '4': '待评价',
        '5': '已完成',
    }

    oid = models.CharField(max_length=20, primary_key=True, verbose_name="订单编号")
    pay_method = models.SmallIntegerField(choices=PAY_METHOD, default=3, verbose_name='支付方式')
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, verbose_name="订单用户")
    odate = models.DateTimeField(auto_now=True, verbose_name="时间")
    oIsPay = models.SmallIntegerField(choices=ORDER_status, default=1, verbose_name="订单状态")
    ototal = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="总价")
    oaddress = models.CharField(max_length=150, verbose_name="订单地址")
    # 虽然订单总价可以由多个商品的单价以及数量求得，但是由于用户订单的总价的大量使用，忽略total的冗余度

    class Meta:
        verbose_name = "订单"
        verbose_name_plural = verbose_name

    def __str__(self):
        # return self.user.uname + "在" + str(self.odate) + "的订单"
        return "{0}在的订单{1}".format(self.user.uname, self.odate)


# 无法实现：真实支付，物流信息
class OrderDetailInfo(models.Model):  # 大订单中的具体某一商品订单

    goods = models.ForeignKey(GoodsInfo, on_delete=models.CASCADE, verbose_name="商品")  # 关联商品信息
    order = models.ForeignKey(OrderInfo, on_delete=models.CASCADE, verbose_name="订单")
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="商品价格")
    count = models.IntegerField(verbose_name="商品数")

    class Meta:
        verbose_name = "订单详情"
        verbose_name_plural = verbose_name

    def __str__(self):
        # return self.goods.gtitle + "(数量为" + str(self.count)  + ")"
        return "{0}(数量为{1})".format(self.goods.gtitle, self.count)