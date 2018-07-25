import random
import asyncio
import aiohttp
import json
from discord import Game
from discord.ext.commands import Bot

with open("config.json") as f:
    data = json.load(f)

url = 'https://www.youtube.com/watch?v=7KJjVMqNIgA'
BOT_PREFIX = ("?", "!")
TOKEN = data['client']['botToken'] 

client = Bot(command_prefix=BOT_PREFIX)
players = {}


playlist = {}


def check_queue(id):
    if playlist[id] != []:
      player = playlist[id].pop(0)
      players[id] = player
      player.start()

@client.event
async def on_ready():
    await client.change_presence(game=Game(name="with humans"))
    print("Logged in as " + client.user.name)


async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.servers:
            print(server.name)
        await asyncio.sleep(600)


@client.command(pass_context=True)
async def play(ctx):
  
  server  = ctx.message.server
  author = ctx.message.author
  voice_channel = author.voice_channel
  try:
    await client.join_voice_channel(voice_channel)
  except Exception as e:
    await client.say("I'm already in a voice channel.")
  player = await voice_channel.create_ytdl_player(url,after=lambda:check_queue(server.id))
  players[server.id] = player
  player.start()


@client.command(pass_context=True)
async def pause(ctx):
    players[ctx.message.server.id].pause()

@client.command(pass_context=True)
async def resume(ctx):
    players[ctx.message.server.id].resume()

@client.command(pass_context=True)
async def stop(ctx):
    players[ctx.message.server.id].stop()
    

@client.command(pass_context=True)
async def join(ctx):
    #"""Joins your voice channel"""
    author = ctx.message.author
    voice_channel = author.voice_channel
    vc = await client.join_voice_channel(voice_channel)

@client.command(pass_context = True)
async def leave(ctx):
    for x in client.voice_clients:
        if(x.server == ctx.message.server):
            return await x.disconnect()
    return await client.say("I am not connected to any voice channel on this server!")


@client.command(pass_context=True)
async def queue(ctx):
  server = ctx.message.server.id
  vc = client.voice_client_in(server)
  player = await vc.create_ytdl_player(url)

  if server.id in playlist:
    playlist[server.id].append(player)
  else:
    playlist[server.id]=[player]

  await client.say("Queued: "+url)
client.loop.create_task(list_servers())
client.run(TOKEN)
