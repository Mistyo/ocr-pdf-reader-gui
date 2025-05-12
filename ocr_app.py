import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from gtts import gTTS
from num2words import num2words
import io
import tempfile
import time

# ------------------------ Streamlit Setup ------------------------
st.set_page_config(page_title="Faateh's Fwee OCR Utility Toolkit(personal beta use)", layout="centered")
st.title("🧰 Faateh's Fwee OCR Utility Toolkit(personal beta use)")

# ------------------------ Language Settings ------------------------
st.sidebar.subheader("🌐 OCR Language Settings")
lang_choice = st.sidebar.multiselect("Select OCR Language(s)", ["English", "Urdu"], default=["English"])

# Use separate language codes for OCR (Tesseract) and TTS (gTTS)
ocr_lang_map = {"English": "eng", "Urdu": "urd"}
tts_lang_map = {"English": "en", "Urdu": "ur"}

selected_langs = "+".join([ocr_lang_map[lang] for lang in lang_choice])

# ------------------------ Tabs ------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📄 PDF to Text",
    "🖼️ Image to Text",
    "📢 PDF to Audio",
    "🔢 Number to Audio"
])

# ------------------------ Tab 1: PDF to Text ------------------------
with tab1:
    uploaded_pdf = st.file_uploader("Upload a PDF file", type=["pdf"], key="pdf_text")

    if uploaded_pdf:
        pdf_bytes = uploaded_pdf.read()
        doc = fitz.open("pdf", pdf_bytes)
        total_pages = len(doc)
        st.success(f"✅ PDF loaded with {total_pages} pages.")

        start_page = st.number_input("Start Page", min_value=1, max_value=total_pages, value=1)
        end_page = st.number_input("End Page", min_value=start_page, max_value=total_pages, value=min(start_page + 49, total_pages))
        batch_size = 20

        if st.button("🔍 Start PDF OCR"):
            output_text = ""

            with st.spinner("Processing PDF..."):
                for i in range(start_page - 1, end_page, batch_size):
                    batch_start = i
                    batch_end = min(i + batch_size, end_page)
                    st.info(f"📖 Pages {batch_start + 1} to {batch_end}")

                    for page_num in range(batch_start, batch_end):
                        page = doc[page_num]
                        text = page.get_text().strip()

                        preview_pix = page.get_pixmap(dpi=80)
                        preview_img = Image.open(io.BytesIO(preview_pix.tobytes("png")))
                        st.image(preview_img, caption=f"Page {page_num + 1}", use_column_width=True)

                        if len(text) > 30:
                            output_text += f"\n\n--- Page {page_num + 1} (Text Layer) ---\n{text}"
                            st.success(f"✅ Page {page_num + 1}: Extracted text directly.")
                        else:
                            st.warning(f"🖼️ Page {page_num + 1} needs OCR...")
                            full_pix = page.get_pixmap(dpi=300)
                            full_img = Image.open(io.BytesIO(full_pix.tobytes("png")))
                            ocr_text = pytesseract.image_to_string(full_img, lang=selected_langs)
                            output_text += f"\n\n--- Page {page_num + 1} (OCR) ---\n{ocr_text.strip()}"

                        time.sleep(0.5)

            st.success("✅ Done!")
            st.text_area("Preview OCR Output", output_text[:1000], height=300)
            st.download_button("📥 Download Full Text", output_text, file_name="pdf_text_output.txt")

# ------------------------ Tab 2: Image to Text ------------------------
with tab2:
    uploaded_images = st.file_uploader("Upload image(s)", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)

    if uploaded_images:
        all_image_text = ""
        for idx, uploaded_image in enumerate(uploaded_images):
            image = Image.open(uploaded_image)
            st.image(image, caption=f"Image {idx+1} Preview", use_column_width=True)

            with st.spinner(f"OCR in progress for Image {idx+1}..."):
                ocr_text = pytesseract.image_to_string(image, lang=selected_langs)
                all_image_text += f"\n\n--- Image {idx+1} ---\n{ocr_text.strip()}"

        st.success("✅ OCR complete!")
        st.text_area("Extracted Text", all_image_text[:1000], height=300)
        st.download_button("📥 Download Image OCR Text", all_image_text, file_name="image_text_output.txt")

# ------------------------ Tab 3: PDF to Audio ------------------------
with tab3:
    audio_pdf = st.file_uploader("Upload a PDF file for Audio Conversion", type=["pdf"], key="audio_pdf")

    if audio_pdf:
        pdf_bytes = audio_pdf.read()
        doc = fitz.open("pdf", pdf_bytes)
        total_pages = len(doc)
        st.success(f"✅ PDF loaded with {total_pages} pages.")

        start_audio = st.number_input("Start Page", min_value=1, max_value=total_pages, value=1, key="start_audio")
        end_audio = st.number_input("End Page", min_value=start_audio, max_value=total_pages, value=min(start_audio + 9, total_pages), key="end_audio")

        if st.button("🔊 Generate Audio"):
            full_text = ""

            with st.spinner("Extracting text from PDF..."):
                for i in range(start_audio - 1, end_audio):
                    page = doc[i]
                    text = page.get_text().strip()

                    if len(text) > 30:
                        full_text += text + "\n"
                    else:
                        pix = page.get_pixmap(dpi=300)
                        img = Image.open(io.BytesIO(pix.tobytes("png")))
                        ocr_text = pytesseract.image_to_string(img, lang=selected_langs)
                        full_text += ocr_text + "\n"

            if full_text.strip():
                st.success("✅ Text extraction complete!")
                st.text_area("📄 Preview Text", full_text[:1000], height=300)

                with st.spinner("Generating audio..."):
                    tts = gTTS(full_text, lang=tts_lang_map[lang_choice[0].strip()])
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                        tts.save(f.name)
                        st.audio(f.name, format="audio/mp3")
                        with open(f.name, "rb") as audio_file:
                            st.download_button("📥 Download MP3", audio_file.read(), file_name="pdf_audio.mp3")
            else:
                st.error("❌ No text found to convert.")

# ------------------------ Tab 4: Number to Audio ------------------------
# ------------------------ Tab 4: Number to Audio ------------------------
with tab4:
    st.header("🔢 Number to Audio Converter")

    number_input = st.text_input("Enter a number", placeholder="e.g., 69696;)")
    lang_for_number = st.selectbox("Select language", ["English", "Urdu"])

    if st.button("🗣️ Convert and Speak"):
        try:
            # Clean input and handle language selection
            number_value = int(number_input.replace(",", "").strip())
            
            # Convert number to words
            if lang_for_number == "Urdu":
                spoken_text = num2words(number_value, lang="ur")
                gtts_lang = "ur"
            else:
                spoken_text = num2words(number_value, lang="en")
                gtts_lang = "en"

            st.success(f"📝 {number_input} → {spoken_text}")

            # TTS Conversion with selected language
            tts = gTTS(text=spoken_text, lang=gtts_lang)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                tts.save(f.name)
                st.audio(f.name, format="audio/mp3")
                with open(f.name, "rb") as audio_file:
                    st.download_button("📥 Download Spoken Number", audio_file.read(), file_name="spoken_number.mp3")

        except ValueError:
            st.error("❌ Please enter a valid number.")
        except Exception as e:
            st.error(f"❌ TTS Error: {e}")
