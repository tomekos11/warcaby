from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
import json
import asyncio
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .cv_optimised.test import ImageProcess, Board

class YourConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = "chat"
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()
        # CV scripts
        # script_directory = os.path.dirname(os.path.abspath(__file__))
        # image_path = os.path.join(script_directory, 'plansza.jpg')
        image_path = ('C:/Users/MikolajSalamak/PycharmProjects/warcaby/My_app/cv_optimised/plansza.jpg')

        board = Board(image_path)# Wycięcie samej planszy z obrazu
        if board.board is not None:
            proc = ImageProcess(board.board)
            board = proc.frame_table()#uzyskanie pionków
            #Send message
            async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
              'success' : True,
              'type' : 'initial_board_positions',
              'message' : 'test',
              'positions' : board.tolist()
            })
        else:
            async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
              'success' : False,
              'type' : 'initial_board_positions',
              'message' : 'test',
              'positions' : board
            })


    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
    
    def initial_board_positions(self, event):
      message = event['message']
      positions = event['positions']
      success = event['success']

      self.send(text_data=json.dumps({
        'success' : success,
        'type' : 'board_positions',
        'message' : message,
        'moves' : [[positions]],
      }))

    def current_position_message(self, event):
      message = event['message']
      moves = event['moves']
      success = event['success']
      is_legal = event['is_legal']

      self.send(text_data=json.dumps({
        'success' : success,
        'is_legal' : is_legal,
        'type' : 'new_position',
        'message' : message,
        'moves' : moves,
      }))
    