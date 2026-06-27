from django.contrib.auth import login
from django.shortcuts import redirect, render
from .models import User


def register(request):
    if request.method == 'POST':
        user = User.objects.create_user(
            phone=request.POST['phone'],
            fullname=request.POST.get('fullname', ''),
            password=request.POST.get('password') or None,
            role=User.Role.CUSTOMER,
        )
        login(request, user)
        return redirect('home')
    return render(request, 'accounts/register.html')
