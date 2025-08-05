import fitz  # PyMuPDF

# Logic to extract paragraphs from pdfs
def extract_paragraphs_from_pdf(file_obj, gap_threshold=20):
    """
    Extracts paragraphs from a PDF file-like object using layout-based block parsing.
    
    Parameters:
        file_obj (BytesIO): The in-memory PDF file
        gap_threshold (float): Vertical gap in points used to split paragraphs

    Returns:
        List[str]: List of paragraph strings
    """
    doc = fitz.open(stream=file_obj, filetype="pdf")
    paragraphs = []

    for page in doc:
        blocks = page.get_text("blocks")
        blocks = sorted(blocks, key=lambda b: (b[1], b[0]))  # sort by y, then x

        paragraph = ""
        last_bottom = None

        for b in blocks:
            text = b[4].strip()
            top = b[1]

            if not text:
                continue

            if last_bottom is not None and top - last_bottom > gap_threshold:
                if paragraph:
                    paragraphs.append(paragraph.strip())
                    paragraph = text
                else:
                    paragraph = text
            else:
                paragraph += " " + text if paragraph else text

            last_bottom = b[3]

        if paragraph:
            paragraphs.append(paragraph.strip())

    return paragraphs

# DOESNT WORK - Function that chunks by paragraph for pdfplumber output
        # def chunk_paragraphs(text):
        #     lines = text.split("\n")
        #     paragraph = ""
        #     paragraphs = []

        #     for line in lines:
        #         stripped = line.strip()

        #         # Empty line means paragraph break
        #         if not stripped:
        #             if paragraph:
        #                 paragraphs.append(paragraph.strip())
        #                 paragraph = ""
        #         else:
        #             # Heuristic: if previous line didn't end with a punctuation, add space
        #             if paragraph and not paragraph.endswith(('.', ':', ';', '?', '!', '-', '”', '’')):
        #                 paragraph += " " + stripped
        #             else:
        #                 paragraph += " " + stripped if paragraph else stripped

        #     # Add the last paragraph
        #     if paragraph:
        #         paragraphs.append(paragraph.strip())

        #     return paragraphs