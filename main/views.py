from django.shortcuts import render, redirect

# Create your views here.

def home(request):
    if request.method=="POST":
        print(request.FILES)
        return redirect('home')
    return render(request, 'main/home.html')
