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

BotToken = '' # Discord bot token
OctoPrintUrl = '' # Octoprints url
OctoPrintApiKey = ''  # Octoprints api
jpgPath = '' # full path to temporary screenshot i.e /tmp/screen.jpg

Client = discord.Client() #Initialise Client 
client = commands.Bot(command_prefix = '?') #Initialise client bot

def OctoRequest(RequestType):
    if RequestType == 'jobs':
        uri = '/api/job?apikey=%s' % (OctoPrintApiKey)
    if RequestType == 'printers':
        uri = '/api/printer?apikey=%s' % (Oct0PrintApiKey)
    url = OctoPrintUrl + uri
    rawdata = urlopen(url)
    parsed = json.loads(jobs.read().decode('utf-8'))
    rawdata.closed()
    
    if RequestType == 'screenshot':
        uri = '/webcam/?action=snapshot'
        url = OctoPrintUrl + uri
        urllib.request.urlretrieve(url,jpgPath)
        return
    return parsed

def jobDef():
    jobapi_dict = OctoRequest('jobs')
    filename = jobapi_dict['job']['file']['name']
    printTime = jobapi_dict['progress']['printTime']
    completion = jobapi_dict['progress']['completion']
    estimatedPrintTime = jobapi_dict['job']['estimatedPrintTime']
    estimatedPrintTime = convertSec(estimatedPrintTime)
    mytest = ('We are currently printing %s, and are %smins (%s) into a estimated %s print.' % (filename,printTime,completion,convertSec(estimatedPrintTime)))
    return (mytest)

def printerDef():
    printer_dict OctoRequest('printers')
    bedtempactual = printer_dict['temperature']['bed']['actual']
    bedtemptarget = printer_dict['temperature']['bed']['target']
    tooltempactual = printer_dict['temperature']['tool0']['actual']
    tooltemptarget = printer_dict['temperature']['tool0']['target']
    mytest = ('Bed Temp %sC, Target Temp %sC, Nozzel Temp: %sC, Target Bed Temp: %sC' % (bedtempactual,bedtemptarget,tooltempactual,tooltemptarget))
    return (mytest)

def convertSec(seconds):
  if seconds >= 86400:
    mins, sec = divmod(seconds,60)
    hour, mins = divmod(mins, 60)
    day,hour = divmod(hour, 24)
    day,hour = int(day), int(hour)
    mins,sec = int(mins), round(sec, 1)
    return ('%s day %s hour %s minutes %s seconds' % (day,hour,mins,sec))
    
  if seconds >= 3600:
    mins, sec = divmod(seconds,60)
    hour, mins = divmod(mins, 60)
    hour, mins = int(hour), int(mins)
    sec = round(sec, 1)
    return ('%s hour %s minutes %s seconds' % (hour,mins,sec))
    
  if seconds >= 60:
    mins, sec = divmod(seconds,60)
    mins, sec = int(mins), round(sec, 1)
    return ('%s minutes %s seconds' % (mins,sec))
    
  if seconds < 60:
    seconds = round(seconds, 1)
    return ('%s seconds' % (seconds))


@client.event 
async def on_ready():
    print('Bot is online and connected to Discord')

@client.event
async def on_message(message):
    if message.content.upper().startswith('!SCREENSHOT'):
        OctoRequest('screenshot')
        await client.send_file(message.channel, jpgPath)
    if message.content.upper().startswith('!JOB'):
        MyMsg = jobDef()
        await client.send_message(message.channel, MyMsg)
    if message.content.upper().startswith('!TEMPS'):
        MyMsg = printerDef()
        await client.send_message(message.channel, MyMsg)

client.run(BotToken)
