from twitchio.ext import commands
from peewee import IntegrityError, fn

from whisprite.db.models.counters import Counter

COUNT_TOKEN = "{count}"


class CountersMixin:
    """
    Adds support to the bot class for managing counters,
    such as vore/bird dickery/Falc calling himself daddy
    """

    @commands.command(
        name="newcounter",
        aliases=["mkcounter", "addcounter", "newcount", "mkcount", "addcount"],
    )
    async def new_counter(
        self: commands.Bot, ctx: commands.Context, name: str, *, text: str
    ) -> None:
        if not ctx.author.is_mod:
            return await ctx.send("NO!")

        name = name.lower()

        if COUNT_TOKEN not in text:
            raise commands.BadArgument(f"Missing {COUNT_TOKEN} in counter description!")

        try:
            inst = Counter.create(name=name, text=text)
            self.load_counter(inst)
            await ctx.send(f"Created a counter named {name}")
        except IntegrityError as e:
            await ctx.send(f"We already have a counter named {name}! [{str(e)}]")

    @commands.command(name="delcounter", aliases=["rmcounter"])
    async def del_counter(self: commands.Bot, ctx: commands.Context, name: str) -> None:
        if not ctx.author.is_mod:
            return await ctx.send("Seriously? No!")

        name = name.lower()

        rows_affected = Counter.delete().where(fn.LOWER(Counter.name) == name).execute()
        if not rows_affected:
            return await ctx.send("No matching counter found!")

        await ctx.send(f"Successfully deleted counter {name}")

    def load_counters(self) -> None:
        for counter in Counter.select():
            self.load_counter(counter)

    def load_counter(self, counter: Counter) -> None:
        counter.mount_handlers(self)
