from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import LogCreateSerializer, LogSerializer
from .models import Log
import json
import asyncio
import nats

NATS_URL = "nats://natslogging:4222"

async def publish_to_nats(data):
    nc = await nats.connect(NATS_URL)
    topic = f"log.{data.get('visibilite').lower()}.{data.get('level').lower()}"
    await nc.publish(topic, json.dumps(data).encode())
    await nc.close()

@api_view(['POST'])
def create_log(request):
    serializer = LogCreateSerializer(data=request.data)
    if serializer.is_valid():
        asyncio.run(publish_to_nats(serializer.validated_data))
        return Response({"message": "Log publié via NATS"}, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def list_logs(request):
    queryset = Log.objects.all()

    for param in ['level', 'type_action', 'visibilite']:
        val = request.GET.get(param)
        if val:
            queryset = queryset.filter(**{f"{param}__iexact": val})

    identifiant = request.GET.get('identifiant_utilisateur')
    if identifiant:
        queryset = queryset.filter(identifiant_utilisateur=identifiant)

    queryset = queryset.order_by('-created_at')
    limit = request.GET.get('limit')
    if limit and limit.isdigit():
        queryset = queryset[:int(limit)]
    else:
        queryset = queryset[:100]

    serializer = LogSerializer(queryset, many=True)
    return Response(serializer.data)
