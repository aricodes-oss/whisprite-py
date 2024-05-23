from asyncio import sleep

from twitchio.ext import commands
from peewee import IntegrityError, fn

from whisprite.db.models.commands import UserCommand as Command, CommandAlias
from .counters import COUNT_TOKEN


class CommandsMixin:
    """
    Adds suppot to the bot class for managing collections,
    such as quotes and horror movie rules
    """

    @commands.command(
        name="newcommand",
        aliases=["mkcommand", "addcommand", "newcmd", "mkcmd", "addcmd"],
    )
    async def new_command(
        self: commands.Bot,
        ctx: commands.Context,
        name: str,
        *,
        content: str,
    ) -> None:
        if not ctx.author.is_mod:
            return await ctx.send("Nada.")

        name = name.lower()

        if Command.select().where(fn.LOWER(Command.name) == name).count():
            return await ctx.send("We already have that command!")

        if COUNT_TOKEN in content:
            return await ctx.send(f"Try !newcounter {name} instead")

        try:
            inst = Command.create(name=name, content=content)
            self.load_user_command(inst)
            await ctx.send(f"Created a command named {name}")
        except IntegrityError as e:
            await ctx.send(f"Error creating command {name}! [{str(e)}]")

    @commands.command(name="delcommand", aliases=["rmcommand", "delcmd", "rmcmd"])
    async def delete_command(self, ctx: commands.Context, name: str) -> None:
        if not ctx.author.is_mod:
            await ctx.send(f"Successfully deleted command {name}!")
            await sleep(3.5)
            return await ctx.send("Nah, not really. Good try though!")

        name = name.lower()

        inst = None

        try:
            # Try to find a command first
            inst = Command.select().where(fn.LOWER(Command.name) == name).get()
        except Exception:
            # If not, look up by alias
            try:
                inst = (
                    CommandAlias.select()
                    .where(fn.LOWER(CommandAlias.name) == name)
                    .get()
                    .command
                )
            except Exception:
                return await ctx.send(f"No command found for name {name}")

        inst.delete_instance(recursive=True)
        self.remove_command(name)
        await ctx.send(f"Successfully deleted command {name}")

    @commands.command(name="addalias", aliases=["newalias", "mkalias"])
    async def new_alias(
        self: commands.Bot, ctx: commands.Context, base_name: str, name: str
    ) -> None:
        if not ctx.author.is_mod:
            return await ctx.send("Sure! (sarcastic)")

        base_name = base_name.lower()
        name = name.lower()

        cmd = self.get_command(base_name)
        if cmd is None:
            return await ctx.send(f"No command found for name {name}")

        try:
            alias = CommandAlias.create(command=cmd, name=name)
            self.load_alias(alias)
            await ctx.send(f"Added alias {name} to command {cmd.name}")
        except Exception as e:
            return await ctx.send(f"Failed to create alias {name} for {base_name}: {e}")

    def load_user_commands(self):
        for cmd in Command.select():
            self.load_user_command(cmd)

    def load_user_command(self, cmd: Command):
        cmd.mount_handlers(self)

    def load_aliases(self):
        for alias in CommandAlias.select():
            self.load_alias(alias)

    def load_alias(self, alias: CommandAlias):
        cmd = self.get_command(alias.target)
        if cmd is None:
            return

        if cmd.aliases is None:
            cmd.aliases = []

        cmd.aliases.append(alias.name)
        self.remove_command(cmd.name)
        self.add_command(cmd)
