import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
import os
import json
import requests  # pyright: ignore[reportMissingModuleSource]
from urllib.parse import urlparse, parse_qs
from typing import Optional, List, Dict, Any, Tuple
import re
import traceback
from evaluator import AnswerRelevanceEvaluator
url = "https://suppliertest.cpsol.net/djauth/cas/weblogin.do"
url1 = "https://suppliertest.cpsol.net/djauth/cas/new/casTokenLogin.do"
url2="https://suppliertest.cpsol.net/djauth/cas/exchangetoken.do"

url3= "https://smart.cpsol.net/djintelligent/ai-backend/ai/v2/submitStream.do"
base_headers = {"Content-Type": "application/json"}
payload = {
    "userName": "4000001",
    "password": "8521f5a31b6d92af9c5004e33229db8f",
    "appName": "DJSUPPLIER",
}
class GetRes:
    def load_test_cases(path: str) -> List[Dict[str, Any]]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("test_cases.json 必须是 JSON 数组(list)")
        return data


    def select_cases(cases: List[Dict[str, Any]], case_id: Optional[int]) -> List[Dict[str, Any]]:
        if case_id is None:
            return cases
        picked = [c for c in cases if c.get("id") == case_id]
        if not picked:
            raise ValueError(f"未找到 id={case_id} 的用例")
        return picked

    def _extract_query_param_from_url(u: str, key: str) -> Optional[str]:
        qs = parse_qs(urlparse(u).query)
        return qs.get(key, [None])[0]

    def _print_req_resp(tag: str, r: requests.Response) -> None:
        # 兼容流式响应（text/event-stream）与普通 JSON
        ctype = (r.headers.get("content-type") or "").lower()
        if "application/json" in ctype:
            try:

                return
            except Exception:
                pass


    def read_submit_stream_text(r: requests.Response) -> str:
        """
        从 submitStream 的流式响应中提取/拼接“文本内容”。

        兼容两类常见返回：
        - SSE(text/event-stream): 每行形如 "data: {...json...}" 或直接是 JSON
        - 非流式：直接 JSON/纯文本
        """
        ctype = (r.headers.get("content-type") or "").lower()

        # 非 SSE：直接按 json/text 取
        if "text/event-stream" not in ctype:
            if "application/json" in ctype:
                try:
                    obj = r.json()
                    # 兜底：尽量从常见字段里找文本
                    for k in ("text", "answer", "content", "message"):
                        if isinstance(obj, dict) and k in obj and isinstance(obj[k], str):
                            return obj[k]
                    return json.dumps(obj, ensure_ascii=False)
                except Exception:
                    return r.text
            return r.text

        # SSE：流式逐行拼接
        r.encoding = "utf-8"
        pieces: List[str] = []

        for raw_line in r.iter_lines(decode_unicode=True):
            if not raw_line:
                continue
            line = raw_line.strip()
            # SSE 标准：data: xxxx
            if line.startswith("data:"):
                line = line[len("data:"):].strip()
            # 常见结束标记
            if line in ("[DONE]", "DONE"):
                break

            # data 可能是 JSON，也可能直接是文本
            try:
                evt = json.loads(line)
                # 尽量覆盖常见流式结构：choices[0].delta.content / delta / content / text
                if isinstance(evt, dict):
                    # OpenAI 风格
                    choices = evt.get("choices")
                    if isinstance(choices, list) and choices:
                        c0 = choices[0] if isinstance(choices[0], dict) else None
                        if c0:
                            delta = c0.get("delta") if isinstance(c0.get("delta"), dict) else None
                            if delta and isinstance(delta.get("content"), str):
                                pieces.append(delta["content"])
                                continue
                            if isinstance(c0.get("content"), str):
                                pieces.append(c0["content"])
                                continue
                    # 其他常见字段
                    for k in ("content", "text", "answer", "message"):
                        if isinstance(evt.get(k), str):
                            pieces.append(evt[k])
                            break
                else:
                    pieces.append(str(evt))
            except Exception:
                pieces.append(line)

        return "".join(pieces)


    def extract_complete_analysis_text(s: str) -> str:
        """
        处理你贴的这种内容：
        - 前面夹杂大量 'event:send'
        - 末尾有 'event:complete<analysis>...'

        目标：截取 complete 的 <analysis> 里的文本（没有 </analysis> 也能兜底）。
        """
        if not s:
            return ""
        # 先把反复出现的 event:send 清掉（你这个流里几乎每个 token 前都有它）
        s = s.replace("event:send", "")

        # 优先截取 event:complete 后面的内容
        idx = s.find("event:complete")
        if idx >= 0:
            s = s[idx + len("event:complete") :]

        # 截取 <analysis>...</analysis> 或 <analysis>...（兜底）
        m = re.search(r"<analysis>(.*?)(?:</analysis>|$)", s, flags=re.S)
        if m:
            return m.group(1).strip()

        # 再兜底：没有 <analysis> 标签就直接返回剩余文本
        return s.strip()


