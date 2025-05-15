import random
import string
from typing import Dict

from fastapi.testclient import TestClient

def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))

def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"

def get_superuser_token_headers(client: TestClient) -> Dict[str, str]:
    login_data = {
        "username": "admin@example.com",  # 根据实际情况修改
        "password": "admin"  # 根据实际情况修改
    }
    r = client.post("/api/v1/auth/login", data=login_data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    tokens = r.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"} 