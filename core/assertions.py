import json
import re
from typing import Any, Dict, List, Optional, Union
from jsonschema import validate, ValidationError


class AssertionError(Exception):
    def __init__(self, message: str, actual: Any = None, expected: Any = None):
        super().__init__(message)
        self.message = message
        self.actual = actual
        self.expected = expected


class Assertions:
    def __init__(self, response):
        self.response = response
    
    def status_code(self, expected_code: int) -> 'Assertions':
        actual_code = self.response.status_code
        if actual_code != expected_code:
            raise AssertionError(
                f"状态码断言失败: 期望 {expected_code}, 实际 {actual_code}",
                actual_code, expected_code
            )
        return self
    
    def status_code_in(self, expected_codes: List[int]) -> 'Assertions':
        actual_code = self.response.status_code
        if actual_code not in expected_codes:
            raise AssertionError(
                f"状态码断言失败: 期望在 {expected_codes} 中, 实际 {actual_code}",
                actual_code, expected_codes
            )
        return self
    
    def json_equals(self, expected: Any) -> 'Assertions':
        actual = self.response.json
        if actual != expected:
            raise AssertionError(
                "JSON响应断言失败: 响应内容不匹配",
                actual, expected
            )
        return self
    
    def json_contains(self, expected: Dict[str, Any]) -> 'Assertions':
        actual = self.response.json
        if not isinstance(actual, dict):
            raise AssertionError("响应不是字典类型，无法进行包含断言")
        
        for key, value in expected.items():
            if key not in actual:
                raise AssertionError(f"响应中缺少键: {key}")
            if actual[key] != value:
                raise AssertionError(
                    f"键 '{key}' 的值不匹配: 期望 {value}, 实际 {actual[key]}",
                    actual[key], value
                )
        return self
    
    def json_has_key(self, key: str) -> 'Assertions':
        actual = self.response.json
        if not isinstance(actual, dict):
            raise AssertionError("响应不是字典类型")
        
        if key not in actual:
            raise AssertionError(f"响应中缺少键: {key}")
        return self
    
    def json_schema(self, schema: Dict[str, Any]) -> 'Assertions':
        actual = self.response.json
        try:
            validate(instance=actual, schema=schema)
        except ValidationError as e:
            raise AssertionError(f"JSON Schema验证失败: {str(e)}")
        return self
    
    def text_contains(self, expected_text: str) -> 'Assertions':
        actual_text = self.response.text
        if expected_text not in actual_text:
            raise AssertionError(
                f"文本断言失败: 期望包含 '{expected_text}'",
                actual_text, expected_text
            )
        return self
    
    def text_matches(self, pattern: str) -> 'Assertions':
        actual_text = self.response.text
        if not re.search(pattern, actual_text):
            raise AssertionError(
                f"正则表达式断言失败: 文本不匹配模式 '{pattern}'",
                actual_text, pattern
            )
        return self
    
    def header_exists(self, header_name: str) -> 'Assertions':
        if header_name not in self.response.headers:
            raise AssertionError(f"响应头中缺少: {header_name}")
        return self
    
    def header_equals(self, header_name: str, expected_value: str) -> 'Assertions':
        actual_value = self.response.headers.get(header_name)
        if actual_value != expected_value:
            raise AssertionError(
                f"响应头断言失败: {header_name} 期望 '{expected_value}', 实际 '{actual_value}'",
                actual_value, expected_value
            )
        return self
    
    def cookie_exists(self, cookie_name: str) -> 'Assertions':
        if not self.response.get_cookie(cookie_name):
            raise AssertionError(f"Cookie中缺少: {cookie_name}")
        return self
    
    def response_time_less_than(self, max_time_ms: int) -> 'Assertions':
        actual_time_ms = self.response.elapsed.total_seconds() * 1000
        if actual_time_ms > max_time_ms:
            raise AssertionError(
                f"响应时间断言失败: 期望小于 {max_time_ms}ms, 实际 {actual_time_ms:.2f}ms",
                actual_time_ms, max_time_ms
            )
        return self
    
    def is_success(self) -> 'Assertions':
        return self.status_code_in([200, 201, 202, 204])
    
    def is_client_error(self) -> 'Assertions':
        return self.status_code_in(list(range(400, 500)))
    
    def is_server_error(self) -> 'Assertions':
        return self.status_code_in(list(range(500, 600)))


class AssertionChain:
    def __init__(self, response):
        self.assertions = Assertions(response)
    
    def __getattr__(self, name):
        method = getattr(self.assertions, name)
        
        def wrapper(*args, **kwargs):
            method(*args, **kwargs)
            return self
        
        return wrapper
    
    def and_(self):
        return self
    
    def then(self):
        return self