import os

from django.shortcuts import render, redirect, HttpResponseRedirect, reverse
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
# from django.core.cache import cache
#
# import random
from hashlib import sha1

from django.utils.encoding import escape_uri_path

from .models import GoodsBrowser
from . import user_decorator
from .models import *
from .forms import ChangeNicknameForm
from df_order.models import *



def register(request):

    context = {
        'title': '用户注册',
    }
    return render(request, 'df_user/register.html', context)


def register_handle(request):

    username = request.POST.get('user_name')
    password = request.POST.get('pwd')
    confirm_pwd = request.POST.get('confirm_pwd')
    email = request.POST.get('email')
    print('---注册中-----')
    validcode = request.POST.get('validcode')
    if validcode.upper() != request.session.get('valid_code').upper():
        return redirect('/user/register/')
    # 判断两次密码一致性
    if password != confirm_pwd:
        return redirect('/user/register/')
    # 密码加密
    s1 = sha1()
    s1.update(password.encode('utf8'))
    encrypted_pwd = s1.hexdigest()

    # 创建对象
    UserInfo.objects.create(uname=username,
                           upwd=encrypted_pwd,
                           uemail=email)
    # 注册成功
    context = {
        'title': '用户登陆',
        'username': username,
    }
    return render(request, 'df_user/login.html', context)


def register_exist(request):
    username = request.GET.get('uname')
    count = UserInfo.objects.filter(uname=username).count()
    return JsonResponse({'count': count})


def login(request):
    uname = request.COOKIES.get('uname', '')
    context = {
        'title': '用户登陆',
        'error_name': 0,
        'error_pwd': 0,
        'uname': uname,
    }
    return render(request, 'df_user/login.html', context)


def login_handle(request):  # 没有利用ajax提交表单
    # 接受请求信息
    uname = request.POST.get('username')
    upwd = request.POST.get('pwd')
    jizhu = request.POST.get('jizhu', 0)
    users = UserInfo.objects.filter(uname=uname)
    validcode = request.POST.get('validcode')
    if validcode.upper() != request.session.get('valid_code').upper():
        context = {
            'title': '用户登陆',
            'error_name': 0,
            'error_pwd': 0,
            'uname': uname,
            'error_valid_code': 0,
        }
        return render(request, 'df_user/login.html', context)

    if len(users) == 1:  # 判断用户密码并跳转
        s1 = sha1()
        s1.update(upwd.encode('utf8'))
        if s1.hexdigest() == users[0].upwd:
            url = request.COOKIES.get('url', '/')
            red = HttpResponseRedirect(url)  # 继承与HttpResponse 在跳转的同时 设置一个cookie值
            # 是否勾选记住用户名，设置cookie
            if jizhu != 0:
                red.set_cookie('uname', uname)
            else:
                red.set_cookie('uname', '', max_age=-1)  # 设置过期cookie时间，立刻过期
            request.session['user_id'] = users[0].id
            request.session['user_name'] = uname
            return red
        else:
            context = {
                'title': '用户名登陆',
                'error_name': 0,
                'error_pwd': 1,
                'uname': uname,
                'upwd': upwd,
            }
            return render(request, 'df_user/login.html', context)
    else:
        context = {
            'title': '用户名登陆',
            'error_name': 1,
            'error_pwd': 0,
            'uname': uname,
            'upwd': upwd,
        }
        return render(request, 'df_user/login.html', context)


def logout(request):  # 用户登出
    request.session.flush()  # 清空当前用户所有session
    return redirect(reverse("df_goods:index"))


@user_decorator.login
def info(request):  # 用户中心
    username = request.session.get('user_name')
    user = UserInfo.objects.filter(uname=username).first()
    browser_goods = GoodsBrowser.objects.filter(user=user).order_by("-browser_time")
    goods_list = []
    if browser_goods:
        goods_list = [browser_good.good for browser_good in browser_goods]  # 从浏览商品记录中取出浏览商品
        explain = '最近浏览'
    else:
        explain = '无最近浏览'

    context = {
        'title': '用户中心',
        'page_name': 1,
        'user_phone': user.uphone,
        'user_address': user.uaddress,
        'user_name': username,
        'goods_list': goods_list,
        'explain': explain,
    }
    return render(request, 'df_user/user_center_info.html', context)


