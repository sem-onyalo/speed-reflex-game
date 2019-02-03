#!/usr/bin/env python

import argparse
from games import CentreChallenge, SpotChallenge, BoxingChallenge
from managers import AudioManager, VideoManager

_gameName = 'Speed Reflex Game'
_netModels = [
    {
        'modelPath': 'models/mobilenet_ssd_v1_balls/transformed_frozen_inference_graph.pb',
        'configPath': 'models/mobilenet_ssd_v1_balls/ssd_mobilenet_v1_balls_2018_05_20.pbtxt',
        'classNames': {
            0: 'background', 1: 'red ball', 2: 'blue ball'
        }
    },
    {
        'modelPath': 'models/mobilenet_ssd_v1_boxing/transformed_frozen_inference_graph.pb',
        'configPath': 'models/mobilenet_ssd_v1_boxing/ssd_mobilenet_v1_boxing_2019_02_03.pbtxt',
        'classNames': {
            0: 'background', 1: 'boxing gloves'
        }
    }
]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("gameId", type=int, help="The game to play: \
        1 - Centre Challenge \
        2 - Spot Challenge \
        3 - Boxing Challenge")
    parser.add_argument("--res", type=str, default="640,480", help="The resolution of the video. Default is \"640,480\"")
    parser.add_argument("--video_source", type=int, default=0, help="The index of the video source. Default is 0.")
    parser.add_argument("--reps", type=int, default=5, help="The number of player reps per spot challenge game. Default is 5.")
    parser.add_argument("--model_index", type=int, default=0, help="The index of the model to use")
    parser.add_argument("--score_threshold", type=float, default=0.3, help="Only detections with a probability of correctness above the specified threshold")
    parser.add_argument("--tracking_threshold", type=float, default=50, help="Tolerance (delta) between the object being detected and the position it is supposed to be in")
    args = parser.parse_args()
    
    res = list(map(int, args.res.split(',')))

    videoManager = VideoManager.VideoManager(args.video_source, _gameName, res[0], res[1], _netModels[args.model_index], args.score_threshold, args.tracking_threshold)
    audioManager = AudioManager.AudioManager()

    if args.gameId == 1:
        game = CentreChallenge.CentreChallenge(videoManager)
    elif args.gameId == 2:
        game = SpotChallenge.SpotChallenge(videoManager, audioManager, args.reps)
    elif args.gameId == 3:
        game = BoxingChallenge.BoxingChallenge(videoManager, audioManager, playerReps=args.reps)
    else:
        raise RuntimeError('Invalid game choice:', args.gameId)
    
    if game != None:
        while True:
            run = game.runGameStep()
            if not run:
                break

        print('exiting...')
        game.shutdownGame()
    