import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.test_case import TestCase
from core.assertions import AssertionChain
from config.config import config


class TestDongjingGroupLoginAPI(TestCase):
    """东经易网登录API测试用例"""
    
    def __init__(self):
        base_url = config.get_base_url("dongjing_group")
        super().__init__("东经易网登录API测试", base_url)
        
        headers = config.get_headers("dongjing_group")
        self.client.set_headers(headers)
        self.auth_token = None
        self.user_id = None
        self.fid = None
        self.user_area_code = None
    
    def login(self):
        """执行登录操作"""
        login_data = config.get_test_data("login_data.dongjing_group_valid")
        login_endpoint = config.get_api_endpoint("dongjing_group", "login")
        
        response = self.post(login_endpoint, json={
            "username": login_data["username"],
            "password": login_data["password"],
            "loginType": "WEB"
        })
        
        if response.status_code == 200:
            response_data = response.json
            if response_data.get("success"):
                data = response_data.get("data", {})
                self.user_id = data.get("fid")
                self.fid = data.get("fid")
                self.user_area_code = data.get("fkeyarea", 330304004)
                self.set_variable("fuserId", self.user_id)
                self.set_variable("fid", self.fid)
                self.set_variable("fuserBrowseAreaCode", self.user_area_code)
    
    def test_successful_login(self):
        """测试东经易网成功登录"""
        login_data = config.get_test_data("login_data.dongjing_group_valid")
        login_endpoint = config.get_api_endpoint("dongjing_group", "login")
        
        print(f"登录请求数据: username={login_data['username']}, password={login_data['password']}, loginType=WEB")
        print(f"登录接口地址: {login_endpoint}")
        
        response = self.post(login_endpoint, json={
            "username": login_data["username"],
            "password": login_data["password"],
            "loginType": "WEB"
        })
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        self.assert_that(response)\
            .status_code(200)\
            .json_contains({
                "success": True
            })\
            .json_has_key("data")\
            .response_time_less_than(3000)
        
        if response.status_code == 200:
            response_data = response.json
            if response_data.get("success"):
                token_cookie = response.headers.get("Set-Cookie", "")
                print(f"响应Cookie: {token_cookie}")
                
                if "token=" in token_cookie:
                    import re
                    match = re.search(r'token=([^;]+)', token_cookie)
                    if match:
                        self.auth_token = match.group(1)
                        current_cookies = self.client.get_cookies()
                        current_cookies["token"] = self.auth_token
                        self.client.set_cookies(current_cookies)
                        self.set_variable("auth_token", self.auth_token)
                        print(f"登录成功，从Cookie获取到token: {self.auth_token[:20]}...")
                
                data = response_data.get("data", {})
                self.user_id = data.get("fid")
                self.fid = data.get("fid")
                self.user_area_code = data.get("fkeyarea", 330304004)
                self.set_variable("fuserId", self.user_id)
                self.set_variable("fid", self.fid)
                self.set_variable("fuserBrowseAreaCode", self.user_area_code)
                print(f"登录返回用户ID: {self.user_id}")
                print(f"登录返回FID: {self.fid}")
                print(f"登录返回用户区域码: {self.user_area_code}")
        
        return self.auth_token


if __name__ == "__main__":
    test_suite = TestDongjingGroupLoginAPI()
    test_suite.setup()
    test_suite.test_successful_login()
    test_suite.teardown()
