#!/usr/bin/env python3
"""
东经平台登录测试脚本
"""
from tests.test_dongjing_login_api import run_dongjing_login_tests


def main():
    print("开始执行东经平台登录测试...")
    print("=" * 60)
    
    results = run_dongjing_login_tests()
    
    print("\n东经平台登录测试结果:")
    print("-" * 40)
    
    passed = 0
    failed = 0
    
    for result in results:
        status = "✅ 通过" if result['status'] == 'PASSED' else "❌ 失败"
        print(f"{status} - {result['test_name']}")
        
        if result['status'] == 'PASSED':
            passed += 1
        else:
            failed += 1
            if 'error' in result:
                print(f"    错误: {result['error']}")
    
    print("-" * 40)
    print(f"总测试用例: {len(results)}")
    print(f"通过用例: {passed}")
    print(f"失败用例: {failed}")
    print(f"通过率: {passed/len(results)*100:.1f}%")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(main())