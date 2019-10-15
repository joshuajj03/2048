import pygame, sys, random, copy
from pygame.locals import *
pygame.init()
# Create the constants (go ahead and experiment with different values)
BOARDWIDTH = 4  # number of columns in the board
BOARDHEIGHT = 4 # number of rows in the board
TILESIZE = 200
WINDOWWIDTH = 800
WINDOWHEIGHT = 900
BOARDERSIZE = 5
FPS = 60
BLANK = None

#                 R    G    B
BLACK =         (  0,   0,   0)
WHITE =         (255, 255, 255)
GREYTAN =       (178, 166, 153)
CREAM =         (255, 253, 208)
GREY =          (178, 178, 178)
WHITE =         (255, 255, 255)
RED =           (178,   0,   0)
GREEN =         (0  , 178,   0)
TRANSPARENT =   (  0,   0,   0,  255)

BGCOLOR = GREYTAN
TILECOLOR = CREAM
TEXTCOLOR = BLACK
BORDERCOLOR = GREY
BASICFONTSIZE = 40
ENDFONTSIZE = 80

BUTTONCOLOR = WHITE
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = WHITE

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

BOARDSURFACE = pygame.Surface((800, 800))
FPSCLOCK = pygame.time.Clock()
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
DISPLAYSURF.fill(WHITE)
BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)
ENDFONT = pygame.font.Font('freesansbold.ttf', ENDFONTSIZE)
UNDO_SURF = BASICFONT.render('Undo', True, BLACK, RED)
WIN_SURF = ENDFONT.render('You Win!', True, BLACK, GREEN)
LOSE_SURF = ENDFONT.render('You Lose!', True, BLACK, RED)
UNDO_RECT = UNDO_SURF.get_rect()
UNDO_RECT.topleft = (WINDOWWIDTH - 120, 30)
board = []
history = []
points = 0


def main():

    slideTo = ""
    notEnded = True
    hasWon = False

    pygame.display.set_caption('2048')



    setup()
    drawBoard()
    while True:
        global points


        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYUP:
                # check if the user pressed a key to slide a tile
                if event.key in (K_LEFT, K_a):
                    slideTo = LEFT
                elif event.key in (K_RIGHT, K_d):
                    slideTo = RIGHT
                elif event.key in (K_UP, K_w):
                    slideTo = UP
                elif event.key in (K_DOWN, K_s):
                    slideTo = DOWN
            if notEnded:
                if event.type == MOUSEBUTTONUP:
                    x,y = event.pos
                    if UNDO_RECT.collidepoint(x, y):
                        undo()
        

        
        if notEnded:
            if slideTo:
                slide(slideTo)
                slideTo = ""
            DISPLAYSURF.fill(WHITE)
            updatePoints()
            DISPLAYSURF.blit(UNDO_SURF, UNDO_RECT)
        else:
            if hasWon:
                DISPLAYSURF.fill(GREEN)
                DISPLAYSURF.blit(WIN_SURF, (WINDOWWIDTH/2 - 200, 10))
            else:
                DISPLAYSURF.fill(RED)
                DISPLAYSURF.blit(LOSE_SURF, (WINDOWWIDTH / 2 - 200, 10))

        notEnded, hasWon = checkEndConditions()

        drawBoard()
        pygame.display.update()


def drawBoard():
    BOARDSURFACE.fill(GREYTAN)
    pygame.draw.line(BOARDSURFACE, GREY, (2,0), (2,800 -2), BOARDERSIZE)
    pygame.draw.line(BOARDSURFACE, GREY, (800-3,2), (800-3,800-3), BOARDERSIZE)
    pygame.draw.line(BOARDSURFACE, GREY, (2, 800-3), (800-3, 800-3), BOARDERSIZE)
    pygame.draw.line(BOARDSURFACE, GREY, (2, 2), (800-3, 2), BOARDERSIZE)
    for pos in range(TILESIZE - BOARDERSIZE, 800- TILESIZE, TILESIZE):
        pygame.draw.line(BOARDSURFACE, GREY, (pos, 2), (pos, 800), BOARDERSIZE*2)
        pygame.draw.line(BOARDSURFACE, GREY, (2, pos), (800, pos), BOARDERSIZE*2)
    DISPLAYSURF.blit(BOARDSURFACE, (0, 100))
    for column in board:
        for square in column:
            if square.tileValue != 0 and square.isMoving == False:
                square.drawTile()



