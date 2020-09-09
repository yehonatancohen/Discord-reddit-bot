import discord
import json
import praw
import re
import os
from discord.ext import commands
from importlib.machinery import SourceFileLoader
from modules.task import Task

token = os.environ['DISCORD_TOKEN']

c = commands.Bot(command_prefix = '.')
c.remove_command('help')

nsfw_url = os.environ['NSFW_URL']

curr_tasks = []

reddit = praw.Reddit(client_id=os.environ['REDDIT_CLIENT_ID'],
                     client_secret=os.environ['REDDIT_CLIENT_SECRET'],
                     user_agent=os.environ['REDDIT_USER_AGENT'])

@c.event
async def on_ready():
    print(f"{c.user.name}")
    await c.change_presence(activity=discord.Streaming(name=f'.help | {len(c.guilds)} servers', url='https://www.youtube.com/watch?v=dQw4w9WgXcQ'))

@c.event
async def on_guild_join(guild):
    await c.change_presence(activity=discord.Streaming(name=f'.help | {len(c.guilds)} servers', url='https://www.youtube.com/watch?v=dQw4w9WgXcQ'))

@c.event
async def on_guild_remove(guild):
    await c.change_presence(activity=discord.Streaming(name=f'.help | {len(c.guilds)} servers', url='https://www.youtube.com/watch?v=dQw4w9WgXcQ'))

async def create_task(msg : discord.Message,subreddit, guildid, c : discord.Client, reddit : praw.Reddit, nsfw_url, setting):
    id = len(curr_tasks) + 1
    task = Task(msg,id,subreddit,guildid,c,reddit,nsfw_url, setting, os.environ['UPVOTE_UNICODE'],os.environ['DOWNVOTE_UNICODE'], os.environ['WUBBLE_UNICODE'], os.environ['SAD_UNICODE'])
    curr_tasks.append(task)
    await curr_tasks[id - 1].send_submissions()

@c.command(aliases=['new','top'])
async def hot(ctx,subreddit):
    command = ctx.message.content.split(' ')[0].split('?')[1]
    try:
        reddit.subreddit(subreddit)._fetch()
    except:
        await ctx.channel.send("Subreddit does not exist!")
        return
    await create_task(ctx.message,subreddit,ctx.guild.id,c,reddit,nsfw_url,command)

@c.event
async def on_raw_reaction_add(payload):
    if payload.member.bot: return
    msgid = payload.message_id
    task = get_task(msgid)
    if task == None: return
    await task.reaction_added(payload)
    
def get_task(msgid):
    for task in curr_tasks:
        if task.smsg.id == msgid:
            return task
    return None


@c.command()
async def invite(ctx):
    await ctx.channel.send("Invite this bot to your server today! link: \nhttps://discord.com/api/oauth2/authorize?client_id=735196671042125885&permissions=124992&scope=bot")

@c.command(aliases=['helpme'])
async def help(ctx):
    author = ctx.message.author

    embed = discord.Embed(
        colour = discord.Colour.blue()
    )

    embed.set_author(name='Help')

    embed.add_field(name='.hot {subreddit}', value='Sends the hot submissions by order', inline=False)
    embed.add_field(name='.top {subreddit}', value='Sends the top submissions by order', inline=False)
    embed.add_field(name='.new {subreddit}', value='Sends the new submissions by order', inline=False)
    embed.add_field(name='.invite {subreddit}', value="Sends the bot's invite link for you to invite it to your server!", inline=False)

    await ctx.channel.send(embed=embed)

@c.command()
async def servers(ctx):
    await ctx.channel.send(f"**I'm in {len(c.guilds)} servers!**")

@c.command()
async def members(ctx):
    members = 0
    for guild in c.guilds:
        members += len(guild.members)
    await ctx.channel.send(f"**I'm in {len(c.guilds)} servers, with {members} members**")

async def get_tasks(ctx):
    return_list = []
    for task in curr_tasks:
        try:
            if task.author == ctx.author:
                return_list.append(task)
        except:
            await ctx.channel.send("An error occured")
    return return_list
  
c.run(token)