import cv2
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

image_path = 'sample4.jpg'

# Load and preprocess image
image = cv2.imread(image_path)
if image is None:
    print("❌ Image not found or unreadable. Please check the path.")
    exit(1)

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
preprocessed_path = 'preprocessed.jpg'
cv2.imwrite(preprocessed_path, thresh)

# OCR inference
doc = DocumentFile.from_images(preprocessed_path)
model = ocr_predictor(pretrained=True)
result = model(doc)

# Extract text lines
ocr_lines = []
page = result.pages[0]
for block in page.blocks:
    for line in block.lines:
        text = ' '.join([word.value for word in line.words])
        ocr_lines.append(text)

# Save to text file
with open('ocr_output.txt', 'w', encoding='utf-8') as f:
    for line in ocr_lines:
        f.write(line + '\n')

print(f"✅ OCR text lines saved to ocr_output.txt (Total lines: {len(ocr_lines)})")
