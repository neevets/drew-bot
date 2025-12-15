import os
import logging
import pkgutil
import aiohttp
import asyncpg
import redis
import discord
import sentry_sdk

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

BETTERSTACK_BOT_HEARTBEAT = os.getenv("BETTERSTACK_BOT_HEARTBEAT")
BETTERSTACK_DB_HEARTBEAT = os.getenv("BETTERSTACK_DB_HEARTBEAT")
BETTERSTACK_CACHE_HEARTBEAT = os.getenv("BETTERSTACK_CACHE_HEARTBEAT")

sentry_sdk.init(
    dsn=SENTRY_DSN,
    traces_sample_rate=0.1,
)

def console_info(message: str) -> None:
    gradient_print(f"[INFO] {message}", start_color=Color.white, end_color=Color.blue)

def console_warn(message: str) -> None:
    gradient_print(f"[WARNING] {message}", start_color=Color.white, end_color=Color.yellow)

def console_error(message: str) -> None:
    gradient_print(f"[ERROR] {message}", start_color=Color.white, end_color=Color.red)

class Bot(commands.AutoShardedBot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix=DISCORD_PREFIX,
            intents=intents,
            help_command=None,
            case_insensitive=True,
            owner_ids={1424164764858449920},
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="/help | drewbot.ink",
            ),
            status=discord.Status.online,
        )

        self.logger = logging.getLogger("drew.bot")
        self.db: asyncpg.Connection | None = None
        self.cache: redis.Redis | None = None
        self.http_session: aiohttp.ClientSession | None = None

    async def setup_hook(self) -> None:
        await self._setup_logging()
        await self._setup_database()
        await self._setup_cache()
        await self._load_cogs()

        self.http_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )

        if BETTERSTACK_BOT_HEARTBEAT:
            self.bot_heartbeat_loop.start()

        if BETTERSTACK_DB_HEARTBEAT:
            self.db_heartbeat_loop.start()

        if BETTERSTACK_CACHE_HEARTBEAT:
            self.cache_heartbeat_loop.start()

        console_info("Startup completed")
        self.logger.info("Startup completed")

    async def _setup_logging(self) -> None:
        os.makedirs("src/logging", exist_ok=True)

        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
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
            self.logger.addHandler(handler)

        console_info("Logging initialized")

    async def _setup_database(self) -> None:
        try:
            self.db = await asyncpg.connect(POSTGRES_URL)
            console_info("Database initialized")
            self.logger.info("Database initialized")
        except Exception:
            console_error("Database initialization failed")
            self.logger.exception("Database initialization failed")

    async def _setup_cache(self) -> None:
        try:
            self.cache = redis.from_url(REDIS_URL)
            console_info("Cache initialized")
            self.logger.info("Cache initialized")
        except Exception:
            console_error("Cache initialization failed")
            self.logger.exception("Cache initialization failed")

    async def _load_cogs(self) -> None:
        os.makedirs("src/cogs", exist_ok=True)

        for _, cog, _ in pkgutil.iter_modules(["src/cogs"]):
            if cog == "__pycache__":
                continue
            try:
                await self.load_extension(f"src.cogs.{cog}")
                console_info(f"Cog loaded: {cog}")
                self.logger.info("Cog loaded: %s", cog)
            except Exception:
                console_error(f"Failed to load cog: {cog}")
                self.logger.exception("Failed to load cog: %s", cog)

    @tasks.loop(minutes=3)
    async def bot_heartbeat_loop(self) -> None:
        if not self.http_session:
            return

        try:
            async with self.http_session.get(BETTERSTACK_BOT_HEARTBEAT) as r:
                if r.status != 200:
                    console_warn(f"Bot heartbeat failed ({r.status})")
        except Exception:
            console_error("Bot heartbeat error")
            self.logger.exception("Bot heartbeat error")

    @bot_heartbeat_loop.before_loop
    async def before_bot_heartbeat(self) -> None:
        await self.wait_until_ready()
        console_info("Bot heartbeat task started")
        self.logger.info("Bot heartbeat task started")

    @tasks.loop(minutes=30)
    async def db_heartbeat_loop(self) -> None:
        if not self.http_session or not self.db:
            return

        try:
            await self.db.fetch("SELECT 1")
            async with self.http_session.get(BETTERSTACK_DB_HEARTBEAT) as r:
                if r.status != 200:
                    console_warn(f"DB heartbeat failed ({r.status})")
        except Exception:
            console_error("DB heartbeat error")
            self.logger.exception("DB heartbeat error")

    @db_heartbeat_loop.before_loop
    async def before_db_heartbeat(self) -> None:
        await self.wait_until_ready()
        if self.db:
            console_info("DB heartbeat task started")
            self.logger.info("DB heartbeat task started")

    @tasks.loop(minutes=15)
    async def cache_heartbeat_loop(self) -> None:
        if not self.http_session or not self.cache:
            return

        try:
            self.cache.ping()
            async with self.http_session.get(BETTERSTACK_CACHE_HEARTBEAT) as r:
                if r.status != 200:
                    console_warn(f"Cache heartbeat failed ({r.status})")
        except Exception:
            console_error("Cache heartbeat error")
            self.logger.exception("Cache heartbeat error")

    @cache_heartbeat_loop.before_loop
    async def before_cache_heartbeat(self) -> None:
        await self.wait_until_ready()
        if self.cache:
            console_info("Cache heartbeat task started")
            self.logger.info("Cache heartbeat task started")

    async def close(self) -> None:
        console_info("Shutting down")
        self.logger.info("Shutting down")

        if self.http_session:
            await self.http_session.close()

        if self.db:
            await self.db.close()

        await super().close()

def main() -> None:
    if not DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN not set")
    
    Bot().run(DISCORD_TOKEN)

if __name__ == "__main__":
    main()
