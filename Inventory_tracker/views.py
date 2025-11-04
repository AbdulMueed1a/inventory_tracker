from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection

@api_view(["GET"])
def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        return Response({"status": "ok", "db": bool(result)})
    except Exception as e:
        return Response({"status": "error", "db_error": str(e)}, status=500)
