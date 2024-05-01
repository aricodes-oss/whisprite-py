from twitchio.ext import commands
from peewee import IntegrityError

from whisprite.db.models.collections import Collection
from whisprite.utils import pluralizer


class CollectionsMixin:
    """
    Adds support to the bot class for managing collections,
    such as quotes and horror movie rules
    """

    @commands.command(
        name="newcollection",
        aliases=["mkcollection", "addcollection", "newlist", "mklist", "addlist"],
    )
    async def new_collection(self: commands.Bot, ctx: commands.Context, name: str) -> None:
        if not ctx.author.is_mod:
            return await ctx.send("No.")

        name = pluralizer.singular(name.lower())

        try:
            inst = Collection.create(name=name)
            self.load_collection(inst)
            await ctx.send(f"Created a collection of {inst.plural}")
        except IntegrityError:
            await ctx.send(f"We already have a collection of {pluralizer.plural(name)}!")

    @commands.command(name="collections", aliases=["listcollections", "lists"])
    async def find_collection(
        self: commands.Bot, ctx: commands.Context, name: str | None
    ) -> None:
        if name is None:
            collections = ", ".join([c.name for c in Collection.select()])
            return await ctx.send(f"We have the following collections: {collections}")

    @commands.command(name="delcollection", aliases=["rmcollection", "dellist", "rmlist"])
    async def del_collection(self: commands.Bot, ctx: commands.Context, name: str) -> None:
        if not ctx.author.is_mod:
            return await ctx.send("Nope.")

    def load_collections(self: commands.Bot) -> None:
        for collection in Collection.select():
            self.load_collection(collection)

    def load_collection(self: commands.Bot, collection: Collection) -> None:
        collection.mount_handlers(self)
