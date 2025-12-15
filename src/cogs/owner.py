import discord
from discord.ext import commands

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command(name="sync", hidden=True)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def sync(self, ctx: commands.Context):
        await self.bot.tree.sync()
        await ctx.send("Comandos sincronizados", delete_after=15)

    @commands.is_owner()
    @commands.command(name="reload", hidden=True)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def load_cog(self, ctx, cog: str):
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            await ctx.send(f"Cog {cog} loaded successfully.")
        except Exception as e:
            await ctx.send(f"Error loading cog {cog}: {e}")
        
    @commands.is_owner()
    @commands.command(name="load", hidden=True)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def load_cog(self, ctx, cog: str):
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            await ctx.send(f"Cog {cog} loaded successfully.")
        except Exception as e:
            await ctx.send(f"Error loading cog {cog}: {e}")

    @commands.is_owner()
    @commands.command(name="reload", hidden=True)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def reload_cog(self, ctx, cog: str):
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            await ctx.send(f"Cog {cog} loaded successfully.")
        except Exception as e:
            await ctx.send(f"Error loading cog {cog}: {e}")

async def setup(bot):
    await bot.add_cog(Owner(bot))
