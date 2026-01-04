import asyncio
import discord
from discord.ext import commands
from discord.http import Route

class AutoModMax(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="setup_automod_max")
    @commands.has_permissions(manage_guild=True)
    async def setup_automod_max(self, ctx: commands.Context):
        guild = ctx.guild
        route = Route(
            "POST",
            "/guilds/{guild_id}/auto-moderation/rules",
            guild_id=guild.id
        )

        created = 0

        async def create(payload):
            nonlocal created
            try:
                await self.bot.http.request(route, json=payload)
                created += 1
                await asyncio.sleep(1)  # evitar rate limits
            except discord.HTTPException as e:
                print(f"AutoMod error: {e}")

        # 1–6) KEYWORD (máx 6)
        keyword_sets = [
            ["free nitro", "steam gift"],
            ["discord.gg/", "invite.gg/"],
            ["*crypto*", "*airdrop*"],
            ["*scam*", "*fraud*"],
            ["*hack*", "*exploit*"],
            ["*giveaway*", "*reward*"],
        ]

        for i, words in enumerate(keyword_sets, start=1):
            await create({
                "name": f"Keyword Rule {i}",
                "event_type": 1,      # MESSAGE_SEND
                "trigger_type": 1,    # KEYWORD
                "trigger_metadata": {
                    "keyword_filter": words
                },
                "actions": [
                    {
                        "type": 1,  # BLOCK_MESSAGE
                        "metadata": {
                            "custom_message": "🚫 Mensaje bloqueado por AutoMod."
                        }
                    }
                ],
                "enabled": True
            })

        # 7) SPAM (máx 1)
        await create({
            "name": "Spam Detection",
            "event_type": 1,
            "trigger_type": 3,  # SPAM
            "actions": [
                {"type": 1}
            ],
            "enabled": True
        })

        # 8) KEYWORD_PRESET (máx 1)
        await create({
            "name": "Preset Profanity & Slurs",
            "event_type": 1,
            "trigger_type": 4,  # KEYWORD_PRESET
            "trigger_metadata": {
                "presets": [1, 2, 3]  # PROFANITY, SEXUAL_CONTENT, SLURS
            },
            "actions": [
                {"type": 1}
            ],
            "enabled": True
        })

        # 9) MENTION_SPAM (máx 1)
        await create({
            "name": "Mention Spam",
            "event_type": 1,
            "trigger_type": 5,  # MENTION_SPAM
            "trigger_metadata": {
                "mention_total_limit": 5,
                "mention_raid_protection_enabled": True
            },
            "actions": [
                {"type": 1}
            ],
            "enabled": True
        })

        # 10) MEMBER_PROFILE (máx 1)
        await create({
            "name": "Profile Keyword Filter",
            "event_type": 2,      # MEMBER_UPDATE
            "trigger_type": 6,    # MEMBER_PROFILE
            "trigger_metadata": {
                "keyword_filter": ["*scam*", "*crypto*", "*nsfw*"]
            },
            "actions": [
                {"type": 1}
            ],
            "enabled": True
        })

        await ctx.send(f"✅ AutoMod configurado: **{created}/10** reglas creadas.")

async def setup(bot):
    await bot.add_cog(AutoModMax(bot))
