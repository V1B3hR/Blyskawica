import json

transcript_path = r"C:\Users\brigh\.gemini\antigravity\brain\215ee250-7011-4562-8455-115ff623acd3\.system_generated\logs\transcript.jsonl"
output_path = r"c:\Projekty\Blyskawica_V8\scratch\plan_output_all.txt"

matches = []
with open(transcript_path, "r", encoding="utf-8") as f:
    for line_idx, line in enumerate(f):
        data = json.loads(line)
        content = json.dumps(data)
        if "PLAN IMPLEMENTACJI" in content:
            # We want to save the step details and the content
            matches.append({
                "step_index": data.get("step_index"),
                "source": data.get("source"),
                "type": data.get("type"),
                "content": data.get("content", ""),
                "tool_calls": data.get("tool_calls", [])
            })

with open(output_path, "w", encoding="utf-8") as out:
    for match in matches:
        out.write(f"=== STEP {match['step_index']} ({match['source']} - {match['type']}) ===\n")
        out.write(f"Content: {match['content']}\n")
        if match['tool_calls']:
            out.write(f"Tool Calls: {json.dumps(match['tool_calls'], indent=2)}\n")
        out.write("\n" + "="*50 + "\n\n")

print(f"Found {len(matches)} matches. Written to plan_output_all.txt")
