from django.shortcuts import render

from django.http import HttpResponse
from .models import Image

def home(request):
	data = Image.objects.all()
	person = {
	"person_img": data
	}
	return render(request, 'guesswho_app/home.html', person)

def post(request):
	data = Image.objects.all()
	person = {
	"person_img": data
	}
	return render(request, 'guesswho_app/post_img.html', person)
