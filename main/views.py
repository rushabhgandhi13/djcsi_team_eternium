from django.shortcuts import render, redirect
from .models import Imag

# Create your views here.

def home(request):
    if request.method=="POST":
        img=Imag()
        img.image=request.FILES.get('roomimage')
        img.save()
        return redirect('decor', pk=img.img_id)
    return render(request, 'main/home.html')

def decor(request, pk):
    img=Imag.objects.get(img_id=pk)
    return render(request, 'main/decor.html', {'img': img})
