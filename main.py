#!/usr/bin/env python

import argparse
import cv2 as cv

from games import CentreChallenge, SpotChallenge
from managers import AudioManager, VideoManager

_gameName = 'Speed Reflex Game'
_netModels = [
    {
        'modelPath': 'models/mobilenet_ssd_v1_balls/transformed_frozen_inference_graph.pb',
        'configPath': 'models/mobilenet_ssd_v1_balls/ssd_mobilenet_v1_balls_2018_05_20.pbtxt',
        'classNames': {
            0: 'background', 1: 'red ball', 2: 'blue ball'
        }
    }
]

def initGame(netModel, classToDetect, scoreThreshold, trackingThreshold, gameId):
    videoManager = VideoManager.VideoManager(_gameName, netModel, scoreThreshold, trackingThreshold)
    
    if gameId == 1:
        return CentreChallenge.CentreChallenge(videoManager, classToDetect)
    elif gameId == 2:
        audioManager = AudioManager.AudioManager()
        return SpotChallenge.SpotChallenge(videoManager, audioManager, classToDetect)
    else:
        print('That is not a valid game')

if __name__ == '__main__':
    netModelIdx = 0
    scoreThreshold = 0.3
    trackingThreshold = 50
    detectClassName = "red ball"

    parser = argparse.ArgumentParser()
    parser.add_argument("objective", type=int, help="The game to play: \
        1 - Centre Challenge \
        2 - Spot Challenge")
    args = parser.parse_args()

    game = initGame(_netModels[netModelIdx], detectClassName, scoreThreshold, trackingThreshold, args.objective)
    
    if game != None:
        cmd = -1
        while True:
            img, run = game.runGameStep(cmd)
            cv.imshow(_gameName, img)
            cmd = cv.waitKey(1)
            if not run or cmd == 27: # ESC
                break

    print('exiting...')
    cv.destroyAllWindows()
    