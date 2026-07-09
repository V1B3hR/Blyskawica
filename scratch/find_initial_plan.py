import json

transcript_path = r"C:\Users\brigh\.gemini\antigravity\brain\215ee250-7011-4562-8455-115ff623acd3\.system_generated\logs\transcript.jsonl"
output_path = r"c:\Projekty\Blyskawica_V8\scratch\initial_plans.txt"

with open(transcript_path, "r", encoding="utf-8") as f, open(output_path, "w", encoding="utf-8") as out:
    for idx, line in enumerate(f):
        data = json.loads(line)
        tcs = data.get("tool_calls", [])
        for tc in tcs:
            args_str = json.dumps(tc.get("arguments", {}), ensure_ascii=False)
            if "FAZA 4" in args_str or "Faza 4" in args_str:
                out.write(f"=== STEP {data.get('step_index')} {tc.get('name')} ===\n")
                out.write(args_str + "\n")
                out.write("==================================================\n\n")

print("Done scanning for Faza 4 in tool calls.")
