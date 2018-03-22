import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import time

import urllib.request
from urllib.request import urlopen
import json
import configparser

Client = discord.Client()  # Initialise Client
client = commands.Bot(command_prefix='?')  # Initialise client bot


def load_cfg():
    global BotToken
    global OctoPrintUrl
    global OctoPrintApiKey
    global jpgPath

    cfg = configparser.ConfigParser()
    cfg.read('config.cfg')

    OctoPrintUrl = cfg.get('setting', 'url')
    OctoPrintApiKey = cfg.get('setting', 'apikey')
    BotToken = cfg.get('setting', 'bot_token')
    jpgPath = cfg.get('setting', 'jpg_path')


def octoreq(rtype):
    if rtype == 'screenshot':
        uri = '/webcam/?action=snapshot'
        req = OctoPrintUrl + uri
        urllib.request.urlretrieve(req, jpgPath)
        return
    else:
        req = OctoPrintUrl + '/api/' + rtype + '?apikey=' + OctoPrintApiKey
        raw = urlopen(req)

    return json.loads(raw.read().decode('utf-8'))


def jobdef():
    jobapi_dict = octoreq('job')
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

        mins, sec = int(mins), int(sec)
        if day == 1:
            dlabel = ' day '
        else:
            dlabel = ' days '
        if hour == 1:
            hlabel = ' hour '
        else:
            hlabel = ' hours '
        if mins == 1:
            mlable = ' minute '
        else:
            mlable = ' minutes '
        if sec == 1:
            slabel = ' second'
        else:
            slabel = ' seconds'
        return str(day) + dlabel + str(hour) + hlabel + str(mins) + mlable + str(sec) + slabel

    if seconds >= 3600:
        mins, sec = divmod(seconds, 60)
        hour, mins = divmod(mins, 60)
        hour, mins = int(hour), int(mins)

        sec = int(sec)
        if hour == 1:
            hlabel = ' hour '
        else:
            hlabel = ' hours '
        if mins == 1:
            mlable = ' minute '
        else:
            mlable = ' minutes '
        if sec == 1:
            slabel = ' second'
        else:
            slabel = ' seconds'
        return str(hour) + hlabel + str(mins) + mlable + str(sec) + slabel

    if seconds >= 60:
        mins, sec = divmod(seconds, 60)
        mins, sec = int(mins), int(sec)
        if mins == 1:
            mlable = ' minute '
        else:
            mlable = ' minutes '
        if sec == 1:
            slabel = ' second'
        else:
            slabel = ' seconds'
        return str(mins) + mlable + str(sec) + slabel

    if seconds < 60:
        seconds = int(seconds)
        if seconds == 1:
            return '%s second' % seconds
        return '%s seconds' % seconds

load_cfg()
print(jobdef())

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
