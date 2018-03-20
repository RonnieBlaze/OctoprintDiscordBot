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
    completion = jobapi_dict['progress']['completion']
    estimatedPrintTime = jobapi_dict['job']['estimatedPrintTime']
    state = jobapi_dict['state']
    convertSec(estimatedPrintTime)
    if state == "Printing":
        mytest = ("We are currently printing %s, and are %s (%.2f%%) into a estimated %s print." % (filename,convertSec(printTime),completion,convertSec(estimatedPrintTime)))
        return (mytest)
    if state == "Operational":
        mytest = ("We are currently Not Printing")
        return (mytest)

def printerDef():
    u = urlopen(OctoRequest('printers'))
    printer_dict = json.loads(u.read().decode('utf-8'))
    bedtempactual = printer_dict['temperature']['bed']['actual']
    bedtemptarget = printer_dict['temperature']['bed']['target']
    tooltempactual = printer_dict['temperature']['tool0']['actual']
    tooltemptarget = printer_dict['temperature']['tool0']['target']
    mytest = ("Bed Temp %sC, Target Temp %sC, Nozzel Temp: %sC, Target Temp: %sC" % (bedtempactual,bedtemptarget,tooltempactual,tooltemptarget))
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
