
from io import BytesIO
import random
from datetime import datetime, timedelta, timezone
from dateutil.parser import parse as parse_date
from discord.ext import commands
import aiohttp
import discord

GARFIELD_URL = "https://www.gocomics.com/garfield/"
GARFIELD_TIMEZONE = timezone(offset=timedelta(hours=-5))
FIRST_COMIC_DATE = datetime(year=1978, month=6, day=19)


class GarfieldCommand(commands.Cog):
    """ Also made by garlicOS® """

    async def get_comic_url_by_date(self, year_month_day: str) -> str:
        """ Get the URL of a Garfield comic by date, formatted 'yyyy/mm/dd'. """
        url = GARFIELD_URL + year_month_day
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                html = await response.text()

        # Traverse the HTML extract the comic URL within a <picture> tag
        image_tag_beg = html.find('<picture class="item-comic-image">')
        image_tag_end = html.find("</picture>", image_tag_beg)
        src_beg = html.find('src="', image_tag_beg, image_tag_end)
        src_end = html.find('"', src_beg + 5, image_tag_end)
        return html[src_beg + 5 : src_end]


    async def load_file_from_url(self, url: str) -> BytesIO:
        """ Download a file and load it into memory as a BytesIO object. """
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return BytesIO(await response.read())


    def random_comic_date(self) -> datetime:
        """ Random date between today and the first Garfield comic. """
        days_range = datetime.now() - FIRST_COMIC_DATE
        random_day_since_first = random.randint(0, days_range.days)
        return FIRST_COMIC_DATE + timedelta(days=random_day_since_first)


    @commands.command(aliases=["garf", "dailygarfield"])
    async def garfield(self, ctx: commands.Context, *, comic_date_text: str=None) -> None:
        """
        Download a Garfield comic by date and post it to Discord.
        If no date given, download a random comic.
        Download today's with "today" or "now".
        """
        if comic_date_text is not None:
            comic_date_text = comic_date_text.lower()
            if comic_date_text in ("today", "now"):
                comic_date = datetime.now(tz=GARFIELD_TIMEZONE)
            elif comic_date_text == "yesterday":
                comic_date = datetime.now(tz=GARFIELD_TIMEZONE) - timedelta(days=1)
            elif comic_date_text == "tomorrow":
                comic_date = datetime.now(tz=GARFIELD_TIMEZONE) - timedelta(days=364)
            elif comic_date_text == "random":
                comic_date = self.random_comic_date()
            else:
                comic_date = parse_date(comic_date_text)
        else:
            comic_date = self.random_comic_date()

        year_month_day = comic_date.strftime("%Y/%m/%d")
        print(f"Fetching comic URL for {year_month_day}...")
        comic_url = await self.get_comic_url_by_date(year_month_day)

        print("Got comic URL:", comic_url)
        print("Downloading...")
        comic = await self.load_file_from_url(comic_url)

        print(f"Posting to {ctx.channel}...")
        await ctx.send(file=discord.File(
            fp=comic,
            filename=comic_date.strftime("%Y-%m-%d") + ".gif",
        ))


def setup(bot):
    bot.add_cog(GarfieldCommand())
