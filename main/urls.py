from django.urls import path, include
from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('decor/<int:pk>/', views.decor, name='decor'),
    path('segment/<int:pk>/', views.sam_segment, name='segment'),
    path('suggestions/<int:pk>/', views.suggestions, name='suggestions'),
]
if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)