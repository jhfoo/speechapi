# core
from contextlib import asynccontextmanager
import time
import threading

# community
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler 

def my_job():
  print(f"Job started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
  time.sleep(5)
  print(f"Job completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")


isThreadRunning = True

def speak():
  print (f'Speech thread started')
  while isThreadRunning:
    time.sleep(1)

  print (f'Speech thread stopped')

@asynccontextmanager
async def lifespan(app: FastAPI):
  scheduler = BackgroundScheduler()
  scheduler.add_job(my_job, 'interval', seconds=10)
  scheduler.start()
  print (f'Schedulder started')

  SpeechThread = threading.Thread(target=speak)
  SpeechThread.start()

  yield
  isThreadRunning = False
  scheduler.shutdown()
  print (f'FastAPI service stopped')

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


