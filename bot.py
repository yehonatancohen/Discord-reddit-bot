import discord
import json
from discord.ext import commands
from importlib.machinery import SourceFileLoader
import praw
from modules.task import Task

cfg = SourceFileLoader('cfg', 'config.cfg').load_module()

token = cfg.DISCORD_TOKEN

max_command_amount = cfg.MAX_COMMAND_AMOUNT

c = commands.Bot(command_prefix = '.')
c.remove_command('help')

nsfw_url = cfg.NSFW_URL

curr_tasks = []

reddit = praw.Reddit(client_id=cfg.REDDIT_CLIENT_ID,
                     client_secret=cfg.REDDIT_CLIENT_SECRET,
                     user_agent=cfg.REDDIT_USER_AGENT)

@c.event
async def on_ready():
    await c.change_presence(activity=discord.Streaming(name=f'{len(c.guilds)} servers', url='https://www.youtube.com/watch?v=dQw4w9WgXcQ')) #Rick roll status :P

@c.command(aliases=['hot'])
async def get_hot(ctx,subreddit):
    tmp_task = Task
    id = len(curr_tasks) + 1
    tmp_task.init(tmp_task,ctx.message,id,subreddit,ctx.guild.id,c,reddit,nsfw_url)
    curr_tasks.append(tmp_task)
    await tmp_task.send_submissions(tmp_task)

@c.command()
async def print_info(ctx):
    tsk = curr_tasks[0]
    await ctx.channel.send(tsk.urls)
    pass

@c.event
async def on_raw_reaction_add(payload):
    msgid = payload.message_id
    task = get_task(msgid)
    await task.reaction_added(task,payload)

def get_task(msgid):
    for task in curr_tasks:
        if task.smsg.id == msgid:
            return task
    return None

@c.command()
async def invite(ctx):
    await ctx.channel.send("Invite this bot to your server today! link: https://discord.com/api/oauth2/authorize?client_id=735196671042125885&permissions=124992&scope=bot")
  
c.run(token)