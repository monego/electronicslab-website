import httpx
from django.conf import settings


def update_aulas_task():
    url = settings.DOMAIN_NAME_SLASH + 'api/aulas/aulas/update/'
    response = httpx.get(url, timeout=120)
    if response.status_code != 200:
        raise Exception(f"Failed to access the endpoint: {response.content}")
    return response.json()
