from audiosockets import BaseProcessorSocket
from audiosockets.utils import LogMelSpectrogram

class LogMelSpecProcessor(BaseProcessorSocket):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)

    def process_data(self,data):
        fs = data["fs"]
        audio = data["data"]
        lms = LogMelSpectrogram(fs)(audio)
        print(lms.shape)

processor = LogMelSpecProcessor("VAD", "server_info.json")
processor.start()