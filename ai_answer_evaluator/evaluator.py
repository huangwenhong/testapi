import sys
sys.stdout.reconfigure(encoding="utf-8")
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd  # 用于优雅地处理结果

# 1. 加载环境变量中的API密钥
load_dotenv()

class AnswerRelevanceEvaluator:
    def __init__(self, model=None):
        """
        DeepSeek（OpenAI 兼容）用法：
        - API Key：优先读取 DEEPSEEK_API_KEY，其次读取 OPENAI_API_KEY
        - Base URL：优先读取 DEEPSEEK_BASE_URL，其次读取 OPENAI_BASE_URL，默认 https://api.deepseek.com
        """
        api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = (
            os.getenv("DEEPSEEK_BASE_URL")
            or os.getenv("OPENAI_BASE_URL")
            or "https://api.deepseek.com"
        )

        if not api_key:
            raise RuntimeError(
                "未检测到 API Key。请在环境变量或 .env 中设置 DEEPSEEK_API_KEY（推荐）或 OPENAI_API_KEY。"
            )

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model or os.getenv("DEEPSEEK_MODEL") or "deepseek-chat"
        # 2. 定义评估提示词（System Prompt）
        self.evaluation_prompt = """你是一个专业的问答质量评估专家。请严格评估给定的“答案”是否直接、相关且有效地回答了“问题”。

评估标准：
1. **相关性**：答案是否直接回应了问题的核心意图？避免答非所问或回避问题。
2. **有用性**：答案是否提供了解决问题或满足查询需求的具体、有价值的信息？
3. **是否包含幻觉**：答案是否包含了明显的事实错误或编造的信息？

请基于以上三点，对以下问答对进行评估。

{format_instructions}

问题：{question}
答案：{answer}
"""
        # 3. 定义输出格式（让LLM返回结构化JSON）
        self.format_instructions = """
你必须以以下严格的JSON格式输出评估结果，不要有任何其他文字：
{
  "relevance": "是/否/部分相关",
  "usefulness": "是/否",
  "hallucination": "是/否",
  "confidence": 一个介于0到1之间的数字，表示你对此评估的置信度,
  "reason": "一段简要的解释，说明评估依据"
}
"""

    def evaluate_single_pair(self, question, answer):
        """评估单个问答对"""
        try:
            # 构造完整的用户提示词
            user_prompt = self.evaluation_prompt.format(
                format_instructions=self.format_instructions,
                question=question,
                answer=answer
            )
            
            # 调用LLM API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个只输出JSON的评估助手。"},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,  # 温度设为0，使输出尽可能确定
                response_format={"type": "json_object"}  # 强制JSON输出
            )
            
            # 解析返回的JSON
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"评估过程中出错: {e}")
            return {
                "relevance": "错误",
                "usefulness": "错误",
                "hallucination": "错误",
                "confidence": 0.0,
                "reason": f"API调用失败: {str(e)}"
            }

    def evaluate_batch(self, test_cases):
        """批量评估多个问答对"""
        results = []
        for case in test_cases:
            eval_result = self.evaluate_single_pair(case["question"], case["answer"])
            # 将原始数据和评估结果合并
            combined = {**case, **eval_result}
            results.append(combined)
            # 打印进度（可选）
            print(f"已评估: Q: {case['question'][:50]}... -> 相关性: {eval_result['relevance']}")
        return results

if __name__ == "__main__":
    # 示例：直接测试一个问答对
    evaluator = AnswerRelevanceEvaluator()
    
    #test_question = "Python中如何读取一个JSON文件？"
    #test_answer = "使用内置的json模块，例如：import json; with open('data.json') as f: data = json.load(f)"
    
    single_result = evaluator.evaluate_single_pair(test_question, test_answer)
    print("\n=== 单条评估结果 ===")
    print(json.dumps(single_result, indent=2, ensure_ascii=False))