def login_and_get_token() -> Tuple[requests.Session, str]:
    """
    登录并获取 token
    返回: (session, token)
    """
    s = requests.Session()
    
    # 1) weblogin：拿 onceToken
    resp = s.post(url, headers=base_headers, json=payload, timeout=60)
    GetRes._print_req_resp("weblogin", resp)
    data0 = resp.json()
    u0 = data0["data"]["url"]
    once_token = GetRes._extract_query_param_from_url(u0, "onceToken")
    if not once_token:
        raise RuntimeError("未从 weblogin 的 url 中解析到 onceToken")
    
    # 2) casTokenLogin：通常会返回新的跳转 url / token / cookie（按实际响应解析）
    payload1 = {"onceToken": once_token, "appName": "DJSUPPLIER"}
    resp1 = s.post(url1, headers=base_headers, json=payload1, timeout=60)
    GetRes._print_req_resp("casTokenLogin", resp1)
    data1 = resp1.json()
    u1 = (data1.get("data") or {}).get("url") or (data1.get("data") or {}).get("loginUrl") or ""
    once_token1 = GetRes._extract_query_param_from_url(u1, "onceToken") if u1 else None
    
    # 3) exchangetoken：把 token 换成业务侧可用的 token（常见字段：token/accessToken/jwt…）
    payload2 = {"onceToken": once_token1 or once_token, "appName": "DJSUPPLIER"}
    resp2 = s.post(url2, headers=base_headers, json=payload2, timeout=60)
    GetRes._print_req_resp("exchangetoken", resp2)
    data2 = resp2.json()
    token = (
        (data2.get("data") or {}).get("token")
        or (data2.get("data") or {}).get("accessToken")
        or (data2.get("data") or {}).get("jwt")
    )
    
    # 有些系统不在 JSON 里返回 token，而是通过 Set-Cookie 下发
    cookie_token = s.cookies.get("token") or resp2.cookies.get("token")
    if not token and cookie_token:
        token = cookie_token
    
    return s, token


def build_headers_with_token(token: str) -> Dict[str, str]:
    """
    构建包含 token 的请求头
    """
    headers3 = {
        "Content-Type": "application/json",
        "appName": "DJINTELLIGENT",
    }
    if token:
        headers3["Authorization"] = f"Bearer {token}"
        headers3["Cookie"] = f"token={token}; appName=DJINTELLIGENT"
    return headers3


def main(case_id: Optional[int] = None):
    """批量评估主函数"""
    if case_id is None and len(sys.argv) >= 2 and sys.argv[1].strip():
        case_id = int(sys.argv[1])
    
    test_cases_path = os.path.join(os.path.dirname(__file__), "generated_test_cases.json")
    cases = GetRes.select_cases(GetRes.load_test_cases(test_cases_path), case_id)
    evaluator = AnswerRelevanceEvaluator()
    
    # 登录获取 token
    s, token = login_and_get_token()
    headers3 = build_headers_with_token(token)
    
    try:
        results: List[Dict[str, Any]] = []
        for case in cases:
            query = case.get("question") or ""
            payload3 = {
                "query": query,
                "inputs": {"type": "sql_tool", "supplier_id": "", "org_id": "", "role": "manage"},
            }
            resp3 = s.post(url3, headers=headers3, json=payload3, timeout=(60, 300), stream=True)
            GetRes._print_req_resp(f"submitStream(id={case.get('id')})", resp3)
            final_text = GetRes.read_submit_stream_text(resp3)
            answer = GetRes.extract_complete_analysis_text(final_text)
            single_result = evaluator.evaluate_single_pair(query, answer)
            merged = {
                "id": case.get("id"),
                "question": query,
                "keywords": case.get("keywords"),
                "answer": answer,
                **single_result,
            }
            results.append(merged)
            print("\n=== 单条评估结果 ===")
            print(json.dumps(merged, indent=2, ensure_ascii=False))
        print("\n=== 批量评估汇总 ===")
        print(json.dumps(results, indent=2, ensure_ascii=False))
    except Exception:
        traceback.print_exc()
        raise


if __name__ == "__main__":
    # 批量评估（取消注释以运行）
    main()
    
    # 测试代码：写死 query 进行单元测试
    # 1. 登录获取 token
    # s, token = login_and_get_token()
    # headers3 = build_headers_with_token(token)
    
    # # 2. 写死 query 进行测试
    # query = "温州东诚包装有限公司根组织的青田三本供应商本月日均接单数据"  # 写死的测试 query
    # payload3 = {
    #     "query": query,
    #     "inputs": {"type": "sql_tool", "supplier_id": "", "org_id": "", "role": "manage"},
    # }
    
    # # 3. 调用接口并打印结果
    # print(f"\n=== 测试 Query ===")
    # print(f"Query: {query}\n")
    
    # resp3 = s.post(url3, headers=headers3, json=payload3, timeout=(60, 300), stream=True)
    # GetRes._print_req_resp("submitStream(测试)", resp3)
    # final_text = GetRes.read_submit_stream_text(resp3)
    # answer = GetRes.extract_complete_analysis_text(final_text)
    
    # print(f"\n=== 测试结果 ===")
    # print(f"Answer: {answer}")
