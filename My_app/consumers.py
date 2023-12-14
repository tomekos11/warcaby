from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
import json
import asyncio
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .cv_optimised.test import ImageProcess, Board
import os

iteration_counter = 0

def InitialiseBoardJSON(board, details, filename):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_directory, filename)

    with open(file_path, 'w') as jsonfile:
        json.dump({
          "details" : details,
          "board" : board.tolist()
        }, jsonfile, indent=2)

def modifyBoardJSON(board, details, old_board_filename):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_directory, old_board_filename)

    with open(file_path, 'w') as jsonfile:
        json.dump({
          "details" : details,
          "board" : board
        }, jsonfile, indent=2)

def deleteBoardJSON(old_board_filename):
    try:
        script_directory = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_directory, old_board_filename)
        os.remove(file_path)
        print(f'Plik {old_board_filename} został usunięty.')
    except FileNotFoundError:
        print(f'Plik {old_board_filename} nie istnieje.')
    except Exception as e:
        print(f'Wystąpił błąd podczas usuwania pliku: {e}')

def countPawnAmount(board):
    pawn_counter = 0
    black_counter = 0
    white_counter = 0
  
    for row in board:
      for cell in row:
        if cell != 0:
          pawn_counter+=1
        if cell == 1 or cell == 2:
          white_counter+=1
        elif cell == -1 or cell == -2:
          black_counter+=1
    
    if white_counter == 0 or black_counter == 0:
        endGame()

    data = {
      "pawn_counter" : pawn_counter,
      "white_counter" : white_counter,
      "black_counter" : black_counter
    }
    return data

def endGame():
      deleteBoardJSON('old_board.json')

def checkIfValid(board, old_board_filename):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(script_directory, old_board_filename), 'r') as old_board:
        old_board = json.load(old_board)

    if(old_board == board.tolist()):
        print('plansze sa takie same')
        return 0

    return 1

class YourConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = "chat"
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()
        
        image_path = 'C:/Users/TOM/Desktop/Projekt_Warcaby/Warcaby/My_app/cv_optimised/plansza.jpg'

        board = Board(image_path)# Wycięcie samej planszy z obrazu
        if board.board is not None:
            proc = ImageProcess(board.board)
            board = proc.frame_table()#uzyskanie pionków
            details = {
                "iteration_counter" : iteration_counter,
                "pawns" : countPawnAmount(board)
            }
            InitialiseBoardJSON(board, details, "old_board.json")
            #Send message
            async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
              'success' : True,
              'is_legal' : True,
              'type' : 'new_position_message',
              'message' : 'Inicjalizacja planszy',
              'board' : board.tolist()
            })


    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )
        endGame()

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        image_path = 'C:/Users/TOM/Desktop/Projekt_Warcaby/Warcaby/My_app/cv_optimised/plansza.jpg'

        board = Board(image_path)# Wycięcie samej planszy z obrazu
        if board.board is not None:
            proc = ImageProcess(board.board)
            board = proc.frame_table()#uzyskanie pionków
            global iteration_counter
            
            if checkIfValid(board, "old_board.json") == 1:
                iteration_counter+=1
                details = {
                    "iteration_counter" : iteration_counter,
                    "pawns" : countPawnAmount(board)
                }
                modifyBoardJSON(board.tolist(), details, "old_board.json")

                async_to_sync(self.channel_layer.group_send)(
                          self.group_name,
                          {
                            'success': True,
                            'type' : 'new_position_message',
                            'message' : 'Wykonano prawidłowy ruch',
                            'is_legal' : True,
                            'board' : board.tolist()
                          })
            else:
                async_to_sync(self.channel_layer.group_send)(
                        self.group_name,
                        {
                          'success': True,
                          'type' : 'new_position_message',
                          'message' : 'Cofnij ten ruch!!',
                          'is_legal' : False,
                          'board' : board.tolist()
                        })
        

    def new_position_message(self, event):
      message = event['message']
      board = event['board']
      success = event['success']
      is_legal = event['is_legal']

      self.send(text_data=json.dumps({
        'success' : success,
        'is_legal' : is_legal,
        'type' : 'new_position',
        'message' : message,
        'board' : board
      }))