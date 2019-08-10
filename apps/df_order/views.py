from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse
from django.conf import settings

from datetime import datetime
from decimal import Decimal

from .models import OrderInfo, OrderDetailInfo
from df_cart.models import CartInfo
from df_user.models import UserInfo
from df_user import user_decorator
from alipay import AliPay
import os


@user_decorator.login
def order(request):
    uid = request.session['user_id']
    user = UserInfo.objects.get(id=uid)
    cart_ids = request.GET.getlist('cart_id')

    order_info = OrderInfo()  # 创建一个订单对象
    now = datetime.now()
    order_info.oid = '%s%d' % (now.strftime('%Y%m%d%H%M%S'), uid)  # 订单号为订单提交时间和用户id的拼接

    carts = []
    total_price = 0
    for goods_id in cart_ids:
        cart = CartInfo.objects.get(id=goods_id)
        carts.append(cart)
        total_price = total_price + float(cart.count) * float(cart.goods.gprice)

    total_price = float('%0.2f' % total_price)
    trans_cost = 0  # 运费
    total_trans_price = trans_cost + total_price
    context = {
        'title': '提交订单',
        'page_name': 1,
        'user': user,
        'carts': carts,
        'total_price': float('%0.2f' % total_price),
        'trans_cost': trans_cost,
        'total_trans_price': total_trans_price,
        'order_id': order_info.oid,
        # 'value':value
    }
    return render(request, 'df_order/place_order.html', context)

'''
事务提交：
这些步骤中，任何一环节一旦出错则全部退回1
1. 创建订单对象
2. 判断商品库存是否充足
3. 创建 订单 详情 ，多个
4，修改商品库存
5. 删除购物车
'''


@user_decorator.login
@transaction.atomic()  # 事务
def order_handle(request):
    tran_id = transaction.savepoint()  # 保存事务发生点
    cart_ids = request.POST.get('cart_ids')  # 用户提交的订单购物车，此时cart_ids为字符串，例如'1,2,3,'
    user_id = request.session['user_id']  # 获取当前用户的id
    data = {}
    try:
        order_info = OrderInfo()  # 创建一个订单对象
        now = datetime.now()
        order_info.oid = '%s%d' % (now.strftime('%Y%m%d%H%M%S'), user_id)  # 订单号为订单提交时间和用户id的拼接
        order_info.odate = now  # 订单时间
        order_info.user_id = int(user_id)  # 订单的用户id
        order_info.ototal = Decimal(request.POST.get('total'))  # 从前端获取的订单总价
        order_info.save()  # 保存订单

        for cart_id in cart_ids.split(','):  # 逐个对用户提交订单中的每类商品即每一个小购物车
            cart = CartInfo.objects.get(pk=cart_id)  # 从CartInfo表中获取小购物车对象
            order_detail = OrderDetailInfo()  # 大订单中的每一个小商品订单
            order_detail.order = order_info  # 外键关联，小订单与大订单绑定
            goods = cart.goods  # 具体商品
            if cart.count <= goods.gkucun:  # 判断库存是否满足订单，如果满足，修改数据库
                goods.gkucun = goods.gkucun - cart.count
                goods.save()
                order_detail.goods = goods
                order_detail.price = goods.gprice
                order_detail.count = cart.count
                order_detail.save()
                cart.delete()  # 并删除当前购物车
            else:  # 否则，则事务回滚，订单取消
                transaction.savepoint_rollback(tran_id)
                return HttpResponse('库存不足')
        data['ok'] = 1
        transaction.savepoint_commit(tran_id)
    except Exception as e:
        print("%s" % e)
        print('未完成订单提交')
        transaction.savepoint_rollback(tran_id)  # 事务任何一个环节出错，则事务全部取消
    return JsonResponse(data)

def orderpay(request):
    '''订单支付'''
    order_id = request.POST.get('order_id')
    total_trans_price = request.POST.get('total_trans_price')

    #业务处理:使用python sdk调用支付宝的支付接口
    alipay = AliPay(
        appid=settings.ALIPAY_APPID,
        app_notify_url=None,  # 默认回调url
        app_private_key_path=os.path.join(settings.BASE_DIR, 'apps/df_order/app_private_key.pem'),
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_path=os.path.join(settings.BASE_DIR, 'apps/df_order/alipay_public_key.pem'),
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True  # 默认False
    )

    #调用支付接口
    # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order_id,    #订单id
        total_amount=str(total_trans_price),    #支付总结
        subject='蜘蛛侠数据%s'%order_id,
        return_url=None,
        notify_url=None # 可选, 不填则使用默认notify url
    )

    #返回应答
    url = settings.ALIPAY_URL + "?" + order_string
    print(url)
    return JsonResponse({"code": 0, "message": "请求支付成功","url": url})

#查询订单状态
def checkorder(request):
    # 创建用于进行支付宝支付的工具对象
    order_id = request.GET.get("order_id")
    print(order_id)
    alipay = AliPay(
        appid=settings.ALIPAY_APPID,
        app_notify_url=None,  # 默认回调url
        app_private_key_path=os.path.join(settings.BASE_DIR, "apps/df_order/app_private_key.pem"),
        alipay_public_key_path=os.path.join(settings.BASE_DIR, "apps/df_order/alipay_public_key.pem"),
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        sign_type="RSA2",  # RSA2,官方推荐，配置公钥的时候能看到
        debug=True  # 默认False  配合沙箱模式使用
    )

    while True:
        # 调用alipay工具查询支付结果
        response = alipay.api_alipay_trade_query(order_id)  # response是一个字典
        # 判断支付结果
        code = response.get("code")  # 支付宝接口调用成功或者错误的标志
        print(code)
        trade_status = response.get("trade_status")  # 用户支付的情况

        if code == "10000" and trade_status == "TRADE_SUCCESS":
            # 表示用户支付成功
            # 返回前端json，通知支付成功
            return JsonResponse({"code": 0, "message": "支付成功"})

        elif code == "40004" or (code == "10000" and trade_status == "WAIT_BUYER_PAY"):
            # 表示支付宝接口调用暂时失败，（支付宝的支付订单还未生成） 后者 等待用户支付
            # 继续查询
            print(code)
            print(trade_status)
            continue
        else:
            # 支付失败
            # 返回支付失败的通知
            return JsonResponse({"code": 1, "message": "支付失败"})

