#%%
import sounddevice as sd
import soundfile as sf
import queue
import subprocess
import datetime
import argparse
import os

# Callback Function for SoundDevice's InputStream
def queue_cb(data, frames, time, status):
    q.put(data.copy())

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-l","--list_devices", action="store_true",help="Show list of all devices")
parser.add_argument('-d', '--device', type=int, 
                    default = 7,
                    help='input device (numeric ID or substring)')
parser.add_argument('-r', '--samplerate', type=int, help='sampling rate')
parser.add_argument('-c', '--channels', type=int, default=1, help='number of input channels')
parser.add_argument('-t', '--subtype', type=str, help='sound file subtype (e.g. "PCM_24")')
parser.add_argument("-D","--dir", type=str, default="data", help="Destination directory")
args = parser.parse_args()

# List the devices
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)

# If sample rate is not specified, use the default sample rate
if args.samplerate is None:
    args.samplerate = int(sd.query_devices(args.device, "input")["default_samplerate"])

# If the data destination does not exist, create the directories
if not os.path.exists(args.dir):
    os.makedirs(args.dir)

# Create the Queue object
q = queue.Queue()

recording_len = 5 # seconds

# Get the file's directory name
dirname = os.path.abspath(os.path.dirname(__file__))

# Initialize an input stream
with sd.InputStream(samplerate=args.samplerate, device = args.device, channels = args.channels, callback=queue_cb):
    print('#' * 80,'\npress Ctrl+C to stop the recording\n','#' * 80)
    # Record forever
    while True:
        try:
            # Obtain the starting time
            start_time = datetime.datetime.now()
            start_str = start_time.strftime("%Y%m%d-%H%M%S-{}".format(start_time.microsecond))
            
            # Obtain the paths for the data destination
            args.filename = os.path.join(args.dir,"{}.wav").format(start_str)
            args.filename = os.path.abspath(args.filename)

            # Open a sound file 
            with sf.SoundFile(args.filename, mode="x", samplerate=args.samplerate, channels=args.channels, subtype=args.subtype) as file:
                while True:
                    # Continuously obtain the data from the microphone
                    file.write(q.get())

                    # Obtain the current time and elapsed time
                    end_time = datetime.datetime.now()
                    dt = end_time - start_time

                    # If the recording length reaches the desired length, open a
                    #   new terminal and call on the processor
                    if (dt.seconds >= recording_len):
                        cmd = ['xterm','-e','python3', \
                                os.path.join(dirname,'audio_process.py'), \
                                args.filename]
                        subprocess.Popen(cmd)
                        # Break out of the loop to start a new recording file
                        break

        except KeyboardInterrupt:
            print("\nRecording interrupted: "+ args.filename)
            os.remove(args.filename)
            parser.exit(0)
        except Exception as e:
            parser.exit(type(e).__name__ + ': ' + str(e))