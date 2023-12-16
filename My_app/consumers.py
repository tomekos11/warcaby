from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
import json
import asyncio
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .cv_optimised.test import ImageProcess, Board
import os
import numpy as np

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

def calcPossibleMoves(y, x):
    possible_moves = [(y+1, x+1), (y+1, x-1), (y-1, x-1), (y-1, x+1)]
    
    # Filter moves to stay within the boundaries (0 to 7)
    valid_moves = [(new_y, new_x) for new_y, new_x in possible_moves if 0 <= new_y <= 7 and 0 <= new_x <= 7]
    
    return valid_moves

def countPawnAmount(board):
    pawn_counter = 0
    black_pawns_counter = 0
    black_queens_counter = 0
    white_pawns_counter = 0
    white_queens_counter = 0
    pawns = []
    taken_position = []

    # plansza sie zaczyna w lewym gornym rogu
    # i = y
    # j = x
    for i, row in enumerate(board):
        pawns.append([])
        for j, cell in enumerate(row):
            if cell == 1:
                white_pawns_counter += 1
                pawns[i].append({
                  "color": "white", #blue
                  "role" : "pawn",
                  "actual_position": (i,j),
                  "possible_moves": calcPossibleMoves(i,j)
                  })
                taken_position.append((i,j))
            elif cell == 2:
                white_queens_counter += 1
                pawns[i].append({
                  "color": "white", #blue
                  "role" : "queen",
                  "actual_position": (i,j),
                  "possible_moves": calcPossibleMoves(i,j)
                  })
                taken_position.append((i,j))
            elif cell == -1:
                black_pawns_counter += 1
                pawns[i].append({
                  "color": "black", #green
                  "role" : "pawn",
                  "actual_position": (i,j),
                  "possible_moves": calcPossibleMoves(i,j)
                  })
                taken_position.append((i,j))
            elif cell == -2:
                black_queens_counter += 1
                pawns[i].append({
                  "color": "black", #green
                  "role" : "queen",
                  "actual_position": (i,j),
                  "possible_moves": calcPossibleMoves(i,j)
                  })
                taken_position.append((i,j))
            # else:
            #     pawns[i].append('empty slot')
            # print(pawns[i][j], '\n')
            
    pawn_counter = white_pawns_counter + white_queens_counter + black_pawns_counter + black_queens_counter
    if (white_pawns_counter + white_queens_counter) == 0 or (black_pawns_counter + white_pawns_counter) == 0:
        endGame()

    data = {
      "pawn_counter" : pawn_counter,
      "white_pawns_counter" : white_pawns_counter,
      "white_queens_counter" : white_queens_counter,
      "black_pawns_counter" : black_pawns_counter,
      "black_queens_counter" : black_queens_counter,
      "pawns_data" : pawns,
      "taken_positions" : taken_position
    }
    # print(data)
    return data

def endGame():
      deleteBoardJSON('old_board.json')

def checkIfValid(board, old_board_filename):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(script_directory, old_board_filename), 'r') as old_board_file:
        file = json.load(old_board_file)

    if(file['board'] == board.tolist()):
        print('plansze sa takie same')
        return 0
    
    print(file['details']['iteration_counter'])
    if file['details']['iteration_counter'] > 0:
        old_pawns_positions = file['details']['pawns']['taken_positions']
        print(old_pawns_positions)

        actual = countPawnAmount(board)
        actual_pawns_positions = actual['taken_positions']
        print(actual_pawns_positions)
        
        tuple1 = (0, 1, 1, 3)
        tuple2 = (2, 3, 4, 5)

        common_elements = tuple(set(tuple1) & set(tuple2))
        print(common_elements)
        # for i, (elem1, elem2) in enumerate(zip(old_pawns_positions, actual_pawns_positions)):
        #     if tuple(elem1) != elem2:
        #         print(f"Różnica na indeksie {i}: {elem1} != {elem2}")
        #     else:
        #         print("Tablice są identyczne.")
        return 1

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

        image_path = 'C:/Users/TOM/Desktop/Projekt_Warcaby/Warcaby/My_app/cv_optimised/plansza2.jpg'

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
                          'board' : board.tolist(),
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
        'board' : board,
      }))