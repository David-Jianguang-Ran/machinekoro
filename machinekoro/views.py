from django.shortcuts import render,redirect

from . import controllers


# Create your views here.
def cover_view(request):
    return render(request, 'static.html')


def new_game_poke(request):
    """
    This function makes new MatchSession db object AND
    new TokenRegister db object when poked,
    then it redirects client to main_view with kwarg token = uuid string
    :param request:
    :return:
    """
    match_controller = controllers.MatchController()
    match_id = match_controller.initialize_new_match()
    token = match_controller.add_player_to_match(match_id, prime=True)
    return redirect(main_view,token=token)


def join_game_poke(request, match_id):
    """
    This function makes new TokenRegister db object when poked,
    then redirects client to main_view with kwarg token = uuid string
    :param request:
    :return:
    """
    match_controller = controllers.MatchController()
    token = match_controller.add_player_to_match(match_id, prime=False)
    if token:
        return redirect(main_view,token=token)
    else:
        return redirect(error_view,error_msg='Game Session Already in Progress, Connection Failed')


def main_view(request, token):
    """
    This function renders 'the one template to rule them all' with the context token passed in
    :param request:
    :param token:
    :return:
    """
    ws_url = "ws://127.0.0.1:8000/ws/consumers/" + token + "/"
    context={
        "ws_url":ws_url
    }
    return render(request,'reactEnabled.html',context)


def error_view(request, error_msg):
    context = {
        'message' : error_msg
    }
    return render(request,'error.html',context)