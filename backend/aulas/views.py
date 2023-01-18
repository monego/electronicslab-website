from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from .forms import DisciplinaForm

@login_required(login_url="http://localhost:5173/login")
def index(request):
    form = DisciplinaForm

    if request.method == 'POST':
        print(request.POST)
        form = DisciplinaForm(request.POST)
        if form.is_valid():
            form.save()
    context = {'form': form}
    return render(request, 'aulas/index.html', context)
