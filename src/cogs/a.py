import discord
from discord.ext import commands
from datetime import datetime


class TOSGate(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.col = bot.db.users      # MongoDB
        self.redis = bot.cache       # Redis (sync)
        print("[TOSGate] Cog initialized")

    # ==========================
    # BLOQUEO GLOBAL
    # ==========================
    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        user_id = ctx.author.id
        print(f"[TOSGate] on_command fired | user={user_id} | cmd={ctx.command}")

        # owners pasan
        if user_id in self.bot.owner_ids:
            print("[TOSGate] Owner detected → bypass")
            #return

        redis_key = f"user:{user_id}:tos"

        # 1️⃣ Redis
        try:
            redis_value = self.redis.get(redis_key)
            print(f"[TOSGate] Redis GET {redis_key} → {redis_value}")
            if redis_value:
                print("[TOSGate] Redis says ACCEPTED → allow command")
                return
        except Exception as e:
            print(f"[TOSGate] Redis error: {e}")

        # 2️⃣ Mongo
        print("[TOSGate] Querying MongoDB")
        user = await self.col.find_one({"_id": str(user_id)})
        print(f"[TOSGate] Mongo result → {user}")

        # Usuario nuevo
        if not user:
            print("[TOSGate] New user detected")

            lang = "en"
            if ctx.interaction:
                print(f"[TOSGate] Interaction locale raw → {ctx.interaction.locale}")
                if ctx.interaction.locale:
                    lang = ctx.interaction.locale.split("-")[0]

            print(f"[TOSGate] Language set to → {lang}")

            user = {
                "_id": str(user_id),
                "tos_accepted": False,
                "language": lang,
                "created_at": datetime.utcnow(),
            }

            await self.col.insert_one(user)
            print("[TOSGate] User inserted into MongoDB")

        # ❌ No aceptó → mostrar TOS y BLOQUEAR
        if not user["tos_accepted"]:
            print("[TOSGate] TOS NOT accepted → blocking command")

            try:
                await ctx.send(
                    embed=discord.Embed(
                        description=(
                            "You must accept the **Terms of Service** to use the bot."
                        ),
                        color=0x2F3136,
                    ),
                    view=AcceptView(self),
                )
                print("[TOSGate] TOS message sent")
            except Exception as e:
                print(f"[TOSGate] Failed to send TOS message: {e}")

            return

        # 3️⃣ Cachear si ya aceptó
        try:
            self.redis.set(redis_key, "1")
            print("[TOSGate] Redis SET accepted")
        except Exception as e:
            print(f"[TOSGate] Redis SET error: {e}")

        print("[TOSGate] User accepted → command allowed")


# ==========================
# VIEW + BUTTON
# ==========================
class AcceptView(discord.ui.View):
    def __init__(self, cog: TOSGate):
        super().__init__(timeout=None)
        self.cog = cog
        print("[TOSGate] AcceptView created")

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
    async def accept(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        user_id = interaction.user.id
        print(f"[TOSGate] Accept button clicked | user={user_id}")

        # Mongo
        try:
            await self.cog.col.update_one(
                {"_id": str(user_id)},
                {"$set": {"tos_accepted": True}},
            )
            print("[TOSGate] Mongo updated: tos_accepted=True")
        except Exception as e:
            print(f"[TOSGate] Mongo update error: {e}")

        # Redis
        try:
            self.cog.redis.set(f"user:{user_id}:tos", "1")
            print("[TOSGate] Redis SET accepted")
        except Exception as e:
            print(f"[TOSGate] Redis SET error: {e}")

        try:
            await interaction.response.edit_message(
                content="✅ You can now use the bot.",
                embed=None,
                view=None,
            )
            print("[TOSGate] Confirmation message edited")
        except Exception as e:
            print(f"[TOSGate] Interaction response error: {e}")


async def setup(bot: commands.AutoShardedBot):
    print("[TOSGate] setup() called")
    await bot.add_cog(TOSGate(bot))
    print("[TOSGate] Cog added")
