from twitchio.ext.commands import Bot, Command, Context
from peewee import CharField, ForeignKeyField

from .base import BaseModel


class UserCommand(BaseModel):
    name = CharField(unique=True)
    content = CharField()

    def mount_handlers(self, bot: Bot) -> None:
        async def handler(ctx: Context) -> None:
            await ctx.send(self.content)

        bot.add_command(Command(self.name, handler))


# Not attached to the UserCommand
class CommandAlias(BaseModel):
    name = CharField(unique=True)
    target = CharField()
