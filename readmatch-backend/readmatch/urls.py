"""
URL configuration for readmatch project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from users import views

urlpatterns = [
    path('api/upload-csv/', views.upload_csv, name='upload_csv'),
    path('api/match/', views.trigger_match, name='find_match'),
    path('api/shuffle/', views.shuffle_match, name='shuffle_match'),
    path('api/view-matches/<int:user_id>/', views.view_matches, name='view_matches'),
]
