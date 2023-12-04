from My_app.settings import BASE_DIR
from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home_view(request):
  template_path = BASE_DIR / 'My_app' / 'frontend' / 'views' / 'home.html'

  return render(request, template_path)