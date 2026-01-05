import inspect
import time
from typing import Dict, Any, List, Optional, Callable
from .http_client import HTTPClient, ResponseWrapper
from .assertions import AssertionChain, AssertionError


class TestStep:
    def __init__(self, name: str, action: Callable, **kwargs):
        self.name = name
        self.action = action
        self.kwargs = kwargs
        self.result = None
        self.duration = 0
        self.error = None


class TestCase:
    def __init__(self, name: str, base_url: str = ""):
        self.name = name
        self.base_url = base_url
        self.client = HTTPClient(base_url)
        self.steps: List[TestStep] = []
        self.setup_hooks: List[Callable] = []
        self.teardown_hooks: List[Callable] = []
        self.variables: Dict[str, Any] = {}
        self.start_time = 0
        self.end_time = 0
        self.passed = False
        self.error = None
    
    def setup(self, func: Callable = None):
        if func is not None:
            self.setup_hooks.append(func)
            return func
        else:
            for hook in self.setup_hooks:
                hook(self)
    
    def teardown(self, func: Callable = None):
        if func is not None:
            self.teardown_hooks.append(func)
            return func
        else:
            for hook in self.teardown_hooks:
                hook(self)
    
    def set_variable(self, key: str, value: Any):
        self.variables[key] = value
    
    def get_variable(self, key: str, default: Any = None) -> Any:
        return self.variables.get(key, default)
    
    def request(self, method: str, endpoint: str, **kwargs) -> ResponseWrapper:
        step_name = f"{method.upper()} {endpoint}"
        
        def action():
            response = self.client.request(method, endpoint, **kwargs)
            return ResponseWrapper(response)
        
        return self._add_step(step_name, action)
    
    def get(self, endpoint: str, **kwargs) -> ResponseWrapper:
        return self.request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> ResponseWrapper:
        return self.request("POST", endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> ResponseWrapper:
        return self.request("PUT", endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> ResponseWrapper:
        return self.request("DELETE", endpoint, **kwargs)
    
    def step(self, name: str) -> Callable:
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                return self._add_step(name, lambda: func(*args, **kwargs))
            return wrapper
        return decorator
    
    def _add_step(self, name: str, action: Callable) -> Any:
        step = TestStep(name, action)
        self.steps.append(step)
        
        start_time = time.time()
        try:
            result = action()
            step.duration = time.time() - start_time
            step.result = result
            return result
        except Exception as e:
            step.duration = time.time() - start_time
            step.error = e
            raise
    
    def assert_that(self, response: ResponseWrapper) -> AssertionChain:
        return AssertionChain(response)
    
    def run(self) -> bool:
        self.start_time = time.time()
        
        try:
            # 执行前置钩子
            for hook in self.setup_hooks:
                hook(self)
            
            # 执行测试步骤
            for step in self.steps:
                step_start = time.time()
                try:
                    step.result = step.action()
                    step.duration = time.time() - step_start
                except Exception as e:
                    step.duration = time.time() - step_start
                    step.error = e
                    self.error = e
                    self.passed = False
                    break
            else:
                self.passed = True
            
            # 执行后置钩子
            for hook in self.teardown_hooks:
                try:
                    hook(self)
                except Exception as e:
                    if self.passed:
                        self.error = e
                        self.passed = False
        
        except Exception as e:
            self.error = e
            self.passed = False
        
        finally:
            self.end_time = time.time()
            self.client.close()
        
        return self.passed
    
    def get_duration(self) -> float:
        return self.end_time - self.start_time
    
    def get_summary(self) -> Dict[str, Any]:
        passed_steps = len([s for s in self.steps if s.error is None])
        total_steps = len(self.steps)
        
        return {
            "name": self.name,
            "passed": self.passed,
            "duration": self.get_duration(),
            "steps_passed": passed_steps,
            "steps_total": total_steps,
            "error": str(self.error) if self.error else None
        }


class TestSuite:
    def __init__(self, name: str):
        self.name = name
        self.test_cases: List[TestCase] = []
        self.setup_hooks: List[Callable] = []
        self.teardown_hooks: List[Callable] = []
    
    def add_test_case(self, test_case: TestCase):
        self.test_cases.append(test_case)
    
    def setup(self, func: Callable) -> Callable:
        self.setup_hooks.append(func)
        return func
    
    def teardown(self, func: Callable) -> Callable:
        self.teardown_hooks.append(func)
        return func
    
    def run(self) -> Dict[str, Any]:
        results = {
            "suite_name": self.name,
            "total_cases": len(self.test_cases),
            "passed_cases": 0,
            "failed_cases": 0,
            "start_time": time.time(),
            "results": []
        }
        
        # 执行套件前置钩子
        for hook in self.setup_hooks:
            hook()
        
        # 执行测试用例
        for test_case in self.test_cases:
            passed = test_case.run()
            
            if passed:
                results["passed_cases"] += 1
            else:
                results["failed_cases"] += 1
            
            results["results"].append(test_case.get_summary())
        
        # 执行套件后置钩子
        for hook in self.teardown_hooks:
            try:
                hook()
            except Exception:
                pass
        
        results["end_time"] = time.time()
        results["duration"] = results["end_time"] - results["start_time"]
        
        return results