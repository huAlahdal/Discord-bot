from lib.bot import bot

VERSION = "0.5 beta"

bot.run(VERSION)

# import discord
# from discord import client
# from discord import member
# from discord.ext import commands

# intents = discord.Intents.default()
# intents.members = True

# client = commands.Bot(command_prefix="$", intents=intents)

# @client.event
# async def on_ready():
#     print("Bot is Ready")

# @client.event
# async def on_member_update(before, after):
#     hasRole = "None"
#     for roles in after.roles:
#         if "hYsteria" in roles.name:
#             hasRole = "hYsteria"
#             break
#         else:
#             hasRole = "None"

#     if "hYsteria" in hasRole and (before.nick == None or "hYs" not in before.nick):
#         await after.edit(nick="hYs " + str(before.name))
#     elif "hYsteria" not in hasRole and (before.nick != None and "hYs" in before.nick):
#         await after.edit(nick=str(before.name))
        
#     # if len(before.roles) < len(after.roles):
#     #     # The user has gained a new role, so lets find out which one
#     #     newRole = next(role for role in after.roles if role not in before.roles)
#     #     if newRole.name == "hYsteria":
#     #         await after.edit(nick="hYs " + str(before.name)) 

# @client.command()
# async def hello(ctx):
#     await ctx.send("Hi")

# client.run("ODUwMzg5MTI4MTcyMTQyNjEy.YLpAlw.zFEaou2Wval3KiIUpaRenhqe6LY")