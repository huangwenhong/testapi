import requests
import json
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class HTTPClient:
    def __init__(self, base_url: str = "", timeout: int = 30, retries: int = 3):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        
        # 设置重试策略
        retry_strategy = Retry(
            total=retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 设置默认请求头
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "APITestFramework/1.0"
        })
    
    def set_headers(self, headers: Dict[str, str]):
        self.session.headers.update(headers)
    
    def clear_headers(self):
        self.session.headers.clear()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "APITestFramework/1.0"
        })
    
    def get_cookies(self) -> Dict[str, str]:
        return dict(self.session.cookies)
    
    def set_cookies(self, cookies: Dict[str, str]):
        self.session.cookies.update(cookies)
    
    def clear_cookies(self):
        self.session.cookies.clear()
    
    def _build_url(self, endpoint: str) -> str:
        if endpoint.startswith("http"):
            return endpoint
        return f"{self.base_url}/{endpoint.lstrip('/')}"
    
    def _prepare_data(self, data: Any) -> Optional[str]:
        if data is None:
            return None
        if isinstance(data, (dict, list)):
            return json.dumps(data)
        return str(data)
    
    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = self._build_url(endpoint)
        
        # 处理请求数据
        if 'data' in kwargs and kwargs['data'] is not None:
            if 'json' not in kwargs:  # 如果同时提供了data和json，优先使用json
                kwargs['data'] = self._prepare_data(kwargs['data'])
        
        # 设置超时
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        try:
            response = self.session.request(method.upper(), url, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f"HTTP请求失败: {str(e)}")
    
    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> requests.Response:
        return self.request("GET", endpoint, params=params, **kwargs)
    
    def post(self, endpoint: str, data: Any = None, json: Any = None, **kwargs) -> requests.Response:
        return self.request("POST", endpoint, data=data, json=json, **kwargs)
    
    def put(self, endpoint: str, data: Any = None, json: Any = None, **kwargs) -> requests.Response:
        return self.request("PUT", endpoint, data=data, json=json, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("DELETE", endpoint, **kwargs)
    
    def patch(self, endpoint: str, data: Any = None, json: Any = None, **kwargs) -> requests.Response:
        return self.request("PATCH", endpoint, data=data, json=json, **kwargs)
    
    def head(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("HEAD", endpoint, **kwargs)
    
    def options(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("OPTIONS", endpoint, **kwargs)
    
    def close(self):
        self.session.close()


class ResponseWrapper:
    def __init__(self, response: requests.Response):
        self.response = response
        self.status_code = response.status_code
        self.headers = response.headers
        self.url = response.url
        self.elapsed = response.elapsed
    
    @property
    def text(self) -> str:
        return self.response.text
    
    @property
    def json(self) -> Any:
        try:
            return self.response.json()
        except json.JSONDecodeError:
            raise ValueError("响应内容不是有效的JSON格式")
    
    def get_header(self, key: str, default: Any = None) -> Any:
        return self.headers.get(key, default)
    
    def get_cookie(self, name: str) -> Optional[str]:
        return self.response.cookies.get(name)
    
    def __str__(self) -> str:
        return f"Response(status_code={self.status_code}, url='{self.url}')"