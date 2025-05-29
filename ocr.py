import streamlit as st
import cv2
import tempfile
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

# Initialize model once
model = ocr_predictor(pretrained=True)

st.set_page_config(page_title="OCR App", layout="wide")
st.title("📝 Multi-Image OCR App")

uploaded_files = st.file_uploader(
    "Upload image files (JPG, PNG, TIFF)...",
    type=["jpg", "jpeg", "png", "tiff"],
    accept_multiple_files=True
)

if uploaded_files:
    ocr_output = []

    for uploaded_file in uploaded_files:
        # Save uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        # Read and preprocess image
        image = cv2.imread(tmp_path)
        if image is None:
            st.warning(f"⚠️ Could not read {uploaded_file.name}")
            continue

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Save preprocessed image for OCR
        preprocessed_path = tmp_path.replace('.jpg', '_preprocessed.jpg')
        cv2.imwrite(preprocessed_path, thresh)

        # Run OCR
        doc = DocumentFile.from_images(preprocessed_path)
        result = model(doc)

        # Extract text
        ocr_lines = []
        page = result.pages[0]
        for block in page.blocks:
            for line in block.lines:
                text = ' '.join([word.value for word in line.words])
                ocr_lines.append(text)

        ocr_text = "\n".join(ocr_lines)
        ocr_output.append((uploaded_file.name, ocr_text))

        # Display OCR result
        st.subheader(f"📄 OCR Result for: {uploaded_file.name}")
        st.text_area("Extracted Text:", ocr_text, height=200)

    # Save all results to a text file
    if st.button("💾 Download Combined OCR Output"):
        combined_text = ""
        for filename, text in ocr_output:
            combined_text += f"=== {filename} ===\n{text}\n\n"

        st.download_button(
            label="📥 Download as TXT",
            data=combined_text,
            file_name="ocr_output.txt",
            mime="text/plain"
        )
