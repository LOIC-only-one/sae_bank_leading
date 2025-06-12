import asyncio
import json
import nats
import django
import os
import sys
from asgiref.sync import sync_to_async

# Configuration de Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "logging_service.settings")
django.setup()

from logging_api.serializers import LogCreateSerializer

@sync_to_async
def enregistrer_log(data):
    serializer = LogCreateSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        print("✅ Log enregistré :", serializer.validated_data)
    else:
        print("❌ Erreur de validation du log :", serializer.errors)

async def message_handler(msg):
    try:
        data = json.loads(msg.data.decode())
        await enregistrer_log(data)
    except Exception as e:
        print("⚠️ Exception lors du traitement du message :", str(e))

async def main():
    nc = await nats.connect("nats://natslogging:4222")
    print("✅ Connexion NATS établie. En écoute...")

    topics = [
        "log.agents.info", "log.agents.error", "log.agents.warning",
        "log.membres.info", "log.membres.error", "log.membres.warning"
    ]

    for topic in topics:
        await nc.subscribe(topic, cb=message_handler)

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du listener NATS.")
