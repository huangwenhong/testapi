# API测试框架

一个简单易用的Python单接口测试框架，支持HTTP接口测试、断言验证和测试报告生成。

## 功能特性

- ✅ 支持HTTP/HTTPS请求（GET、POST、PUT、DELETE等）
- ✅ 丰富的断言验证方法
- ✅ JSON Schema验证支持
- ✅ 测试用例管理和组织
- ✅ 多环境配置支持
- ✅ 详细的HTML测试报告
- ✅ 数据驱动测试
- ✅ 重试机制和超时设置
- ✅ 灵活的测试钩子（setup/teardown）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 配置测试环境

编辑 `config.yaml` 文件，配置你的API环境：

```yaml
environments:
  dev:
    base_url: "https://your-api-server.com"
    headers:
      Content-Type: "application/json"
      Authorization: "Bearer your-token"
```

### 2. 编写测试用例

创建测试用例文件 `tests/test_example.py`：

```python
from core.test_case import TestCase
from core.assertions import AssertionChain
from config.config import config

class MyAPITest(TestCase):
    def __init__(self):
        base_url = config.get_base_url("dev")
        super().__init__("我的API测试", base_url)
        
        # 设置请求头
        headers = config.get_headers("dev")
        self.client.set_headers(headers)
    
    def test_get_user(self):
        # 发送GET请求
        response = self.get("/users/1")
        
        # 断言验证
        self.assert_that(response)\
            .status_code(200)\
            .json_has_key("id")\
            .json_has_key("name")\
            .response_time_less_than(1000)

def create_test_suite():
    from core.test_case import TestSuite
    
    suite = TestSuite("示例测试套件")
    test_case = MyAPITest()
    test_case.step("获取用户信息")(test_case.test_get_user)
    suite.add_test_case(test_case)
    
    return suite
```

### 3. 运行测试

```bash
# 运行所有测试
python run_tests.py

# 运行指定测试套件
python run_tests.py --suite user

# 指定测试环境
python run_tests.py --env staging

# 指定报告输出目录
python run_tests.py --report-dir my_reports
```

## 核心组件

### HTTP客户端 (HTTPClient)

封装了HTTP请求功能，支持重试机制和超时设置。

```python
from core.http_client import HTTPClient

client = HTTPClient(base_url="https://api.example.com")
response = client.get("/users/1")
print(response.status_code)
print(response.json)
```

### 断言验证 (Assertions)

提供丰富的断言方法验证响应结果。

```python
from core.assertions import AssertionChain

# 链式断言
assertion = AssertionChain(response)
assertion.status_code(200)\
    .json_contains({"name": "John"})\
    .json_schema(user_schema)\
    .response_time_less_than(1000)

# 状态码断言
assertion.status_code(200)
assertion.status_code_in([200, 201, 204])
assertion.is_success()
assertion.is_client_error()

# JSON断言
assertion.json_equals(expected_data)
assertion.json_contains({"key": "value"})
assertion.json_has_key("id")
assertion.json_schema(schema)

# 文本断言
assertion.text_contains("success")
assertion.text_matches(r"\\d+")

# 响应头断言
assertion.header_exists("Content-Type")
assertion.header_equals("Content-Type", "application/json")

# 性能断言
assertion.response_time_less_than(500)
```

### 测试用例管理 (TestCase)

管理测试用例的执行流程和生命周期。

```python
from core.test_case import TestCase

class MyTest(TestCase):
    def __init__(self):
        super().__init__("测试用例名称", "https://api.example.com")
    
    @TestCase.setup
    def setup(self):
        # 测试前置操作
        pass
    
    @TestCase.teardown
    def teardown(self):
        # 测试后置操作
        pass
    
    def test_method(self):
        # 测试步骤
        response = self.get("/endpoint")
        self.assert_that(response).status_code(200)
```

### 测试报告 (Reporter)

生成详细的HTML和JSON格式的测试报告。

```python
from core.reporter import Reporter

reporter = Reporter("reports")
report_files = reporter.generate_reports(test_results)
```

## 配置说明

### 环境配置

在 `config.yaml` 中配置多个环境：

```yaml
environments:
  dev:
    base_url: "https://dev-api.example.com"
    headers:
      Authorization: "Bearer dev-token"
  
  staging:
    base_url: "https://staging-api.example.com"
    headers:
      Authorization: "Bearer staging-token"
  
  production:
    base_url: "https://api.example.com"
    headers:
      Authorization: "Bearer prod-token"
```

### 测试数据

支持数据驱动测试：

```yaml
test_data:
  user_credentials:
    - {username: "user1", password: "pass1"}
    - {username: "user2", password: "pass2"}
    - {username: "user3", password: "pass3"}
  
  expected_schemas:
    user_schema:
      type: "object"
      required: ["id", "name"]
      properties:
        id: {type: "integer"}
        name: {type: "string"}
```

## 项目结构

```
apitest/
├── core/                 # 核心模块
│   ├── http_client.py   # HTTP客户端
│   ├── assertions.py    # 断言验证
│   ├── test_case.py     # 测试用例管理
│   └── reporter.py      # 测试报告
├── config/              # 配置管理
│   └── config.py
├── tests/               # 测试用例
│   ├── test_user_api.py
│   └── test_post_api.py
├── config.yaml          # 配置文件
├── requirements.txt     # 依赖列表
├── run_tests.py         # 主运行脚本
└── README.md           # 说明文档
```

## 示例用例

框架提供了两个完整的示例测试用例：

1. **用户API测试** (`tests/test_user_api.py`)
   - 获取用户列表
   - 根据ID获取用户
   - 创建用户
   - 更新用户
   - 删除用户

2. **帖子API测试** (`tests/test_post_api.py`)
   - 获取帖子列表
   - 根据ID获取帖子
   - 创建帖子
   - 更新帖子
   - 删除帖子
   - 获取用户的所有帖子

## 高级用法

### 自定义断言

```python
from core.assertions import Assertions

class CustomAssertions(Assertions):
    def custom_assertion(self, expected):
        # 实现自定义断言逻辑
        pass
```

### 测试钩子

```python
class MyTest(TestCase):
    @TestCase.setup
    def setup_database(self):
        # 数据库初始化
        pass
    
    @TestCase.teardown
    def cleanup_database(self):
        # 数据库清理
        pass
```

### 变量管理

```python
class MyTest(TestCase):
    def test_with_variables(self):
        # 设置变量
        self.set_variable("user_id", 123)
        
        # 使用变量
        user_id = self.get_variable("user_id")
        response = self.get(f"/users/{user_id}")
```

## 故障排除

### 常见问题

1. **依赖安装失败**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **SSL证书验证失败**
   ```python
   client = HTTPClient(base_url="https://api.example.com")
   client.session.verify = False  # 不推荐生产环境使用
   ```

3. **连接超时**
   ```python
   # 在config.yaml中调整超时设置
   framework:
     timeout: 60  # 60秒超时
   ```

## 贡献指南

欢迎提交Issue和Pull Request来改进这个框架。

## 许可证

MIT License