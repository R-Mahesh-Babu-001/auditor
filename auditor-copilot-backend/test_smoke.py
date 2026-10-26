import requests, json, sys

BASE = "http://localhost:8000"
LLM = {"provider": "azure_openai", "model_name": "gpt-5.2-chat", "temperature": 0.2}

PASS = []
FAIL = []

def stream_test(label, url, body):
    print(f"\n=== {label} ===")
    try:
        r = requests.post(url, json=body, stream=True, timeout=40)
        print(f"Status: {r.status_code}")
        lines = []
        for line in r.iter_lines(decode_unicode=True):
            if line:
                lines.append(line)
        output = "\n".join(lines)
        if "[ERROR]" in output:
            print(f"FAIL: {output[:300]}")
            FAIL.append(label)
        elif lines:
            print(output[:400])
            PASS.append(label)
        else:
            print("FAIL: empty response")
            FAIL.append(label)
    except Exception as e:
        print(f"FAIL: {e}")
        FAIL.append(label)

def json_test(label, url, body):
    print(f"\n=== {label} ===")
    try:
        r = requests.post(url, json=body, timeout=40)
        print(f"Status: {r.status_code}")
        data = r.json()
        print(json.dumps(data, indent=2)[:400])
        if r.status_code == 200:
            PASS.append(label)
        else:
            FAIL.append(label)
    except Exception as e:
        print(f"FAIL: {e}")
        FAIL.append(label)

def get_test(label, url):
    print(f"\n=== {label} ===")
    try:
        r = requests.get(url, timeout=10)
        print(f"Status: {r.status_code}")
        print(json.dumps(r.json(), indent=2))
        PASS.append(label)
    except Exception as e:
        print(f"FAIL: {e}")
        FAIL.append(label)

# ── Health ──────────────────────────────────────────────────────────────────
get_test("GET /health", f"{BASE}/health")

# ── Chat ────────────────────────────────────────────────────────────────────
stream_test("POST /api/chat/stream",
    f"{BASE}/api/chat/stream",
    {"query": "Name 2 financial audit risks.", "llm_config": LLM})

# ── Analysis ─────────────────────────────────────────────────────────────────
stream_test("POST /api/analysis/stream",
    f"{BASE}/api/analysis/stream",
    {"scenario": "Revenue recognition variance of 15% vs budget.", "llm_config": LLM})

# ── Compliance ───────────────────────────────────────────────────────────────
stream_test("POST /api/compliance/stream",
    f"{BASE}/api/compliance/stream",
    {"query": "What IT controls apply to user access management?", "llm_config": LLM, "mode": "IT"})

json_test("POST /api/compliance/run",
    f"{BASE}/api/compliance/run",
    {"query": "List 2 SOX compliance requirements.", "llm_config": LLM, "mode": "IT"})

# ── Corporate ────────────────────────────────────────────────────────────────
stream_test("POST /api/corporate/stream",
    f"{BASE}/api/corporate/stream",
    {"query": "Summarize corporate governance best practices.", "llm_config": LLM})

# ── Documents ────────────────────────────────────────────────────────────────
stream_test("POST /api/documents/query/stream",
    f"{BASE}/api/documents/query/stream",
    {"question": "What are common internal control weaknesses?", "llm_config": LLM})

# ── SOP Flowchart ────────────────────────────────────────────────────────────
json_test("POST /api/sop/flowchart",
    f"{BASE}/api/sop/flowchart",
    {"sop_text": "Step 1: Receive invoice. Step 2: Verify against PO. Step 3: Approve payment. Step 4: Process in ERP."})

# ── Memory clear ─────────────────────────────────────────────────────────────
json_test("POST /api/memory/clear",
    f"{BASE}/api/memory/clear",
    {"agent": "chat_memory", "user_id": "test_user"})

# ── Summary ──────────────────────────────────────────────────────────────────
print(f"\n{'='*50}")
print(f"PASSED ({len(PASS)}): {', '.join(PASS)}")
if FAIL:
    print(f"FAILED ({len(FAIL)}): {', '.join(FAIL)}")
else:
    print("All tests passed!")
sys.exit(len(FAIL))
