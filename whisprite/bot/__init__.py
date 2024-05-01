from twitchio.ext import commands
from twitchio.message import Message

from .collections import CollectionsMixin
from .counters import CountersMixin


class Bot(commands.Bot, CollectionsMixin, CountersMixin):
    async def event_ready(self) -> None:
        self.load_collections()
        self.load_counters()

        # TODO: load from database or something
        await self.join_channels(["ariaverge"])
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
