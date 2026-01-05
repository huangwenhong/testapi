#!/usr/bin/env python3
"""
API测试框架主运行脚本
"""
import argparse
import sys
import os
from core.reporter import Reporter
from tests.test_user_api import create_user_test_suite
from tests.test_post_api import create_post_test_suite
from tests.test_login_api import create_login_test_suite
from tests.test_dongjing_login_api import run_dongjing_login_tests


def main():
    parser = argparse.ArgumentParser(description='API测试框架')
    parser.add_argument('--suite', choices=['user', 'post', 'login', 'dongjing', 'all'], default='all', 
                       help='选择要运行的测试套件 (user: 用户API, post: 帖子API, login: 登录API, dongjing: 东经平台登录, all: 全部)')
    parser.add_argument('--report-dir', default='reports', 
                       help='测试报告输出目录')
    parser.add_argument('--env', choices=['dev', 'staging', 'production', 'dongjing'], default='dev',
                       help='选择测试环境')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("API测试框架启动")
    print(f"测试环境: {args.env}")
    print(f"测试套件: {args.suite}")
    print("=" * 60)
    
    # 创建测试套件
    test_suites = []
    
    if args.suite in ['user', 'all']:
        test_suites.append(create_user_test_suite())
    
    if args.suite in ['post', 'all']:
        test_suites.append(create_post_test_suite())
    
    if args.suite in ['login', 'all']:
        test_suites.append(create_login_test_suite())
    
    if args.suite in ['dongjing', 'all']:
        # 东经平台测试使用专门的运行函数
        dongjing_results = run_dongjing_login_tests()
        # 将结果转换为标准格式
        dongjing_suite_result = {
            'name': '东经平台登录测试',
            'total_cases': len(dongjing_results),
            'passed_cases': sum(1 for r in dongjing_results if r['status'] == 'PASSED'),
            'failed_cases': sum(1 for r in dongjing_results if r['status'] == 'FAILED'),
            'duration': 0,  # 东经测试不单独计算时间
            'results': [{
                'name': r['test_name'],
                'passed': r['status'] == 'PASSED',
                'steps_passed': 1 if r['status'] == 'PASSED' else 0,
                'steps_total': 1,
                'duration': 0,
                'error': r.get('error', '')
            } for r in dongjing_results]
        }
        test_suites.append(dongjing_suite_result)
    
    if not test_suites:
        print("错误: 没有找到可用的测试套件")
        sys.exit(1)
    
    # 运行测试
    all_results = []
    
    for suite in test_suites:
        print(f"\n执行测试套件: {suite['name'] if isinstance(suite, dict) else suite.name}")
        print("-" * 40)
        
        # 处理不同类型的测试套件
        if isinstance(suite, dict):
            # 东经平台测试结果已经是字典格式
            result = suite
        else:
            # 标准测试套件需要运行
            result = suite.run()
        
        all_results.append(result)
        
        # 打印套件结果
        print(f"测试用例总数: {result['total_cases']}")
        print(f"通过用例数: {result['passed_cases']}")
        print(f"失败用例数: {result['failed_cases']}")
        print(f"执行时间: {result['duration']:.2f}秒")
        
        # 打印每个用例的详细结果
        for case_result in result['results']:
            status = "✅ 通过" if case_result['passed'] else "❌ 失败"
            print(f"  {status} - {case_result['name']} "
                  f"({case_result['steps_passed']}/{case_result['steps_total']} 步骤, "
                  f"{case_result['duration']:.2f}秒)")
            
            if case_result['error']:
                print(f"    错误: {case_result['error']}")
    
    # 生成测试报告
    reporter = Reporter(args.report_dir)
    
    # 合并所有结果
    combined_result = {
        "suite_name": "综合测试报告",
        "total_cases": sum(r['total_cases'] for r in all_results),
        "passed_cases": sum(r['passed_cases'] for r in all_results),
        "failed_cases": sum(r['failed_cases'] for r in all_results),
        "duration": sum(r['duration'] for r in all_results),
        "results": [case for r in all_results for case in r['results']]
    }
    
    # 生成报告
    report_files = reporter.generate_reports(combined_result)
    
    print("\n" + "=" * 60)
    print("测试执行完成")
    print("=" * 60)
    
    # 打印总体统计
    total_cases = combined_result['total_cases']
    passed_cases = combined_result['passed_cases']
    failed_cases = combined_result['failed_cases']
    passed_rate = (passed_cases / total_cases * 100) if total_cases > 0 else 0
    
    print(f"总体统计:")
    print(f"  总用例数: {total_cases}")
    print(f"  通过用例: {passed_cases}")
    print(f"  失败用例: {failed_cases}")
    print(f"  通过率: {passed_rate:.1f}%")
    print(f"  总执行时间: {combined_result['duration']:.2f}秒")
    
    print(f"\n测试报告已生成:")
    for format_name, file_path in report_files.items():
        print(f"  {format_name.upper()}报告: {file_path}")
    
    # 返回退出码
    sys.exit(0 if failed_cases == 0 else 1)


if __name__ == "__main__":
    main()