def setup():
    for x in range(4):
        xcoord = 3+ x*(TILESIZE)
        column = []
        for y in range(4):
            ycoord = 103+ y * (TILESIZE)
            column.append(numberTile(xcoord, ycoord, x, y))
        board.append(column)
    tileArray = []
    x = 0
    while x<2:
        rand1=random.randrange(0,4)
        rand2 = random.randrange(0,4)
        if board[rand1][rand2].tileValue == 0:
            board[rand1][rand2].changeValue(2)
            x+=1
    historyCopy = []
    for x in range(BOARDWIDTH):
        copycolumn = []
        for y in range(BOARDWIDTH):
            copycolumn.append(numberTile(board[x][y].xpos, board[x][y].ypos, board[x][y].xbox, board[x][y].ybox))
            copycolumn[y].changeValue(board[x][y].tileValue)
        historyCopy.append(copycolumn)
    history.append(historyCopy)

def slide(direct):
     global points
     historyCopy = []
     for x in range(BOARDWIDTH):
        copycolumn = []
        for y in range(BOARDWIDTH):
            copycolumn.append(numberTile(board[x][y].xpos, board[x][y].ypos, board[x][y].xbox, board[x][y].ybox))
            copycolumn[y].changeValue(board[x][y].tileValue)
        historyCopy.append(copycolumn)
     history.append(historyCopy)
     boardCopy = []
     for x in range(BOARDWIDTH):
         copycolumn =[]
         for y in range(BOARDWIDTH):
             copycolumn.append(numberTile(board[x][y].xpos, board[x][y].ypos, board[x][y].xbox, board[x][y].ybox))
             copycolumn[y].changeValue(board[x][y].tileValue)
             copycolumn[y].hasMerged= board[x][y].hasMerged
         boardCopy.append(copycolumn)
     canMove = True
     hasMoved = False
     while canMove:
            canMove = False
            xValues =[]
            yValues = []
            if( direct == UP):
                for x in range(BOARDWIDTH):
                    for y in range(1, BOARDHEIGHT):
                        if( (board[x][y-1].tileValue == 0 or board[x][y-1].isMoving or (board[x][y-1].tileValue == board[x][y].tileValue and not board[x][y-1].hasMerged and not board[x][y].hasMerged) )and board[x][y].tileValue> 0):
                            canMove =True
                            board[x][y].isMoving = True
                            xValues.append(x)
                            yValues.append(y)
                            hasMoved = True
            elif(direct == DOWN):
                for x in range(BOARDWIDTH):
                    for y in reversed(range(BOARDHEIGHT-1)):
                        if( (board[x][y+1].tileValue == 0 or board[x][y+1].isMoving or (board[x][y+1].tileValue == board[x][y].tileValue and not board[x][y+1].hasMerged and not board[x][y].hasMerged))and board[x][y].tileValue> 0):
                            canMove =True
                            board[x][y].isMoving = True
                            xValues.append(x)
                            yValues.append(y)
                            hasMoved = True
            elif(direct == LEFT):
                for x in range(1,BOARDWIDTH):
                    for y in range(BOARDHEIGHT):
                        if( (board[x-1][y].tileValue == 0 or board[x-1][y].isMoving or (board[x-1][y].tileValue == board[x][y].tileValue and not board[x-1][y].hasMerged and not board[x][y].hasMerged))and board[x][y].tileValue> 0):
                            canMove =True
                            board[x][y].isMoving = True
                            xValues.append(x)
                            yValues.append(y)
                            hasMoved = True
            elif(direct == RIGHT):
                for x in reversed(range(BOARDWIDTH-1)):
                    for y in range(BOARDHEIGHT):
                        if( (board[x+1][y].tileValue == 0 or board[x+1][y].isMoving or (board[x+1][y].tileValue == board[x][y].tileValue and not board[x+1][y].hasMerged and not board[x][y].hasMerged))and board[x][y].tileValue> 0):
                            canMove =True
                            board[x][y].isMoving = True
                            xValues.append(x)
                            yValues.append(y)
                            hasMoved = True
            for x in range(BOARDWIDTH):
                for y in range(BOARDHEIGHT):
                    if(direct == UP and board[x][y].isMoving):
                        if(board[x][y-1].isMoving or board[x][y-1].tileValue == 0):
                            boardCopy[x][y-1].changeValue(board[x][y].tileValue)
                        else:
                            boardCopy[x][y - 1].changeValue(board[x][y].tileValue + board[x][y - 1].tileValue)
                            boardCopy[x][y-1].hasMerged =True
                            points += board[x][y].tileValue
                        if (y < 3 and not board[x][y+1].isMoving) or (y==3):
                            boardCopy[x][y].changeValue(0)
                    elif(direct == DOWN and board[x][y].isMoving):
                        if (board[x][y + 1].isMoving or board[x][y + 1].tileValue == 0):
                            boardCopy[x][y + 1].changeValue(board[x][y].tileValue)
                        else:
                            boardCopy[x][y + 1].changeValue(board[x][y].tileValue + board[x][y + 1].tileValue)
                            boardCopy[x][y+1].hasMerged =True
                            points += board[x][y].tileValue
                        if (y >0 and not board[x][y-1].isMoving) or (y==0):
                            boardCopy[x][y].changeValue(0)
                    elif(direct == LEFT and board[x][y].isMoving):
                        if (board[x-1][y].isMoving or board[x-1][y].tileValue == 0):
                            boardCopy[x-1][y].changeValue(board[x][y].tileValue)
                        else:
                            boardCopy[x-1][y].changeValue(board[x][y].tileValue + board[x-1][y].tileValue)
                            boardCopy[x-1][y].hasMerged =True
                            points += board[x][y].tileValue
                        if (x < 3 and not board[x + 1][y].isMoving) or (x==3):
                            boardCopy[x][y].changeValue(0)


                    elif(direct == RIGHT and board[x][y].isMoving):
                        if (board[x+1][y].isMoving or board[x+1][y].tileValue == 0):
                            boardCopy[x+1][y].changeValue(board[x][y].tileValue)
                        else:
                            boardCopy[x+1][y].changeValue(board[x][y].tileValue + board[x+1][y].tileValue)
                            boardCopy[x+1][y].hasMerged =True
                            points += board[x][y].tileValue
                        if(x>0 and not board[x-1][y].isMoving) or (x==0):
                            boardCopy[x][y].changeValue(0)

            slideAnimation(xValues, yValues, direct)
            for x in range(BOARDWIDTH):
                board.pop(0)
            for x in range(BOARDWIDTH):
                copycolumn = []
                for y in range(BOARDWIDTH):
                    copycolumn.append(
                        numberTile(boardCopy[x][y].xpos, boardCopy[x][y].ypos, boardCopy[x][y].xbox, boardCopy[x][y].ybox))
                    copycolumn[y].changeValue(boardCopy[x][y].tileValue)
                    copycolumn[y].hasMerged = boardCopy[x][y].hasMerged
                board.append(copycolumn)
            for column in board:
                for tile in column:
                    tile.isMoving = False
     for column in board:
         for tile in column:
             tile.hasMerged = False
     if hasMoved:
         addTile()

