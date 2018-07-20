from django.urls import path
from . import views

urlpatterns = [
    path('', views.cover_view, name='static'),
    path('/new/',views.new_game_poke,name="new_game"),
    path('/join/<game_id>', views.join_game_poke, name="join_game"),
    path('/main/', views.main_view, name='react')
]
