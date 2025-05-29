import re
import csv

# Load OCR lines
with open('ocr_output.txt', 'r', encoding='utf-8') as f:
    ocr_lines = [line.strip() for line in f.readlines()]

print(f"Total OCR lines: {len(ocr_lines)}")
print("Sample lines:")
for line in ocr_lines[:20]:
    print(f"'{line}'")

# Step 1: Extract subject codes dynamically
subject_code_pattern = re.compile(r'\b\d{2}[A-Z]{3}\d{2}\b')

subject_codes = []
for line in ocr_lines:
    matches = subject_code_pattern.findall(line)
    if len(matches) >= 3:  # heuristic: at least 3 subject codes on one line
        subject_codes = matches
        break

if not subject_codes:
    print("❌ No subject codes found, using default.")
    subject_codes = ['20MSS25', '20MSS12', '20MSS13', '20MSS14', '20MSS15', '20MSS16', '20MSS17', '20MSS18']

print("Extracted subject codes:", subject_codes)

columns = ['Register No.'] + subject_codes

rows = []
i = 0
while i < len(ocr_lines):
    line = ocr_lines[i]

    # Try to find register number with possible spaces inside digits (16 digits total)
    reg_match = re.search(r'((?:\d\s*){16})', line)
    if reg_match:
        raw_reg = reg_match.group(1)
        reg_no = ''.join(filter(str.isdigit, raw_reg))  # Clean 16-digit register no

        # Extract grades on same line after reg_no (after the matched raw_reg string)
        after_reg = line.split(raw_reg)[1].strip()
        grades = []
        if after_reg:
            candidates = after_reg.split()
            for c in candidates:
                if re.fullmatch(r'[A-Z+\-]+', c):
                    grades.append(c)

        # Collect more grades from subsequent lines until total grades == number of subjects
        j = i + 1
        while len(grades) < len(subject_codes) and j < len(ocr_lines):
            next_line = ocr_lines[j].strip()
            if re.fullmatch(r'[A-Z+\-]+', next_line):
                grades.append(next_line)
            j += 1

        if len(grades) == len(subject_codes):
            rows.append([reg_no] + grades)
            i = j  # move index forward after collected grades
        else:
            i += 1  # incomplete row, move one line forward
    else:
        i += 1

if not rows:
    print("❌ No valid table rows found.")
else:
    # Save as comma-separated CSV file
    with open('extracted_table.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)
    print(f"✅ Extracted table saved to extracted_table.csv with {len(rows)} rows")
