# Audiosockets

## Prerequisites

### Basic Compilers

You might not have `gcc` or `make`, so make sure to install them

```
sudo apt install gcc make
```

### Install PortAudio
In case you do not have it, you will need to install PortAudio. To do that, first run

```
sudo apt install libasound-dev
```

Then download the latest PortAudio at its [Downloads Page](http://files.portaudio.com/download.html), e.g. (2021-04-23)

```
wget http://files.portaudio.com/archives/pa_stable_v190700_20210406.tgz
```

Then unzip it (`tar -xvf <file>`), go into the directory and run

```
./configure
make
sudo make install
```

```
sudo apt install portaudio19-dev
```

```
yay -S portaudio
```

## Installation

Clone the repository, go into the repository and run 

```
pip install -e package
```

## Quickstart

### Configuration File
Here are the instructions for using v3. First create a configuration JSON file which contains the following structure

```json
{
    "PORT": 5050,
    "HEADER": 64,
    "FORMAT": "utf-8",
    "DISCONNECT_MSG": "DISCONNECT",
    "logging_format": "%(asctime)s - %(message)s", 
    "logging_level": "info"
}
```

This configuration file establishes a few parameters:
- `PORT`: The port number where the server will be running, and where the clients will access
- `HEADER`: A large enough byte size for the header to receive a header
- `FORMAT`: A decoding format for the strings 
- `DISCONNECT_MSG`: A disconnecting message that will be agreed upon every node in the network to understand when something will disconnect from the server
- `logging_format`: A format for viewing the `logging` module
- `logging_level`: The level for the `logging` module. That may be `info`, `debug`, `warning`, `error`, `critical` or any of those choices with any letter capitalization

## Usage 

For using a recorder, simply start up a server on a script by running 

```python
from audiosockets import MailmanSocket

server = MailmanSocket()
server.start()
```

Start recording something with 

```python
from audiosockets import RecorderSocket

recorder = RecorderSocket()
recorder.start()
```

Finally, if you wish to process the data, create a new processor by inheriting from `BaseProcessorSocket` and overwrite the method `process_data(data)` in order to process the data in whichever way you wish. 

```python
from audiosockets import BaseProcessorSocket
from audiosockets.utils import LogMelSpectrogram

class MyProcessor(BaseProcessorSocket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def process_data(self, data):
        audio, fs = data["data"], data["fs"]
        lms = LogMelSpectrogram(fs)(audio)
        print(lms)
```

