import httpx
from django.conf import settings
from celery import shared_task

@shared_task
def update_aulas_task():
    url = settings.DOMAIN_NAME_SLASH + 'api/aulas/aulas/'
    headers = {"Authorization": f"Bearer {settings.CELERY_TOKEN}"}
    response = httpx.post(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to access the endpoint: {response.content}")
    return response.json()
