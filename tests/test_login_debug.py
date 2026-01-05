import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.http_client import HTTPClient
from config.config import config

def test_login():
    base_url = config.get_base_url("dongjing_group")
    headers = config.get_headers("dongjing_group")
    login_endpoint = config.get_api_endpoint("dongjing_group", "login")
    login_data = config.get_test_data("login_data.dongjing_group_valid")
    
    client = HTTPClient(base_url)
    client.set_headers(headers)
    
    url = base_url + login_endpoint
    payload = {
        "username": login_data["username"],
        "password": login_data["password"],
        "loginType": "WEB"
    }
    
    print(f"请求URL: {url}")
    print(f"请求头: {headers}")
    print(f"请求体: {payload}")
    print("=" * 50)
    
    response = client.post(login_endpoint, json=payload)
    
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"响应内容: {response.text}")
    print("=" * 50)
    
    try:
        import json
        resp_json = response.json
        print(f"JSON解析成功:")
        print(f"  success: {resp_json.get('success')}")
        print(f"  msg: {resp_json.get('msg')}")
        print(f"  data: {json.dumps(resp_json.get('data'), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"JSON解析失败: {e}")

if __name__ == "__main__":
    test_login()
