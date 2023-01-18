#!/usr/bin/env python3

from django.shortcuts import render

def index(request):
    return render(request, 'index.html')
