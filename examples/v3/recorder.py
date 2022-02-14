#%%
from audiosockets import RecorderSocket

recorder = RecorderSocket("server_info.json")
recorder.start()