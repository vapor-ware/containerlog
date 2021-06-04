""""""

import asyncio
import random
import time

from containerlog import enable_contextvars, get_logger
from containerlog.contextvars import bind, context_binding, unbind

enable_contextvars()

logger = get_logger()
l2 = get_logger("other")


async def nested():
    with context_binding(scope="nested"):
        l2.info("additional call")


async def run(name: str):
    logger.info("starting runner", name=name)
    bind(runner=name)

    for _ in range(10):
        wait = random.randrange(1, 15) / 10
        logger.info("waiting for next message", now=time.time(), wait=wait)
        await nested()
        await asyncio.sleep(wait)

    logger.info("unbinding runner name")
    unbind("runner")
    logger.info("done")


async def start():
    coros = []
    for i in range(5):
        coros.append(run(f"runner-{i}"))
    await asyncio.gather(*coros)


if __name__ == "__main__":
    asyncio.run(start())
