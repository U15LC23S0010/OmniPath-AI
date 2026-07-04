import json
import os

transcript_path = r"C:\Users\Lenovo\.gemini\antigravity\brain\687d32b7-f02f-4c75-ac1e-47ae6c6e5bdc\.system_generated\logs\transcript_full.jsonl"
file_states = {}

print("Starting recovery...")

try:
    with open(transcript_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
            except:
                continue
                
            if 'tool_calls' in data:
                for tc in data['tool_calls']:
                    args = tc.get('arguments', {})
                    
                    if tc['name'] == 'default_api:write_to_file':
                        if 'TargetFile' in args and 'CodeContent' in args:
                            path = args['TargetFile'].lower().replace('\\', '/')
                            file_states[path] = args['CodeContent']
                            
                    elif tc['name'] == 'default_api:replace_file_content':
                        if 'TargetFile' in args:
                            path = args['TargetFile'].lower().replace('\\', '/')
                            if path in file_states:
                                target = args.get('TargetContent', '')
                                replace = args.get('ReplacementContent', '')
                                file_states[path] = file_states[path].replace(target, replace)
                                
                    elif tc['name'] == 'default_api:multi_replace_file_content':
                        if 'TargetFile' in args:
                            path = args['TargetFile'].lower().replace('\\', '/')
                            if path in file_states:
                                chunks = args.get('ReplacementChunks', [])
                                for chunk in chunks:
                                    target = chunk.get('TargetContent', '')
                                    replace = chunk.get('ReplacementContent', '')
                                    file_states[path] = file_states[path].replace(target, replace)
                                    
except Exception as e:
    print("Error reading transcript:", e)

# Write the recovered files back
recovered = []
for path, content in file_states.items():
    if "carrerai" in path and content.strip():
        # Re-normalize path to windows for saving
        save_path = path.replace('/', '\\')
        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as out:
                out.write(content)
            recovered.append(save_path)
        except Exception as e:
            print(f"Failed to write {save_path}: {e}")

print("Recovered files:")
for r in recovered:
    print("-", r)
