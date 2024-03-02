from django.shortcuts import render
from django.contrib import messages
from .models import ContactUs

# Create your views here.

def index(request):
    """" A view to return the index pages """
    return render(request, 'home/index.html')


def privacy(request):
    return render(request, 'home/privacy.html')

def error_404(request, exception):
    return render(request, '404.html', status=404)

def newsletter_signup(request):
    """ Function to render the newsletter signup page"""
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email-address']
        message = request.POST['message']
        contact = ContactUs(
            name=name,
            email=email,
            message=message
        )
        contact.save()
        messages.info(request, "Your form was successfully submitted")
    return render(request, 'home/newsletter_signup.html')
