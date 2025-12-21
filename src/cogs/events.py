import os
import sentry_sdk
import discord
from discord import app_commands
from discord.ext import commands
from rgbprint import gradient_print, Color

ANTI_DEBOUNCE_SECONDS = 15

class Events(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    async def cooldown_message(self, user_id, command_name) -> bool:
        key = f"cooldown:{user_id}:{command_name}"
        exists = self.bot.cache.get(key)
        if exists:
            return False
        self.bot.cache.set(key, "1", ex=ANTI_DEBOUNCE_SECONDS)
        return True

    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            if await self.cooldown_message(interaction.user.id, interaction.command.name):
                embed = discord.Embed(
                    title='Cooldown',
                    description=f'You must wait `{round(error.retry_after)}` seconds before using this command again.',
                    color=0xFFFFFF
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        elif isinstance(error, app_commands.CommandError):
            embed = discord.Embed(
                title="Error",
                description=f'{error}',
                color=0xFFFFFF
            )
            await interaction.author.send(embed=embed)
            sentry_sdk.capture_exception(error)
            raise error
        else:
            sentry_sdk.capture_exception(error)
            raise error

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        try:
            if isinstance(error, commands.CommandNotFound):
                embed = discord.Embed(
                    title="Search",
                    description=f"The command `{ctx.invoked_with}` was not found. Use `{self.bot.command_prefix}help` to see all commands",
                    color=0xFFFFFF
                )
                await ctx.send(embed=embed, delete_after=30)
            elif isinstance(error, commands.CommandOnCooldown):
                if await self.cooldown_message(ctx.author.id, ctx.command.name):
                    embed = discord.Embed(
                        title="Cooldown",
                        description=f"You must wait `{round(error.retry_after)}` seconds before using this command again.",
                        color=0xFFFFFF
                    )
                    await ctx.send(embed=embed, delete_after=30)
            elif isinstance(error, commands.MissingRequiredArgument):
                embed = discord.Embed(
                    title="Arguments",
                    description=f"Argument `{error.param.name}` is missing to execute the command.",
                    color=0xFFFFFF
                )
                await ctx.send(embed=embed, delete_after=30)
            elif isinstance(error, commands.NoPrivateMessage):
                embed = discord.Embed(
                    title="Guild",
                    description="This command can only be used in `guild` messages.",
                    color=0xFFFFFF
                )
                await ctx.send(embed=embed, delete_after=30)
            elif isinstance(error, commands.PrivateMessageOnly):
                embed = discord.Embed(
                    title="DM",
                    description="This command can only be used in `DM` messages.",
                    color=0xFFFFFF
                )
                await ctx.send(embed=embed, delete_after=30)
            elif isinstance(error, commands.BotMissingPermissions):
                embed = discord.Embed(
                    title="Permissions",
                    description=f"I don't have the permission `{error.missing_permissions}` to process the command.",
                    color=0xFFFFFF
                )
                await ctx.send(embed=embed, delete_after=30)
            elif isinstance(error, commands.NotOwner):
                embed = discord.Embed(
                    title="Restricted",
                    description="You `aren't` the owner of me.",
                    color=0xFFFFFF
                )
                await ctx.author.send(embed=embed, delete_after=30)
            elif isinstance(error, commands.CommandError):
                embed = discord.Embed(
                    title="Error",
                    description=f'{error}',
                    color=0xFFFFFF
                )
                await ctx.author.send(embed=embed)
                sentry_sdk.capture_exception(error)
                raise error
            else:
                sentry_sdk.capture_exception(error)
                raise error
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise e

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        gradient_print(f"Connected to gateway as {self.bot.user.name}#{self.bot.user.discriminator} ({self.bot.user.id})", start_color=Color.white, end_color=Color.blue)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.bot.user:
            return
        
        if self.bot.user in message.mentions:
            try:
                command = message.content[len(message.mentions[0].mention):].strip()

                if command:
                    content = f"{os.getenv('DISCORD_PREFIX')}{command}"
                    ctx = await self.bot.get_context(message)
                    ctx.message.content = content

                    await self.bot.invoke(ctx)  
            except Exception:
                pass
        
        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(Events(bot))
