import asyncio

from tbsky_session.api import run_fastapi_server
from tbsky_session.core import init_logging


def main():
    init_logging()
    asyncio.run(run_fastapi_server())
