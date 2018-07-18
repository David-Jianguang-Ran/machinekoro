from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from machinekoro import consumers

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/consumers/<serial>/",consumers.PlayerSocket)
        ])
    ),
    # will the routing below break vanilla django views? i'm worried
    "http": AuthMiddlewareStack(
        URLRouter([
            path("/consumers/poke_dealer/<serial>/", consumers.DealerSocket),
            path("/consumers/poke_bot/<serial>/", consumers.BotSocket)
        ])
    )
})

