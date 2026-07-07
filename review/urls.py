from django.urls import path
from . import views

urlpatterns = [
    path('<slug:slug>/add-review/', views.add_review, name='add_review'),
]
