!pip install streamlit
!pip install pytesseract
import streamlit as st
from PIL import Image
import pytesseract

st.set_page_config(
    page_title="Image to Text Converter",
    page_icon="📝"
)

st.title("📝 Image to Text Converter")
st.write("Upload an image and extract the text from it using OCR.")

uploaded_file = st.file_uploader(
    "Choose an image",
    type=["png", "jpg", "jpeg", "webp"]
)

if uploaded_file:
    image = Image.open(uploaded_file)

    st.subheader("Uploaded Image")
    st.image(image, caption="Your image", use_container_width=True)

    if st.button("Extract Text"):
        with st.spinner("Extracting text..."):
            text = pytesseract.image_to_string(image)

        st.subheader("Extracted Text")

        if text.strip():
            st.text_area(
                "OCR Result",
                text,
                height=300
            )

            st.download_button(
                label="Download Text",
                data=text,
                file_name="extracted_text.txt",
                mime="text/plain"
            )
        else:
            st.warning("No text could be detected in the image.")
