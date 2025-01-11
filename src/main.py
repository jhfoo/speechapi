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

# custom
from SpeechSvc import SpeechService

def my_job():
  global SpeechQueue

  print(f"Job started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
  now = datetime.now()
  hour = now.hour
  ampm = 'am'
  if hour >= 12:
    hour -= 12
    ampm = 'pm'
  print (f'Speech service: {SpeechSvc.status}')
  SpeechSvc.enqueue(f'Job started at {hour} {now.minute} {ampm}')
  time.sleep(5)
  print(f"Job completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

SpeechSvc = SpeechService()

@asynccontextmanager
async def lifespan(app: FastAPI):
  global SpeechSvc

  scheduler = BackgroundScheduler()
  scheduler.add_job(my_job, 'interval', seconds=10)
  scheduler.start()
  print (f'Schedulder started')

  SpeechSvc.start()

  yield
  SpeechSvc.stop()
  scheduler.shutdown()
  print (f'STOPPED: scheduler')
  
  SpeechSvc.join()
  print (f'STOPPED: speech service')

  print (f'FastAPI service stopped')

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
  return {"message": "Hello World"}

@app.get("/speak")
async def speak(text: str):
  global SpeechSvc

  SpeechSvc.enqueue(text)
  return {"message": text}

if __name__ == "__main__":
  import uvicorn

  uvicorn.run(app, host="0.0.0.0", port=8000)