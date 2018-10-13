#!/usr/bin/env python

import argparse
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

if __name__ == '__main__':
    netModelIdx = 0
    scoreThreshold = 0.3
    trackingThreshold = 50
    detectClassName = "red ball"

    parser = argparse.ArgumentParser()
    parser.add_argument("gameId", type=int, help="The game to play: \
        1 - Centre Challenge \
        2 - Spot Challenge")
    args = parser.parse_args()

    videoManager = VideoManager.VideoManager(_gameName, _netModels[netModelIdx], scoreThreshold, trackingThreshold)
    
    if args.gameId == 1:
        game = CentreChallenge.CentreChallenge(videoManager, detectClassName)
    elif args.gameId == 2:
        audioManager = AudioManager.AudioManager()
        game = SpotChallenge.SpotChallenge(videoManager, audioManager, detectClassName)
    else:
        raise RuntimeError('Invalid game choice:', args.gameId)
    
    if game != None:
        while True:
            run = game.runGameStep()
            if not run:
                break

        print('exiting...')
        game.shutdownGame()
    