import json

transcript_path = r"C:\Users\brigh\.gemini\antigravity\brain\215ee250-7011-4562-8455-115ff623acd3\.system_generated\logs\transcript.jsonl"
output_path = r"c:\Projekty\Blyskawica_V8\scratch\step_list.txt"

with open(transcript_path, "r", encoding="utf-8") as f:
    with open(output_path, "w", encoding="utf-8") as out:
        for line_idx, line in enumerate(f):
            data = json.loads(line)
            step_idx = data.get("step_index")
            source = data.get("source")
            step_type = data.get("type")
            tool_calls = [tc.get("name") for tc in data.get("tool_calls", [])]
            content = data.get("content", "")
            # check if content has PLAN IMPLEMENTACJI
            has_plan = "PLAN IMPLEMENTACJI" in content or "PLAN IMPLEMENTACJI" in json.dumps(data)
            out.write(f"Line {line_idx}: Step {step_idx} ({source} - {step_type}) | Tools: {tool_calls} | HasPlan: {has_plan}\n")

print("Done listing steps.")
