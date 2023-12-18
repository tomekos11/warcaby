from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
import json
import asyncio
import time
import cv2
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from copy import deepcopy

from .cv_optimised.algorithm_OK import Rules, Checkers
from .cv_optimised.test import ImageProcess, Board

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

rules = Rules(False, False, False, False)
rulesChanged = True
prevBoard = []

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
        global rules
        global prevBoard
        global rulesChanged
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if message['type'] == 'init':
            rulesChanged = True
            rules = Rules(message['settings']['forceTake'], message['settings']['takeBackward'],
                          message['settings']['queenStopsAfterTake'], message['settings']['queenMoveMaxOne'])

        ret, frame = cap.read()
        cv2.imwrite('frame.jpg', frame)
        image = cv2.imread('frame.jpg')

        board = Board(image)  # Wycięcie samej planszy z obrazu
        game = Checkers(rules)
        if board.board is not None:
            proc = ImageProcess(board.board)
            board = proc.frame_table()  # uzyskanie pionków
            # Send message
            boardListForGame = board.tolist()
            for rowKey, row in enumerate(boardListForGame):
                for colKey, col in enumerate(row):
                    if col == -1:
                        boardListForGame[rowKey][colKey] = 2
                    elif col == -2:
                        boardListForGame[rowKey][colKey] = 4
                    elif col == 1:
                        boardListForGame[rowKey][colKey] = 1
                    elif col == 2:
                        boardListForGame[rowKey][colKey] = 3
            print('------------------------------------------------')
            game.setBoard(boardListForGame)
            game.printBoard()
            boardToReturn = deepcopy(boardListForGame)
            S, W = game.minimaxPlay(1, maxDepth=4, evaluate=Checkers.evaluate2, enablePrint=True)
            if S:
                boardToReturn = game.makeBoardFromMoveList(boardToReturn)
            # if prevBoard != boardToReturn or rulesChanged:
            #     prevBoard = boardToReturn
            #     rulesChanged = False
            #     if S:
            #         boardToReturn = game.makeBoardFromMoveList(boardToReturn)
            #         print('koniec')
            async_to_sync(self.channel_layer.group_send)(self.group_name,{'success': True,'type': 'initial_board_positions','message': '','positions': boardToReturn})
        else:
            async_to_sync(self.channel_layer.group_send)(self.group_name,{'success': False,'type': 'initial_board_positions','message': '','positions': []})

    def initial_board_positions(self, event):
        message = event['message']
        positions = event['positions']
        success = event['success']

        self.send(text_data=json.dumps({
            'success': success,
            'type': 'board_positions',
            'message': message,
            'moves': positions,
        }))

    def current_position_message(self, event):
        message = event['message']
        moves = event['moves']
        success = event['success']
        is_legal = event['is_legal']

        self.send(text_data=json.dumps({
            'success': success,
            'is_legal': is_legal,
            'type': 'new_position',
            'message': message,
            'moves': moves,
        }))
