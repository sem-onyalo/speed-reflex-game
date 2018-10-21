import time

class Player:
    maxRep = 2
    currentRep = 0
    showResult = False
    isObjectInSpot = False
    labelDetections = True
    freezeRoundResult = False
    winItemFreezeStartTime = None
    winRoundFreezeStartTime = None
    
    itemWon = False
    roundWon = False
    isActive = False
    resetItem = False

    # Constants
    winItemFreezeMaxTime = 0.5
    winRoundFreezeMaxTime = 7

    def runStep(self):
        self.itemWon = False
        self.roundWon = False
        self.resetItem = False
        self.labelDetections = True

        isRoundComplete = False
        if self.showResult:
            continueToSleep = True
            currentTime = time.time()
            if self.freezeRoundResult and self.winRoundFreezeStartTime != None and currentTime - self.winRoundFreezeStartTime > self.winRoundFreezeMaxTime:
                self.winRoundFreezeStartTime = None
                self.freezeRoundResult = False
                continueToSleep = False
                isRoundComplete = True
            elif self.winItemFreezeStartTime != None and currentTime - self.winItemFreezeStartTime > self.winItemFreezeMaxTime:
                self.winItemFreezeStartTime = None
                continueToSleep = False

            if continueToSleep:
                self.labelDetections = False
            else:
                self.resetItem = True
                self.showResult = False
                
        elif self.isObjectInSpot:
            self.itemWon = True
            self.showResult = True
            self.isObjectInSpot = False
            self.labelDetections = False
            self.currentRep = self.currentRep + 1
            if self.currentRep == self.maxRep:
                self.roundWon = True
                self.freezeRoundResult = True
                self.winRoundFreezeStartTime = time.time()
            else:
                self.winItemFreezeStartTime = time.time()
                
        return isRoundComplete

    def reset(self, isActive=False):
        self.itemWon = False
        self.roundWon = False
        self.resetItem = False
        self.isActive = isActive
        self.currentRep = 0
        self.showResult = False
        self.isObjectInSpot = False
        self.labelDetections = True
        self.freezeRoundResult = False
        self.winItemFreezeStartTime = None
        self.winRoundFreezeStartTime = None