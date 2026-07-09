import json

transcript_path = r"C:\Users\brigh\.gemini\antigravity\brain\215ee250-7011-4562-8455-115ff623acd3\.system_generated\logs\transcript.jsonl"
output_path = r"c:\Projekty\Blyskawica_V8\scratch\faza4_details.txt"

with open(transcript_path, "r", encoding="utf-8") as f, open(output_path, "w", encoding="utf-8") as out:
    for idx, line in enumerate(f):
        data = json.loads(line)
        content = data.get("content", "")
        # Check in content
        if "FAZA 4" in content or "Faza 4" in content:
            pos = content.find("FAZA 4")
            if pos == -1:
                pos = content.find("Faza 4")
            out.write(f"--- STEP {data.get('step_index')} (source: {data.get('source')}, type: {data.get('type')}) ---\n")
            out.write(content[pos:pos+2000] + "\n")
            out.write("===================================\n\n")
        
        # Check in tool calls
        tcs = data.get("tool_calls", [])
        for tc in tcs:
            args_str = json.dumps(tc.get("arguments", {}))
            if "FAZA 4" in args_str or "Faza 4" in args_str:
                pos = args_str.find("FAZA 4")
                if pos == -1:
                    pos = args_str.find("Faza 4")
                out.write(f"--- STEP {data.get('step_index')} TOOL CALL {tc.get('name')} ---\n")
                out.write(args_str[pos:pos+2000] + "\n")
                out.write("===================================\n\n")

print("Done, output written to scratch/faza4_details.txt")
