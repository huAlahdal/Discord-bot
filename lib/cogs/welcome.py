from discord.errors import Forbidden
from lib.bot import Ready
import discord
from discord.ext import commands
from discord.ext.commands import Cog
from ..db import db

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.welcome_channel = self.bot.get_channel(851992108540887040)
            self.goodbye_channel = self.bot.get_channel(853300436093763615)
            self.bot.cogs_ready.ready_up("welcome")

    @Cog.listener()
    async def on_member_join(self, member):
        db.execute("INSERT INTO exp (UserID) VALUES (?)", member.id)
        await self.welcome_channel.send(f"Welcome to **{member.guild.name}** {member.mention}! Head to <#850345058054307840> and say Hi.! & if you have any suggestions feel free to add it on <#853292240855105556>")

        try:
            await member.send(f"Welcome to **{member.guild.name}**! Enjoy your stay!")
        except Forbidden:
            pass

        # await member.add_roles(member.guild.get_role(850315648558432257))

    @Cog.listener()
    async def on_member_remove(self, member):
        db.execute("DELETE FROM exp WHERE UserID = ?", member.id)
        await self.goodbye_channel.send(F"{member.display_name} has left {member.guild.name}")

def setup(bot):
    bot.add_cog(Welcome(bot))
