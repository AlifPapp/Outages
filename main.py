import asyncio
import json
import os

import discord
from discord.ext import commands, tasks
from pymongo import MongoClient

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
        
        if botishosted == True:
            self.Secrets = json.loads(os.environ.get('Secrets'))
        else: 
            with open("./Secrets.json","r") as f: 
                self.Secrets = json.load(f)

        self.owner_id = 377418029706772480
        self.githubrepo = "https://github.com/Zseni051/Outages"
        self.outages_channel = 1008524900442570822
        self.ping_users = f"<@!{self.owner_id}>"

        self.mongodb = MongoClient(self.Secrets["MongoDB"])

        self.Yellow = int("FFB744" , 16)
        self.Black = int("000000" , 16)
        self.Green = int("2EC550" , 16)
        self.Red = int("D72D42" , 16)
        self.Blue = int("7289DA" , 16)

        self.load_extension(f'cmnds')
        
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
    guild = bot.get_guild(debug_guilds[0])
    channel = guild.get_channel(bot.outages_channel)
    cluster = bot.mongodb["Outages"]["Users"]
    cluster.update_one({"id": user}, {"$set":{"status": status}})
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
    await asyncio.sleep(1)
    ping_msg = await channel.send(f"**Pinged:** {bot.ping_users}")
    await asyncio.sleep(1)
    await ping_msg.delete()
    return

def user_avatar_url(user):
    try: 
        user_avatar_url = user.avatar.url
    except: 
        user_avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
    return user_avatar_url
#####################################################################################################################################
bot.run(bot.Secrets["Token"])
