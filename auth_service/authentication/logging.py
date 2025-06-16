import asyncio
import json
import nats

NATS_URL = "nats://natslogging:4222"
async def publish_log(topic, data):
    nc = await nats.connect(NATS_URL)
    await nc.publish(topic, json.dumps(data).encode())
    await nc.flush()
    await nc.close()

def send_log(topic, data):
    asyncio.run(publish_log(topic, data))