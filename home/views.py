from django.shortcuts import render

# Create your views here.

def index(request):
    """" A view to return the index pages """
    return render(request, 'home/index.html')


def privacy(request):
    return render(request, 'home/privacy.html')