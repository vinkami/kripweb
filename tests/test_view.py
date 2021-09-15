from kripweb.view import View
from queue import Queue
import asyncio


loop = asyncio.get_event_loop()


def test_just_to_make_a_loop():
    async def wait(): await asyncio.sleep(1)
    loop.run_until_complete(wait())


def test_func():
    async def action():
        return 1

    q = View(action, False)()

    assert isinstance(q, Queue)
    assert q.get(block=False) == 1
