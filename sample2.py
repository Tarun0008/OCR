import easyocr
import cv2
import pandas as pd
import re

# Load the image
image_path = 'sample2.jpg'
image = cv2.imread(image_path)

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Perform OCR
results = reader.readtext(image_path)

# Extract bounding boxes and text
ocr_data = [(res[0], res[1]) for res in results]

# Known subject codes (from the image)
subject_codes = ['20MSS11', '20MSS12', '20MSS13', '20MSS14', '20MSS15', '20MSS16', '20MSS17', '20MSS18']
columns = ['Register No.'] + subject_codes

# Step 1: Filter all texts that match register numbers (11-digit numbers)
rows = []
for i in range(len(ocr_data)):
    _, text = ocr_data[i]
    if re.fullmatch(r'\d{16}', text):
        reg_no = text
        grades = []
        j = i + 1
        while len(grades) < 8 and j < len(ocr_data):
            next_text = ocr_data[j][1]
            # Accept grade-like entries only
            if re.fullmatch(r'[AOBUWF+\-]+', next_text):
                grades.append(next_text)
            j += 1
        if len(grades) == 8:
            rows.append([reg_no] + grades)

# Step 2: Create DataFrame
df = pd.DataFrame(rows, columns=columns)

# Step 3: Save to Excel
output_path = 'parsed_results.xlsx'
df.to_excel(output_path, index=False)
print(f"✅ Data extracted and saved to {output_path}")
