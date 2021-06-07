import discord
from discord import client
from discord.ext import commands, tasks

from datetime import datetime
import os
import psutil

defaultprefix = "ts!"
#####################################################################################################################################
############################################################ C L I E N T ############################################################
#####################################################################################################################################
intents = discord.Intents.all()
client = commands.Bot(command_prefix = commands.when_mentioned_or(defaultprefix),
                      case_insensitive=True,
                      intents = intents)
client.remove_command('help')


#####################################################################################################################################
############################################################# VARIABLES #############################################################
#####################################################################################################################################
client.developerid = 416508283528937472, 0

client.Yellow = int("FFB744" , 16)
client.Black = int("000000" , 16)
client.Green = int("3BA55C" , 16)
client.Red = int("D72D42" , 16)
client.Blue = int("7289DA" , 16)

client.status = ""
#####################################################################################################################################
############################################################### EVENTS ##############################################################
#####################################################################################################################################
@client.event
async def on_ready():
    print('Logged in as')
    print('Name:', client.user.name)
    print('ID:', client.user.id)
    print('------')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Timely's Status"))
    print('Main.py Loaded!')
    targetguild = client.get_guild(835851709884530738)
    client.member = targetguild.get_member(836198930873057290)
    Loop_CheckStatus.start()

@client.event
async def on_connect():
    print("Bot has connected")

@client.event
async def on_disconnect():
    print("Bot has disconnected")

    channel = client.get_channel(845586893789986857)
    em = discord.Embed(title = "TimelyBot has awoken!",
                       description = "But for how long?",
                       color = client.Blue,
                       timestamp=datetime.utcnow())
    await channel.send(embed = em)
#####################################################################################################################################
########################################################## C O M M A N D S ##########################################################
#####################################################################################################################################
@client.command()
async def prefix(ctx):
    em = discord.Embed(title = "Prefixes",
                           description = f"**1:**{client.user.mention}\n**2:** `{defaultprefix}`",
                           colour = client.Blue)

    em.set_footer(text=f"`{defaultprefix}info`")
    em.timestamp = datetime.utcnow()
    await ctx.send(embed = em)

@client.command()
async def info(ctx):
    channel = client.get_channel(845586893789986857)

    em = discord.Embed(title = "What's my job?",
                           description = f"I update you on whether <@!836198930873057290> is currently up or down in {channel.mention}",
                           colour = client.Blue)
    
    if client.member.status == discord.Status.offline:
        em.set_footer(text="Timely is offline")
    else: 
        em.set_footer(text="Timely is online")
    em.timestamp = datetime.utcnow()
    await ctx.send(embed = em)

@client.command()
async def botinfo(ctx):
    memory_total = psutil.virtual_memory()._asdict()["total"]
    memory_used = psutil.virtual_memory()._asdict()["used"]
    memory_percent = psutil.virtual_memory()._asdict()["percent"]
    cpu_percent = psutil.cpu_percent()

    em = discord.Embed(title=f"Bot Info - {client.user}",
                  colour=client.Blue)
    em.set_thumbnail(url=client.user.avatar_url)
    
    Vars = [f"{int(memory_used/1000000)}/{int(memory_total/1000000)} ({memory_percent}%)",
            f"[discord.py](https://discordpy.readthedocs.io/en/latest/) {discord.__version__}",
            f"[Heroku](https://dashboard.heroku.com/)"]

    em.add_field(name="System", value=f"CPU: {cpu_percent}%\nMemory: {Vars[0]}\nFramework: {Vars[1]}\nHosted on: {Vars[2]}", inline=True)

    em.set_footer(text=f"ID: {client.user.id}")
    em.timestamp = datetime.utcnow()
    await ctx.reply(embed = em)
#####################################################################################################################################
############################################################# L O O P S #############################################################
#####################################################################################################################################
@tasks.loop(seconds = 10) # repeat after every 10 seconds
async def Loop_CheckStatus():
    #Initial TimelyStatus Setup
    if client.status == "":
        if client.member.status == discord.Status.offline:
            client.status = "offline"
            await sendstatus("offline")
        else:
            client.status = "online"
            await sendstatus("online")
    
    #Check for change in status
    if client.member.status == discord.Status.offline:
        if client.status == "online":
            client.status = "offline"
            await sendstatus("offline")
    else:
        if client.status == "offline":
            client.status = "online"
            await sendstatus("online")
    return


async def sendstatus(status):
    channel = client.get_channel(845586893789986857)
    if status == "online":
        em = discord.Embed(title = "TimelyBot has awoken!",
                           description = "But for how long?",
                           color = client.Blue,
                           timestamp=datetime.utcnow())
        await channel.send(embed = em)
    if status == "offline":
        em = discord.Embed(title = "TimelyBot is taking a nap!",
                           description = "The developers are trying their best to wake it up.",
                           color = client.Red,
                           timestamp=datetime.utcnow())
        await channel.send(embed = em)
    return

#####################################################################################################################################
token = open("token.txt","r").readline()
client.run(token.strip())
#client.run(str(os.environ.get('BOT_TOKEN')))
