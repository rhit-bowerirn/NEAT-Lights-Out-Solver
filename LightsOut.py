import random
import copy
import pygame
from pygame.locals import KEYDOWN, K_q
import sys
import time
import sympy
from sympy import *



class LightsOut:   
    def __init__(self, colLength, rowLength, boardWidth, boardHeight, onColor, offColor, winEvent):
        self.winEvent = winEvent
        self.window = pygame.display.set_mode((boardWidth, boardHeight))
        self.onColor = onColor
        self.offColor = offColor

        self.colLength = colLength
        self.rowLength = rowLength
        self.boardWidth = boardWidth
        self.boardHeight = boardHeight
        self.turnsTaken = 0
        
        self.adjacencyMatrix = self.calculateAdjacencyMatrix()
        self.board = self.generateRandomBoard()
        self.solution = self.findSolution()

        while (self.checkForWin() or self.solution == -1):          
            self.board = self.generateRandomBoard()
            self.solution = self.findSolution()
            
        self.initialState = copy.deepcopy(self.board)
        self.drawBoard()


    #Create the matrix used to solve every position of the board
    def calculateAdjacencyMatrix(self):
        adjacencyMatrix = []
        #Essentially just running the checks in update on each tile then updating the matrix accordingly
        for row in range (self.rowLength):
            for col in range (self.colLength):
                adjacencyList = [0] * self.rowLength * self.colLength
                adjacencyList[(row * self.rowLength) + col] = 1
                if row > 0:
                    adjacencyList[((row - 1) * self.rowLength) + col] = 1
                if row < self.rowLength - 1:
                    adjacencyList[((row + 1) * self.rowLength) + col] = 1
                if col > 0:
                    adjacencyList[(row * self.rowLength) + (col - 1)] = 1
                if col < self.colLength - 1:
                    adjacencyList[row * self.rowLength + (col + 1)] = 1
                adjacencyMatrix.append(adjacencyList)
        return adjacencyMatrix

    #Create a random board
    def generateRandomBoard(self):
        board = []
        for r in range(self.rowLength * self.colLength):
            board.append(random.randint(0, 1))
        return board

    #Solve the current board state
    def findSolution(self):
        len = self.rowLength * self.colLength
        augMat = copy.deepcopy(self.adjacencyMatrix)
        for r in range (len):
            augMat[r].append(self.board[r])
        rref = Matrix.rref(Matrix(augMat))[0]
        lastRow = rref.row(len - 1)

        #Only happens in the constructor, we can easily check for this
        if lastRow[len - 1] == 0 and lastRow[len] != 0:
            return -1
    
        #Since lights have 2 states, take the numerator % 2 to find the number of state changes for each tile
        solution = rref.col(len)
        for i in range (len):
            solution[i] *= fraction(solution[i])[1]
            solution[i] %= 2
        return solution

    #Used for NEAT to make sure the test games stay the same across each generation
    def restore(self):
        self.board = self.initialState
        self.solution = self.findSolution()
        self.turnsTaken = 0

    def currentSolution(self):
        return self.solution
    
    def turns(self):
        return self.turnsTaken

    def turnsRemaining(self):
        turnsRemaining = 0
        for i in range(len(self.solution)):
            turnsRemaining += self.solution[i]
        return turnsRemaining

    #Used for NEAT, takes a set of state changes to apply to the board
    def play(self, inputs):
        pygame.init()
        self.window = pygame.display.set_mode((self.boardWidth, self.boardHeight))
        self.drawBoard()
        for r in range (self.rowLength):
            for c in range (self.colLength):
                if inputs[r * self.rowLength + c]:
                    self.updateBoard((c * self.boardWidth // self.colLength, r * self.boardHeight // self.rowLength))
                    time.sleep(0.15)
        self.solution = self.findSolution()
        pygame.quit()
        time.sleep(.1)

    #Used for playing the game, takes the coordinates of the mouse click
    def updateBoard(self, pos):
        self.turnsTaken += 1
        col = pos[0] // (self.boardWidth // self.colLength)
        row = pos[1] // (self.boardHeight // self.rowLength)
        self.board[(row * self.rowLength) + col] ^= 1
        if row > 0:
            self.board[((row - 1) * self.rowLength) + col] ^= 1
        if row < self.rowLength - 1:
            self.board[((row + 1) * self.rowLength) + col] ^= 1
        if col > 0:
            self.board[(row * self.rowLength) + (col - 1)] ^= 1
        if col < self.colLength - 1:
            self.board[row * self.rowLength + (col + 1)] ^= 1
        
        self.solution = self.findSolution()
        self.drawBoard()
        
        if self.checkForWin():
            win = pygame.event.Event(self.winEvent, message = "You Win!")
            pygame.event.post(win)
            
    #Check if the game is over
    def checkForWin(self):
        for i in range(self.rowLength * self.colLength):
            if self.board[i]:
                return False
        return True

    #Draw the board
    def drawBoard(self):
        cellBorder = 1
        celldimX = (self.boardWidth // self.colLength) - (2 * cellBorder)
        celldimY = (self.boardHeight // self.rowLength) - (2 * cellBorder)
        for r in range(self.rowLength):  # 0,1,2,3
            for c in range(self.colLength):  # 0,1,2,3
                if self.board[r * self.rowLength + c]:
                    color = self.onColor
                else: 
                    color = self.offColor
                pygame.draw.rect(self.window, color, pygame.Rect(
                (celldimY * c) + (2 * c) + 1,
                (celldimX * r) + (2 * r) + 1,
                celldimX, celldimY))
        pygame.display.update()

    def toString(self):
        if self.checkForWin():
            return f'You won in {self.turnsTaken} turns!'
            
        solutionString = ""
        solutionList = self.solution.tolist()
        for r in range (self.rowLength):
            solutionString += "\n"
            for c in range (self.colLength):
                solutionString += f'[{solutionList[r * self.rowLength + c][0]}]'
        return f'Turns Taken: {self.turnsTaken}, Solution: {solutionString}'


def main():
    pygame.init()
    WIN = pygame.USEREVENT + 1
    colLength = 3
    rowLength = 3
    onColor = (255, 255, 0)
    offColor = (160, 160, 160)
    game = LightsOut(colLength, rowLength, 750, 750, onColor, offColor, WIN)
    print(game.toString())
    
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                game.updateBoard(event.pos)
                print(game.toString())
            if event.type == WIN:
                pygame.quit()
                sys.exit()
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_q:
                pygame.quit()
                sys.exit()

if __name__ == '__main__':
    main()
