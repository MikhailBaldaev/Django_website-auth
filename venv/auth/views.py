from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from auth.tokens import generate_token


from Login import settings

# Create your views here.
def home(request):
    context = {}
    return render(request, 'auth/index.html', context)


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        email = request.POST.get('email')
        password1 = request.POST.get('pass1')
        password2 = request.POST.get('pass2')

        if User.objects.filter(username=username):
            messages.error(request, f'Username {username} already exist! Please try another one.')
            return redirect('home')

        '''if User.objects.filter(email=email):
            messages.error(request, f'Email {email} already registered! Please try another one.')
            return redirect('home')'''

        if len(username) > 10:
            messages.error(request, 'Username should be under 10 charecters')
            return redirect('home')

        if password1 != password2:
            messages.error(request, 'Passwords should be the same!')
            return redirect('home')

        if not username.isalnum:
            messages.error(request, 'Username should contain only numbers and letters!')
            return redirect('home')

        my_user = User.objects.create_user(username, email, password1)
        my_user.first_name = first_name
        my_user.last_name = last_name
        my_user.is_active = False

        my_user.save()

        messages.success(request, 'You have created an account.')

        # Email sender

        subject = 'Welcome to the WebSite!'
        message = f'Hello, {my_user.first_name}!\nThank you for visiting our WebSite!\nPlease, confirm you email to confirm ' \
                  f'your email!'
        from_email = settings.EMAIL_HOST_USER
        to_list = [my_user.email]
        send_mail(subject, message, from_email, to_list, fail_silently=False)

        # Mail confirmation

        current_site = get_current_site(request)
        email_subject = 'Email confirmation on the WebSite'
        email_message = render_to_string('email.html', {
            'name': my_user.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(my_user.pk)),
            'token': generate_token.make_token(my_user),
        })
        email = EmailMessage(
            email_subject,
            email_message,
            settings.EMAIL_HOST_USER,
            [my_user.email],

        )
        email.fail_silently = True
        email.send()

        return redirect('signin')

    context = {}
    return render(request, 'auth/signup.html', context)


def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('pass1')

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            context = {'first_name': user.first_name}
            return render(request, 'auth/index.html', context)
        else:
            messages.error(request, 'Wrong username or password')
            return redirect('home')

    context = {}
    return render(request, 'auth/signin.html', context)


def signout(request):
    logout(request)
    messages.success(request, 'You logged out')
    '''context = {}
    return render(request, 'auth/signout.html', context)'''
    return redirect('home')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        my_user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        my_user = None
    if my_user and generate_token.check_token(my_user, token):
        my_user.is_active = True
        my_user.save()
        login(requst, my_user)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')

