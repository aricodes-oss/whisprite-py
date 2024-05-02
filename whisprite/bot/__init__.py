from twitchio.ext import commands
from twitchio.message import Message

import inspect

from .collections import CollectionsMixin
from .counters import CountersMixin
from .channels import ChannelsMixin

from whisprite.db.models.channels import Channel
from whisprite.utils import pluralizer


class Bot(commands.Bot, CollectionsMixin, CountersMixin, ChannelsMixin):
    async def event_ready(self) -> None:
        # Load all of our model commands on startup, with names like
        # load_collections() or load_commands()
        for name, func in inspect.getmembers(self, inspect.ismethod):
            if name.startswith("load_") and pluralizer.isPlural(name):
                func()

        await self.join_channels([c.username for c in Channel.select()])
        print("Ret-2-go!")

    async def event_message(self, message: Message) -> None:
        # Ignore messages that we sent, to avoid recursion
        if message.echo:
            return

        print(f"RCV [{message.content}]")
        await self.handle_commands(message)

    async def event_command_error(self, context: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.BadArgument):
            return await context.send(error.message)

        await context.send(str(error))

    @commands.command()
    async def hello(self, ctx: commands.Context) -> None:
        await ctx.send(f"Hello {ctx.author.display_name}!")
