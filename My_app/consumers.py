from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
import json
import asyncio
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class YourConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = "chat"
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        async_to_sync(self.channel_layer.group_send)(
          self.group_name,
          {
            'type' : 'chat_message',
            'message' : 'test'
          }
        )
    
    def chat_message(self, event):
      message = event['message']

      self.send(text_data=json.dumps({
        'type' : 'chat',
        'message' : message
      }))
    

    
