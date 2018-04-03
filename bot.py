import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import time

import urllib.request
from urllib.request import urlopen
import json
import configparser
import platform

Client = discord.Client()  # Initialise Client
client = commands.Bot(command_prefix='?')  # Initialise client bot


def load_cfg():
    global BotToken
    global OctoPrintUrl
    global OctoPrintApiKey
    global jpgPath
    global channel
    
    cfg = configparser.ConfigParser()
    cfg.read('config.cfg')

    OctoPrintUrl = cfg.get('setting', 'url')
    OctoPrintApiKey = cfg.get('setting', 'apikey')
    BotToken = cfg.get('setting', 'bot_token')
    jpgPath = cfg.get('setting', 'jpg_path')
    channel = cfg.get('setting', 'channel')


def progress_bar (percent):
    if percent <= 0:
        percent = 0
    elif percent > 100:
        percent = 1
    else:
        percent = percent / 100
    progress = 45 * percent
    bar = ''
    for i in range(0, int(progress)):
        bar += "="
    bar = '[' + bar.ljust(45) + ']  ' + '%.0f%%' % (percent * 100)
    return bar


def api_call(request_type):

    if request_type == 'screenshot':
        uri = '/webcam/?action=snapshot'
        req = OctoPrintUrl + uri

        try:
            urllib.request.urlretrieve(req, jpgPath)
        except urllib.request.HTTPError as e:
            print('Http Error')
            print('Error code: ', e.code)
        except urllib.request.URLError as e:
            print('URL Error')
            print('Reason: ', e.reason)

        return

    else:
        req = OctoPrintUrl + '/api/' + request_type + '?apikey=' + OctoPrintApiKey
        try:
            raw = urlopen(req)
        except urllib.request.HTTPError as e:
            print('Http Error')
            print('Error code: ', e.code)
            return -1
        except urllib.request.URLError as e:
            print('URL Error')
            print('Reason: ', e.reason)
            return -1
    return json.loads(raw.read().decode('utf-8'))


def get_jobs():
    response = api_call('jobs')

    if response == -1:
        status = 'Error retrieving data'
        return status

    if response['state'] != 'Printing':
        status = ('```css\n'
                  'We are currently not printing')
        return status

    status = ['```css',
              'We are currently printing ' + response['job']['file']['name'][:-6],
              'Elapsed Printing Time: ' + convert_sec(response['progress']['printTime']),
              progress_bar(response['progress']['completion']),
              'Estimated Time Left: ' + convert_sec(response['job']['estimatedPrintTime']),
              '```']

    return '\n'.join(status)


def get_printers():
    response = api_call('printers')

    if response == -1:
        status = 'Error retrieving data'
        return status

    status = ['```css',
              '   Bed Temp: ' + str(response['temperature']['bed']['actual']) + '°C',
              'Target Temp: ' + str(response['temperature']['bed']['target']) + '°C',
              '¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯',
              '',
              'Nozzle Temp: ' + str(response['temperature']['tool0']['actual']) + '°C',
              'Target Temp: ' + str(response['temperature']['tool0']['target']) + '°C',
              '¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯',
              '```']

    return '\n'.join(status)


def convert_sec(seconds):
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
    await client.change_presence(game=discord.Game(name='Started')) #This is buggy, let us know if it doesn't work.


@client.event
async def on_message(message):
    if message.content.upper().startswith('!SCREENSHOT'):
        api_call('screenshot')
        await client.send_file(message.channel, jpgPath)
    if message.content.upper().startswith('!JOB'):
        MyMsg = get_jobs()
        await client.send_message(message.channel, MyMsg)
    if message.content.upper().startswith('!TEMPS'):
        MyMsg = get_printers()
        await client.send_message(message.channel, MyMsg)


load_cfg()

client.run(BotToken)
