# core
from contextlib import asynccontextmanager

# community
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler 
import sounddevice as sd 
import numpy as np
from piper.voice import PiperVoice

# custom
from SpeechSvc import SpeechService
import TalkingClock



SpeechSvc = SpeechService()

@asynccontextmanager
async def lifespan(app: FastAPI):
  global SpeechSvc

  SpeechSvc.start()
  scheduler = BackgroundScheduler()
  TalkingClock.addJob(scheduler)
  # scheduler.add_job(my_job, 'interval', seconds=60)
  scheduler.start()
  SpeechSvc.enqueue('Scheduler started')

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