from audiosockets import BaseProcessorSocket

processor = BaseProcessorSocket("VAD", "server_info.json")
processor.start()