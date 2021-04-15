#%%
from audiosockets import MailmanSocket

mailman = MailmanSocket("server_info.json")
mailman.start()
