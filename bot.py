import discord
import json
import praw
import re
from discord.ext import commands
from importlib.machinery import SourceFileLoader
from modules.task import Task

cfg = SourceFileLoader('cfg', 'config.cfg').load_module()

token = cfg.DISCORD_TOKEN

c = commands.Bot(command_prefix = '.')
c.remove_command('help')

nsfw_url = cfg.NSFW_URL

curr_tasks = []

reddit = praw.Reddit(client_id=cfg.REDDIT_CLIENT_ID,
                     client_secret=cfg.REDDIT_CLIENT_SECRET,
                     user_agent=cfg.REDDIT_USER_AGENT)

@c.event
async def on_ready():
    print(f"{c.user.name}")
    await c.change_presence(activity=discord.Streaming(name=f'{len(c.guilds)} servers', url='https://www.youtube.com/watch?v=dQw4w9WgXcQ')) #Rick roll status :P

async def create_task(msg : discord.Message,subreddit, guildid, c : discord.Client, reddit : praw.Reddit, nsfw_url, setting):
    id = len(curr_tasks) + 1
    task = Task(msg,id,subreddit,guildid,c,reddit,nsfw_url, setting, cfg.UPVOTE_UNICODE, cfg.DOWNVOTE_UNICODE, cfg.WUBBLE_UNICODE, cfg.SAD_UNICODE)
    curr_tasks.append(task)
    await curr_tasks[id - 1].send_submissions()

@c.command(aliases=['new','top'])
async def hot(ctx,subreddit):
    command = ctx.message.content.split(' ')[0].split('.')[1]
    await create_task(ctx.message,subreddit,ctx.guild.id,c,reddit,nsfw_url,command)

@c.event
async def on_raw_reaction_add(payload):
    msgid = payload.message_id
    task = get_task(msgid)
    await task.reaction_added(payload)

def get_task(msgid):
    for task in curr_tasks:
        if task.smsg.id == msgid:
            return task
    return None

@c.command()
async def invite(ctx):
    await ctx.channel.send("Invite this bot to your server today! link: https://discord.com/api/oauth2/authorize?client_id=735196671042125885&permissions=124992&scope=bot")
  
c.run(token)