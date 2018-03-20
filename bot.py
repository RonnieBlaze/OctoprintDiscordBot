import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import time
import urllib.request
from urllib.request import urlopen
import json

# Variables
#

BotToken = ""    # Discord bot token
OctoPrintUrl = ""                                      # Octoprints url
OctoPrintApiKey = ""                        # Octoprints api
jpgPath = ""                                                        # full path to temporary screenshot i.e /tmp/screen.jpg
Client = discord.Client() #Initialise Client 
client = commands.Bot(command_prefix = "?") #Initialise client bot

def pbar (precent):
    
  if precent <= 0:
    precent = 0
  elif precent > 100:
    precent = 1
  else:
    precent = precent / 100

  progress = 45 * precent 
  bar = ''
    
  for i in range(0,int(progress)):
    bar += '='
  
  bar = '[' + bar.ljust(45) + ']'
  return bar 

def OctoRequest(RequestType):
    if RequestType == "screenshot":
        uri = "/webcam/?action=snapshot"
    if RequestType == "jobs":
        uri = "/api/job?apikey=%s" % (OctoPrintApiKey)
    if RequestType == "printers":
        uri = "/api/printer?apikey=%s" % (OctoPrintApiKey)
    url = OctoPrintUrl + uri
    return url

def jobDef():
    u = urlopen(OctoRequest('jobs'))
    jobapi_dict = json.loads(u.read().decode('utf-8'))
    filename = jobapi_dict['job']['file']['name']
    printTime = jobapi_dict['progress']['printTime']
    printTimeLeft = jobapi_dict['progress']['printTimeLeft']
    completion = jobapi_dict['progress']['completion']
    estimatedPrintTime = jobapi_dict['job']['estimatedPrintTime']
    state = jobapi_dict['state']
    convertSec(estimatedPrintTime)
    if state == "Printing":
        mytest = ("```css\nWe are currently printing %s\nElapsed Printing Time: %s (%.0f%%).\nEstimated Print Time:  %s.\nEstimated Time Left:   %s```" % (filename,convertSec(printTime),completion,convertSec(estimatedPrintTime),convertSec(printTimeLeft)))
        return (mytest)
    if state == "Operational":
        mytest = ("```css\nWe are currently Not Printing111")
        return (mytest)

def printerDef():
    u = urlopen(OctoRequest('printers'))
    printer_dict = json.loads(u.read().decode('utf-8'))
    bedtempactual = printer_dict['temperature']['bed']['actual']
    bedtemptarget = printer_dict['temperature']['bed']['target']
    tooltempactual = printer_dict['temperature']['tool0']['actual']
    tooltemptarget = printer_dict['temperature']['tool0']['target']
    mytest = ("```css\nBed Temp       (%sC\%sC)\nNozzel Temp: (%sC\%sC)```" % (bedtempactual,bedtemptarget,tooltempactual,tooltemptarget))
    return (mytest)

def convertSec(seconds):
    if seconds >= 86400:
        min, sec = divmod(seconds,60)
        hour, min = divmod(min, 60)
        day,hour = divmod(hour, 24)
        day = int(day)
        hour = int(hour)
        min = int(min)
        sec = round(sec, 1)
        return ("%s day %s hour %s minutes %s seconds" % (day,hour,min,sec))
    if seconds >= 3600:
        min, sec = divmod(seconds,60)
        hour, min = divmod(min, 60)
        min = int(min)
        hour = int(hour)
        sec = round(sec, 1)
        return  ("%s hour %s minutes %s seconds" % (hour,min,sec))
    if seconds >= 60:
        min, sec = divmod(seconds,60)
        min = int(min)
        sec = round(sec, 1)
        return  ("%s minutes %s seconds" % (min,sec))
    if seconds < 60:
        seconds = round(seconds, 1)
        return  ("%s seconds" % (seconds))

@client.event 
async def on_ready():
    print("Bot is online and connected to Discord")

@client.event
async def on_message(message):
    if message.content.upper().startswith('!SCREENSHOT'):
        urllib.request.urlretrieve(OctoRequest('screenshot'), jpgPath)
        await client.send_file(message.channel, jpgPath)
    if message.content.upper().startswith('!JOB'):
        MyMsg = jobDef()
        await client.send_message(message.channel, MyMsg)
    if message.content.upper().startswith('!TEMPS'):
        MyMsg = printerDef()
        await client.send_message(message.channel, MyMsg)

client.run(BotToken)
