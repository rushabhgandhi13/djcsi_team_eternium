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
    if request.method == "POST":
        color=str(request.POST.get('color'))
        final=[]
        for i in (0, 2, 4):
            decimal = int(color[i+1:i+3], 16)
            final.append(decimal)
        return redirect('decor', pk=pk)
    return render(request, 'main/decor.html', {'img': img})

