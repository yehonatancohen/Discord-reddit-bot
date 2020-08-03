from discord.ext import commands
import discord
import praw

class Task:
    id = 0
    subreddit = ""
    guildid = 0
    msg : discord.Message
    smsg : discord.Message
    c : discord.Client
    curr_submission = 0
    author : discord.Member
    reddit : praw.Reddit
    nsfw_url = ""
    setting = ""
    upvote_unicode = ""
    downvote_unicode = ""
    wubble_unicode = ""
    sad_unicode = ""

    def __init__(self, msg : discord.Message, id,subreddit, guildid, c : discord.Client, reddit : praw.Reddit, nsfw_url, setting, upvote, downvote, wubble, sad):
        self.id = id
        self.subreddit = subreddit
        self.guildid = guildid
        self.msg = msg
        self.c = c
        self.author = msg.author
        self.reddit = reddit
        self.nsfw_url = nsfw_url
        self.setting = setting
        self.upvote_unicode = upvote
        self.downvote_unicode = downvote
        self.wubble_unicode = wubble
        self.sad_unicode = sad

    async def send_submissions(self):
        await self.send_msg()
        await self.smsg.add_reaction("◀️")
        await self.smsg.add_reaction("▶️")
        await self.smsg.add_reaction(self.upvote_unicode)
        await self.smsg.add_reaction(self.downvote_unicode)

    async def get_reaction(self,member : discord.Member, emoji):
        msg = await self.smsg.channel.fetch_message(self.smsg.id)
        for reaction in msg.reactions:
            if str(reaction.emoji) != emoji:
                continue
            async for user in reaction.users():
                if user == member:
                    return reaction
        return None
    
    def get_post(self):
        i = 0
        for submission in getattr(self.reddit.subreddit(self.subreddit),self.setting)():
            if i == self.curr_submission and submission.stickied:
                self.curr_submission += 1
            elif i == self.curr_submission and not submission.stickied:
                return submission 
            i += 1
        return None

    def upvotes_parse(self, upvotes):
        if upvotes > 1000:
            upvotes = round(upvotes / 1000)
            return "**" + str(upvotes) + "K Upvotes**"
        elif upvotes > 1000000:
            round(upvotes / 1000000)
            return "**" + str(upvotes) + "M Upvotes**"
        else:
            return "**" + str(upvotes) + " Upvotes**"

    def get_message(self):
        channel = self.msg.channel
        submission = self.get_post()
        msg = ""
        upvotes = self.upvotes_parse(submission.score)
        if submission.over_18:
                if channel.is_nsfw():
                    if not submission.is_self:
                        msg = submission.title + "\n" + upvotes + "\n" + submission.author.name + "\n" + submission.url
                    else:
                        msg = submission.title + "\n" + upvotes + "\n" + submission.author.name
                else:
                    msg = self.nsfw_url
        else:
            if not submission.is_self:
                msg = submission.title + "\n" + upvotes + "\n" + submission.url + "\n" + submission.author.name
            else:
                msg = submission.title + "\n" + upvotes + "\n" + submission.author.name + "\n"
        return msg
        
    async def edit_msg(self):
        msg = self.get_message()
        await self.smsg.edit(content=msg)

    async def send_msg(self):
        msg = self.get_message()
        self.smsg = await self.msg.channel.send(msg)

    async def reaction_added(self,payload : discord.RawReactionActionEvent):
        reaction = await self.get_reaction(payload.member,str(payload.emoji))
        reaction_upvote = await self.get_reaction(payload.member,self.upvote_unicode)
        reaction_downvote = await self.get_reaction(payload.member,self.downvote_unicode)


        if payload.member == self.c.user:
            return

        if payload.member != self.author and (payload.emoji.name == "▶️" or payload.emoji.name == "◀️"):
            try:
                await reaction.remove(payload.member)
                return
            except:
                return

        if payload.emoji.name == "▶️":
            self.curr_submission += 1
            await self.edit_msg()
            if reaction_upvote != None:
                await reaction_upvote.remove(payload.member)
            if reaction_downvote != None:
                await reaction_downvote.remove(payload.member)
        if payload.emoji.name == "◀️":
            if self.curr_submission > 0:
                self.curr_submission -= 1
                await self.edit_msg()
                if reaction_upvote != None:
                    await reaction_upvote.remove(payload.member)
                if reaction_downvote != None:
                    await reaction_downvote.remove(payload.member)

        if str(payload.emoji) == self.upvote_unicode:
            if reaction_downvote == None:
                return
            else:
                await reaction_downvote.remove(payload.member)
                return
        if str(payload.emoji) == self.downvote_unicode:
            if reaction_upvote == None:
                return
            else:
                await reaction_upvote.remove(payload.member)
                return
        await reaction.remove(payload.member)