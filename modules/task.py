from discord.ext import commands
import discord

class Task:
    id = 0
    urls = []
    subreddit = ""
    guildid = 0
    msg = discord.Message
    smsg = discord.Message
    c = discord.Client
    curr_submission = 0
    author = discord.Member
    def init(self, msg : discord.Message, id, urls, subreddit, guildid, c : discord.Client):
        self.id = id
        self.urls = urls
        self.subreddit = subreddit
        self.guildid = guildid
        self.msg = msg
        self.c = c
        self.author = msg.author

    async def send_submissions(self):
        self.smsg = await self.msg.channel.send(self.urls[self.curr_submission])

        await self.smsg.add_reaction("◀️")
        await self.smsg.add_reaction("▶️")

    async def get_reaction(self,payload : discord.RawReactionActionEvent, memeber : discord.Member):
        self.smsg = await self.smsg.channel.fetch_message(self.smsg.id)
        for reaction in self.smsg.reactions:
            async for user in reaction.users():
                if user == memeber:
                    return reaction
        return None


    async def reaction_added(self,payload : discord.RawReactionActionEvent):
        reaction = await self.get_reaction(self,payload,payload.member)
        if payload.member.bot or payload.member != self.author:
            #await reaction.remove(payload.member)
            return
        if payload.emoji.name == "▶️":
            self.curr_submission += 1
            await self.smsg.edit(content=self.urls[self.curr_submission])
        if payload.emoji.name == "◀️":
            if self.curr_submission > 0:
                self.curr_submission -= 1
                await self.smsg.edit(content=self.urls[self.curr_submission])
        await reaction.remove(payload.member)