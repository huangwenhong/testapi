import os
import yaml
import json
from typing import Dict, Any


class Config:
    def __init__(self, config_file: str = None):
        if config_file is None:
            config_dir = os.path.dirname(os.path.abspath(__file__))
            config_file = os.path.join(config_dir, "..", "config.yaml")
        self.config_file = config_file
        self.config_data = {}
        self.environments = {}
        self.test_data = {}
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config_data = yaml.safe_load(f) or {}
        else:
            self.config_data = {}
        
        # 加载环境配置
        self.environments = self.config_data.get('environments', {})
        
        # 加载测试数据
        self.test_data = self.config_data.get('test_data', {})
    
    def get_environment(self, env_name: str) -> Dict[str, Any]:
        """获取指定环境的配置"""
        return self.environments.get(env_name, {})
    
    def get_base_url(self, env_name: str) -> str:
        """获取指定环境的基础URL"""
        env_config = self.get_environment(env_name)
        return env_config.get('base_url', '')
    
    def get_headers(self, env_name: str) -> Dict[str, str]:
        """获取指定环境的请求头"""
        env_config = self.get_environment(env_name)
        return env_config.get('headers', {})
    
    def get_api_endpoint(self, env_name: str, api_name: str) -> str:
        """获取指定环境的API接口地址"""
        env_config = self.get_environment(env_name)
        apis = env_config.get('apis', {})
        return apis.get(api_name, '')
    
    def get_test_data(self, data_key: str, default: Any = None) -> Any:
        """获取测试数据，支持嵌套key（如 login_data.dongjing_group_valid）"""
        keys = data_key.split('.')
        value = self.test_data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
        
        return value if value is not None else default
    
    def set_environment(self, env_name: str, config: Dict[str, Any]):
        """设置环境配置"""
        self.environments[env_name] = config
    
    def set_test_data(self, data_key: str, data: Any):
        """设置测试数据"""
        self.test_data[data_key] = data
    
    def save_config(self):
        """保存配置到文件"""
        self.config_data['environments'] = self.environments
        self.config_data['test_data'] = self.test_data
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.config_data, f, default_flow_style=False, allow_unicode=True)


# 全局配置实例
config = Config()