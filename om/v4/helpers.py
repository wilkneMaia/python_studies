import re

import pandas as pd


def extract_maintenance_order_data(file_path, page_number, initial_data_regex, final_data):
    """Extracts maintenance order data from the PDF between initial_data_regex and final_data sections."""
    try:
        import fitz  # PyMuPDF

        pdf_document = fitz.open(file_path)

        if page_number < 0 or page_number >= pdf_document.page_count:
            print(
                f"Page {page_number} does not exist in the document. The document has {pdf_document.page_count} pages.")
            return None

        page = pdf_document.load_page(page_number)
        page_text = page.get_text()

        # Use regex to find the initial data matching the provided regex
        initial_data_match = re.search(initial_data_regex, page_text)
        if not initial_data_match:
            print(
                f"Initial data matching regex '{initial_data_regex}' not found.")
            return None

        initial_data = initial_data_match.group()
        order_start = page_text.find(initial_data)
        note_start = page_text.find(final_data)

        if order_start == -1 or note_start == -1:
            print(
                f"Sections {initial_data} and/or {final_data} were not found on the page.")
            return None

        order_data = page_text[order_start:note_start].strip()
        lines = order_data.split('\n')
        df = pd.DataFrame(lines, columns=['line'])

        return df

    except Exception as e:
        print(f"Error opening file: {e}")
        return None


def find_value_after_label(df, label, offset=1):
    """Finds the value in the DataFrame after a specific label."""
    try:
        index = df[df['line'].str.contains(label, case=False, na=False)].index
        if not index.empty:
            value_index = index[0] + offset
            if value_index < len(df):
                value = df.iloc[value_index]['line'].strip()
                return value
        return None
    except Exception as e:
        print(f"Error finding value after label {label}: {e}")
        return None


def contains_om_number(text):
    """Check if text contains 'OM' followed by any number."""
    pattern = r'OM \d+'
    return bool(re.search(pattern, text))