def checkEndConditions():
    for column in board:
        for tile in column:
            if (tile.tileValue >= 2048):
                return True, True
    ended = False
    for x in range(BOARDWIDTH):
        for y in range(1, BOARDHEIGHT):
            if (board[x][y - 1].tileValue == 0 or board[x][y - 1].tileValue == board[x][y].tileValue) and board[x][y].tileValue > 0:
                ended = True
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT-1):
            if (board[x][y + 1].tileValue == 0 or board[x][y + 1].tileValue == board[x][y].tileValue) and board[x][y].tileValue > 0:
                ended = True
    for x in range(1, BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if (board[x-1][y].tileValue == 0 or board[x-1][y].tileValue == board[x][y].tileValue) and board[x][y].tileValue > 0:
                ended = True
    for x in range(BOARDWIDTH-1):
        for y in range(BOARDHEIGHT):
            if (board[x+1][y].tileValue == 0 or board[x+1][y].tileValue == board[x][y].tileValue) and board[x][y].tileValue > 0:
                ended = True
    return ended, False


def updatePoints():
    POINTS_SURF = BASICFONT.render("Points: " + str(points) , True, BLACK)
    DISPLAYSURF.blit(POINTS_SURF, (300, 30))


def slideAnimation(xArray, yArray, direct):
    for posChange in range(0, TILESIZE, 50):
        drawBoard()
        if( direct == UP):
            for num in range(len(xArray)):
                board[xArray[num]][yArray[num]].drawTile(board[xArray[num]][yArray[num]].xpos, board[xArray[num]][yArray[num]].ypos-posChange)
        elif (direct == DOWN):
            for num in range(len(xArray)):
                board[xArray[num]][yArray[num]].drawTile(board[xArray[num]][yArray[num]].xpos, board[xArray[num]][yArray[num]].ypos + posChange)
        elif (direct == LEFT):
            for num in range(len(xArray)):
                board[xArray[num]][yArray[num]].drawTile(board[xArray[num]][yArray[num]].xpos - posChange, board[xArray[num]][yArray[num]].ypos)
        elif (direct == RIGHT):
            for num in range(len(xArray)):
                board[xArray[num]][yArray[num]].drawTile(board[xArray[num]][yArray[num]].xpos + posChange, board[xArray[num]][yArray[num]].ypos)
        FPSCLOCK.tick(FPS)
        pygame.display.update()

def addTile():
    x=0
    while x<1:
        rand1=random.randrange(0,4)
        rand2 = random.randrange(0,4)
        rand3 = random.randrange(0,10)
        if board[rand1][rand2].tileValue == 0:
            if(rand3 < 8):
                board[rand1][rand2].changeValue(2)
            else:
                board[rand1][rand2].changeValue(4)
            x+=1

def undo():
    if(len(history) > 0):

        for x in range(BOARDWIDTH):
            board.pop(0)
        for x in range(BOARDWIDTH):
            copycolumn = []
            for y in range(BOARDHEIGHT):
                copycolumn.append(
                    numberTile(history[len(history) - 1][x][y].xpos, history[len(history) - 1][x][y].ypos, history[len(history) - 1][x][y].xbox, history[len(history) - 1][x][y].ybox))
                copycolumn[y].changeValue(history[len(history) - 1][x][y].tileValue)
            board.append(copycolumn)
        history.pop(len(history) - 1)




                





class numberTile:

    def __init__(self, x_pos, y_pos, x_box, y_box):
        self.tileSurf = pygame.Surface((TILESIZE-BOARDERSIZE*2.5, TILESIZE-BOARDERSIZE*2.5))
        self.isOpen = True
        self.tileValue = 0
        self.numDigits = 1
        self.xpos = x_pos
        self.ypos = y_pos
        self.xbox = x_box
        self.ybox = y_box
        self.isMoving = False
        self.hasMerged = False

    def changeValue(self, newValue):
        self.tileValue = newValue
        self.numDigits = 1
        while self.tileValue >10:
            self.tileValue= self.tileValue %10
            self.numDigits +=1
        self.tileValue = newValue

    def drawTile(self, x_pos = -1, y_pos = -1):
        if x_pos == -1:
            x_pos = self.xpos
            y_pos = self.ypos
        self.tileSurf.fill(CREAM)
        numText = BASICFONT.render(str(self.tileValue), True, BLACK)
        self.tileSurf.blit(numText, ((TILESIZE-10)/2 - self.numDigits*25 + 27, (TILESIZE-10)/2 -20))
        DISPLAYSURF.blit(self.tileSurf, (x_pos, y_pos))








main()