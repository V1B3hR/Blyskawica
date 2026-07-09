import json

transcript_path = r"C:\Users\brigh\.gemini\antigravity\brain\215ee250-7011-4562-8455-115ff623acd3\.system_generated\logs\transcript.jsonl"
output_path = r"c:\Projekty\Blyskawica_V8\scratch\inspect_output.txt"

with open(transcript_path, "r", encoding="utf-8") as f, open(output_path, "w", encoding="utf-8") as out:
    for i in range(20):
        line = f.readline()
        if not line:
            break
        data = json.loads(line)
        out.write(f"Keys: {list(data.keys())}\n")
        if "type" in data:
            out.write(f"Type: {data['type']}\n")
        # Let's dump the whole object structure or keys of nested elements
        for k, v in data.items():
            if isinstance(v, dict):
                out.write(f"  Dict Key: {k} -> Keys: {list(v.keys())}\n")
            elif isinstance(v, list):
                out.write(f"  List Key: {k} -> Len: {len(v)}\n")
                if len(v) > 0 and isinstance(v[0], dict):
                    out.write(f"    Item 0 Keys: {list(v[0].keys())}\n")
        out.write("-" * 40 + "\n")
