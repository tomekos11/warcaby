from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
import time

class YourConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("some_group", self.channel_name)

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.send(text_data=json.dumps({
            'message': 'Personalizowna wiadomosc' +  str(time.time())
        }))
        