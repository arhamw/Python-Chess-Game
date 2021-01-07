"""
This is the main driver file. It will be responsible for handling user input and displaying the current
GameState object.
"""

import pygame as p
from Chess import ChessEngine

p.init()
WIDTH = HEIGHT = 512 # 400 is also a good option
DIMENSION = 8 # dimension of a chess board is 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 # for animations
IMAGES = {}

'''
Initialize a global dictionary of images. This will be called exactly once in main.
It exists as a standalone function to make adding different chess sets easier
'''
def load_images():
    pieces = ["wP", "wR", "wN", "wB", "wK", "wQ", "bP", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    # Note: we can access an image by saying "IMAGES ["wP"]"

'''
The main driver for our code. This will handle user input and update the graphics.
'''
def main():
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False # flag variable for when a move is made
    animate = False # flag variable for when we should animate a move
    print(gs.board)
    load_images() # only do this once
    running = True
    sqSelected = () # no square is selected, keeps track of the last click of the user (tuple: (row, col))
    playerClicks = [] # keeps track of player clicks (two tuples: [(6,4), (4, 4)])
    gameOver = False
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos() # (x, y) location of mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col): # the user clicked the same square twice
                        sqSelected = () # deselect
                        playerClicks = [] # clear player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected) # append for both 1st and 2nd clicks
                    if len(playerClicks) == 2: # after 2nd click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = () # reset user clicks
                                playerClicks = []
                                break
                        if not moveMade:
                            playerClicks = [sqSelected]
            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                if e.key == p.K_r: # reset the board when 'r' is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black wins by checkmate')
            else:
                drawText(screen, 'White wins by checkmate')
        elif gs.stalemate:
            gameOver = True
            drawText(screen, 'Stalemate')
        clock.tick(MAX_FPS)
        p.display.flip()
'''
Highlight square selected and moves for piece selected
'''
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c, = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): # sqSelected is a piece that can be moved
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(120) # transparency value-> transparent; 255 opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r*SQ_SIZE))
            # highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (SQ_SIZE * move.endCol, SQ_SIZE * move.endRow))
    if len(gs.moveLog) > 0:
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(150)  # transparency value-> transparent; 255 opaque
        s.fill(p.Color('red'))
        screen.blit(s, (gs.moveLog[-1].endCol * SQ_SIZE, gs.moveLog[-1].endRow * SQ_SIZE))

'''
Responsible for all graphics within a current game state.
'''
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen) # draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board) #draw pieces on top of those squares

'''
Draw the squares on the board
'''
def drawBoard(screen):
    global colors
    colors = [p.Color("cornsilk"), p.Color("darkkhaki")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Draw the piecs on the board using the current GameState.board
'''
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": # non empty square
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Animating a move
'''
def animateMove(move, screen, board, clock):
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 5 # frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(int(c * SQ_SIZE), int(r * SQ_SIZE), SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawText(screen, text):
    font = p.font.SysFont("Times", 32, False, False)
    textObject = font.render(text, 0, p.Color('Red'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH//2 - textObject.get_width()//2, HEIGHT//2 - textObject.get_height()//2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(1, 1))

if __name__ == "__main__":
    main()