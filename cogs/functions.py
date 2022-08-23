import json
import discord
from datetime import datetime

with open("./json/help.json","r") as f: 
    helpfile = json.load(f)

def cmd_aliases(cmd):
    if helpfile[cmd]['aliases'] == "False":
        return []
    else:
        return helpfile[cmd]['aliases'].split(', ')

def cmd_descshort(cmd):
    return helpfile[cmd]['desc_short']

def user_avatar_url(user):
    try: 
        user_avatar_url = user.avatar.url
    except: 
        user_avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
    return user_avatar_url

def basic_embed(title, description, color, footer: str=""):
    em = discord.Embed(title = title,
                       description = description,
                       color = color)
    if footer is not None:
        em.set_footer(text=footer)
    return em

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
        #remove uncompatible **kwargs
        if "ephemeral" in kwargs:
            kwargs.pop("ephemeral")
        if type == "reply":
            return await ctx.reply(*args, **kwargs)
        if type == "edit":
            return await ctx.edit(*args, **kwargs)

class View_Timeout(discord.ui.View):
    def __init__(self, slash, timeout):
        self.slash = slash
        super().__init__(timeout=timeout)
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await response(self.slash, "edit", self.message, view = self)

class ButtonItem(discord.ui.Button):
    """Create a basic button.
    
    Function must look like:
        1: :code:`function(self, self2, interaction, arg)`
            2: :code:`do stuff here`
            3: :code:`return arg`"""
    def __init__(self, self2, emoji, function, arg):
        self.self2 = self2
        self.function = function
        self.arg = arg
        super().__init__(emoji=emoji, style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        self.arg = await self.function(self.self2, self, interaction, self.arg)

class DropdownItem(discord.ui.Select):
    """Create a basic dropdown menu.
    
    Function must look like:
        1: :code:`function(self, self2, interaction, arg)`
            2: :code:`do stuff here`
            3: :code:`return arg`"""
    def __init__(self, self2, placeholder, min, max, selects, function, arg):
        self.self2 = self2
        self.function = function
        self.arg = arg
        options = []
        for x in selects:
            options.append(discord.SelectOption(label=x))
        super().__init__(placeholder=placeholder, min_values=min, max_values=max, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.arg = await self.function(self.self2, self, interaction, self.arg)
