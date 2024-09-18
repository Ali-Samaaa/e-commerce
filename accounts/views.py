from django.shortcuts import render, redirect
from django.views import View
from .forms import UserRegistrationForm, VerifyCodeForm, UserLoginFrom
from utils import send_opt_code
import random
from .models import OptCode, User
from django.contrib import messages
from datetime import timedelta
from django.utils import timezone


class UserRegisterView(View):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            random_code = random.randint(1000, 9999)
            send_opt_code(form.cleaned_data['phone'], random_code)
            OptCode.objects.create(phone_number=form.cleaned_data['phone'], code=random_code)
            request.session['user_registration_info'] = {
                'phone_number': form.cleaned_data['phone'],
                'email': form.cleaned_data['email'],
                'full_name': form.cleaned_data['full_name'],
                'password': form.cleaned_data['password']
            }
            messages.success(request, 'we sent you a message', 'success')
            return redirect('accounts:verify_code')
        return render(request, self.template_name, {'form': form})


class UserRegisterVerifyCodeView(View):
    form_class = VerifyCodeForm

    def get(self, request):
        form = self.form_class()
        return render(request, 'accounts/verify.html', {'form': form})

    def post(self, request):
        user_session = request.session['user_registration_info']
        code_instance = OptCode.objects.get(phone_number=user_session['phone_number'])
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if cd['code'] == code_instance.code:
                user = OptCode.objects.filter(phone_number=user_session['phone_number']).values('created')
                user = list(user)
                expired = user[0]['created'] + timedelta(minutes=2)
                if timezone.now() <= expired:
                    User.objects.create_user(user_session['phone_number'], user_session['email'], user_session['full_name'],
                                             user_session['password'])
                    code_instance.delete()
                    messages.success(request, 'you registered', 'success')
                    return redirect('home:home')
                else:
                    messages.error(request, 'you code is expired, please try again', 'danger')
                    code_instance.delete()
                    return render(request, 'accounts/register.html', {'form': form})
            else:
                messages.error(request, 'this code is wrong.', 'danger')
                return redirect('accounts:verify_code')
        return redirect('home:home')


class UserLoginView(View):
    form_class = UserLoginFrom

    def get(self, request):
        form = self.form_class()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            code = random.randint(1000, 9999)
            # send_opt_code(form.cleaned_data['phone_number'], code=code)
            OptCode.objects.create(phone_number=form.cleaned_data['phone_number'], code=code)
            print('B'*90)
            print(code)
            request.session['user_login_info'] = {
                'phone_number': form.cleaned_data['phone_number'],
                'password': form.cleaned_data['password']
            }
            messages.success(request, 'we send you a sms', 'success')
            return redirect('accounts:verify_code')
        return render(request, 'accounts/login.html', {'form': form})


class UserLoginVerifyCodeView(View):
    form_class = VerifyCodeForm

    def get(self, request):
        form = self.form_class()
        return render(request, 'accounts/verify.html', {'form': form})

    def post(self, request):
        user_session = request.session['user_login_info']
        code = OptCode.objects.filter(phone_number=user_session['code'])
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if cd['code'] == code.code:
                user = code.values('created')
                user = list(user)
                expired = user[0]['created'] + timedelta(minutes=2)
                print('A'*90)
                print(code.code)
                if timezone.now() <= expired:
                    User.objects.create_user(user_session['phone_number'], user_session['email'],
                                             user_session['full_name'], user_session['password'])
                    code.delete()
                    messages.success(request, 'you logged successfully', 'success')
                    return redirect('home:home')
                else:
                    messages.error(request, 'you code is expired, please try again', 'danger')
                    code.delete()
                    return redirect('accounts:user_login')
            else:
                messages.error(request, 'this code is wrong', 'danger')
                return redirect('home:verify_code')
        else:
            return redirect('home:home')
