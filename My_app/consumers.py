from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
import json
import asyncio
import time
import cv2
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from copy import deepcopy

from .algorithm.NextMoveAlgorithm import Rules, Checkers
from .algorithm.ImageProcessor import ImageProcessor

from ultralytics import YOLO

model = YOLO("My_app/algorithm/best.pt")

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
        print("START")
        global rules
        global prevBoard
        global rulesChanged
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if message['type'] == 'init':
            rulesChanged = True
            rules = Rules(message['settings']['forceTake'], message['settings']['takeBackward'],
                          message['settings']['queenStopsAfterTake'], message['settings']['queenMoveMaxOne'])

        _, frame = cap.read()
        cv2.imwrite('frame.jpg', frame)
        image = cv2.imread('frame.jpg')


        data = ImageProcessor(model, image)
        board = data.get_board()
        board_with_index = data.return_board_with_correct_index()
        # data.draw_image_with_perspective_changed()
        # data.draw_yolo_image()
        game = Checkers(rules)
        if board['status'] == 'ok':
            print('------------------------------------------------')
            game.setBoard(board_with_index)
            game.printBoard()
            boardToReturn = deepcopy(board_with_index)
            S, W = game.minimaxPlay(1, maxDepth=5, evaluate=Checkers.evaluate2, enablePrint=True)
            if S:
                boardToReturn = game.makeBoardFromMoveList(boardToReturn)
                print(boardToReturn)
            # if prevBoard != boardToReturn or rulesChanged:
            #     prevBoard = boardToReturn
            #     rulesChanged = False
            #     if S:
            #         boardToReturn = game.makeBoardFromMoveList(boardToReturn)
            #         print('koniec')
            async_to_sync(self.channel_layer.group_send)(self.group_name,{'success': True, 'isWinner': W, 'type': 'initial_board_positions', 'message': '','positions': boardToReturn, 'status': board['status'] })
        else:
            # data.draw_yolo_image()
            async_to_sync(self.channel_layer.group_send)(self.group_name,{'success': False, 'isWinner': None, 'type': 'initial_board_positions', 'message': '', 'positions': board_with_index, 'status': board['status'] })

    def initial_board_positions(self, event):
        message = event['message']
        positions = event['positions']
        success = event['success']
        status = event['status']
        isWinner = event['isWinner']

        self.send(text_data=json.dumps({
            'success': success,
            'type': 'board_positions',
            'message': message,
            'moves': positions,
            'status' : status,
            'isWinner' : isWinner == 'WHITE' or isWinner == 'BLACK',
            'winnerColor': 1 if isWinner == 'WHITE' else 0
        }))

    # def current_position_message(self, event):
    #     message = event['message']
    #     moves = event['moves']
    #     success = event['success']
    #     is_legal = event['is_legal']
    #
    #     self.send(text_data=json.dumps({
    #         'success': success,
    #         'is_legal': is_legal,
    #         'type': 'new_position',
    #         'message': message,
    #         'moves': moves,
    #     }))
