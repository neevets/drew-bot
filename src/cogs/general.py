import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

import asyncpg
import redis
import time
import psutil

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Displays a list of available commands")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
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

    @app_commands.command(name="ping", description="Check the bot's latency")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild.id, i.user.id))
    async def ping(self, interaction: discord.Interaction):
        websocket_latency = round(self.bot.latency * 1000)

        try:
            start = time.perf_counter()
            await self.bot.http.request(
                discord.http.Route("GET", "/users/@me")
            )
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
            title="Latency",
            color=0xFFFFFF
        )

        embed.add_field(name="WebSocket", value=f"{websocket_latency}ms", inline=True)
        embed.add_field(name="REST", value=f"{rest_latency}ms", inline=True)
        embed.add_field(name="API", value=f"{api_latency}ms", inline=True)
        embed.add_field(name="Database", value=f"{db_latency}ms", inline=True)
        embed.add_field(name="Cache", value=f"{cache_latency}ms", inline=True)

        await interaction.response.send_message(embed=embed)

    @commands.command(name="ping", aliases=["latency", "rtt"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ping(self, ctx):
        websocket_latency = round(self.bot.latency * 1000)

        try:
            start = time.perf_counter()
            await self.bot.http.request(
                discord.http.Route("GET", "/users/@me")
            )
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

        embed.add_field(name="WebSocket", value=f"{websocket_latency}ms", inline=True)
        embed.add_field(name="REST", value=f"{rest_latency}ms", inline=True)
        embed.add_field(name="API", value=f"{api_latency}ms", inline=True)
        embed.add_field(name="Database", value=f"{db_latency}ms", inline=True)
        embed.add_field(name="Cache", value=f"{cache_latency}ms", inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="about", aliases=["stats"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def about(self, ctx):
        disk_usage = psutil.disk_usage('/')
        cpu_usage = psutil.cpu_percent(interval=1)
        ram_usage = psutil.virtual_memory().percent

        await ctx.send(
            f"Disk Usage: {disk_usage.percent}%\n"
            f"CPU Usage: {cpu_usage}%\n"
            f"RAM Usage: {ram_usage}%"
        )

async def setup(bot):
    await bot.add_cog(General(bot))