@user_decorator.login
def order(request, index):
    user_id = request.session['user_id']
    orders_list = OrderInfo.objects.filter(user_id=int(user_id)).order_by('-odate')
    paginator = Paginator(orders_list, 2)
    page = paginator.page(int(index))
    context = {
        'paginator': paginator,
        'page': page,
        # 'orders_list':orders_list,
        'title': "用户中心",
        'page_name': 1,
    }
    return render(request, 'df_user/user_center_order.html', context)


@user_decorator.login
def site(request):
    user = UserInfo.objects.get(id=request.session['user_id'])
    if request.method == "POST":
        user.ushou = request.POST.get('ushou')
        user.uaddress = request.POST.get('uaddress')
        user.uyoubian = request.POST.get('uyoubian')
        user.uphone = request.POST.get('uphone')
        user.save()
    context = {
        'page_name': 1,
        'title': '用户中心',
        'user': user,
    }
    return render(request, 'df_user/user_center_site.html', context)




from PIL import Image, ImageDraw, ImageFont
import random


def get(request):
    return render(request, 'login.html')

def GetValidImg(request):
    obj = ValidCodeImg()
    img_data,valid_code = obj.getValidCodeImg()
    request.session['valid_code'] = valid_code
    print("---------------")
    # f = open('test.png', 'wb')
    # f.write(img_data)
    # f.close()
    return HttpResponse(img_data)

from PIL import Image, ImageDraw, ImageFont
import random


class ValidCodeImg:
    def __init__(self, width=125, height=40, code_count=4, font_size=32, point_count=25, line_count=3,
                 img_format='png'):
        '''
        function : 生成一个经过降噪后的随机验证码的图片
        param :
        width：图片宽度 单位px
        height: 图片高度 单位px
        code_count: 验证码个数
        font_size: 字体大小
        point_count: 噪点个数
        line_count: 划线个数
        img_format: 图片格式
        '''
        self.width = width
        self.height = height
        self.code_count = code_count
        self.font_size = font_size
        self.point_count = point_count
        self.line_count = line_count
        self.img_format = img_format

    # 声明了静态方法，类可以不用实例化就可以调用该方法，当然也可以实例化后调用
    @staticmethod
    def getRandomColor():
        '''获取一个随机颜色(r,g,b)格式的'''
        c1 = random.randint(0, 255)
        c2 = random.randint(0, 255)
        c3 = random.randint(0, 255)
        return (c1, c2, c3)

    @staticmethod
    def getRandomStr():
        '''获取一个每个字符颜色随机的字符串'''
        random_num = str(random.randint(0, 9))
        random_low_alpha = chr(random.randint(97, 122))
        random_upper_alpha = chr(random.randint(65, 90))
        # 从序列中随机选取一个元素
        random_char = random.choice([random_num, random_low_alpha, random_upper_alpha])
        return random_char

    def getValidCodeImg(self):
        # 获取一个Image对象,参数分别时RGB模式.宽150,高30,随机颜色
        image = Image.new('RGB', (self.width, self.height), self.getRandomColor())

        # 获取一个画笔对象,将图片对象传过去
        draw = ImageDraw.Draw(image)

        # 获取一个font字体对象参数时ttf的字体文件的目录,以及字体的大小
        font_obj = ImageFont.truetype('static/Kumofont.ttf', size=self.font_size)

        temp = []

        for i in range(self.code_count):
            # 循环5次，获取5个随机字符串
            random_char = self.getRandomStr()

            # 在图片上一次写入得到的随机字符串,参数是:定位,字符串,颜色,字体
            # draw.text((10+i*30,-2),random_char,self.getRandomColor(),font=font_obj)
            # draw.text((10+i*30,-2),random_char,self.getRandomColor(),font=font_obj)
            draw.text((10 + i * 30, 2), random_char, self.getRandomColor(), font=font_obj)
            # 保存随机字符,以供验证用户输入的验证码是否正确时使用
            temp.append(random_char)
            valid_str = "".join(temp)

        # 噪点躁线
        # 划线
        for i in range(self.line_count):
            x1 = random.randint(0, self.width)
            x2 = random.randint(0, self.width)
            y1 = random.randint(0, self.height)
            y2 = random.randint(0, self.height)
            draw.line((x1, y1, x2, y2), fill=self.getRandomColor())
        # 画点
        for i in range(self.point_count):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            # 画点
            draw.point([x, y], fill=self.getRandomColor())
            # 画弧
            draw.arc((x, y, x + 4, y + 4), 0, 90, fill=self.getRandomColor())

        # 在内存中生成图片
        from io import BytesIO
        f = BytesIO()
        # 将生成的图片数据保存在io对象中
        image.save(f, self.img_format)
        # 从io对象里面取上一步保存的数据
        data = f.getvalue()
        f.close()

        return data, valid_str










