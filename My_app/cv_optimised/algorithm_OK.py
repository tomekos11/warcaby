from collections import Counter
import random
from copy import deepcopy


class Checkers():
    WHITE = 1
    BLACK = 2
    WHITE_KING = 3
    BLACK_KING = 4
    movesX = [1, 1, -1, -1]
    movesY = [1, -1, 1, -1]
    OO = 10 ** 9

    def __init__(self, rules):
        self.size = 8
        self.board = []
        self.rules = rules
        self.moveList = []

    def setBoard(self, board):
        self.board = deepcopy(board)

    def printBoard(self, x: int = None, y: int = None):
        for i in range(self.size):
            for j in range(self.size):
                if i == x and j == y:
                    print("\033[92m", end="")

                if self.board[i][j] == 0:
                    print("-", end=" ")
                else:
                    print(self.board[i][j], end=" ")

                if i == x and j == y:
                    print("\033[0m", end="")
            print()
        print()

    def makeBoardFromMoveList(self, beforeBoard):
        variants = []
        print('DUPA', self.moveList)
        for variantKey, variant in enumerate([self.moveList]):
            variants.append([])
            for moveKey, move in enumerate(variant):
                if len(variants[variantKey]) == 0:
                    moveTable = deepcopy(beforeBoard)
                    variants[variantKey].append(moveTable)
                else:
                    moveTable = deepcopy(variants[variantKey][len(variants[variantKey]) - 1])
                    # Wykonanie wybranego ruchu
                    x = variant[moveKey - 1][0]
                    y = variant[moveKey - 1][1]
                    nx = move[0]
                    ny = move[1]

                    moveTable[nx][ny] = moveTable[x][y]
                    moveTable[x][y] = 0

                    if abs(nx - x) == 2:
                        dx = nx - x
                        dy = ny - y
                        moveTable[x + dx // 2][y + dy // 2] = 0
                    elif abs(nx - x) >= 2:
                        dirX = 1 if nx > x else -1
                        dirY = 1 if ny > y else -1
                        for i in range(1, abs(nx - x)):
                            nextX = x + dirX * i
                            nextY = y + dirY * i
                            if self.isValid(nextX, nextY) and moveTable[nextX][nextY] != 0:
                                moveTable[nextX][nextY] = 0
                                break

                    if moveTable[nx][ny] == self.WHITE and nx == self.size - 1:
                        moveTable[nx][ny] = self.WHITE_KING
                    if moveTable[nx][ny] == self.BLACK and nx == 0:
                        moveTable[nx][ny] = self.BLACK_KING
                    # print("moves", variant, pawn, variant[moveKey-1][0], variant[moveKey-1][1],  "------------")
                    if variants[variantKey][len(variants[variantKey]) - 1] != moveTable:
                        variants[variantKey].append(moveTable)

        return variants

    def encodeBoard(self):
        # Przypisanie wartosci kazdemu polu
        value = 0
        for i in range(self.size):
            for j in range(self.size):
                num = i * self.size + j + 5
                value += num * self.board[i][j]
        return value

    def isValid(self, x, y):
        # Czy ruch miesci sie na planszy
        return x >= 0 and y >= 0 and x < self.size and y < self.size

    def nextPositions(self, x, y, befX=-1, befY=-1):
        # Nastepne mozliwe ruchy
        if self.board[x][y] == 0:
            return []
        player = self.board[x][y] % 2
        return self.playerMoves(x, y, player, befX=befX, befY=befY)

    def playerMoves(self, x, y, player, befX=-1, befY=-1):
        # Wygenerowania ruchow dla zasad
        normalMoves = []
        gainMoves = []
        dir = 1 if player == self.WHITE else - 1
        if self.board[x][y] <= 2 or (self.board[x][y] > 2 and self.rules.kingOnlyOneField):
            for i in range(4):
                if befX != -1 and befY != -1:
                    dirX = -1 if x > befX else 1
                    dirY = -1 if y > befY else 1
                    if self.movesX[i] == dirX and self.movesY[i] == dirY:
                        continue
                        # print("xd")
                nextX = x + dir * self.movesX[i]
                nextY = y + dir * self.movesY[i]
                if self.isValid(nextX, nextY):
                    if self.board[nextX][nextY] == 0 and (i < 2 or self.board[x][y] > 2):
                        normalMoves.append((nextX, nextY))
                    elif self.board[nextX][nextY] % 2 != player % 2 and self.board[nextX][nextY] != 0 and (
                            i < 2 or self.rules.rearBeating or self.board[x][y] > 2):
                        # print(self.board[nextX][nextY], player)
                        nextX += dir * self.movesX[i]
                        nextY += dir * self.movesY[i]
                        if self.isValid(nextX, nextY) and self.board[nextX][nextY] == 0:
                            # print('bb', x,y,nextX,nextY)
                            gainMoves.append((nextX, nextY))
        else:
            for i in range(4):
                gain = False
                if befX != -1 and befY != -1:
                    dirX = -1 if x > befX else 1
                    dirY = -1 if y > befY else 1
                    if self.movesX[i] == dirX and self.movesY[i] == dirY:
                        continue
                for j in range(1, len(self.board)):
                    nextX = x + j * self.movesX[i]
                    nextY = y + j * self.movesY[i]
                    if self.isValid(nextX, nextY):
                        if self.board[nextX][nextY] == 0 and gain == False:
                            normalMoves.append((nextX, nextY))
                        elif self.board[nextX][nextY] % 2 != player and self.board[nextX][nextY] != 0 and gain == False:
                            gain = True
                            nextX += self.movesX[i]
                            nextY += self.movesY[i]
                            if self.isValid(nextX, nextY) and self.board[nextX][nextY] == 0:
                                gainMoves.append((nextX, nextY))
                                nxt = j + 1 if self.rules.kingStopAfterBeating else len(self.board)
                                for k in range(j, nxt):
                                    nextX += self.movesX[i]
                                    nextY += self.movesY[i]
                                    if self.isValid(nextX, nextY) and self.board[nextX][nextY] == 0:
                                        gainMoves.append((nextX, nextY))
                                    else:
                                        break
                            else:
                                break
        # print(normalMoves, gainMoves)
        return normalMoves, gainMoves

    def nextMoves(self, player):
        # Lista ruchow, ktore gracz moze wykonac
        captureMoves = []
        normalMoves = []
        for x in range(self.size):
            for y in range(self.size):
                if self.board[x][y] != 0 and self.board[x][y] % 2 == player:
                    normal, capture = self.nextPositions(x, y)
                    if len(normal) != 0:
                        normalMoves.append(((x, y), normal))
                    if len(capture) != 0:
                        captureMoves.append(((x, y), capture))
        if len(captureMoves) and self.rules.obligationBeating:
            return captureMoves
        return captureMoves + normalMoves

    def playMove(self, x, y, nx, ny):
        # Wykonanie wybranego ruchu
        self.board[nx][ny] = self.board[x][y]
        self.board[x][y] = 0

        removed = 0
        if abs(nx - x) == 2:
            dx = nx - x
            dy = ny - y
            removed = self.board[x + dx // 2][y + dy // 2]
            self.board[x + dx // 2][y + dy // 2] = 0
        elif abs(nx - x) >= 2:
            dirX = 1 if nx > x else -1
            dirY = 1 if ny > y else -1
            for i in range(1, abs(nx - x)):
                nextX = x + dirX * i
                nextY = y + dirY * i
                if self.isValid(nextX, nextY) and self.board[nextX][nextY] != 0:
                    removed = (self.board[nextX][nextY], nextX, nextY)
                    self.board[nextX][nextY] = 0
                    break
        """
        Tutaj nie wiem do konca jak sie zachowac, bo przy biciu do tylu i obowiazkowym wyjdzie
        to smiesznie (?)
        """
        if self.board[nx][ny] == self.WHITE and nx == self.size - 1:
            self.board[nx][ny] = self.WHITE_KING
            return False, removed, True
        if self.board[nx][ny] == self.BLACK and nx == 0:
            self.board[nx][ny] = self.BLACK_KING
            return False, removed, True
        if abs(nx - x) < 2 or removed == 0:
            return False, removed, False
        return True, removed, False

    def undoMove(self, x, y, nx, ny, removed=0, promoted=False):
        # Cofniecie wykonanego ruchu
        if promoted:
            if self.board[nx][ny] == self.WHITE_KING:
                self.board[nx][ny] = self.WHITE

            if self.board[nx][ny] == self.BLACK_KING:
                self.board[nx][ny] = self.BLACK

        self.board[x][y] = self.board[nx][ny]
        self.board[nx][ny] = 0

        if abs(nx - x) > 2 and isinstance(removed, tuple):
            self.board[removed[1]][removed[2]] = removed[0]

        if abs(nx - x) == 2:
            dx = nx - x
            dy = ny - y
            self.board[x + dx // 2][y + dy // 2] = removed

    def evaluate1(self, maximizer):
        # Ocena planszy
        boardScore = 0
        for row in self.board:
            for cell in row:
                if cell != 0:
                    if cell % 2 == maximizer:
                        boardScore += (cell + 1) // 2
                    else:
                        boardScore -= (cell + 1) // 2
        return boardScore * 1000

    def evaluate2(self, maximizer):
        # Funkcja oceniajaca, 3
        men = 0
        kings = 0
        backRow = 0
        middleBox = 0
        middleRow = 0
        vulnerable = 0
        protected = 0
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] != 0:
                    sign = 1 if self.board[i][j] % 2 == maximizer else -1
                    if self.board[i][j] <= 2:
                        men += sign * 1
                    else:
                        kings += sign * 1
                    if sign == 1 and (
                            (i == 0 and maximizer == self.WHITE) or (i == self.size - 1 and maximizer == self.BLACK)):
                        backRow += 1
                    if i == self.size / 2 - 1 or i == self.size / 2:
                        if j >= self.size / 2 - 2 and j < self.size / 2 + 2:
                            middleBox += sign * 1
                        else:
                            middleRow += sign * 1

                    myDir = 1 if maximizer == self.WHITE else -1
                    vul = False
                    for k in range(4):
                        x = i + self.movesX[k]
                        y = j + self.movesY[k]
                        n = i - self.movesX[k]
                        m = j - self.movesY[k]
                        opDir = abs(x - n) / (x - n)
                        if self.isValid(x, y) and self.board[x][y] != 0 and self.board[x][y] % 2 != maximizer \
                                and self.isValid(n, m) and self.board[n][m] == 0 and (
                                self.board[x][y] > 2 or myDir != opDir):
                            vul = True
                            break

                    if vul:
                        vulnerable += sign * 1
                    else:
                        protected += sign * 1

        return men * 2000 + kings * 4000 + backRow * 400 + middleBox * 250 + middleRow * 50 - 300 * vulnerable + 300 * protected

    def cellContains(self, x, y, player):
        # Czy pionek gracza znajduje sie na polu
        return self.board[x][y] != 0 and self.board[x][y] % 2 == player

    def minimax(self, player, maximizer, depth=0, alpha=-OO, beta=OO, maxDepth=4, evaluate=evaluate1, moves=None):
        # Score z minimaxa
        if moves == None:
            moves = self.nextMoves(player)
            # print('mv', player, moves)
        if len(moves) == 0 or depth == maxDepth:
            score = evaluate(self, maximizer)
            # self.printBoard()##
            # print('score', score)
            if score < 0:
                score += depth
            return score

        bestValue = -self.OO
        if player != maximizer:
            bestValue = self.OO
        moves.sort(key=lambda move: len(move[1]))
        for position in moves:
            x, y = position[0]
            for nx, ny in position[1]:
                canCapture, removed, promoted = self.playMove(x, y, nx, ny)
                played = False
                # print(player, depth, canCapture, self.evaluate2(player), x, y, nx, ny)
                # self.printBoard()##
                if canCapture:
                    _, nextCaptures = self.nextPositions(nx, ny, befX=x, befY=y)
                    # print(x, y, nx, ny, nextCaptures)##
                    if len(nextCaptures) != 0:
                        played = True
                        nMoves = [((nx, ny), nextCaptures)]
                        if player == maximizer:
                            # print('1', bestValue, player)##
                            bestValue = max(bestValue,
                                            self.minimax(player, maximizer, depth, alpha, beta, maxDepth, evaluate,
                                                         nMoves))
                            alpha = max(alpha, bestValue)
                        else:
                            # print('2', bestValue, player)##
                            bestValue = min(bestValue,
                                            self.minimax(player, maximizer, depth, alpha, beta, maxDepth, evaluate,
                                                         nMoves))
                            beta = min(beta, bestValue)
                if not played:
                    if player == maximizer:
                        # print('3', bestValue, player)##
                        bestValue = max(bestValue,
                                        self.minimax((player + 1) % 2, maximizer, depth + 1, alpha, beta, maxDepth,
                                                     evaluate))
                        alpha = max(alpha, bestValue)
                    else:
                        # print('4', bestValue, player)##
                        bestValue = min(bestValue,
                                        self.minimax((player + 1) % 2, maximizer, depth + 1, alpha, beta, maxDepth,
                                                     evaluate))
                        beta = min(beta, bestValue)
                self.undoMove(x, y, nx, ny, removed, promoted)
                if beta <= alpha:
                    break
            if beta <= alpha:
                break
        return bestValue

    def minimaxPlay(self, player, moves=None, maxDepth=4, evaluate=evaluate1, enablePrint=True, depth=0):
        # Wykonanie ruchu z minimaxa
        if moves == None:
            moves = self.nextMoves(player)
            # print('moves', moves)##
        if len(moves) == 0:
            if enablePrint:
                winner = "WHITE" if player == self.BLACK else "BLACK"
            return False, winner

        random.shuffle(moves)

        bestValue = -self.OO
        bestMove = []
        for position in moves:
            x, y = position[0]
            for nx, ny in position[1]:
                # print('fMove', x, y, nx, ny)##
                canCapture, removed, promoted = self.playMove(x, y, nx, ny)
                _, nextCaptures = self.nextPositions(nx, ny, befX=x, befY=y)
                if canCapture and len(nextCaptures):
                    nxt_player = player
                    nextCaptures = [((nx, ny), [(i[0], i[1])]) for i in nextCaptures]
                else:
                    nxt_player = 0 if player == 1 else 0
                    nextCaptures = None
                # print('nextCap', nextCaptures, nxt_player)##
                value = self.minimax(nxt_player, player, maxDepth=maxDepth, evaluate=evaluate, moves=nextCaptures)
                self.undoMove(x, y, nx, ny, removed, promoted)
                print('value', value, x, y, nx, ny)  ##
                if value > bestValue:
                    # bestMove = []
                    bestValue = value
                    bestMove = (x, y, nx, ny)
        print('dupa', bestMove)
        # self.searchForNextCapturedMove(bestMove)
        x, y, nx, ny = bestMove
        if enablePrint:
            if len(moves):
                print(moves)
            self.moveList.append((x, y, nx, ny))
            print(f"Move from ({x}, {y}) to ({nx}, {ny})")

        canCapture, removed, _ = self.playMove(x, y, nx, ny)
        print('this', canCapture, removed)
        if enablePrint:
            self.printBoard(nx, ny)

        if canCapture:
            _, captures = self.nextPositions(nx, ny, befX=x, befY=y)
            if len(captures) != 0:
                self.minimaxPlay(player, [((nx, ny), captures)], maxDepth, evaluate, enablePrint)
        reset = removed != 0
        return True, None

    def searchForNextCapturedMove(self, move, actualMove=[]):
        self.printBoard()
        print("pp", move, actualMove)
        for i in move:
            x, y, nx, ny = i[-4], i[-3], i[-2], i[-1]
            if not len(actualMove):
                actualMove.append((x, y))
            canCapture, removed, promoted = self.playMove(x, y, nx, ny)
            if canCapture:
                print(x, y, nx, ny)
                _, captures = self.nextPositions(nx, ny, befX=x, befY=y)
                print('cap', captures)
                if len(captures):
                    actualMove.append((nx, ny))
                    # print('capb', captures)
                    captures = [(nx, ny, x, y) for x, y in captures]
                    #### tu tylko te ktore maja poczatek jak xy
                    print('capaf', captures)
                    print(x, y, nx, ny)
                    self.searchForNextCapturedMove(captures, actualMove)
                    actualMove.pop()
                else:
                    actualMove.append((nx, ny))
                    self.moveList.append(deepcopy(actualMove))
                    actualMove.pop()
            else:
                self.moveList.append([(x, y), (nx, ny)])
                actualMove = []
            self.undoMove(x, y, nx, ny, removed, promoted)

    def parse(self, moveList):
        if len(moveList) > 1:
            return [[(moveList[0][0], moveList[0][1])] + [(moveList[0][2], moveList[0][3])] + [(move[2], move[3])] for
                    move in moveList[1:]]
        else:
            return [[(moveList[0][0], moveList[0][1])] + [(moveList[0][2], moveList[0][3])]]


class Rules():
    def __init__(self, obligation=False, rear=False, stopAfter=False, kingField=False):
        self.obligationBeating = obligation
        self.rearBeating = rear
        self.kingStopAfterBeating = stopAfter
        self.kingOnlyOneField = kingField


# rules = Rules(True, True, False, False)
# game = Checkers(rules)
# blocked_board = [
#     [0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0],
#     [1, 0, 0, 0, 0, 0, 0, 0],
#     [0, 2, 0, 2, 0, 0, 0, 2],
#     [0, 0, 2, 0, 0, 0, 0, 0],
#     [0, 0, 0, 2, 0, 2, 0, 0],
#     [2, 0, 0, 0, 2, 0, 2, 0]
# ]
# game.setBoard(blocked_board)
# player_to_move = 1  # 0 - black, 1 - white, biale w dol, czarne w gore
# S, W = game.minimaxPlay(player_to_move, maxDepth=4, evaluate=Checkers.evaluate2, enablePrint=True)
# if S and len(game.moveList):
#     print(game.parse(game.moveList))