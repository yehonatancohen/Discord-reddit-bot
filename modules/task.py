from discord.ext import commands
import discord
import praw

class Task:
    id = 0
    subreddit = ""
    guildid = 0
    msg = discord.Message
    smsg = discord.Message
    c = discord.Client
    curr_submission = 0
    author = discord.Member
    reddit = praw.Reddit
    nsfw_url = ""
    setting = ""
    def __init__(self, msg : discord.Message, id,subreddit, guildid, c : discord.Client, reddit : praw.Reddit, nsfw_url, setting):
        self.id = id
        self.subreddit = subreddit
        self.guildid = guildid
        self.msg = msg
        self.c = c
        self.author = msg.author
        self.reddit = reddit
        self.nsfw_url = nsfw_url
        self.setting = setting

    async def send_submissions(self):
        self.smsg = await self.send_msg()
        await self.smsg.add_reaction("◀️")
        await self.smsg.add_reaction("▶️")

    async def get_reaction(self,payload : discord.RawReactionActionEvent, memeber : discord.Member):
        msg = await self.smsg.channel.fetch_message(self.smsg.id)
        for reaction in msg.reactions:
            async for user in reaction.users():
                if user == memeber:
                    return reaction
        return None
    
    def get_hot_post(self):
        i = 0
        for submission in self.reddit.subreddit(self.subreddit).hot(limit=self.curr_submission + 1):
            if i == self.curr_submission:
                return submission 
            i += 1
        return None

    def get_new_post(self,index,subreddit):
        i = 0
        for submission in self.reddit.subreddit(self.subreddit).new(limit=self.curr_submission + 1):
            if i == self.curr_submission:
                return submission 
            i += 1
        return None

    def get_top_post(self,index,subreddit):
        i = 0
        for submission in self.reddit.subreddit(self.subreddit).top(limit=self.curr_submission + 1):
            if i == self.curr_submission:
                return submission 
            i += 1
        return None

    async def edit_msg(self):
        channel = self.smsg.channel
        submission = self.get_hot_post()
        if submission.over_18:
                if channel.is_nsfw():
                    if not submission.is_self:
                        await self.smsg.edit(content=(submission.title + "\n" + submission.url))
                    else:
                        await self.smsg.edit(content=submission.title)
                else:
                    await self.smsg.edit(content=self.nsfw_url)
        else:
            if not submission.is_self:
                await self.smsg.edit(content=(submission.title + "\n" + submission.url))
            else:
                await self.smsg.edit(content=submission.title)

    async def send_msg(self):
        submission = self.get_hot_post()
        smsg = discord.Message
        channel = self.msg.channel
        if submission.over_18:
                if channel.is_nsfw():
                    if not submission.is_self:
                        smsg = await self.msg.channel.send(content=(submission.title + "\n" + submission.url))
                    else:
                        smsg = await self.msg.channel.send(content=submission.title)
                else:
                    smsg = await self.msg.channel.send(content=self.nsfw_url)
        else:
            if not submission.is_self:
                smsg = await self.msg.channel.send(content=(submission.title + "\n" + submission.url))
            else:
                smsg = await self.msg.channel.send(content=submission.title)
        return smsg

    async def reaction_added(self,payload : discord.RawReactionActionEvent):
        reaction = await self.get_reaction(payload,payload.member)
        if payload.member == self.c.user:
            return
        if payload.member != self.author:
            await reaction.remove(payload.member)
            return
        if payload.emoji.name == "▶️":
            self.curr_submission += 1
            await self.edit_msg()
        if payload.emoji.name == "◀️":
            if self.curr_submission > 0:
                self.curr_submission -= 1
                await self.edit_msg()
        await reaction.remove(payload.member)