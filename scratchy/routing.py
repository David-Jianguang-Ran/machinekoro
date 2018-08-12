from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter , ChannelNameRouter
from django.urls import path

from machinekoro import consumers

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/consumers/<token>/",consumers.PlayerWSConsumer)
        ])
    ),
    "channel": ChannelNameRouter({
        'game_processor' : consumers.GameProcessorConsumer,
        'bot_processor' : consumers.BotProcessorConsumer
    })
})

