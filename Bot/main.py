import asyncio
import json
import datetime
from discord import app_commands, SelectOption, Interaction
from discord.ui import Button, View, Select
import traceback
import discord
from discord.ext import commands
import sys
import os

from config import load_config  

config = load_config()

bot = commands.AutoShardedBot(command_prefix=config["prefix"], case_insensitive = True,intents=discord.Intents.all())
bot.remove_command("help")

@bot.event
async def on_ready():
    await loadcogs()
    #await bot.change_presence(status=discord.Status.dnd,activity=discord.Activity(type=discord.ActivityType.listening,name=get_verse()))
    print('server.status:running')
    print('╔═══ Logged in as ═══╗')
    print(bot.user.name)
    print(bot.user.id)


async def loadcogs():
    for files in os.listdir(f'Bot\\cogs'):
        if files.endswith(".py"):
            await bot.load_extension(f'cogs.{files[:-3]}')

# YOUR BOT TOKEN
bot.run(config["token"])