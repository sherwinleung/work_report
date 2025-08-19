from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import RegisterForm
from .models import User

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def user_list(request):
    users = User.objects.all().order_by("-date_joined")
    return render(request, "accounts/user_list.html", {"users": users})
