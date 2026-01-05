import json
import time
import os
from datetime import datetime
from typing import Dict, Any, List
from jinja2 import Template


class HTMLReporter:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_report(self, test_results: Dict[str, Any]) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_report_{timestamp}.html"
        filepath = os.path.join(self.output_dir, filename)
        
        # HTML模板
        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API测试报告 - {{ suite_name }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; border-bottom: 2px solid #eee; padding-bottom: 20px; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .summary-card { background: #f8f9fa; padding: 20px; border-radius: 6px; text-align: center; }
        .summary-card.passed { background: #d4edda; color: #155724; }
        .summary-card.failed { background: #f8d7da; color: #721c24; }
        .test-case { border: 1px solid #ddd; border-radius: 6px; margin-bottom: 15px; overflow: hidden; }
        .test-case-header { background: #f8f9fa; padding: 15px; cursor: pointer; display: flex; justify-content: between; align-items: center; }
        .test-case-header.passed { background: #d4edda; }
        .test-case-header.failed { background: #f8d7da; }
        .test-case-content { padding: 0; max-height: 0; overflow: hidden; transition: max-height 0.3s ease; }
        .test-case-content.expanded { max-height: 1000px; padding: 15px; }
        .step { margin-bottom: 10px; padding: 10px; border-left: 4px solid #007bff; background: #f8f9fa; }
        .step.passed { border-left-color: #28a745; }
        .step.failed { border-left-color: #dc3545; }
        .timestamp { color: #6c757d; font-size: 0.9em; }
        .duration { color: #6c757d; font-size: 0.9em; }
        .error { background: #f8d7da; color: #721c24; padding: 10px; border-radius: 4px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>API测试报告</h1>
            <p class="timestamp">生成时间: {{ generation_time }}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card {{ 'passed' if passed_cases > 0 else '' }}">
                <h3>通过用例</h3>
                <p style="font-size: 2em; font-weight: bold;">{{ passed_cases }}</p>
            </div>
            <div class="summary-card {{ 'failed' if failed_cases > 0 else '' }}">
                <h3>失败用例</h3>
                <p style="font-size: 2em; font-weight: bold;">{{ failed_cases }}</p>
            </div>
            <div class="summary-card">
                <h3>总用例数</h3>
                <p style="font-size: 2em; font-weight: bold;">{{ total_cases }}</p>
            </div>
            <div class="summary-card">
                <h3>执行时间</h3>
                <p style="font-size: 2em; font-weight: bold;">{{ "%.2f"|format(duration) }}s</p>
            </div>
            <div class="summary-card {{ 'passed' if passed_rate >= 80 else 'failed' if passed_rate < 50 else '' }}">
                <h3>通过率</h3>
                <p style="font-size: 2em; font-weight: bold;">{{ "%.1f"|format(passed_rate) }}%</p>
            </div>
        </div>
        
        <h2>测试用例详情</h2>
        {% for result in results %}
        <div class="test-case">
            <div class="test-case-header {{ 'passed' if result.passed else 'failed' }}" onclick="toggleTestCase({{ loop.index0 }})">
                <div>
                    <h3 style="margin: 0;">{{ result.name }}</h3>
                    <p style="margin: 5px 0 0 0;" class="duration">
                        持续时间: {{ "%.2f"|format(result.duration) }}s | 
                        步骤: {{ result.steps_passed }}/{{ result.steps_total }}
                    </p>
                </div>
                <span style="font-size: 1.5em;">{{ '✅' if result.passed else '❌' }}</span>
            </div>
            <div class="test-case-content" id="test-case-{{ loop.index0 }}">
                {% if result.error %}
                <div class="error">
                    <strong>错误信息:</strong><br>
                    {{ result.error }}
                </div>
                {% endif %}
            </div>
        </div>
        {% endfor %}
    </div>
    
    <script>
        function toggleTestCase(index) {
            const content = document.getElementById('test-case-' + index);
            content.classList.toggle('expanded');
        }
    </script>
</body>
</html>
        """
        
        # 计算通过率
        total_cases = test_results["total_cases"]
        passed_cases = test_results["passed_cases"]
        passed_rate = (passed_cases / total_cases * 100) if total_cases > 0 else 0
        
        # 渲染模板
        template = Template(html_template)
        html_content = template.render(
            suite_name=test_results["suite_name"],
            generation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_cases=total_cases,
            passed_cases=passed_cases,
            failed_cases=test_results["failed_cases"],
            duration=test_results["duration"],
            passed_rate=passed_rate,
            results=test_results["results"]
        )
        
        # 写入文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        return filepath


class JSONReporter:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_report(self, test_results: Dict[str, Any]) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_report_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        # 添加生成时间
        test_results["generation_time"] = datetime.now().isoformat()
        
        # 写入JSON文件
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        
        return filepath


class Reporter:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        self.html_reporter = HTMLReporter(output_dir)
        self.json_reporter = JSONReporter(output_dir)
    
    def generate_reports(self, test_results: Dict[str, Any]) -> Dict[str, str]:
        """生成多种格式的报告"""
        return {
            "html": self.html_reporter.generate_report(test_results),
            "json": self.json_reporter.generate_report(test_results)
        }