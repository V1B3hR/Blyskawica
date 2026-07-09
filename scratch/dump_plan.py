import json

transcript_path = r"C:\Users\brigh\.gemini\antigravity\brain\215ee250-7011-4562-8455-115ff623acd3\.system_generated\logs\transcript.jsonl"
output_path = r"c:\Projekty\Blyskawica_V8\scratch\full_original_plan.txt"

plan_found = False
with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        if data.get("type") == "USER_INPUT":
            content = data.get("content", "")
            if "PLAN IMPLEMENTACJI" in content:
                with open(output_path, "w", encoding="utf-8") as out:
                    out.write(content)
                print("Found and dumped implementation plan to scratch/full_original_plan.txt")
                plan_found = True
                break

if not plan_found:
    print("Could not find implementation plan in USER_INPUT steps.")
