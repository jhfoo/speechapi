# core
import threading
import queue
import time

# community
import sounddevice as sd 
import numpy as np
from piper.voice import PiperVoice

DEFAULT_VOICE = 'data/en_GB-jenny_dioco-medium.onnx'

class SpeechService (threading.Thread):
  def __init__(self, VoiceName = DEFAULT_VOICE, DeviceId = 3):
    threading.Thread.__init__(self)

    self.TextQueue = queue.Queue()
    self.StatusLock = threading.Lock()
    self._status = 'STOPPED'
    self.voice = PiperVoice.load(VoiceName)
    print (f'Voice model loaded')

    print (f'Sample rate: {self.voice.config.sample_rate}')
    dtype = 'int16'
    self.stream = sd.OutputStream(
      samplerate=self.voice.config.sample_rate, 
      channels=1, 
      device = DeviceId, 
      dtype=dtype
    )
    self.stream.start()
    self.setStatus('STARTING')

  @property
  def status(self):
    return self._status

  def setStatus(self, NewStatus):
    with self.StatusLock:
      self._status = NewStatus

  def run(self):
    if self._status == 'STARTING':
      self.setStatus('RUNNING')
    else:
      raise Exception(f'Instance not initialized (status: {self._status})')

    self.enqueue('Speech service online. All operations within normal parameters.')
    while self._status == 'RUNNING':
      while not self.TextQueue.empty():
        self.speak(self.TextQueue.get())
      time.sleep(1)

    self.setStatus('STOPPED')

  def enqueue(self, text):
    with self.StatusLock:
      self.TextQueue.put(text)

  def speak(self, text):
    for bytes in self.voice.synthesize_stream_raw(text):
      data = np.frombuffer(bytes, dtype=np.int16)
      self.stream.write(data)
    print (f'speak: {text}')

  def stop(self):
    self.setStatus('STOPPING')
