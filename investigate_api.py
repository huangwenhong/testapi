"""
东经易网API端点探测脚本
用于调查正确的API端点和响应结构
"""

import requests
import json
from urllib.parse import urljoin

BASE_URL = "http://grouptest.cpsol.net"

COMMON_PATHS = [
    "",
    "/",
    "/home",
    "/login",
    "/api",
    "/api/",
    "/api/login",
    "/api/user/login",
    "/api/auth/login",
    "/api/member/login",
    "/api/accounts/login",
    "/api/v1/login",
    "/api/v1/auth/login",
    "/api/products",
    "/api/v1/products",
    "/api/goods",
    "/api/item/list",
    "/api/order",
    "/api/orders",
    "/api/v1/orders",
    "/api/cart",
    "/api/v1/cart",
    "/api/member",
    "/api/user",
    "/api/member/info",
    "/api/user/info",
]

def probe_endpoint(path):
    """探测单个端点"""
    url = urljoin(BASE_URL, path)
    
    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        return {
            "path": path,
            "status_code": response.status_code,
            "url": response.url,
            "content_type": response.headers.get("Content-Type", ""),
            "response_size": len(response.content),
            "response_preview": response.text[:200] if response.text else ""
        }
    except requests.exceptions.ConnectionError as e:
        return {
            "path": path,
            "status_code": "CONNECTION_ERROR",
            "error": str(e)
        }
    except Exception as e:
        return {
            "path": path,
            "status_code": "ERROR",
            "error": str(e)
        }

def probe_with_post(path, data=None):
    """使用POST方法探测端点"""
    url = urljoin(BASE_URL, path)
    
    try:
        response = requests.post(url, json=data, timeout=10, allow_redirects=True)
        return {
            "path": path,
            "method": "POST",
            "status_code": response.status_code,
            "content_type": response.headers.get("Content-Type", ""),
            "response_size": len(response.content),
            "response_preview": response.text[:300] if response.text else ""
        }
    except Exception as e:
        return {
            "path": path,
            "method": "POST",
            "status_code": "ERROR",
            "error": str(e)
        }

def main():
    print("=" * 80)
    print("东经易网 API端点探测")
    print(f"目标服务器: {BASE_URL}")
    print("=" * 80)
    
    results = []
    
    print("\n1. 探测GET端点...")
    for path in COMMON_PATHS:
        result = probe_endpoint(path)
        results.append(result)
        
        status = result.get("status_code", "UNKNOWN")
        print(f"  {path:30s} -> {status}")
    
    print("\n2. 探测登录端点(POST)...")
    login_paths = [
        "/api/login",
        "/api/user/login",
        "/api/auth/login",
        "/api/member/login",
        "/api/accounts/login",
        "/login",
    ]
    
    login_credentials = [
        {"account": "testuser", "pwd": "testpass"},
        {"username": "testuser", "password": "testpass"},
        {"account": "testuser", "password": "testpass"},
        {"mobile": "testuser", "password": "testpass"},
    ]
    
    for path in login_paths:
        for credentials in login_credentials:
            result = probe_with_post(path, credentials)
            results.append(result)
            
            status = result.get("status_code", "UNKNOWN")
            print(f"  POST {path:30s} (creds: {list(credentials.keys())}) -> {status}")
    
    print("\n" + "=" * 80)
    print("探测结果汇总")
    print("=" * 80)
    
    success_results = [r for r in results if str(r.get("status_code", "")).startswith("2")]
    
    print(f"\n成功响应的端点 ({len(success_results)}个):")
    for r in success_results:
        print(f"\n  路径: {r['path']}")
        print(f"  状态码: {r.get('status_code')}")
        print(f"  响应预览: {r.get('response_preview', 'N/A')[:100]}")
    
    if success_results:
        print("\n" + "=" * 80)
        print("建议的API端点配置:")
        print("=" * 80)
        for r in success_results:
            if r.get('response_preview'):
                try:
                    data = json.loads(r['response_preview'])
                    if isinstance(data, dict):
                        print(f"\n{r['path']} 返回JSON结构:")
                        print(f"  键名: {list(data.keys())}")
                except:
                    pass
    
    return results

if __name__ == "__main__":
    main()
