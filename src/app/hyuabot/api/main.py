import asyncio
import sys

from hypercorn.config import Config

from app.hyuabot.api import create_app, AppSettings

py_ver = int(f"{sys.version_info.major}{sys.version_info.minor}")
if py_ver > 37 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
hypercorn_config = Config()
app_settings = AppSettings()
app = create_app(app_settings)
