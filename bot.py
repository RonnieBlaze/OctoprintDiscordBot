import discord
import asyncio
import time
import urllib.request
import json
import platform
from discord.ext.commands import Bot
from discord.ext import commands
from urllib.request import urlopen

# Variables
#

BotToken = ""    # Discord bot token
OctoPrintUrl = ""                                      # Octoprints url
OctoPrintApiKey = ""                        # Octoprints api
jpgPath = ""                                                        # full path to temporary screenshot i.e /tmp/screen.jpg
channel = discord.Object(id='')                           # Channel Id you want the bot to reply in

Client = discord.Client() #Initialise Client 
client = commands.Bot(command_prefix = "!") #Initialise client bot

#async def my_background_task():
#    await client.wait_until_ready()
#    counter = 0
#    while not client.is_closed:
#        counter += 1
#        await client.send_message(channel, counter)
#        await asyncio.sleep(60) # task runs every 60 seconds

@client.event 
async def on_ready():
    print('Logged in as '+client.user.name+' (ID:'+client.user.id+') | Connected to '+str(len(client.servers))+' servers | Connected to '+str(len(set(client.get_all_members())))+' users')
    print('--------')
    print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__, platform.python_version()))
    print('--------')
    print('Use this link to invite {}:'.format(client.user.name))
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(client.user.id))
    print('--------')
    print('Support Discord Server: ')
    print('Github Link: https://github.com/RonnieBlaze/OctoprintDiscordBot')
    print('--------')
    print('You are running ') #Do not change this. This will really help us support you, if you need support.
    print('Created by ')
    return await client.change_presence(game=discord.Game(name='Idle')) #This is buggy, let us know if it doesn't work.

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
        bar += "="
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
    filename = jobapi_dict['job']['file']['name'][:-6]
    printTime = jobapi_dict['progress']['printTime']
    printTimeLeft = jobapi_dict['progress']['printTimeLeft']
    completion = round(jobapi_dict['progress']['completion'])
    estimatedPrintTime = jobapi_dict['job']['estimatedPrintTime']
    state = jobapi_dict['state']
    convertsec(estimatedPrintTime)
    if state == "Printing":
        mytest = ("```css\nWe are currently printing %s\nElapsed Printing Time: %s\n%s[%.0f%%]\nEstimated Print Time:  %s\nEstimated Time Left:   %s```" % (filename,convertsec(printTime),pbar(completion),completion,convertsec(estimatedPrintTime),convertsec(printTimeLeft)))
        return (mytest)
    if state == "Operational":
        mytest = ("```css\nWe are currently Not Printing```")
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

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    if message.content.startswith('!screenshot'):
        urllib.request.urlretrieve(OctoRequest('screenshot'), jpgPath)
        await client.send_file(channel, jpgPath)
    if message.content.startswith('!job'):
        MyMsg = jobDef()
        await client.send_message(channel, MyMsg)
    if message.content.startswith('!temps'):
        MyMsg = printerDef()
        await client.send_message(channel, MyMsg)

#client.loop.create_task(my_background_task())
client.run(BotToken)
