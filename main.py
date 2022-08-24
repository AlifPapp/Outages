import asyncio
import json
import os

import discord
from discord.ext import commands, tasks
from pymongo import MongoClient

from cogs.functions import user_avatar_url

#import keep_alive
#keep_alive.keep_alive()

debug_guilds = [420513434996572191]
botishosted = False

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(debug_guilds=debug_guilds,
                         command_prefix=commands.when_mentioned,
                         case_insensitive=True,
                         intents=discord.Intents.all(),
                         status=discord.Status.idle,
                         activity=discord.Activity(type=discord.ActivityType.watching, name="Zseni's bots"))
        self.remove_command('help')
        self.serverprefix = "@Outages "

        with open("./json/help.json","r") as f: 
            self.helpfile = json.load(f)
            self.helpcmd = [] # alphabetical order list of commands
            for x in self.helpfile: 
                self.helpcmd.append(x)
            self.helpcmd = sorted(self.helpcmd)

        if botishosted == True:
            self.Secrets = json.loads(os.environ.get('Secrets'))
        else: 
            with open("./json/Secrets.json","r") as f: 
                self.Secrets = json.load(f)

        self.owner_id = 377418029706772480
        self.githubrepo = "https://github.com/Zseni051/Outages"

        self.mongodb = MongoClient(self.Secrets["MongoDB"])

        self.Yellow = int("FFB744" , 16)
        self.Black = int("000000" , 16)
        self.Green = int("2EC550" , 16)
        self.Red = int("D72D42" , 16)
        self.Blue = int("7289DA" , 16)

        for filename in os.listdir('cogs'):
            if filename.endswith('.py'):
                self.load_extension(f'cogs.{filename[:-3]}')
        
    async def on_ready(self):
        print('Logged in as')
        print('Name:', self.user.name)
        print('ID:', self.user.id)
        print('------')
        print('main.py Loaded!')

        Loop_CheckStatus.start()

    async def on_connect(self):
        print("Bot has connected")
        await self.sync_commands(force=True)

    async def on_disconnect(self):
        print("Bot has disconnected")

if __name__ == "__main__":
    bot = Bot()

@tasks.loop(seconds = 5) # repeat every 5 seconds
async def Loop_CheckStatus():
    cluster = bot.mongodb["Outages"]["Users"]
    for userdata in cluster.find():
        guild = bot.get_guild(debug_guilds[0])
        member = guild.get_member(int(userdata["id"]))
        if member == None:
            print(f"{int(userdata['id'])} is not in the guild")
            continue
        user_status = userdata["status"]
        if member.status == discord.Status.offline:
            if user_status == "online":
                await sendstatus(userdata["id"], "offline")
        else:
            if user_status == "offline": 
                await sendstatus(userdata["id"], "online")
    return

async def sendstatus(user, status):
    cluster = bot.mongodb["Outages"]["Users"]
    cluster.update_one({"id": user}, {"$set":{"status": status}})
    member = cluster.find_one({"id": user})
    ping_msg = member["ping"]
    guild = bot.get_guild(debug_guilds[0])
    channel = guild.get_channel(member["channel"])
    
    user = await bot.fetch_user(user)
    if status == "online":
        em = discord.Embed(title = f"**{user.name}** is now online",
                           description = "",
                           color = bot.Blue)
    elif status == "offline":
        em = discord.Embed(title = f"**{user.name}** is now offline",
                           description = "",
                           color = bot.Red)
    em.set_thumbnail(url = user_avatar_url(user))
    await channel.send(embed = em)
    
    if ping_msg.isspace() == False:
        await asyncio.sleep(1)
        ping_msg = await channel.send(ping_msg)
        await asyncio.sleep(1)
        await ping_msg.delete()
    return
#####################################################################################################################################
bot.run(bot.Secrets["Token"])
