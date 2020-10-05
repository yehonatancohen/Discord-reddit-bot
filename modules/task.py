from discord.ext import commands
import discord
import praw
import time

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
    start_time : time

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
        self.start_time = time.time()

    async def send_submissions(self):
        msg = self.get_message()
        self.smsg = await self.msg.channel.send(embed=msg)
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

    def setting_func(self, setting):
        return_dict = {
            'hot' : self.reddit.subreddit(self.subreddit).hot(limit=self.curr_submission + 3),
            'new' : self.reddit.subreddit(self.subreddit).new(limit=self.curr_submission + 3),
            'top' : self.reddit.subreddit(self.subreddit).top(limit=self.curr_submission + 3)
        }
        return return_dict.get(setting)
    
    def get_post(self):
        i = 0
        submissions = self.setting_func(self.setting)
        for submission in submissions:
            if i == self.curr_submission and submission.stickied:
                self.curr_submission += 1
            elif i == self.curr_submission and not submission.stickied:
                return submission 
            i += 1
        return None

    def get_message(self):
        channel = self.msg.channel
        submission = self.get_post()
        embed : praw.Embed
        if submission.over_18:
                if channel.is_nsfw():
                    if not submission.is_self:
                        embed=discord.Embed(title=submission.title, url=f"https://www.reddit.com{submission.permalink}", color=0xfa0000)
                        embed.set_image(url=submission.url)
                        embed.set_footer(text=f"⬆️ {submission.score} | 💬 {submission.num_comments} | NSFW")
                    else:
                        embed=discord.Embed(title=submission.title, url=f"https://www.reddit.com{submission.permalink}", color=0xfa0000)
                        embed.set_footer(text=f"⬆️ {submission.score} | 💬 {submission.num_comments} | NSFW")
                else:
                    embed=discord.Embed(title="This is a NSFW submission", url=f"https://www.reddit.com{submission.permalink}", color=0xfa0000)
                    embed.set_image(url=self.nsfw_url)
                    embed.set_footer(text=f"⬆️ {submission.score} | 💬 {submission.num_comments}")
        else:
            if not submission.is_self:
                embed=discord.Embed(title=submission.title, url=f"https://www.reddit.com{submission.permalink}", color=0xfa0000)
                embed.set_image(url=submission.url)
                embed.set_footer(text=f"⬆️ {submission.score} | 💬 {submission.num_comments}")
            else:
                embed=discord.Embed(title=submission.title, url=f"https://www.reddit.com{submission.permalink}", color=0xfa0000)
                embed.set_image(url=submission.url)
                embed.set_footer(text=f"⬆️ {submission.score} | 💬 {submission.num_comments}")
        return embed
        
    async def edit_msg(self):
        msg = self.get_message()
        await self.smsg.edit(embed=msg)

    async def send_msg(self):
        msg = self.get_message()
        self.smsg = await self.msg.channel.send(embed=msg)

    async def reaction_added(self,payload : discord.RawReactionActionEvent):
        if payload.member.bot: return

        reaction = await self.get_reaction(payload.member,str(payload.emoji))
        
        if payload.member != self.author:
            try:
                await reaction.remove(payload.member)
                return
            except:
                return

        if payload.emoji.name == "▶️":
            self.curr_submission += 1
            await self.edit_msg()
        if payload.emoji.name == "◀️":
            if self.curr_submission > 0:
                self.curr_submission -= 1
                await self.edit_msg()
        if str(payload.emoji) == self.downvote_unicode or str(payload.emoji) == self.upvote_unicode:
            return

        await reaction.remove(payload.member)