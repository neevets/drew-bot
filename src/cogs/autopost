import discord
from discord import app_commands
from discord.ext import commands

class Autopost(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command(name="autopfp-start", description="...")
    @app_commands.describe(channel="...")
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.user.id)
    async def autopfp_start(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        
        embed = discord.Embed(
            color=0xFFFFFF
        )
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Autopost(bot))
