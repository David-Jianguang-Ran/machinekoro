from django.shortcuts import render,redirect

from . import controllers

# Create your views here.


# place holder views

def cover_view(request):
    return render(request, 'static.html')


def new_game_poke(request):
    match_controller = controllers.MatchController()
    match_id = match_controller.initialize_new_match()
    token = match_controller.add_player_to_match(match_id, prime=True)
    return redirect(main_view,token=token)


def join_game_poke(request, match_id):
    match_controller = controllers.MatchController()
    token = match_controller.add_player_to_match(match_id, prime=False)
    return redirect(main_view,token=token)


def main_view(request, token):
    context={
        "token":token
    }
    return render(request,'reactEnabled.html',context)