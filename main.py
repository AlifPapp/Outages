import discord
from discord import client
from discord.ext import commands, tasks

from datetime import datetime
import os
import psutil

import ssl
from pymongo import MongoClient

defaultprefix = "ts!"

intents = discord.Intents.all()
client = commands.Bot(command_prefix = commands.when_mentioned_or(defaultprefix),
                      case_insensitive=True,
                      intents = intents)
client.remove_command('help')

client.developerid = 416508283528937472, 0

client.Yellow = int("FFB744" , 16)
client.Black = int("000000" , 16)
client.Green = int("2EC550" , 16)
client.Red = int("D72D42" , 16)
client.Blue = int("7289DA" , 16)

#MongoClientLink = open("MongoClient.txt","r").readline()
#cluster = MongoClient(MongoClientLink.strip(), ssl_cert_reqs=ssl.CERT_NONE)
cluster = MongoClient(str(os.environ.get('MONGO_LINK')), ssl_cert_reqs=ssl.CERT_NONE)
client.botstatus = cluster["bot"]["status"]
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
    
    client.check_user = 416508283528937472
    targetguild = client.get_guild(835851709884530738)
    client.member = targetguild.get_member(client.check_user)
    client.channel = 836460335279112223
    
    print('Watching_user:', client.member)
    print('Guild:', targetguild.name)
    print('Channel:', client.channel)

    #Insert if None
    botstatus = client.botstatus.find_one({"bot_id": client.check_user})
    if botstatus is None:
        status = {"bot_id": client.check_user, "status": "online"}
        client.botstatus.insert_one(status)

    Loop_CheckStatus.start()

@client.event
async def on_connect():
    print("Bot has connected")

@client.event
async def on_disconnect():
    print("Bot has disconnected")
#####################################################################################################################################
########################################################## C O M M A N D S ##########################################################
#####################################################################################################################################
# thelp
@client.command()
async def help(ctx):
    channel = client.get_channel(client.channel)

    em = discord.Embed(title = "Hi, I'm TimelyStatus",
                           description = f"I update you on whether <@!{client.check_user}> is currently up or down in {channel.mention}\nFeel free to follow this channel to get updates in your own server.",
                           colour = client.Blue)
    em.add_field(name="Prefix",value=f"**1:** {client.user.mention}\n**2:** `{defaultprefix}`")
    em.add_field(name="Commands",value=f"**1:** `{defaultprefix}help`\n**2:** `{defaultprefix}botinfo`")
    
    if client.member.status == discord.Status.offline:
        em.set_footer(text="Timely is offline")
    else: 
        em.set_footer(text="Timely is online")
    em.timestamp = datetime.utcnow()
    await ctx.send(embed = em)


# tbotinfo
@client.command(aliases=['bi'])
async def botinfo(ctx):
    memory_total = psutil.virtual_memory()._asdict()["total"]
    memory_used = psutil.virtual_memory()._asdict()["used"]
    memory_percent = psutil.virtual_memory()._asdict()["percent"]
    cpu_percent = psutil.cpu_percent()

    users_sum = 0
    for x in client.guilds:
        users_sum += len(x.members)

    em = discord.Embed(title=f"Bot Info - {client.user}",
              colour=client.Blue)
    em.set_thumbnail(url=client.user.avatar_url)

    Vars = [client.user.created_at.strftime("%d/%m/%Y"),
            len(client.guilds),
            f"{int(memory_used/1000000)}/{int(memory_total/1000000)} MB ({memory_percent}%)",
            f"[discord.py](https://discordpy.readthedocs.io/en/latest/) {discord.__version__}",
            f"[MongoDB](https://www.mongodb.com/)",
            f"[Heroku](https://dashboard.heroku.com/)"]

    fields = [(":file_folder:Info",f"Owner: {client.user.mention}\nCreated: {Vars[0]}\nGuilds: {Vars[1]}\nUsers: {users_sum}",False),
              (":file_cabinet:System",f"CPU: {cpu_percent}%\nMemory: {Vars[2]}\nFramework: {Vars[3]}\nDataBase: {Vars[4]}\nHosted on: {Vars[5]}",True)]

    for name, value, inline in fields:
        em.add_field(name=name, value=value, inline=inline)

    em.set_footer(text=f"ID: {client.user.id}")
    em.timestamp = datetime.utcnow()
    await ctx.reply(embed = em)

#####################################################################################################################################
####################################################### C H E C K  &  S E N D #######################################################
#####################################################################################################################################
@tasks.loop(seconds = 10) # repeat after every 10 seconds
async def Loop_CheckStatus():
    #Check for change in status
    botstatus = client.botstatus.find_one({"bot_id": client.check_user})
    status = botstatus["status"]
    if client.member.status == discord.Status.offline:
        if status == "online":
            await sendstatus("offline")
            client.botstatus.update_one({"bot_id":client.check_user},{"$set":{"status":"offline"}})
    else:
        if status == "offline":
            await sendstatus("online")
            client.botstatus.update_one({"bot_id":client.check_user},{"$set":{"status":"online"}})
    return


async def sendstatus(status): #Send message
    channel = client.get_channel(client.channel)
    if status == "online":
        em = discord.Embed(title = "<:online_status:851753067611553803> TimelyBot has awoken!",
                           description = "But for how long?",
                           color = client.Blue,
                           timestamp=datetime.utcnow())
    if status == "offline":
        em = discord.Embed(title = "<:offline_status:851753226407641098> TimelyBot is taking a nap!",
                           description = "The developers are trying their best to wake it up.",
                           color = client.Red,
                           timestamp=datetime.utcnow())
        
    #em.set_author(name=f"{client.member.name}", icon_url = client.member.avatar_url)
    await channel.send(embed = em)
    return

#####################################################################################################################################
#token = open("token.txt","r").readline()
#client.run(token.strip())
client.run(str(os.environ.get('BOT_TOKEN')))
