import pyaudio
import threading
import wave

class AudioManager:
    winItemAudioKey = "winItem"
    winLevelAudioKey = "winLevel"

    audioFiles = {
        "winItem": "audio/220184__gameaudio__win-spacey.wav",
        "winLevel": "audio/258142__tuudurt__level-win.wav"
    }
    audioStatus = {
        "winItem": False,
        "winLevel": False
    }

    def _playAudio(self, audioName):
        self.audioStatus[audioName] = True
        wf = wave.open(self.audioFiles[audioName], 'rb')
        pa = pyaudio.PyAudio()
        stream = pa.open(format = pa.get_format_from_width(wf.getsampwidth()),
                        channels = wf.getnchannels(),
                        rate = wf.getframerate(),
                        output = True)

        chunk = 1024
        data = wf.readframes(chunk)
        while len(data) > 0:
            stream.write(data)
            data = wf.readframes(chunk)

        stream.stop_stream()
        stream.close()
        pa.terminate()
        self.audioStatus[audioName] = False

    def playAudio(self, name):
        playAudioThread = threading.Thread(target=self._playAudio, args=[name])
        playAudioThread.start()