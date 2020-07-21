import discord
import json
from discord.ext import commands

token = ''

c = commands.Bot(command_prefix = '.')
c.remove_command('help')


@c.event
async def on_ready():
    await c.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,name=f'{len(c.guilds)} servers'))



c.run(token)