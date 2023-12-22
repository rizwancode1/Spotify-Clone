from django.shortcuts import render 
from django.contrib.auth.models import User

# Create your views here.

def login_view(request):
    return render(request, 'accounts/login.html')



