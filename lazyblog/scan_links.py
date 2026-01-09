import os
import re

directory = r'd:\github\salary\lazyblog\files'

# Pattern to find the problematic links
# Looking for [ followed by * (maybe escaped), some content, and ending with * (maybe escaped) ]
# And capturing the url part too to be sure it's a link
# The broken pattern seen was [* ... \* ](url)
# The valid but maybe unwanted pattern is [* ... *](url)

# Regex explanation:
# \[             Literal [
# \s*            Optional whitespace
# \\?\*          Literal * or escaped \*
# ([\s\S]*?)     Capture content (non-greedy, including newlines)
# \\?\*          Literal * or escaped \*
# \s*            Optional whitespace
# \]             Literal ]
# \(             Literal (
# (.*?)          Capture URL
# \)             Literal )

pattern = re.compile(r'\[\s*\\?\*([\s\S]*?)\\?\*\s*\]\((.*?)\)', re.MULTILINE)

for filename in os.listdir(directory):
    if filename.endswith(".md"):
        filepath = os.path.join(directory, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            matches = pattern.findall(content)
            if matches:
                print(f"File: {filename}")
                for text, url in matches:
                    print(f"  Found: [{text.strip()[:20]}...]({url[:20]}...)")
        except Exception as e:
            print(f"Error reading {filename}: {e}")
