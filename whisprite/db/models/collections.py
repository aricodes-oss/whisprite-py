from peewee import CharField, ForeignKeyField, fn, DateTimeField
from twitchio.ext.commands import Bot, Command, Context

from whisprite.utils import pluralizer
from .base import BaseModel
from .types import CommandMapping


class Collection(BaseModel):
    """
    Represents a list of items that we keep track of.
    """

    name = CharField(unique=True)

    @property
    def has_entries(self) -> bool:
        return self.select().join(CollectionEntry).count() >= 1

    @property
    def singular(self) -> str:
        return pluralizer.singular(self.name)

    @property
    def plural(self) -> str:
        return pluralizer.plural(self.name)

    def mount_handlers(self, bot: Bot) -> None:
        c = self  # Shorthand, am lazy

        # Creating as closures to avoid polluting the model namespace
        async def new_handler(ctx: Context, content: str) -> None:
            if not ctx.author.is_mod:
                return await ctx.reply("No!")

            CollectionEntry.create(collection=c, author=ctx.author.id, value=content)
            await ctx.send(f"Successfully added new {c.singular}: {content}")

        async def find_handler(ctx: Context) -> None:
            if not c.has_entries:
                return await ctx.send(f"We don't have any {c.plural} yet :(")

            entry = (
                CollectionEntry.select()
                .where(CollectionEntry.collection == self)
                .order_by(fn.Random())
                .limit(1)
                .get()
            )
            author = (await bot.fetch_users(ids=[entry.author]))[0].display_name
            await ctx.send(f"{entry.value} (submitted by {author})")

        async def del_handler(ctx: Context, content: str) -> None:
            if not ctx.author.is_mod:
                await ctx.reply("Uh...no.")
                return

            rows_deleted = (
                CollectionEntry.delete()
                .where(CollectionEntry.value == content, CollectionEntry.collection == c)
                .execute()
            )
            if not rows_deleted:
                await ctx.send("No entry found for that query!")
                return

            await ctx.send(f"Deleted {rows_deleted} {c.singular} matching {content}")

        mapping: CommandMapping = [
            (
                f"new{c.singular}",
                new_handler,
                {"aliases": [f"add{c.singular}", f"create{c.singular}"]},
            ),
            (
                c.singular,
                find_handler,
                {"aliases": [f"find{c.singular}", c.plural, f"random{c.singular}"]},
            ),
            (
                f"delete{c.singular}",
                del_handler,
                {"aliases": [f"del{c.singular}", f"rm{c.singular}"]},
            ),
        ]

        for name, handler, *rest in mapping:
            kwargs = {}
            if len(rest):
                kwargs = rest[0]

            bot.add_command(Command(name, handler, **kwargs))


class CollectionEntry(BaseModel):
    """
    Represents an entry in a collection
    """

    collection = ForeignKeyField(Collection, backref="entries")
    value = CharField()
    author = CharField()
    created_at = DateTimeField(null=True)
