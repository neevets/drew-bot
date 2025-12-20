import sentry_sdk
import discord
from discord import app_commands
from discord.ext import commands
from upstash_redis import Redis
from rgbprint import gradient_print, Color

ANTI_DEBOUNCE_SECONDS = 10

class Events(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.cache: Redis = bot.cache

    async def cooldown_message(self, user_id, command_name) -> bool:
        key = f"cooldown:{user_id}:{command_name}"
        exists = self.cache.get(key)
        if exists:
            return False
        self.cache.set(key, "1", ex=ANTI_DEBOUNCE_SECONDS)
        return True
    
    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            embed = discord.Embed(
                title='Cooldown',
                description=f'You must wait `{round(error.retry_after)}` seconds before using this command again.',
                color=0xFFFFFF
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        #elif isinstance(error, app_commands.CommandError):
            #sentry_sdk.capture_exception(error)
            #raise error

        else:
            sentry_sdk.capture_exception(error)
            raise error

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            if await self.cooldown_message(ctx.author.id, ctx.command.name):
                embed = discord.Embed(
                    title="Cooldown",
                    description=f"You must wait `{round(error.retry_after)}` seconds before using this command again.",
                    color=0xFFFFFF
                )
                await ctx.send(embed=embed, delete_after=30)

        elif isinstance(error, commands.CommandError):
            sentry_sdk.capture_exception(error)
            raise error

        else:
            sentry_sdk.capture_exception(error)
            raise error

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        gradient_print(f"Connected to gateway as {self.bot.user.name}#{self.bot.user.discriminator} ({self.bot.user.id})", start_color=Color.white, end_color=Color.blue)

async def setup(bot):
    await bot.add_cog(Events(bot))
