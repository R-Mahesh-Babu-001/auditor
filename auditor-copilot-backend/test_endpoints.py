import requests, json

BASE = "http://localhost:8000"
LLM = {"provider": "azure_openai", "model_name": "gpt-5.2-chat", "temperature": 0.2}

tests = [
    ("analysis/stream",        "POST", f"{BASE}/api/analysis/stream",
        {"scenario": "Revenue variance 15% vs budget.", "llm_config": LLM}, True),
    ("compliance/stream",      "POST", f"{BASE}/api/compliance/stream",
        {"query": "List 2 IT access controls.", "llm_config": LLM, "mode": "IT"}, True),
    ("compliance/run",         "POST", f"{BASE}/api/compliance/run",
        {"query": "List 2 SOX requirements.", "llm_config": LLM, "mode": "IT"}, False),
    ("corporate/stream",       "POST", f"{BASE}/api/corporate/stream",
        {"query": "Corporate governance summary.", "llm_config": LLM}, True),
    ("documents/query/stream", "POST", f"{BASE}/api/documents/query/stream",
        {"question": "Common internal control weaknesses?", "llm_config": LLM}, True),
    ("sop/flowchart",          "POST", f"{BASE}/api/sop/flowchart",
        {"sop_text": "Step 1: Receive invoice. Step 2: Verify PO. Step 3: Approve payment."}, False),
    ("memory/clear",           "POST", f"{BASE}/api/memory/clear",
        {"agent": "chat_memory", "user_id": "test_user"}, False),
]

for (label, method, url, body, streaming) in tests:
    print(f"\n{'='*55}\n{label}")
    try:
        r = requests.post(url, json=body, stream=streaming, timeout=25)
        print(f"  Status: {r.status_code}")
        if streaming:
            lines = [l for l in r.iter_lines(decode_unicode=True) if l]
            out = "\n".join(lines)
            status = "FAIL" if "[ERROR]" in out or not lines else "PASS"
            print(f"  {status}: {out[:300]}")
        else:
            data = r.json()
            status = "PASS" if r.status_code == 200 else "FAIL"
            print(f"  {status}: {json.dumps(data)[:300]}")
    except Exception as e:
        print(f"  FAIL: {e}")
