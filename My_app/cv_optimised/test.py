import copy
import cv2
import numpy as np
from math import atan2, cos, sin, sqrt, pi
import os

class ImageProcess:
    def __init__(self, image):
        self.param1 = 70#regulacja
        self.param2 = 15#regulacja
        self.fields1 = self.fields2 = []
        self.FieldTable = [[1 for j in range(8)] for i in range(8)]
        self.img = image
        self.imageSplit()    

    def imageSplit(self):        
        # Przygotowanie obrazu do oceny, przekształcenie na odcienie szarości
        self.edgesImage = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        # Zastosowanie filtru medianowego     
        self.edgesImage = cv2.medianBlur(self.edgesImage, 5)
        # Lub zastosowanie rozmycia Gaussowskiego

        # Algorytm Otsu do automatycznego wyznaczania progu binaryzacji, todo do sprawdzenia jak sobie radzi
        self.edgesImage = cv2.Canny(self.edgesImage, self.param1, self.param2)

        # Pobranie rozmiaru obrazu
        rows, cols, depth = self.img.shape
        # Obrót o 180 stopni
        matrix = cv2.getRotationMatrix2D((cols / 2, rows / 2), -180, 1)
        self.trimmed = cv2.warpAffine(self.img, matrix, (cols, rows))

        # Zbiór punktów na podstawie których wycinamy pionki
        dic = self.pointsToCut(rows, cols)
        #Przygotowanie wycinków wszystkich punktów
        self.cutAndSaveBoardFields(dic, rows, cols)

    def cutAndSaveBoardFields(self, dic, rows, cols):
        for i in range(8):
            for j in range(8):
                if (i + j) % 2 == 1:
                    x1 = dic[i, j][0] - 10 if (dic[i, j][0] - 10) > 0 else dic[i, j][0]
                    y1 = dic[i, j][1] - 10 if (dic[i, j][1] - 10) > 0 else dic[i, j][1]
                    x2 = dic[i, j][0] + int(cols/8) + 10 if (dic[i, j][0] + int(cols/8) + 10) < cols else dic[i, j][0] + int(cols/8)
                    y2 = dic[i, j][1] + int(rows/8) + 10 if (dic[i, j][1] + int(rows/8) + 10) < rows else dic[i, j][1] + int(rows/8)
                    self.FieldTable[i][j] = self.trimmed[y1:y2, x1:x2]

    def pointsToCut(self, rows, cols):
        points = []
        for i in range(1, rows - int(rows/8/2), int(rows/8)):
            for j in range(1, cols - int(cols/8/2), int(cols/8)):
                points.append([j, i])
        dic = {}
        for i in range(8):
            for j in range(8):
                dic[i, j] = points[8 * i + j]
        return dic
        
    def frame_table(self):
        # Pusta tablica, w ktorej beda pionki
        result = [[0 for _ in range(8)] for _ in range(8)]
        for i in range(8):
            for j in range(8):
                if (i + j) % 2 == 1:
                    # Wyszukiwanie pionka, określanie koloru oraz typu
                    result[i][j] = self.searchForPawn(self.FieldTable[i][j], [i, j])
        return self.valueForPawn(result)
    
    def valueForPawn(self, board):
        """
        1 - > WHITE
        2 - > WHITE_KING
        -1 - > BLACK
        -2 - > BLACK_KING
        """
        for i in range(8):
            for j in range(8):
                if board[i][j] == 1:
                    board[i][j] = 1
                elif board[i][j] == -1:
                    board[i][j] = -1
                elif board[i][j] == 2:
                    board[i][j] = 2
                elif board[i][j] == -2:
                    board[i][j] = -2
                else:
                    board[i][j] = 0

        return np.rot90(board, k=2)
    
    def checkIsKing(self, img, radius, circle):
        # Sprawdzenie, czy pionek jest krolowka   
        circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=23 , minRadius= int(radius/2), maxRadius= int(radius - 0.2 * radius))
        if circles is None or not self.checkCircleIsCorrectKing(radius, circle, circles):
            return False
        else:
            return True     

    def checkCircleIsCorrectKing(self, radius, circle, circles):
        THRESOLD = 3
        # Ocena, czy znaleziony okrag moze nalezec do krolowki
        for i in circles[0]:
            if (radius > i[2] 
                and (circle[0] > i[0] - i[2] and circle[0] < i[0] + i[2]) and (circle[1] > i[1] - i[2] and circle[1] < i[1] + i[2])
                and (i[0] + i[2] < circle[0] + radius - THRESOLD) and (i[0] - i[2] > circle[0] - radius + THRESOLD) 
                and (i[1] + i[2] < circle[1] + radius - THRESOLD) and(i[1] + i[2] > circle[1] - radius + THRESOLD)):
                return True
        return False

    def checkCircleIsCorrect(self, img, circles):
        # Sprawdzenie poprawnosci znalezionych okregow
        contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        maxCont = max(contours, key=cv2.contourArea)            
        x, y, w, h = cv2.boundingRect(maxCont)        
        for i in circles[0]:
            if (w + 0.1 * w > 2 * i[2] or h + 0.1 * h > 2 * i[2]) and (w * 0.3 < i[2] or h * 0.3 < i[2]):
                return True, i
        return False, []

    def searchForPawn(self, img, pos):
        # Przygotowanie obrazu do oceny 
        img_color = copy.deepcopy(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_gray = copy.deepcopy(img)
        img = cv2.medianBlur(img, 5)
        img_copy = copy.deepcopy(img)
        # Transformacja Hougha do znalezienia okręgów na obrazie, todo dodanie ustawiania
        circles = cv2.HoughCircles(copy.deepcopy(img), cv2.HOUGH_GRADIENT, 1, 20, param1=150, param2=24, minRadius=0,
                                   maxRadius=100)
        # Nie ma okregow, to 0
        if circles is not None:
            # Na inty
            circles = np.uint16(np.around(circles))
            # Rysowanie do testów
            for i in circles[0, :]:
                cv2.circle(img, (i[0], i[1]), i[2], (255, 255, 255), 2)
            # board.showActualImage(img, 'circles')
            # Sprawdzenie okregow, wybranie najbardziej prawdopodobnego
            isGood, circle = self.checkCircleIsCorrect(img_gray, circles)
            if not isGood:
                return 0
        else:
            return 0
        # Rysowanie jak poszło wyszukiwanie okregow

        radius = circle[2]
        # Ocena, czy na obrazie znajduje sie drugi okrag - damka
        isKing = self.checkIsKing(img_copy, radius, circle)
        # Obliczenie sredniej pikseli wokol srodka okregu
        d = int(circle[2] / 1.6)
        x = circle[0]
        y = circle[1]
        suma = [0, 0, 0]
        x_p = y - d if y - d > 0 else 0
        y_p = x - d if x - d > 0 else 0
        for row in img_color[x_p:y + d, y_p:x + d]:
            for px in row:
                suma[0] += px[0]
                suma[1] += px[1]
                suma[2] += px[2]

        if suma[0] > suma[1]:
            return 2 if isKing else 1
        else:
            return -2 if isKing else -1

class Board:
    def __init__(self, image):
        self.image = image
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.board = self.getOnlyBoard(self.image)

    def setNewAttribute(self, image):
        self.image = image
        self.gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def getOnlyBoard(self, image):        
        # Skorygowanie orientacji (jeżeli plansza jest pochylona)
        adjusted_image = self.ImproveOrientation(image)
        if adjusted_image is not None:
            # Detekcja krawędzi
            self.edges = cv2.Canny(self.gray, 50, 150, apertureSize=3)
            # Znalezienie konturów
            contours, _ = cv2.findContours(self.edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)               
            # Pobranie największego konturu z obrazu(plansza)
            maxCont = max(contours, key=cv2.contourArea)
            # Pobranie oraz przyciecie obrazu na podsatwie maxCont
            x, y, w, h = cv2.boundingRect(maxCont)
            board = adjusted_image[y:y+h, x:x+w]
            self.setNewAttribute(copy.deepcopy(board))           
            #sprawdzenie, czy plansza jest zaslonieta, progi do dodania   
            if self.checkImageIsCovered(copy.deepcopy(board)):
                return None
            return board

    def ImproveOrientation(self, image):
        # Detekcja krawędzi
        edges = cv2.Canny(self.gray, 50, 150, apertureSize=3)
        # Znalezienie konturów
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)                 
        # Sprawdzenie, czy znaleziono kontury
        if contours:
            # Znalezienie największego obszaru (najprawdopodobniej planszy)
            maxContour = max(contours, key=cv2.contourArea)
            # Pobranie współrzędnych prostokąta otaczającego kontur
            x, y, w, h = cv2.boundingRect(maxContour)
            # Obliczenie kąta nachylenia planszy
            angle = self.getOrientation(copy.deepcopy(image))
            if angle < 10: 
                # Korekta orientacji przy użyciu transformacji afinicznej
                M = cv2.getRotationMatrix2D((x + w / 2, y + h / 2), angle, 1)
                adjusted_image = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))
                self.setNewAttribute(adjusted_image)          
                return adjusted_image
            else:
                return image            
        else:
            return None

    def getOrientation(self, img):
        # Konwersja obrazu na odcienie szarości
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)        
        # Binaryzacja obrazu
        _, bw = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        # Znajdowanie konturów w obrazie
        contours, _ = cv2.findContours(bw, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        # Wybór konturu o największej powierzchni
        pts = max(contours, key=cv2.contourArea)
        
        sz = len(pts)
        # Przygotowanie danych punktów dla PCA
        data_pts = np.empty((sz, 2), dtype=np.float64)
        for i in range(data_pts.shape[0]):
            data_pts[i,0] = pts[i,0,0]
            data_pts[i,1] = pts[i,0,1]
        
        mean = np.empty((0))
        # PCA (analiza głównych składowych)
        mean, eigenvectors, eigenvalues = cv2.PCACompute2(data_pts, mean)
        
        # Środek ciężkości konturu
        cntr = (int(mean[0,0]), int(mean[0,1]))
        # Rysowanie punktu środka ciężkości
        cv2.circle(img, cntr, 3, (255, 0, 255), 2)
        
        # Obliczenie kąta orientacji
        angle = atan2(eigenvectors[0,1], eigenvectors[0,0])

        # Zwrócenie obliczonego kąta orientacji
        return angle

    def checkImageIsCovered(self, img):
        #Sprawdzamy, czy plansza jest czyms zakryta po wycieciu
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        h, w = edges.shape
        size = h * w
        contours, _ = cv2.findContours(self.edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        maxContour = max(contours, key=cv2.contourArea)
        return cv2.contourArea(maxContour) < 0.6 * size

    def setNewAttribute(self, image):
        self.image = image
        self.gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def showActualImage(self, image, title="image", wait=True, destroy=False):
        cv2.imshow(title, image)
        if wait == True:
            cv2.waitKey(0)
        if destroy == True:
            cv2.destroyAllWindows()