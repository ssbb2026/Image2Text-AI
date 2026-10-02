
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract
import pandas as pd
import numpy as np


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Image to Text Converter",
    page_icon="📝",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("📝 AI Image to Text Converter")

st.write(
    "Upload an image, crop or enhance it, and extract text using OCR."
)


# ============================================================
# SIDEBAR SETTINGS
# ============================================================

st.sidebar.header("⚙️ Image Processing")


# Rotation
rotation = st.sidebar.slider(
    "Rotate Image",
    min_value=-180,
    max_value=180,
    value=0,
    step=1
)


# Grayscale
grayscale = st.sidebar.checkbox(
    "Convert to Grayscale",
    value=False
)


# Contrast
contrast = st.sidebar.slider(
    "Contrast",
    min_value=0.5,
    max_value=3.0,
    value=1.0,
    step=0.1
)


# Sharpness
sharpness = st.sidebar.slider(
    "Sharpness",
    min_value=0.5,
    max_value=3.0,
    value=1.0,
    step=0.1
)


# Threshold
threshold_enabled = st.sidebar.checkbox(
    "Apply Black & White Threshold",
    value=False
)

threshold_value = st.sidebar.slider(
    "Threshold Value",
    min_value=50,
    max_value=250,
    value=150,
    step=5,
    disabled=not threshold_enabled
)


# OCR Page Segmentation Mode
st.sidebar.header("🔍 OCR Settings")

psm_options = {
    "Automatic": 3,
    "Single Text Block": 6,
    "Single Line": 7,
    "Single Word": 8,
    "Sparse Text": 11,
    "Sparse Text with OSD": 12
}

psm_name = st.sidebar.selectbox(
    "OCR Page Segmentation Mode",
    list(psm_options.keys())
)

psm_value = psm_options[psm_name]


# ============================================================
# FILE UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "📤 Upload an image",
    type=["png", "jpg", "jpeg", "webp", "bmp", "tiff"]
)


# ============================================================
# PROCESS IMAGE
# ============================================================

if uploaded_file:

    original_image = Image.open(uploaded_file)

    # Convert to RGB
    if original_image.mode != "RGB":
        original_image = original_image.convert("RGB")


    # --------------------------------------------------------
    # IMAGE INFORMATION
    # --------------------------------------------------------

    st.subheader("📊 Image Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Width",
            f"{original_image.width}px"
        )

    with col2:
        st.metric(
            "Height",
            f"{original_image.height}px"
        )

    with col3:
        st.metric(
            "File Size",
            f"{uploaded_file.size / 1024:.1f} KB"
        )


    # ========================================================
    # CROP SECTION
    # ========================================================

    st.subheader("✂️ Crop Image")

    st.write(
        "Use the sliders below to select the region containing text."
    )

    width = original_image.width
    height = original_image.height


    col1, col2 = st.columns(2)

    with col1:

        left = st.slider(
            "Left",
            0,
            width,
            0
        )

        right = st.slider(
            "Right",
            0,
            width,
            width
        )


    with col2:

        top = st.slider(
            "Top",
            0,
            height,
            0
        )

        bottom = st.slider(
            "Bottom",
            0,
            height,
            height
        )


    # Make sure coordinates are valid

    if right <= left:
        right = width

    if bottom <= top:
        bottom = height


    cropped_image = original_image.crop(
        (left, top, right, bottom)
    )


    # ========================================================
    # IMAGE PREPROCESSING
    # ========================================================

    processed_image = cropped_image.copy()


    # Rotation
    if rotation != 0:
        processed_image = processed_image.rotate(
            rotation,
            expand=True
        )


    # Grayscale
    if grayscale:
        processed_image = ImageOps.grayscale(
            processed_image
        )


    # Contrast
    if contrast != 1.0:
        processed_image = ImageEnhance.Contrast(
            processed_image
        ).enhance(contrast)


    # Sharpness
    if sharpness != 1.0:
        processed_image = ImageEnhance.Sharpness(
            processed_image
        ).enhance(sharpness)


    # Threshold
    if threshold_enabled:

        if processed_image.mode != "L":
            processed_image = ImageOps.grayscale(
                processed_image
            )

        processed_image = processed_image.point(
            lambda pixel: 255
            if pixel > threshold_value
            else 0
        )


    # ========================================================
    # IMAGE PREVIEW
    # ========================================================

    st.subheader("🖼️ Image Preview")

    col1, col2 = st.columns(2)

    with col1:

        st.write("Original Image")

        st.image(
            original_image,
            use_container_width=True
        )


    with col2:

        st.write("Processed / Cropped Image")

        st.image(
            processed_image,
            use_container_width=True
        )


    # ========================================================
    # OCR
    # ========================================================

    st.subheader("🔎 OCR")

    extract_button = st.button(
        "🚀 Extract Text",
        type="primary",
        use_container_width=True
    )


    if extract_button:

        with st.spinner("Extracting text..."):

            # OCR configuration
            config = f"--psm {psm_value}"

            text = pytesseract.image_to_string(
                processed_image,
                config=config
            )


        st.subheader("📄 Extracted Text")


        if text.strip():

            # ------------------------------------------------
            # TEXT CLEANING
            # ------------------------------------------------

            cleaned_text = "\n".join(
                line.strip()
                for line in text.splitlines()
                if line.strip()
            )


            st.text_area(
                "OCR Result",
                cleaned_text,
                height=350
            )


            # =================================================
            # WORD CONFIDENCE
            # =================================================

            try:

                ocr_data = pytesseract.image_to_data(
                    processed_image,
                    config=config,
                    output_type=pytesseract.Output.DATAFRAME
                )


                ocr_data = ocr_data.dropna(
                    subset=["text"]
                )


                ocr_data = ocr_data[
                    ocr_data["text"].str.strip() != ""
                ]


                if not ocr_data.empty:

                    confidence = ocr_data["conf"]

                    confidence = pd.to_numeric(
                        confidence,
                        errors="coerce"
                    )

                    confidence = confidence[
                        confidence >= 0
                    ]


                    if len(confidence) > 0:

                        average_confidence = confidence.mean()


                        st.subheader(
                            "📈 OCR Confidence"
                        )


                        st.metric(
                            "Average Confidence",
                            f"{average_confidence:.2f}%"
                        )


                        # Confidence table

                        display_data = ocr_data[
                            [
                                "text",
                                "conf",
                                "left",
                                "top",
                                "width",
                                "height"
                            ]
                        ].copy()


                        display_data.columns = [
                            "Text",
                            "Confidence",
                            "Left",
                            "Top",
                            "Width",
                            "Height"
                        ]


                        st.dataframe(
                            display_data,
                            use_container_width=True
                        )


            except Exception as e:

                st.info(
                    f"Confidence information unavailable: {e}"
                )


            # =================================================
            # DOWNLOAD TEXT
            # =================================================

            st.download_button(
                label="⬇️ Download Extracted Text",
                data=cleaned_text,
                file_name="extracted_text.txt",
                mime="text/plain",
                use_container_width=True
            )


            # =================================================
            # DOWNLOAD CSV
            # =================================================

            try:

                if not ocr_data.empty:

                    csv_data = display_data.to_csv(
                        index=False
                    )

                    st.download_button(
                        label="⬇️ Download OCR Details CSV",
                        data=csv_data,
                        file_name="ocr_details.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

            except Exception:
                pass


        else:

            st.warning(
                "⚠️ No text could be detected in the selected image area."
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Image-to-Text Converter | "
    "Powered by Streamlit + Tesseract OCR"
)


