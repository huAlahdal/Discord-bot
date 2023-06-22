from random import choice, randint
from typing import Optional
from aiohttp import request
from discord import Member, Embed
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import BadArgument
from discord.ext.commands import command, cooldown


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="hello", aliases=["hi"])
    @cooldown(1, 60, BucketType.user)
    async def say_hello(self, ctx):
        await ctx.send(f"{choice(('Hello', 'Hi', 'Hey', 'Whats up', 'Sup'))} {ctx.author.mention}!")


    @command(name="dice", aliases=["roll"])
    @cooldown(1, 60, BucketType.user)
    async def roll_dice(self, ctx, die_string: str):
        dice, value = (int(term) for term in die_string.split("d"))

        if dice <=25:
            rolls = [randint(1, value) for i in range(dice)]
            await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")
        else:
            await ctx.send("I can't roll that many dice. Please try a lower number")
    
    @command(name="memes", aliases=["meme"])
    @cooldown(3, 60, BucketType.user)
    async def random_meme(self, ctx):
        memes_url = "https://meme-api.herokuapp.com/gimme/memes"

        async with request("GET", memes_url, headers={}) as response:
            if response.status == 200:
                data = await response.json()
                embed = Embed(colour=ctx.author.colour)
                embed.set_image(url=data["url"])
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"API returned a {response.status} status.")

    @command(name="slap", aliases=["hit"])
    async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = "for no reason"):
	    await ctx.send(f"{ctx.author.display_name} slapped {member.mention} {reason}!")

    @slap_member.error
    async def slap_member_error(self, ctx, exc):
	    if isinstance(exc, BadArgument):
		    await ctx.send("I can't find that member.")

    @command(name="echo", aliases=["say"])
    @cooldown(1, 30, BucketType.user)
    async def echo_message(self, ctx, *, message):
        await ctx.message.delete()
        await ctx.send(message)
        
        
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")

def setup(bot):
    bot.add_cog(Fun(bot))