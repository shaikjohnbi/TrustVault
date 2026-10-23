from django.shortcuts import render


def home(request):
    return render(request, "documents/home.html")


def upload_page(request):
    return render(request, "documents/upload.html")