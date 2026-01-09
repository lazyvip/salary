import os
import re

directory = r'd:\github\salary\lazyblog\files'

# Regex to match links that are wrapped in * or ** or \* inside the brackets
# We want to capture the inner text and the url
# Pattern details:
# \[                 Literal [
# \s*                Leading whitespace inside bracket
# (?:\\?\*)+         One or more stars (literal * or escaped \*)
# ([\s\S]*?)         Group 1: The link text content (non-greedy)
# (?:\\?\*)+         One or more stars (literal * or escaped \*)
# \s*                Trailing whitespace inside bracket
# \]                 Literal ]
# \(                 Literal (
# (.*?)              Group 2: The URL
# \)                 Literal )

pattern = re.compile(r'\[\s*(?:\\?\*)+([\s\S]*?)(?:\\?\*)+\s*\]\((.*?)\)', re.MULTILINE)

def replace_func(match):
    text = match.group(1).strip()
    url = match.group(2).strip()
    return f"[{text}]({url})"

count = 0
for filename in os.listdir(directory):
    if filename.endswith(".md"):
        filepath = os.path.join(directory, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content, n = pattern.subn(replace_func, content)
            
            if n > 0:
                print(f"Fixing {n} links in {filename}")
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                count += n
        except Exception as e:
            print(f"Error processing {filename}: {e}")

print(f"Total links fixed: {count}")
