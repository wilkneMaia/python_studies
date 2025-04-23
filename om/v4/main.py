from extractors import extract_maintenance_order_fields ,extract_equipment_fields
from pdf_processing import process_pdf
from utils import save_to_excel
from utils import save_to_json


def combine_fields(description_fields, equipment_fields, order_fields):
    """Combines description, equipment, maintenance order, and maintenance note fields into a single dictionary."""
    combined_data = {
        "om": description_fields.get("om", ""),
        "issue_center": description_fields.get("issue_center", ""),
        "center_plant": description_fields.get("center_plant", ""),
        "om_description": description_fields.get("om_description", ""),
        "equipment_fields": equipment_fields,
        "order_fields": order_fields
        # **equipment_fields,
        # **order_fields,
    }
    return combined_data


def main():
    input_pdf_path = '../v2/pdf/OM_00.pdf'
    marker = "PERMISSÃO DE TRABALHO SEGURO"
    output_dir = "./output_pdfs"

    separated_texts = process_pdf(input_pdf_path, output_dir, marker)
    all_combined_data = []

    for idx, (file_path, description_fields) in enumerate(separated_texts):
        try:
            print(f"Processing file {idx + 1} of {len(separated_texts)}")
            om = description_fields.get("om", f"document_{idx + 1}")
            equipment_fields = extract_equipment_fields(file_path, 1)
            order_fields = extract_maintenance_order_fields(file_path, 1)

            if om and equipment_fields and order_fields:
                combined_data = combine_fields(
                    description_fields, equipment_fields, order_fields
                )
                all_combined_data.append(combined_data)
            else:
                print(
                    f"Could not extract sufficient data for document {idx + 1}.")
        except Exception as e:
            print(f"Error processing document {idx + 1}: {e}")

    # Save all combined data to a single JSON file
    json_file_path = f"{output_dir}/combined_maintenance_data.json"
    save_to_json(all_combined_data, json_file_path)

    # Save all combined data to an Excel file
    excel_file_path = f"{output_dir}/combined_maintenance_data.xlsx"
    save_to_excel(all_combined_data, excel_file_path)


if __name__ == "__main__":
    main()
