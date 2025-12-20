import sys
import psutil
import time
import aiohttp
import asyncpg
import discord
from discord import app_commands
from discord.ext import commands
from upstash_redis import Redis

class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Displays a list of available slash commands")
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.user.id)
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Commands",
            description="Here's a list of all available commands:",
            color=0xFFFFFF
        )
        
        for command in self.bot.tree.get_commands():
            if command.description:
                embed.add_field(
                    name=f"/{command.name}",
                    value=command.description,
                    inline=False
                )
        embed.set_footer(
            text="Use each command as shown, or type `help [command]` for more details."
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.command(name="help", description="Displays a list of available prefix commands")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_cmd(self, ctx: commands.Context):
        embed = discord.Embed(
            title="Commands",
            description="Here's a list of all available prefix commands:",
            color=0xFFFFFF
        )

        for command in self.bot.commands:
            if not command.hidden:
                description = command.description
                embed.add_field(
                    name=f"{ctx.prefix}{command.name}",
                    value=description,
                    inline=False
                )

        embed.set_footer(
            text="Use each command as shown, or type `help [command]` for more details."
        )

        await ctx.send(embed=embed)

    @app_commands.command(name="ping", description="Check the bot's latency")
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.user.id)
    async def ping(self, interaction: discord.Interaction):
        start = time.perf_counter()

        await interaction.response.send_message(
            embed=discord.Embed(
                description="Pinging…",
                color=0xFFFFFF
            ),
            ephemeral=True
        )

        rtt_latency = round((time.perf_counter() - start) * 1000)

        websocket_latency = round(self.bot.latency * 1000)

        try:
            start = time.perf_counter()
            async with self.bot.http_session.get(
                "https://discord.com/api/v10/users/@me",
                headers={"Authorization": f"Bot {self.bot.http.token}"}
            ):
                pass
            rest_latency = round((time.perf_counter() - start) * 1000)
        except Exception:
            rest_latency = "Error"

        try:
            start = time.perf_counter()
            async with self.bot.http_session.get(
                "https://api.neevets.website",
                timeout=aiohttp.ClientTimeout(total=5)
            ):
                pass
            api_latency = round((time.perf_counter() - start) * 1000)
        except Exception:
            api_latency = "Error"

        try:
            start = time.perf_counter()
            await self.bot.db.fetch("SELECT 1")
            db_latency = round((time.perf_counter() - start) * 1000)
        except Exception:
            db_latency = "Error"

        try:
            start = time.perf_counter()
            self.bot.cache.ping()
            cache_latency = round((time.perf_counter() - start) * 1000)
        except Exception:
            cache_latency = "Error"

        embed = discord.Embed(
            color=0xFFFFFF
        )

        embed.add_field(
            name="RTT",
            value=f"{rtt_latency}ms",
            inline=True
        )
        embed.add_field(
            name="WebSocket",
            value=f"{websocket_latency}ms",
            inline=True
        )
        embed.add_field(
            name="REST",
            value=f"{rest_latency}ms",
            inline=True
        )
        embed.add_field(
            name="API",
            value=f"{api_latency}ms",
            inline=True
        )
        embed.add_field(
            name="Database",
            value=f"{db_latency}ms",
            inline=True
        )
        embed.add_field(
            name="Cache",
            value=f"{cache_latency}ms",
            inline=True
        )

        await interaction.edit_original_response(embed=embed)

    @commands.command(name="ping", aliases=["latency", "rtt"], description="Check the bot's latency")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def ping_cmd(self, ctx: commands.Context):
        start = time.perf_counter()

        embed = discord.Embed(
            description="Pinging…",
            color=0xFFFFFF
        )

        message = await ctx.send(embed=embed)

        rtt_latency = round((time.perf_counter() - start) * 1000)

        websocket_latency = round(self.bot.latency * 1000)

        try:
            start = time.perf_counter()
            async with self.bot.http_session.get(
                "https://discord.com/api/v10/users/@me",
                headers={"Authorization": f"Bot {self.bot.http.token}"}
            ):
                pass
            rest_latency = round((time.perf_counter() - start) * 1000)
        except Exception:
            rest_latency = "Error"

        try:
            start = time.perf_counter()
            async with self.bot.http_session.get(
                "https://api.neevets.website",
                timeout=aiohttp.ClientTimeout(total=5)
            ):
                pass
            api_latency = round((time.perf_counter() - start) * 1000)
        except Exception:
            api_latency = "Error"

        try:
            start = time.perf_counter()
            await self.bot.db.fetch("SELECT 1")
            db_latency = round((time.perf_counter() - start) * 1000)
        except Exception:
            db_latency = "Error"

        try:
            start = time.perf_counter()
            self.bot.cache.ping()
            cache_latency = round((time.perf_counter() - start) * 1000)
        except Exception:
            cache_latency = "Error"

        embed = discord.Embed(
            color=0xFFFFFF
        )

        embed.add_field(
            name="RTT",
            value=f"{rtt_latency}ms",
            inline=True
        )
        embed.add_field(
            name="WebSocket",
            value=f"{websocket_latency}ms",
            inline=True
        )
        embed.add_field(
            name="REST",
            value=f"{rest_latency}ms",
            inline=True
        )
        embed.add_field(
            name="API",
            value=f"{api_latency}ms",
            inline=True
        )
        embed.add_field(
            name="Database",
            value=f"{db_latency}ms",
            inline=True
        )
        embed.add_field(
            name="Cache",
            value=f"{cache_latency}ms",
            inline=True
        )

        await message.edit(content=None, embed=embed)

    @app_commands.command(name="about", description="Shows bot and system statistics")
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.user.id)
    async def about(self, interaction: discord.Interaction):
        python_version = sys.version.split(' ')[0]
        discord_version = discord.__version__
        
        ram_total = round(psutil.virtual_memory().total / (1024 ** 3))
        ram_usage = round(psutil.virtual_memory().used / (1024 ** 3))
        cpu_percent = round(psutil.cpu_percent(interval=0.1))
        disk_total = round(psutil.disk_usage('/').total / (1024 ** 3))
        disk_usage = round(psutil.disk_usage('/').used / (1024 ** 3))

        embed = discord.Embed(
            color=0xFFFFFF
        )

        embed.add_field(
            name='Version',
            value=f'python: {python_version}\ndiscord: {discord_version}',
            inline=False
        )
        embed.add_field(
            name='RAM',
            value=f'total: {ram_total} GB\nusage: {ram_usage} GB',
            inline=False
        )
        embed.add_field(
            name='CPU',
            value=f'usage: {cpu_percent}%',
            inline=False
        )
        embed.add_field(
            name='Disk',
            value=f'total: {disk_total} GB\nusage: {disk_usage} GB',
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.command(name="about", aliases=["stats", "stat"], description="Shows bot and system statistics")
    @commands.cooldown(1, 10, commands.BucketType.user)       
    async def about_cmd(self, ctx):
        python_version = sys.version.split(' ')[0]
        discord_version = discord.__version__
        
        ram_total = round(psutil.virtual_memory().total / (1024 ** 3))
        ram_usage = round(psutil.virtual_memory().used / (1024 ** 3))
        cpu_percent = round(psutil.cpu_percent(interval=0.1))
        disk_total = round(psutil.disk_usage('/').total / (1024 ** 3))
        disk_usage = round(psutil.disk_usage('/').used / (1024 ** 3))

        embed = discord.Embed(
            color=0xFFFFFF
        )

        embed.add_field(
            name='Version',
            value=f'python: {python_version}\ndiscord: {discord_version}',
            inline=False
        )
        embed.add_field(
            name='RAM',
            value=f'total: {ram_total} GB\nusage: {ram_usage} GB',
            inline=False
        )
        embed.add_field(
            name='CPU',
            value=f'usage: {cpu_percent}%',
            inline=False
        )
        embed.add_field(
            name='Disk',
            value=f'total: {disk_total} GB\nusage: {disk_usage} GB',
            inline=False
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))
