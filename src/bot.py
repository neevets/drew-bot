import discord
import sentry_sdk
import os
import logging
import pkgutil
import aiohttp
import asyncpg
import redis


from discord.ext import commands, tasks
from logging.handlers import RotatingFileHandler
from rgbprint import gradient_print, Color
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_PREFIX = os.getenv("DISCORD_PREFIX", ";")
SENTRY_DSN = os.getenv("SENTRY_DSN")
POSTGRES_URL = os.getenv("POSTGRES_URL")
REDIS_URL = os.getenv("REDIS_URL")
BETTERSTACK_HEARTBEAT = os.getenv("BETTERSTACK_HEARTBEAT")

sentry_sdk.init(
    dsn=SENTRY_DSN,
    traces_sample_rate=0.1,
)

def console_info(message: str) -> None:
    gradient_print(
        f"[INFO] {message}",
        start_color=Color.white,
        end_color=Color.blue,
    )

def console_warn(message: str) -> None:
    gradient_print(
        f"[WARNING] {message}",
        start_color=Color.white,
        end_color=Color.yellow,
    )

def console_error(message: str) -> None:
    gradient_print(
        f"[ERROR] {message}",
        start_color=Color.white,
        end_color=Color.red,
    )

class Bot(commands.AutoShardedBot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            intents=intents,
            command_prefix=DISCORD_PREFIX,
            owner_ids={1424164764858449920, 1263092918130966569},
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="/help | drewbot.ink",
            ),
            status=discord.Status.online,
            help_command=None,
            case_insensitive=True
        )

        self.logger = logging.getLogger("drew.bot")
        self.db = None
        self.cache = None
        self.http_session = None

    async def setup_hook(self) -> None:
        await self._setup_logging()
        await self._setup_database()
        await self._setup_cache()
        await self._load_cogs()

        self.http_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )

        if BETTERSTACK_HEARTBEAT:
            self.heartbeat_loop.start()

        console_info("Main startup completed")
        self.logger.info("Main startup completed")

    async def _setup_logging(self) -> None:
        os.makedirs("src/logging", exist_ok=True)

        logger = logging.getLogger("drew.bot")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = RotatingFileHandler(
                "src/logging/bot.log",
                maxBytes=5 * 1024 * 1024,
                backupCount=5,
                encoding="utf-8",
            )
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
                )
            )
            logger.addHandler(handler)

        self.logger = logger
        console_info("Logging initialized")

    async def _setup_database(self) -> None:
        try:
            self.db = await asyncpg.connect(POSTGRES_URL)

            console_info("Database initialized")
            self.logger.info("Database initialized")

        except Exception as e:
            console_error("Database initialization failed")
            self.logger.exception("Database initialization failed")

    async def _setup_cache(self) -> None:
        try:
            self.cache = redis.from_url(REDIS_URL)

            console_info("Cache initialized")
            self.logger.info("Cache initialized")

        except Exception as e:
            console_error("Cache initialization failed: {e}")
            self.logger.exception("Cache initialization failed")

    async def _load_cogs(self) -> None:
        os.makedirs("src/cogs", exist_ok=True)

        console_info("------------------")
        for _, cog, _ in pkgutil.iter_modules(["src/cogs"]):
            if cog != '__pycache__':
                try:
                    if cog not in self.extensions:
                        await self.load_extension(f"src.cogs.{cog}")
                        console_info(f"Cog loaded: {cog}")
                        self.logger.info("Cog loaded: %s", cog)

                except Exception as e:
                    console_error(f"Failed to load cog: {cog}; {e}")
                    self.logger.exception("Failed to load cog: %s", cog)
        console_info("--------------------")

    @tasks.loop(minutes=3)
    async def heartbeat_loop(self) -> None:
        if not self.http_session or not BETTERSTACK_HEARTBEAT:
            return

        try:
            async with self.http_session.get(BETTERSTACK_HEARTBEAT) as response:
                if response.status != 200:
                    console_warn(f"Heartbeat failed ({response.status})")
                    self.logger.warning("Heartbeat failed (%s)", response.status)

        except Exception:
            console_error("Heartbeat error")
            self.logger.exception("Heartbeat error")

    async def close(self) -> None:
        console_info("Shutting down bot...")
        self.logger.info("Shutting down bot...")

        if self.http_session:
            await self.http_session.close()

        if self.db:
            await self.db.close()

        await super().close()

def main() -> None:
    if not DISCORD_TOKEN:
      raise RuntimeError("DISCORD_TOKEN not set in environment variable")

    Bot().run(DISCORD_TOKEN)

if __name__ == "__main__":
    main()
