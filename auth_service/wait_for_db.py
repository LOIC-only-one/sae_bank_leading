import time
from django.db import connections
from django.db.utils import OperationalError

print("⏳ Attente de la base de données...")
while True:
    try:
        conn = connections['default']
        conn.cursor()
        break
    except OperationalError:
        print("⛔ Base non disponible. Nouvelle tentative...")
        time.sleep(1)
print("✅ Base de données disponible.")
