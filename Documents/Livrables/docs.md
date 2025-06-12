```bash
POST /api/logs/

# 1. La vue appelle le serializer
serializer = LogCreateSerializer(data=request.data)

# 2. Il valide les données
serializer.is_valid()

# 3. La vue appelle .save()
log = serializer.save()  # appelle LogCreateSerializer.create() si défini

# 4. La méthode create() est exécutée avec validated_data
```

- Schema du servie de logging
```yaml
logging_service :
    - écoute NATS (logs.info, logs.error, logs.warn…)
    - stocke les logs (en base de données par exemple)
    - expose une API :
        GET /logs
        GET /logs?level=error
        GET /logs?source=auth_service
```