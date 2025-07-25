import os
import json
from difflib import unified_diff

OUTPUT_DIR = 'output'
SAMPLE_DIR = 'sample_dataset/outputs'

files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.json')]

all_match = True
for fname in files:
    out_path = os.path.join(OUTPUT_DIR, fname)
    sample_path = os.path.join(SAMPLE_DIR, fname)
    if not os.path.exists(sample_path):
        print(f"Sample output missing for {fname}")
        continue
    with open(out_path, 'r', encoding='utf-8') as f:
        out_json = json.load(f)
    with open(sample_path, 'r', encoding='utf-8') as f:
        sample_json = json.load(f)
    if out_json == sample_json:
        print(f"{fname}: MATCH ✅")
    else:
        all_match = False
        print(f"{fname}: DIFFER ❌")
        # Show title diff
        if out_json.get('title') != sample_json.get('title'):
            print(f"  Title differs:\n    Output: {out_json.get('title')}\n    Sample: {sample_json.get('title')}")
        # Show outline diff (by lines)
        out_outline = json.dumps(out_json.get('outline', []), indent=2, ensure_ascii=False).splitlines()
        sample_outline = json.dumps(sample_json.get('outline', []), indent=2, ensure_ascii=False).splitlines()
        diff = list(unified_diff(sample_outline, out_outline, fromfile='sample', tofile='output', lineterm=''))
        if diff:
            print("  Outline diff:")
            for line in diff:
                print('   ', line)
if all_match:
    print("\nAll outputs match the sample outputs! 🎉")
else:
    print("\nSome outputs differ from the sample outputs. See above for details.") 