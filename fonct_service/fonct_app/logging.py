import asyncio
import json
import nats

NATS_URL = "nats://natslogging:4222"
async def publish_log(topic, data):
    try:
        nc = await nats.connect(NATS_URL)
        await nc.publish(topic, json.dumps(data).encode())
        await nc.flush()
        await nc.close()
    except Exception as e:
        print(f"[Logging Error] {e}")

def send_log(topic, data):
    asyncio.run(publish_log(topic, data))