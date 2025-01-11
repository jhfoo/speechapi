# core
from contextlib import asynccontextmanager
import time
import threading
import queue
from datetime import datetime

# community
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler 
import sounddevice as sd 
import numpy as np
from piper.voice import PiperVoice

def my_job():
  global SpeechQueue

  print(f"Job started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
  now = datetime.now()
  hour = now.hour
  ampm = 'am'
  print (f'hour: {hour}')
  if hour >= 12:
    hour -= 12
    ampm = 'pm'
  SpeechQueue.put(f'Job started at {hour} {now.minute} {ampm}')
  time.sleep(5)
  print(f"Job completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

def speakText(voice, stream, text):
  print (f'SPEAK: {text}')
  for bytes in voice.synthesize_stream_raw(text):
    data = np.frombuffer(bytes, dtype=np.int16)
    stream.write(data)

isThreadRunning = True
SpeechQueue = queue.Queue()

def speak():
  global SpeechQueue

  print (f'Speech thread started')
  voice = PiperVoice.load('data/en_GB-jenny_dioco-medium.onnx')
  print (f'Voice model loaded')

  print (f'Sample rate: {voice.config.sample_rate}')
  dtype = 'int16'
  DeviceId = 3
  stream = sd.OutputStream(
    samplerate=voice.config.sample_rate, 
    channels=1, 
    device = DeviceId, 
    dtype=dtype
  )
  stream.start()

  speakText(voice, stream, 'Systems online. All operations normal.')

  while isThreadRunning:
    while not SpeechQueue.empty():
      speakText(voice, stream, SpeechQueue.get())
    time.sleep(1)

  stream.stop()
  stream.close()
  print (f'Speech thread stopped')

@asynccontextmanager
async def lifespan(app: FastAPI):
  global isThreadRunning

  scheduler = BackgroundScheduler()
  scheduler.add_job(my_job, 'interval', seconds=10)
  scheduler.start()
  print (f'Schedulder started')

  SpeechThread = threading.Thread(target=speak)
  SpeechThread.start()

  yield
  isThreadRunning = False
  scheduler.shutdown()
  SpeechThread.join()
  print (f'FastAPI service stopped')

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
  global isThreadRunning

  isThreadRunning = False
  return {"message": "Hello World"}


