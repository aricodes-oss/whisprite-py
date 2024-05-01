from peewee import CharField, ForeignKeyField
from playhouse.hybrid import hybrid_property
from twitchio.ext.commands import Bot, Command, Context

from .base import BaseModel
from .types import CommandMapping


class Counter(BaseModel):
    """
    Represents a counter that we can increment
    """

    name = CharField(unique=True)
    text = CharField(max_length=400)

    @hybrid_property
    def value(self) -> int:
        return self.ticks.select().count()

    def mount_handlers(self, bot: Bot) -> None:
        c = self  # Shorthand, am lazy

        # Creating as closures to avoid polluting the model namespace
        async def count_handle(ctx: Context) -> None:
            CounterTick.create(counter=c, author=ctx.author.id)

            await ctx.send(c.text.format(count=self.value))

        mapping: CommandMapping = [(c.name, count_handle)]
        for name, handler, *rest in mapping:
            kwargs = {}
            if len(rest):
                kwargs = rest[0]

            bot.add_command(Command(name, handler, **kwargs))


class CounterTick(BaseModel):
    author = CharField()
    counter = ForeignKeyField(Counter, backref="ticks")
