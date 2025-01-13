# core
import time
from datetime import datetime, timedelta

# custom
import SpeechSvc

_scheduler = None

def getNextJobStartTime():
  now = datetime.now() + timedelta(hours=1)
  next = datetime(now.year, now.month, now.day, now.hour, 0, 0)
  return next

def formatTimeToSpeechText(dt):
  hour = dt.hour
  ampm = 'am'
  if hour >= 12:
    hour -= 12
    ampm = 'pm'
  elif hour == 0:
    hour = 12

  MinText = dt.minute
  if MinText == 0:
    MinText = ''

  return f'{hour} {MinText} {ampm}'

def my_job():
  now = datetime.now()
  hour = now.hour
  ampm = 'am'
  if hour >= 12:
    hour -= 12
    ampm = 'pm'
  # print (f'Speech service: {SpeechSvc.status}')
  SpeechSvc.ServiceThread.enqueue(f'The time now is {formatTimeToSpeechText(now)}')
  _addJob()

def _addJob():
  global _scheduler

  DateTimeNextJob = getNextJobStartTime()
  # SpeechSvc.ServiceThread.enqueue(f'Next job is at {formatTimeToSpeechText(DateTimeNextJob)}')
  _scheduler.add_job(my_job, 'date', run_date = DateTimeNextJob)

def addJob(scheduler):
  global _scheduler

  _scheduler = scheduler
  _addJob()
  SpeechSvc.ServiceThread.enqueue('Talking Clock started')
  
  # print (f'Speech service: {SpeechSvc.status}')

  