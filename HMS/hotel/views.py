from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from accounts.models import *
from room.models import *

@login_required(login_url='login')
def home(request):
    role = str(request.user.groups.all()[0])
    if role != "guest":
        return redirect("employee-profile", pk=request.user.id)
    else:
        return redirect("guest-profile", pk=request.user.id)