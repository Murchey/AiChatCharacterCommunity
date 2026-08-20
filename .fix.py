path = r"d:\Projects\vibecoding\AiChatCharacterCommunity\.github\workflows\release.yml"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find and fix the problematic lines (around line 293)
fixed_lines = []
skip_next = False
for i, line in enumerate(lines):
    if skip_next:
        skip_next = False
        continue
    
    # Check for broken tr command - line ends with $('\n
    if "chinese_name=$('" == line.rstrip("\n"):
        # Merge with next line to form correct command
        if i + 1 < len(lines):
            next_line = lines[i+1]
            # Combine them into one line: chinese_name=$(tr -d '\n\r' < "$txt_file")
            combined = '            chinese_name=$(tr -d \'\\n\\r\' < "$txt_file")\n'
            fixed_lines.append(combined)
            skip_next = True
            print(f"Fixed lines {i+1}-{i+2}")
        else:
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.writelines(fixed_lines)

print(f"Done! Total lines: {len(fixed_lines)}")

# Verify
with open(path, "r", encoding="utf-8") as f:
    all_lines = f.readlines()
for i in range(290, min(300, len(all_lines))):
    print(f"Line {i+1}: {repr(all_lines[i])}")
