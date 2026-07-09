import json

transcript_path = r"C:\Users\brigh\.gemini\antigravity\brain\215ee250-7011-4562-8455-115ff623acd3\.system_generated\logs\transcript.jsonl"
output_path = r"c:\Projekty\Blyskawica_V8\scratch\faza_anywhere.txt"

with open(transcript_path, "r", encoding="utf-8") as f, open(output_path, "w", encoding="utf-8") as out:
    for idx, line in enumerate(f):
        data = json.loads(line)
        content = data.get("content", "")
        # search for FAZA 3 or FAZA 4 in content
        if "FAZA 3" in content or "FAZA 4" in content or "Faza 3" in content or "Faza 4" in content:
            out.write(f"--- LINE {idx} STEP {data.get('step_index')} ({data.get('source')}, {data.get('type')}) ---\n")
            out.write(content + "\n")
            out.write("===================================\n\n")
            
        tcs = data.get("tool_calls", [])
        for tc in tcs:
            args_str = json.dumps(tc.get("arguments", {}))
            if "FAZA 3" in args_str or "FAZA 4" in args_str or "Faza 3" in args_str or "Faza 4" in args_str:
                out.write(f"--- LINE {idx} STEP {data.get('step_index')} TOOL CALL {tc.get('name')} ---\n")
                out.write(args_str + "\n")
                out.write("===================================\n\n")

print("Done scanning for FAZA 3 and 4.")
