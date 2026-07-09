import json

transcript_path = r"C:\Users\brigh\.gemini\antigravity\brain\215ee250-7011-4562-8455-115ff623acd3\.system_generated\logs\transcript.jsonl"
output_path = r"c:\Projekty\Blyskawica_V8\scratch\fazas_raw.txt"

with open(transcript_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Total lines in transcript: {len(lines)}")

with open(output_path, "w", encoding="utf-8") as out:
    for idx, line in enumerate(lines):
        data = json.loads(line)
        # Check both the content and any tool calls/responses
        content_str = json.dumps(data, ensure_ascii=False)
        if "FAZA 4" in content_str or "FAZA 5" in content_str or "Faza 4" in content_str or "Faza 5" in content_str:
            out.write(f"=== STEP {data.get('step_index')} (Source: {data.get('source')}, Type: {data.get('type')}) ===\n")
            # If content is a string
            content = data.get("content")
            if content:
                out.write(f"--- CONTENT ---\n{content}\n")
            # If tool calls are present
            tcs = data.get("tool_calls", [])
            for tc in tcs:
                out.write(f"--- TOOL CALL: {tc.get('name')} ---\n")
                out.write(json.dumps(tc.get("arguments", {}), indent=2, ensure_ascii=False) + "\n")
            out.write("\n" + "="*80 + "\n\n")

print("Done scanning.")
