import discord
from discord.ext import commands

import asyncpg
import redis
import time
import psutil

class GeneralCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        bot_latency = round(self.bot.latency * 1000)

        start_time = time.time()
        try:
            await self.bot.db.fetch("SELECT 1")
            db_latency = round((time.time() - start_time) * 1000)
        except Exception as e:
            db_latency = f"Error; {e}"

        start_time = time.time()
        try:
            self.bot.cache.ping()
            redis_latency = round((time.time() - start_time) * 1000)
        except Exception as e:
            redis_latency = f"Error; {e}"

        await ctx.send(
            f"Bot Latency: {bot_latency}ms\n"
            f"Database Latency: {db_latency}ms\n"
            f"Cache Latency: {redis_latency}ms"
        )

    @commands.command()
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
    await bot.add_cog(GeneralCog(bot))
