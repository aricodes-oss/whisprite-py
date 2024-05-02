from twitchio.ext import commands
from twitchio import PartialUser
from peewee import IntegrityError

from whisprite.db.models.channels import Channel


class ChannelsMixin:
    """
    Adds support to the bot class for managing channels to join
    """

    @commands.command(name="join", aliases=["joinchannel"])
    async def join_command(
        self: commands.Bot,
        ctx: commands.Context,
        user: PartialUser,
    ) -> None:
        if not ctx.author.is_broadcaster:
            return await ctx.send("Nooooooope.")

        try:
            Channel.create(username=user.name)
            await self.join_channels([user.name])
            return await ctx.send(f"Successfully joined channel {user.name}")
        except IntegrityError:
            return await ctx.send("We're already in their chat!")

    @commands.command(name="leave", aliases=["leavechannel", "part"])
    async def leave_command(
        self: commands.Bot,
        ctx: commands.Context,
        user: PartialUser,
    ) -> None:
        if not ctx.author.is_broadcaster:
            return await ctx.send("Still nope!")

        if not Channel.select().where(Channel.username == user.name).count():
            return await ctx.send("We're not in their channel, dumbass")

        Channel.delete().where(Channel.username == user.name).execute()
        await self.part_channels([user.name])
        await ctx.send(f"Successfully left channel {user.name}")
