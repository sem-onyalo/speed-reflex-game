import json
from core import Player, Point, Rectangle

class Challenge:
    _gameSettingsFileName = "game.settings.json"

    # Game mode constants
    gameModeAwaitingCalibration = 'AWCL'
    gameModeAwaitingPlay = 'AWPL'
    gameModeCalibration = 'CLBT'
    gameModeDebug = 'DBUG'
    gameModePlay = 'PLAY'
    gameModeStop = 'STOP'
    gameModeWin = 'GWIN'

    # Colours
    red = (0, 0, 255)
    green = (0, 255, 0)
    blue = (255, 0, 0)
    yellow = (0, 255, 255)

    # Init variables
    player1 = None
    gameMode = None
    defaultFont = None
    audioManager = None
    videoManager = None

    # ##################################################
    #                    CONSTRUCTORS                   
    # ##################################################

    def __init__(self, videoManager, audioManager, playerReps):
        self.videoManager = videoManager
        self.audioManager = audioManager
        self.player1 = Player.Player(playerReps)
        self.gameMode = self.gameModeAwaitingCalibration
        self.defaultFont = self.videoManager.getDefaultFont()

    # ##################################################
    #                      METHODS                     
    # ##################################################

    def shutdownGame(self):
        self.videoManager.shutdown()

    # --------------------------------------------------
    #               GAME SETTINGS METHODS               
    # --------------------------------------------------

    def getGameSettings(self, gameName, defaultValue=None):
        try:
            with open(self._gameSettingsFileName, "r") as file:
                gameSettings = json.loads(file.read())
                if gameName in gameSettings:
                    return gameSettings[gameName]
                else:
                    return defaultValue
        except:
            errorMsg = 'Error: could not retrieve game settings for ' + gameName
            print(errorMsg)
            raise RuntimeError(errorMsg)

    def setGameSettings(self, gameName, value):
        try:
            with open(self._gameSettingsFileName, "r+") as file:
                gameSettings = json.loads(file.read())
                gameSettings[gameName] = value
                file.seek(0)
                file.write(json.dumps(gameSettings))
                file.truncate()
        except:
            errorMsg = 'Error: could not save game settings for ' + gameName
            print(errorMsg)
            raise RuntimeError(errorMsg)

    # --------------------------------------------------
    #                 ADD OBJECT METHODS                
    # --------------------------------------------------

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

    def addTextToRectangle(self, text, rectangle, textScale=1, textColor=(238,238,238), textThickness=2):
        rectWidth = int(rectangle.pt2.x - rectangle.pt1.x)
        rectHeight = int(rectangle.pt2.y - rectangle.pt1.y)
        textSize = self.videoManager.getTextSize(text, self.defaultFont, textScale, textThickness)
        textWidth = textSize[0]
        textHeight = textSize[1]

        textX = int(round((rectWidth - textWidth) / 2)) + rectangle.pt1.x
        textY = int(round((rectHeight - textHeight) / 2)) + rectangle.pt1.y + textHeight

        self.videoManager.addText(text, (textX, textY), self.defaultFont, textScale, textColor, textThickness)
        