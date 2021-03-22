#%%
import argparse
import os
import h5py
import time 
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("filename", help = "Audio file to process")
args = parser.parse_args()

file_id, ext = os.path.splitext(os.path.basename(args.filename))
grandfather = os.path.dirname(os.path.dirname(args.filename))

featureFileName = os.path.join(grandfather, "features", file_id)

print(file_id)
dt = datetime.strptime(file_id,"%Y%m%d-%H%M%S-%f")
print(dt)
print(dt.timestamp())

#%%
# with h5py.File("tmp.h5","w") as hdf:
#     dset = hdf.create_dataset(
#         name = "my_data", data = a
#     )