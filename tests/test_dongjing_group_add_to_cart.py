import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.test_case import TestCase
from core.assertions import AssertionChain
from config.config import config


class TestDongjingGroupAddToCart(TestCase):
    """东经易网添加购物车测试用例"""
    
    def __init__(self):
        base_url = config.get_base_url("dongjing_group")
        super().__init__("东经易网添加购物车测试", base_url)
        
        headers = config.get_headers("dongjing_group")
        self.client.set_headers(headers)
        self.auth_token = None
    
    def setup(self):
        print(f"开始执行东经易网添加购物车测试: {self.name}")
        self.login()
    
    def teardown(self):
        print(f"东经易网添加购物车测试完成: {self.name}")
    
    def login(self):
        login_data = config.get_test_data("login_data.dongjing_group_valid")
        login_endpoint = config.get_api_endpoint("dongjing_group", "login")
        
        if login_data is None:
            print(f"错误: 无法获取登录数据")
            return
        
        print(f"登录请求数据: username={login_data['username']}, password={login_data['password']}")
        print(f"登录接口地址: {login_endpoint}")
        
        response = self.post(login_endpoint, json={
            "username": login_data["username"],
            "password": login_data["password"],
            "loginType": "WEB"
        })
        
        print(f"登录响应状态码: {response.status_code}")
        print(f"登录响应内容: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json
            print(f"登录响应JSON: {response_data}")
            if response_data.get("success") and "token" in response_data:
                self.auth_token = response_data["token"]
                self.client.set_headers({
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.auth_token}"
                })
                self.set_variable("auth_token", self.auth_token)
                print(f"登录成功，获取到token")
            else:
                print(f"登录失败: {response_data.get('msg', '未知错误')}")
    
    def test_add_to_cart(self):
        self.login()
        
        cart_data = config.get_test_data("cart_data.dongjing_group_valid_cart")
        cart_endpoint = config.get_api_endpoint("dongjing_group", "pricing_protocol")
        
        if cart_data is None:
            print(f"错误: 无法获取购物车数据")
            return
        
        print(f"添加购物车请求数据: {cart_data}")
        print(f"添加购物车接口地址: {cart_endpoint}")
        
        response = self.post(cart_endpoint, json=cart_data)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        self.assert_that(response)\
            .status_code(200)\
            .json_contains({
                "success": True
            })\
            .response_time_less_than(5000)
        
        if response.status_code == 200:
            response_data = response.json
            if response_data.get("success"):
                print(f"添加购物车成功")


if __name__ == "__main__":
    test_suite = TestDongjingGroupAddToCart()
    test_suite.setup()
    test_suite.test_add_to_cart()
    test_suite.teardown()
