from datetime import datetime, timedelta
from random import randint
from typing import Optional

from discord import Member, Embed, File
from discord.ext.commands import Cog
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions
from discord.ext.menus import MenuPages, ListPageSource
from PIL import Image, ImageDraw, ImageFont
from ..db import db
import aiohttp
import io

async def drawRank(member, rank, level, xp, final_xp):
    user_avatar_image = str(member.avatar_url_as(format='png', size=512))
    async with aiohttp.ClientSession() as session:
        async with session.get(user_avatar_image) as resp:
            avatar_bytes = io.BytesIO(await resp.read())
    
    background = Image.new("RGB", (1000, 240))
    logo = Image.open(avatar_bytes).resize((200, 200))
    bigsize = (logo.size[0] * 3, logo.size[1] * 3)
    mask = Image.new("L", bigsize, 0)


    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, 255)


    # Black Circle
    draw.ellipse((140 * 3, 140 * 3, 189 * 3, 189 * 3), 0)

    mask = mask.resize(logo.size, Image.ANTIALIAS)
    logo.putalpha(mask)

    background.paste(logo, (20, 20), mask=logo)

    # # Black Circle
    draw = ImageDraw.Draw(background, "RGB")
    # draw.ellipse((160, 160, 208, 208), fill="#000")

    # Green Circle (Discord Status Colours)
    draw.ellipse((162, 162, 206, 206), fill="#43B581")

    # Working with Fonts
    big_font = ImageFont.truetype("arial.ttf", 60)
    medium_font = ImageFont.truetype("arial.ttf", 40)
    small_font = ImageFont.truetype("arial.ttf", 30)

    # Placing Right Upper Part
    text_size = draw.textsize(str(level), font=big_font)
    offset_x = 1000 - 15 - text_size[0]
    offset_y = 10
    draw.text((offset_x, offset_y), str(level), font=big_font, fill="#11ebf2")

    text_size = draw.textsize("LEVEL", font=small_font)
    offset_x -= text_size[0] + 5
    draw.text((offset_x, offset_y + 27), "LEVEL", font=small_font, fill="#11ebf2")

    text_size = draw.textsize(f"#{rank}", font=big_font)
    offset_x -= text_size[0] + 15
    draw.text((offset_x, offset_y), f"#{rank}", font=big_font, fill="#fff")

    text_size = draw.textsize("RANK", font=small_font)
    offset_x -= text_size[0] + 5
    draw.text((offset_x, offset_y + 27), "RANK", font=small_font, fill="#fff")

    # Empty Progress Bar (Gray)
    bar_offset_x = 320
    bar_offset_y = 160
    bar_offset_x_1 = 950
    bar_offset_y_1 = 200
    circle_size = bar_offset_y_1 - bar_offset_y  # Diameter

    # Progress Bar
    draw.rectangle((bar_offset_x, bar_offset_y, bar_offset_x_1, bar_offset_y_1), fill="#727175")

    # Left Circle
    draw.ellipse(
        (bar_offset_x - circle_size // 2, bar_offset_y, bar_offset_x + circle_size // 2, bar_offset_y_1), fill="#727175"
    )

    # Right Circle
    draw.ellipse(
        (bar_offset_x_1 - circle_size // 2, bar_offset_y, bar_offset_x_1 + circle_size // 2, bar_offset_y_1), fill="#727175"
    )


    # Filling Bar
    bar_length = bar_offset_x_1 - bar_offset_x
    progress = (final_xp - xp) * 100 / final_xp
    progress = 100 - progress
    progress_bar_length = round(bar_length * progress / 100)
    bar_offset_x_1 = bar_offset_x + progress_bar_length


    # Progress Bar
    draw.rectangle((bar_offset_x, bar_offset_y, bar_offset_x_1, bar_offset_y_1), fill="#11ebf2")

    # Left Circle
    draw.ellipse(
        (bar_offset_x - circle_size // 2, bar_offset_y, bar_offset_x + circle_size // 2, bar_offset_y_1), fill="#11ebf2"
    )

    # Right Circle
    draw.ellipse(
        (bar_offset_x_1 - circle_size // 2, bar_offset_y, bar_offset_x_1 + circle_size // 2, bar_offset_y_1), fill="#11ebf2"
    )

    text_size = draw.textsize(f"/ {final_xp} XP", font=small_font)

    offset_x = 950 - text_size[0]
    offset_y = bar_offset_y - text_size[1] - 10

    draw.text((offset_x, offset_y), f"/ {final_xp:,} XP", font=small_font, fill="#727175")

    text_size = draw.textsize(f"{xp:,}", font=small_font)
    offset_x -= text_size[0] + 8
    draw.text((offset_x, offset_y), f"{xp:,}", font=small_font, fill="#fff")


    # Blitting Name
    text_size = draw.textsize(member.name, font=medium_font)

    offset_x = bar_offset_x
    offset_y = bar_offset_y - text_size[1] - 5
    draw.text((offset_x, offset_y), member.name, font=medium_font, fill="#fff")

    # Discriminator
    offset_x += text_size[0] + 5
    offset_y += 10

    draw.text((offset_x, offset_y), f"#{member.discriminator}", font=small_font, fill="#727175")
    bytes = io.BytesIO()
    background.save(bytes, 'PNG')
    bytes.seek(0)
    return bytes


class HelpMenu(ListPageSource):
	def __init__(self, ctx, data):
		self.ctx = ctx

		super().__init__(data, per_page=10)

	async def write_page(self, menu, offset, fields=[]):
		len_data = len(self.entries)

		embed = Embed(title="XP Leaderboard",
					  colour=self.ctx.author.colour)
		embed.set_thumbnail(url=self.ctx.guild.icon_url)
		embed.set_footer(text=f"{offset:,} - {min(len_data, offset+self.per_page-1):,} of {len_data:,} members.")

		for name, value in fields:
			embed.add_field(name=name, value=value, inline=False)

		return embed

	async def format_page(self, menu, entries):
		offset = (menu.current_page*self.per_page) + 1

		fields = []
		table = ("\n".join(f"{idx+offset}. {self.ctx.bot.guild.get_member(entry[0]).display_name} (XP: {entry[1]} | Level: {entry[2]})"
				for idx, entry in enumerate(entries)))

		fields.append(("Ranks", table))

		return await self.write_page(menu, offset, fields)

class Exp(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def process_xp(self, message):
        xp, lvl, xplock = db.record("SELECT XP, Level, XPLock FROM exp WHERE UserID = ?", message.author.id)

        if datetime.utcnow() > datetime.fromisoformat(xplock):
            await self.add_xp(message, xp, lvl)

    async def add_xp(self, message, xp, lvl):
        xp_to_add = randint(25, 85)
        new_lvl = int((xp+xp_to_add)//1000)

        db.execute("UPDATE exp SET XP = XP + ?, Level = ?, XPLock = ? WHERE UserID = ?",
                    xp_to_add, new_lvl, (datetime.utcnow()+timedelta(seconds=30)).isoformat(), message.author.id)

        if new_lvl > lvl:
            await self.levelup_channel.send(f"Congrats {message.author.mention} - you reached level {new_lvl:,}!")


    @command(name="level")
    async def display_level(self, ctx, target: Optional[Member]):
        target = target or ctx.author

        xp, lvl = db.record("SELECT XP, Level FROM exp WHERE UserID = ?", target.id) or (None, None)
        ids = db.column("SELECT UserID FROM exp ORDER BY XP DESC")
        try:
            rank = ids.index(target.id)+1
        except ValueError:
            await ctx.send("That member is not tracked by the experience system.")

        if lvl is not None:
            bytes = await drawRank(target, rank, lvl, xp, (lvl+1)*1000)
            file = File(bytes, 'rank.png')
            await ctx.send(file=file)

        else:
            await ctx.send("That member is not tracked by the experience system.")

    @command(name="leaderboard", aliases=["lb"])
    async def display_leaderboard(self, ctx):
        records = db.records("SELECT UserID, XP, Level FROM exp ORDER BY XP DESC")

        menu = MenuPages(source=HelpMenu(ctx, records),
                            clear_reactions_after=True,
                            timeout=60.0)
        await menu.start(ctx)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("exp")
            self.levelup_channel = self.bot.get_channel(853708711846608917)

    @Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            await self.process_xp(message)

def setup(bot):
    bot.add_cog(Exp(bot))
