# Practice file: the practical difference between sync and async in FastAPI.
#
# The event loop is ONE thread that runs all async def code. Think of it as one
# waiter serving the whole restaurant: if the waiter stops, every table waits.
#
# Measured with 3 requests at the same time, each one sleeping for 3 seconds:
#
#   route        | 3 requests | /ping during the wait
#   -------------|------------|----------------------
#   /sync        | 3s         | instant
#   /async-bad   | 9s         | 2.8s (frozen)
#   /async-good  | 3s         | instant
#
# Rules to remember:
#   - async def does NOT make code faster. It only helps if the slow lines use await.
#   - Blocking code (time.sleep, sync SQLAlchemy, requests, password hashing) -> use def
#   - Everything slow can be awaited (asyncio.sleep, httpx.AsyncClient) -> use async def
#   - Not sure -> use def, it is the safe default
#
# How to run it:
#   uvicorn async_demo:app --port 8001
#   time (for i in 1 2 3; do curl -s localhost:8001/sync > /dev/null & done; wait)

import asyncio  # async tools: asyncio.sleep is the sleep that does NOT block
import time  # normal tools: time.sleep is the sleep that BLOCKS its thread

from fastapi import FastAPI

app = FastAPI()


# GOOD: blocking code in a plain def.
#
# def tells FastAPI "this might block", so FastAPI runs it in a separate thread
# from the thread pool. Each request gets its own thread.
#
# time.sleep blocks: the thread stops and does nothing for 3 seconds.
# Only that helper thread is stuck. The event loop stays free for other requests.
#
# 3 requests = 3 threads sleeping at the same time = 3s total. /ping answers instantly.
#
# Limit: every waiting request holds a thread, and the pool has 40 by default,
# so request 41 has to wait for a free thread.
@app.get("/sync")
def sync_route():
    time.sleep(3)
    return {"route": "sync"}


# BAD: blocking code in an async def.
#
# async def tells FastAPI "this is safe to run directly on the event loop".
# That is a promise, and time.sleep breaks it.
#
# time.sleep blocks whichever thread it runs on, and here that is the event loop.
# There is no await, so the function never gives up control.
# The whole server freezes for 3 seconds: EVERYONE WAITS, even unrelated routes.
#
# 3 requests run one after the other = 3 + 3 + 3 = 9s total.
# /ping does no work but took 2.8s, because the loop was frozen when it arrived.
#
# Trap: Python shows no error or warning. It looks like async code,
# but it is worse than a plain def.
@app.get("/async-bad")
async def async_bad_route():
    time.sleep(3)  # BAD: blocks the event loop, everyone waits
    return {"route": "async-bad"}


# GOOD: awaited code in an async def.
#
# asyncio.sleep is a sleep that knows how to work with the event loop.
# await pauses ONLY this function and hands control back to the event loop,
# which serves other requests. 3 seconds later it continues from the next line.
#
# 3 requests = one thread holds all 3 timers = 3s total. /ping answers instantly.
#
# Better than /sync at scale: no thread is used while waiting,
# so one thread can hold thousands of waiting requests.
@app.get("/async-good")
async def async_good_route():
    await asyncio.sleep(3)  # GOOD: pauses this function only, nobody else waits
    return {"route": "async-good"}


# The detector: it does no waiting, so it should answer instantly.
# If /ping is slow, something else is blocking the event loop.
@app.get("/ping")
async def ping():
    return {"status": "pong"}


# Why this matters in Task Manager: the SQLAlchemy session there is synchronous,
# so db.scalars() and db.commit() block just like time.sleep. Changing those
# endpoints to async def would turn them all into /async-bad, so they stay plain def.
# The middleware is safe as async def: its only slow part is await call_next(request).
