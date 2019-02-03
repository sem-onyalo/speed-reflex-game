from core import Player, Point, Rectangle

class Challenge:
    # Game mode constants
    gameModeAwaitingCalibration = 'AWCL'
    gameModeAwaitingPlayConfirm = 'AWPL'
    gameModeCalibration = 'CLBT'
    gameModePlay = 'PLAY'

    # Init variables
    player1 = None
    gameMode = None
    defaultFont = None
    audioManager = None
    videoManager = None

    def __init__(self, videoManager, audioManager, playerReps):
        self.videoManager = videoManager
        self.audioManager = audioManager
        self.player1 = Player.Player(playerReps)
        self.gameMode = self.gameModeAwaitingCalibration
        self.defaultFont = self.videoManager.getDefaultFont()

    def shutdownGame(self):
        self.videoManager.shutdown()

    def getTextPosition(self, text, textFont, textScale, textThickness, widthFactor=1, widthPos='centre', heightPos='centre'):
        topPad = 30 #self.videoManager.imgMargin
        textSize = self.videoManager.getTextSize(text, self.defaultFont, textScale, textThickness)
        textWidth = textSize[0]
        textHeight = textSize[1]

        if widthPos == 'right':
            textX = int(round((self.videoManager.frameWidth / widthFactor - textWidth) / 2)) + self.videoManager.frameWidth - int(round(self.videoManager.frameWidth / widthFactor))
        else: # elif widthPos == 'centre'
            textX = int(round((self.videoManager.frameWidth / widthFactor - textWidth) / 2))

        if heightPos == 'top':
            textY = topPad + textHeight
        else: # elif heightPos == 'centre'
            textY = int(round((self.videoManager.frameHeight - textHeight) / 2)) + textHeight

        return textX, textY, textWidth, textHeight

    def addText(self, text, textScale=1, textColor=(238,238,238), textThickness=2, menuColor=(155,109,29), showBackground=True, widthFactor=1, widthPos='centre', heightPos='centre'):
        textX, textY, textWidth, textHeight = self.getTextPosition(text, self.defaultFont, textScale, textThickness, widthFactor=widthFactor, widthPos=widthPos, heightPos=heightPos)
        menuPadX = 15
        menuPadY = 20
        rectPt1X = textX - menuPadX
        rectPt1Y = textY - textHeight - menuPadY
        rectPt2X = textX + textWidth + menuPadX
        rectPt2Y = textY + menuPadY
        if showBackground:
            self.videoManager.addRectangle((rectPt1X, rectPt1Y), (rectPt2X, rectPt2Y), menuColor, -1)
        self.videoManager.addText(text, (textX, textY), self.defaultFont, textScale, textColor, textThickness)