# def email_code(request):
#     try:
#         uname = request.GET['uname']    #获取用户名
#     except Exception as e:
#         return JsonResponse({"errcode": 1, "errmsg": "参数错误"})
#     try:
#         form = forms.Check_Code(request.GET) #判断验证码的对错
#         fbool = form.is_valid()
#     except Exception as e:
#         return JsonResponse({"errcode":2,"errmsg":"验证码错误"})
#     if not fbool:
#         return JsonResponse({"errcode": 2, "errmsg": "验证码错误"})
#     else:
#         try:
#             user = UserInfo.objects.get(uname=uname)
#         except Exception as e:
#             return JsonResponse({"errcode":3,"errmsg": "该用户名未注册"})
#         email = user.uemail
#         code = str(random.randint(0,999999)).zfill(6) #生成验证码
#         cache.set(uname+"_email_code",code,60*5)
#         resp = sendemail(email,code)
#         if resp == '发送成功':
#             show_email = email[:3] + "***" + email[-8:]
#             return JsonResponse({"errcode":0,"errmsg":show_email.decode('gbk').encode('utf-8')+'邮箱发送成功'})
#         else:
#             return JsonResponse({"errcode":4,"errmsg":"邮箱验证码发送失败,请稍后重试或联系管理员"})


# def download(request):
#     file = open(r'C:\Users\Python\Desktop\daily_fresh_demo(2)\apps\df_user\models.py', 'rb')
#     response = HttpResponse(file)
#     response['Content-Type'] = 'application/octet-stream'  # 设置头信息，告诉浏览器这是个文件
#     response['Content-Disposition'] = 'attachment;filename="models.py"'
#     return response

from django.http import FileResponse

def download(request,name):
    print(name)
    name = name+'.rar'
    path =  os.path.join('static/data/', name)
    file=open(path, 'rb')
    response = FileResponse(file)
    response['Content-Type']='application/octet-stream'
    # 设置文件属性

    response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(name))
    # response['Content-Disposition'] = name
    return response

# from django.core.mail import send_mail, send_mass_mail
# from django.conf import settings
#
# def send_my_email(request):
#     title = "美团骑手offer"
#     msg = "恭喜你成为美团骑手"
#     email_from = settings.DEFAULT_FROM_EMAIL
#     reciever = [
#         '3207196028@qq.com'
#     ]
#     # 发送邮件
#     send_mail(title, msg, email_from, reciever)
#     return HttpResponse("ok")


def user_info(request):
    context = {}
    return render(request, 'df_user/user_info.html', context)

def change_nickname(request):
    redirect_to = request.GET.get('from', reverse('home'))

    if request.method == 'POST':
        form = ChangeNicknameForm(request.POST, user=request.uname)
        if form.is_valid():
            nickname_new = form.cleaned_data['nickname_new']
            userinfo,created = UserInfo.objects.get_or_create(user=request.uname)
            userinfo.nickname = nickname_new
            userinfo.save()
            return redirect(redirect_to)
    else:
        form = ChangeNicknameForm()

    context = {}
    context['page_title'] = '修改昵称'
    context['form_title'] = '修改昵称'
    context['submit_text'] = '修改'
    context['form'] = form
    return render(request, 'df_user/form.html', context)