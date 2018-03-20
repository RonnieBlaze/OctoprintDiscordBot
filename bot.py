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

BotToken = ''           # Discord bot token
OctoPrintUrl = ''       # Octoprints url
OctoPrintApiKey = ''    # Octoprints api
jpgPath = ''            # full path to temporary screenshot i.e /tmp/screen.jpg

Client = discord.Client()  # Initialise Client
client = commands.Bot(command_prefix='?')  # Initialise client bot


def octoreq(rtype):
    if rtype == 'screenshot':
        uri = '/webcam/?action=snapshot'
        req = OctoPrintUrl + uri
        urllib.request.urlretrieve(req, jpgPath)
        return

    if rtype == 'jobs':
        uri = '/api/job?apikey=%s' % OctoPrintApiKey

    if rtype == 'printers':
        uri = '/api/printer?apikey=%s' % OctoPrintApiKey

    req = OctoPrintUrl + uri
    rawdata = urlopen(req)
    parsed = json.loads(rawdata.read().decode('utf-8'))
    rawdata.closed()

    return parsed


def jobdef():
    jobapi_dict = octoreq('jobs')
    fname = jobapi_dict['job']['file']['name']
    ptime = jobapi_dict['progress']['printTime']
    completion = jobapi_dict['progress']['completion']
    eptime = convertsec(jobapi_dict['job']['estimatedPrintTime'])
    mytest = ('We are currently printing %s, and are %s mins (%s) into a estimated %s print.' % (fname, ptime,
                                                                                                 completion, eptime))
    return mytest


def printerdef():
    printer_dict = octoreq('printers')
    bedtempactual = printer_dict['temperature']['bed']['actual']
    bedtemptarget = printer_dict['temperature']['bed']['target']
    tooltempactual = printer_dict['temperature']['tool0']['actual']
    tooltemptarget = printer_dict['temperature']['tool0']['target']
    mytest = ('Bed Temp %sC, Target Temp %sC, Nozzel Temp: %sC, Target Bed Temp: %sC' % (bedtempactual, bedtemptarget,
                                                                                         tooltempactual, tooltemptarget)
              )
    return mytest


def convertsec(seconds):
    if seconds >= 86400:
        mins, sec = divmod(seconds, 60)
        hour, mins = divmod(mins, 60)
        day, hour = divmod(hour, 24)
        day, hour = int(day), int(hour)
        mins, sec = int(mins), round(sec, 1)
        return '%s day %s hour %s minutes %s seconds' % (day, hour, mins, sec)

    if seconds >= 3600:
        mins, sec = divmod(seconds, 60)
        hour, mins = divmod(mins, 60)
        hour, mins = int(hour), int(mins)
        sec = round(sec, 1)
        return '%s hour %s minutes %s seconds' % (hour, mins, sec)

    if seconds >= 60:
        mins, sec = divmod(seconds, 60)
        mins, sec = int(mins), round(sec, 1)
        return '%s minutes %s seconds' % (mins, sec)

    if seconds < 60:
        seconds = round(seconds, 1)
        return '%s seconds' % (seconds)


@client.event
async def on_ready():
    print('Bot is online and connected to Discord')


@client.event
async def on_message(message):
    if message.content.upper().startswith('!SCREENSHOT'):
        octoreq('screenshot')
        await client.send_file(message.channel, jpgPath)
    if message.content.upper().startswith('!JOB'):
        MyMsg = jobdef()
        await client.send_message(message.channel, MyMsg)
    if message.content.upper().startswith('!TEMPS'):
        MyMsg = printerdef()
        await client.send_message(message.channel, MyMsg)


client.run(BotToken)