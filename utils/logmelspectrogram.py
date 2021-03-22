import librosa
import numpy as np


class LogMelSpectrogram:
    def __init__(self, fs, n_mels=128, win_dur=0.025, hop_dur=0.0100, eps = 1e-8):
        """Initialize a tool to compute the log Mel spectrogram

        Args:
            fs (float): Sampling Rate for Spectrogram
            n_mels (int, optional): Number of Mel bins to use. Defaults to 128.
            win_dur (float, optional): Duration of a window in units of seconds.
                Defaults to 0.025.
            hop_dur (float, optional): Duration of a stride/hop in units of 
                seconds. Defaults to 0.01.
            eps (float, optional): Infinitesimally small number for log 
                computation. Defaults to 1e-8.
            use_librosa (bool, optional): Whether or not to use the Librosa's
                Mel spectrogram or Torch Audio's Mel spectrogram. Defaults 
                to True.
        """
        self.sample_rate = fs
        self.n_mels = n_mels
        self.win_dur = win_dur
        self.hop_dur = hop_dur

        # Because of this rounding, if self.sample_rate % 1000 != 0 
        #   (e.g. 22050 Hz), the spectrogram will not obtain a time array that
        #   exactly matches with the hop duration specified above. 
        self.win_length = round(self.sample_rate * self.win_dur)
        self.hop_length = round(self.sample_rate * self.hop_dur)
        self.eps = eps

    
    def method(self,x):
        """Compute the log Mel spectrogram of the given data .

        Args:
            x (array): Array in which to take the Mel Spectrogram

        Returns:
            (array): Mel spectrogram of given signal
        """
        return librosa.feature.melspectrogram(
            y = x,
            sr = self.sample_rate,
            n_fft = self.win_length,
            hop_length = self.hop_length,
            n_mels = self.n_mels,
            fmin = 50.,
            fmax = self.sample_rate // 2
        )
    
    def rescale(self, x):
        """Rescale values to range between -1 and 1

        Args:
            x (array): Array to be rescaled

        Returns:
            (array): Rescaled array
        """
        x = 2 * (x - np.min(x)) / (np.max(x) - np.min(x)) - 1
        return x

    def __call__(self, x,return_time = False):
        # Remove any extra dimensions
        x = np.squeeze(x)

        # Scale the data to range between -1 and 1
        x = self.rescale(x)

        # Pass it through the selected method
        x = self.method(x)

        # Take the Log
        x = np.log(x + self.eps)
        
        if return_time:
            _,n_frames = x.shape
            t_array = librosa.frames_to_time(
                np.arange(n_frames),
                sr= self.sample_rate,
                hop_length = self.hop_length
            )
            return x, t_array
        else:
            return x