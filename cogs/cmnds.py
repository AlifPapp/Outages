
import math
import platform
from typing import Optional

import discord
import psutil
from discord import Embed, Member
from discord.commands import slash_command
from discord.ext import commands

from .functions import ButtonItem, View_Timeout, cmd_aliases, cmd_descshort, response

class cmnds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("cmnds.py Loaded!")

    async def cog_check(self, ctx):
        try: 
            if ctx.guild is not None and not ctx.author.bot: 
                return True
        except: 
            pass

    # add
    @commands.command(aliases=cmd_aliases("add"))
    async def add(self, ctx, user: Optional[Member]=None, channel: Optional[discord.TextChannel]=None, *, msg: str=None):
        await add_cmd(False, self, ctx, user, channel, msg)
    @slash_command(name="add", description=cmd_descshort("botinfo"))
    async def add_slash(self, ctx: discord.ApplicationContext, user: discord.User, channel: discord.TextChannel, msg: str=None):
        await add_cmd(True, self, ctx, user, channel, msg)
    
    # remove
    @commands.command(aliases=cmd_aliases("remove"))
    async def remove(self, ctx, user: Optional[Member]):
        await remove_cmd(False, self, ctx, user)
    @slash_command(name="remove", description=cmd_descshort("botinfo"))
    async def remove_slash(self, ctx: discord.ApplicationContext, user: discord.User):
        await remove_cmd(True, self, ctx, user)

    # list
    @commands.command(aliases=cmd_aliases("list"))
    async def list(self, ctx):
        await list_cmd(False, self, ctx)
    @slash_command(name="list", description=cmd_descshort("botinfo"))
    async def list_slash(self, ctx: discord.ApplicationContext):
        await list_cmd(True, self, ctx)

    # botinfo
    @commands.command(aliases=cmd_aliases("botinfo"))
    async def botinfo(self, ctx):
        await botinfo_cmd(False, self, ctx)
    @slash_command(name="botinfo", description=cmd_descshort("botinfo"))
    async def botinfo_slash(self, ctx: discord.ApplicationContext):
        await botinfo_cmd(True, self, ctx)

    # help
    @commands.command()
    async def help(self, ctx, command: str="na"):
        await help_cmd(False, self, ctx, command)
    @slash_command(name="help", description="Learn about my commands")
    async def help_slash(self, ctx: discord.ApplicationContext, command: str="na"):
        await help_cmd(True, self, ctx, command)

####################################################################################################################################
async def add_cmd(slash, self, ctx, user, channel, msg):
    if ctx.author.id == self.bot.owner_id:
        if user == None:
            await response(slash, "reply", ctx, content="No user specified", mention_author=False, ephemeral=True)
            return
        if channel == None:
            await response(slash, "reply", ctx, content="No channel specified", mention_author=False, ephemeral=True)
            return
        cluster = self.bot.mongodb["Outages"]["Users"]
        if cluster.find_one({"id": user.id}) is None:
            insert = {
                      "id": user.id, 
                      "status": "online",
                      "channel": channel.id,
                      "ping": msg
                      }
            cluster.insert_one(insert)
            await response(slash, "reply", ctx, content="Added user to list of users being monitored", mention_author=False)
        else:
            await response(slash, "reply", ctx, content=f"{user.mention} is already being monitored", mention_author=False)
    else:
        await response(slash, "reply", ctx, content="You do not have permission to use this command", mention_author=False, ephemeral=True)

async def remove_cmd(slash, self, ctx, user):
    if ctx.author.id == self.bot.owner_id:
        cluster = self.bot.mongodb["Outages"]["Users"]
        if cluster.find_one({"id": user.id}):
            cluster.delete_one({"id": user.id})
            await response(slash, "reply", ctx, content=f"Removed {user.mention} from the list of users to be monitored", mention_author=False)
        else:
            await response(slash, "reply", ctx, content=f"{user.mention} is not being monitored", mention_author=False)
    else:
        await response(slash, "reply", ctx, content="You do not have permission to use this command", mention_author=False, ephemeral=True)

async def list_cmd(slash, self, ctx):
    cluster = self.bot.mongodb["Outages"]["Users"]
    list = []
    i = 1
    for userdata in cluster.find():
        user = await self.bot.fetch_user(userdata["id"])
        list.append(f"**{i} - {user.mention} - <#{userdata['channel']}>**")
        i += 1
    em = discord.Embed(title="List of Users", description="\n".join(list), color=self.bot.Blue)
    await response(slash, "reply", ctx, embed = em, mention_author=False)

async def botinfo_cmd(slash, self, ctx):
    memory_total = psutil.virtual_memory()._asdict()["total"]
    memory_used = psutil.virtual_memory()._asdict()["used"]
    memory_usage = f"{round(memory_used/1000000000, 1)}/{round(memory_total/1000000000, 1)}GB"
    cpu_percent = psutil.cpu_percent()

    em = Embed(title=f"Bot Information - {self.bot.user}",
               description=f'{self.bot.user.name} monitores bots or users status and alerts you when they go offline.\n**Github Repo:** {self.bot.githubrepo}',
               colour=self.bot.Blue)

    em.add_field(name=f"💠 Host", value=f"**OS**: `{platform.system()} ({platform.release()})`\n**Library**: `Pycord {discord.__version__}`\n**Memory Usage**: `{memory_usage}`\n**CPU**: `{cpu_percent}%`\n**Ping**: `{round(self.bot.latency * 1000)}ms`", inline=True)
    await response(slash, "reply", ctx, embed = em, mention_author=True)

async def help_cmd(slash, self, ctx, command):
    p = self.bot.serverprefix
    cmd = False
    if command != "na": # Check if command exists
        command = str(command).lower()
        for x in self.bot.helpfile: #Check is a command
            if command == x: 
                cmd = x
                break
            else: #Check if is an aliase
                if command in self.bot.helpfile[x]['aliases'].split(', '):
                    cmd = x
                    break
    if cmd == False: # command not found display list of all commands
        description = f"\n• If you need help with a command, do `{p}help <command>`."
        description += f"\n• If you have any questions/queries this is the [Github Repo](self.bot.githubrepo)\n"

        for x in self.bot.helpfile: 
            description += f"\n**[{x}]({self.bot.helpfile[x]['link']})**\n- {self.bot.helpfile[x]['desc_short']}"
        em = discord.Embed(title = f"{self.bot.user.name} Help",
                           description = description,
                           colour = self.bot.Blue)
        em.set_footer(text=f"{p}help <command> to see more details")
        await response(slash, "reply", ctx, embed = em, mention_author=False)
        return
    else: # command found display help for command
        em = discord.Embed(title = f"{cmd.capitalize()}",
                       description = f"**Description:**\n{self.bot.helpfile[cmd]['desc_long']}",
                       colour = self.bot.Blue)
        em.add_field(name="**Usage:**",value=f"`{p}{self.bot.helpfile[cmd]['usage']}`", inline=False)
        if self.bot.helpfile[cmd]['aliases'] != "False":
            em.add_field(name="**Aliases:**",value=f"{self.bot.helpfile[cmd]['aliases']}", inline=False)
        if self.bot.helpfile[cmd]['cooldown'] != "False":
            em.add_field(name="**Cooldown:**",value=f"{self.bot.helpfile[cmd]['cooldown']}", inline=False)
        await response(slash, "reply", ctx, embed = em, mention_author=False)
#####################################################################################################################################
def setup(bot):
    bot.add_cog(cmnds(bot))
