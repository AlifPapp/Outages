import platform
from typing import Optional

import discord
import psutil
from discord import Embed, Member
from discord.commands import slash_command
from discord.ext import commands


class cmnds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("cmnds.py Loaded!")

    # botinfo
    @commands.command(aliases=["bi"])
    async def botinfo(self, ctx):
        await botinfo_cmd(False, self, ctx)
    @slash_command(name="botinfo", description="Gives information about the bot")
    async def botinfo_slash(self, ctx: discord.ApplicationContext):
        await botinfo_cmd(True, self, ctx)

    # add
    @commands.command()
    async def add(self, ctx, user: Optional[Member], status: str="online"):
        if ctx.author.id == self.bot.owner_id:
            if status in ["online", "offline"]:
                cluster = self.bot.mongodb["Outages"]["Users"]
                if cluster.find_one({"id": user.id}) is None:
                    insert = {"id": user.id, "status": status}
                    cluster.insert_one(insert)
                    await ctx.send(f"Added {user.mention} to the list of users to be monitored")
                else:
                    await ctx.send(f"{user.mention} is already being monitored")
    # remove
    @commands.command()
    async def remove(self, ctx, user: Optional[Member]):
        if ctx.author.id == self.bot.owner_id:
            cluster = self.bot.mongodb["Outages"]["Users"]
            if cluster.find_one({"id": user.id}):
                cluster.delete_one({"id": user.id})
                await ctx.send(f"Removed {user.mention} from the list of users to be monitored")
            else:
                await ctx.send(f"{user.mention} is not being monitored")

    # list
    @commands.command()
    async def list(self, ctx):
        await list_cmd(False, self, ctx)
    @slash_command(name="list", description="Lists all users being monitored")
    async def list_slash(self, ctx: discord.ApplicationContext):
        await list_cmd(True, self, ctx)

####################################################################################################################################

async def list_cmd(slash, self, ctx):
    cluster = self.bot.mongodb["Outages"]["Users"]
    list = []
    i = 1
    for userdata in cluster.find():
        user = await self.bot.fetch_user(userdata["id"])
        list.append(f"**{i} - {user.mention} - {userdata['status']}")
        i += 1
    em = discord.Embed(title="List of Users", description="\n".join(list), color=self.bot.Blue)
    await response(slash, "reply", ctx, embed = em, mention_author=False)

async def botinfo_cmd(slash, self, ctx):
    memory_total = psutil.virtual_memory()._asdict()["total"]
    memory_used = psutil.virtual_memory()._asdict()["used"]
    memory_usage = f"{round(memory_used/1000000000, 1)}/{round(memory_total/1000000000, 1)}GB"
    cpu_percent = psutil.cpu_percent()

    shard_id = ctx.guild.shard_id
    shard = self.bot.get_shard(shard_id)

    em = Embed(title=f"Bot Information - {self.bot.user}",
               description=f'{self.bot.user.name} is an advanced counting bot that can manage a counting channel in your guild. With a simple setup, your channel is ready.',
               colour=self.bot.Blue)

    em.add_field(name=f"💠 Host", value=f"**OS**: `{platform.system()} ({platform.release()})`\n**Library**: `Pycord {discord.__version__}`\n**Memory Usage**: `{memory_usage}`\n**CPU**: `{cpu_percent}%`\n**Ping**: `{round(shard.latency * 1000)}ms`", inline=True)
    em.add_field(name=f"🌐 Links", value=f"**Github Repo:** {self.bot.githubrepo}", inline=False)
    await response(slash, "reply", ctx, embed = em, mention_author=False)

#####################################################################################################################################
async def response(slash, type, ctx, *args, **kwargs):
    if type == "send":
        return await ctx.send(*args, **kwargs)

    if slash == True:
        #remove uncompatible **kwargs
        if "mention_author" in kwargs:
            kwargs.pop("mention_author")

        if type == "reply":
            return await ctx.respond(*args, **kwargs)
        if type == "edit":
            return await ctx.edit_original_message(*args, **kwargs)
    
    if slash == False:
        if type == "reply":
            return await ctx.reply(*args, **kwargs)
        if type == "edit":
            return await ctx.edit(*args, **kwargs)

#####################################################################################################################################
def setup(bot):
    bot.add_cog(cmnds(bot))
