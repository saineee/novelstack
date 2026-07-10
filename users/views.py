from django.shortcuts import render, redirect
from .forms import CreateUserForm

def register(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            return render(request, 'users/registration.html', {'form': form})
    else:
        form = CreateUserForm()
    return render(request, 'users/registration.html', {'form': form})