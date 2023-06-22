from datetime import datetime, timedelta
from random import choice
from discord import Embed
from discord.ext.commands import Cog
from discord.ext.commands import command, has_permissions
from ..db import db

numbers = ("1️⃣", "2⃣", "3⃣", "4⃣", "5⃣",
		   "6⃣", "7⃣", "8⃣", "9⃣", "🔟")

class Reactions(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.polls = []
    
    def stars_icon(sefl, stars):
        loop, y = [], 0
        for x in range(stars + 1):
            if y > 5:
                loop.append('\n')
                y=0 
            loop.append(':star: ')
            y=y+1
        return ''.join(loop)


    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.roles = {
                "valorant_logo": self.bot.guild.get_role(853378542610939935), # Red
                "rainbow6logo": self.bot.guild.get_role(853381763630891010), # Yellow
                "lollogo": self.bot.guild.get_role(853381044090175540), # Green
                "fortnite": self.bot.guild.get_role(853381851966996530), # Blue
                "dota2": self.bot.guild.get_role(853380653604143175), # Purple
                "csgologo": self.bot.guild.get_role(853381328962846770), # Black
                "callofdutymodernwarfare": self.bot.guild.get_role(853378816356646942), # Purple
                "apexlogo": self.bot.guild.get_role(853379684254220298), # Black
            }
            self.reaction_message = await self.bot.get_channel(853293346932129842).fetch_message(853375861964668988)
            self.starboard_channel = self.bot.get_channel(853444234336796672)
            self.bot.cogs_ready.ready_up("reactions")

    @command(name="createpoll", aliases=["mkpoll"])
    @has_permissions(manage_guild=True)
    async def create_poll(self, ctx, hours: float, question: str, *options):
        if len(options) > 10:
            await ctx.send("You can only supply a maximum of 10 options.")

        else:
            embed = Embed(title="Poll",
                            description=question,
                            colour=ctx.author.colour,
                            timestamp=datetime.utcnow())

            fields = [("Options", "\n".join([f"{numbers[idx]} {option}" for idx, option in enumerate(options)]), False),
                        ("Instructions", "React to cast a vote!", False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            message = await ctx.send(embed=embed)

            for emoji in numbers[:len(options)]:
                await message.add_reaction(emoji)

            self.polls.append((message.channel.id, message.id))

            self.bot.scheduler.add_job(self.complete_poll, "date", run_date=datetime.now()+timedelta(seconds=hours*3600),
                                        args=[message.channel.id, message.id])

    async def complete_poll(self, channel_id, message_id):
        message = await self.bot.get_channel(channel_id).fetch_message(message_id)

        most_voted = max(message.reactions, key=lambda r: r.count)

        await message.channel.send(f"The results are in and option {most_voted.emoji} was the most popular with {most_voted.count-1:,} votes!")
        self.polls.remove((message.channel.id, message.id))

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if self.bot.ready and payload.message_id == self.reaction_message.id:
            await payload.member.add_roles(self.roles[payload.emoji.name], reason="Game role reaction.")
        
        elif payload.message_id in (poll[1] for poll in self.polls):
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

            for reaction in message.reactions:
                if (not payload.member.bot
                    and payload.member in await reaction.users().flatten()
                    and reaction.emoji != payload.emoji.name):
                    await message.remove_reaction(reaction.emoji, payload.member)
        
        elif payload.emoji.name == "⭐":
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

            if not message.author.bot and payload.member.id != message.author.id:
                msg_id, stars = db.record("SELECT StarMessageID, Stars FROM starboard WHERE RootMessageID = ?",
                                            message.id) or (None, 0)

                staricon = self.stars_icon(stars)

                embed = Embed(title="Starred message",
                                colour=message.author.colour,
                                timestamp=datetime.utcnow())
                

                fields = [("Author", message.author.mention, False),
                            ("Content", message.content or "See attachment", False),
                            ("Stars", staricon, False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                if len(message.attachments):
                    embed.set_image(url=message.attachments[0].url)

                if not stars:
                    # star_message = await self.starboard_channel.send(embed=embed)
                    db.execute("INSERT INTO starboard (RootMessageID, StarMessageID) VALUES (?, ?)",
                                message.id, None)
                
                elif stars < 2:
                    db.execute("UPDATE starboard SET Stars = Stars + 1 WHERE RootMessageID = ?", message.id)

                elif stars >= 2:
                    try:
                        star_message = await self.starboard_channel.fetch_message(msg_id)
                    except:
                        star_message = await self.starboard_channel.send(embed=embed)
                        db.execute("UPDATE starboard SET StarMessageID = ? WHERE RootMessageID = ?", star_message.id, message.id)
                    await star_message.edit(embed=embed)
                    db.execute("UPDATE starboard SET Stars = Stars + 1 WHERE RootMessageID = ?", message.id)

            else:
                await message.remove_reaction(payload.emoji, payload.member)
    
    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if self.bot.ready and payload.message_id == self.reaction_message.id:
            member = self.bot.guild.get_member(payload.user_id)
            await member.remove_roles(self.roles[payload.emoji.name], reason="Game role reaction.")
        
        elif payload.emoji.name == "⭐":
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            db.execute("UPDATE starboard SET Stars = Stars - 1 WHERE RootMessageID = ?", message.id)


def setup(bot):
    bot.add_cog(Reactions(bot))
