import asyncio
import nats
import json

async def publication(message_data):
    nc = nats.NATS()
    await nc.connect("nats://natslogging:4222")
    await nc.publish("logs", json.dumps(message_data).encode())
    await nc.drain()

def log_nats(message_data):
    asyncio.run(publication(message_data))
