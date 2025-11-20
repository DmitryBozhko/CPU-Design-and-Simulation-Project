import os
import json

def count_ai_lines(directory="src"):
    total_lines = 0
    ai_lines = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                    lines = content.split('\n')
                    total_lines += len(lines)
                    in_ai_block = False
                    for line in lines:
                        if '# AI-BEGIN' in line or '#AI-BEGIN' in line:
                            in_ai_block = True
                        elif '# AI-END' in line or '#AI-END' in line:
                            in_ai_block = False
                        elif in_ai_block:
                            ai_lines += 1
    report = {
        "total_lines": total_lines,
        "ai_tagged_lines": ai_lines,
        "percent": round((ai_lines / total_lines * 100), 1) if total_lines > 0 else 0,
        "tools": ["Claude, ChatGPT, Codex(This one didn't help much)"],
        "method": "count markers (AI-BEGIN/AI-END comments)"
    }
    with open('ai_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print(f"Total lines: {total_lines}")
    print(f"AI-tagged lines: {ai_lines}")
    print(f"Percentage: {report['percent']}%")
    print(f"\nReport saved to ai_report.json")


if __name__ == "__main__":
    count_ai_lines()