from django.urls import path
from .views import cover_view,main_view

urlpatterns = [
    path('', cover_view, name='static'),
    path('react/', main_view, name='react')
]
