import json
import random

import fitz  # PyMuPDF
import spacy

from spacy.tokens import DocBin
from spacy.training import Example


# Define the input path
input_pdf_path = 'OM.pdf'

# Read the input PDF with PyMuPDF to extract text
input_pdf = fitz.open(input_pdf_path)

# Extract text from each page
text_data = []
for page_num in range(input_pdf.page_count):
    page = input_pdf.load_page(page_num)
    text = page.get_text("text")
    text_data.append(text)

# Save the extracted text to a file (optional)
with open('extracted_text.txt', 'w') as file:
    file.write('\n'.join(text_data))

print("Text extraction completed.")

# Load a blank spaCy model
nlp = spacy.blank("pt")

# Define the training data with more examples
TRAIN_DATA_CC = [
    ("Centro de Custo 1370390", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1360338", {"entities": [(16, 24, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1360304", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1360297", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1360304", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1360460", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370392", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370066", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370391", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370391", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370392", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370392", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370392", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370392", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370392", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370390", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    # Adicione mais exemplos de treinamento aqui
]

# Convert the training data to spaCy's format
db = DocBin()
for text, annotations in TRAIN_DATA_CC:
    doc = nlp.make_doc(text)
    ents = []
    for start, end, label in annotations.get("entities"):
        span = doc.char_span(start, end, label=label)
        if span is not None:
            ents.append(span)
    doc.ents = ents
    db.add(doc)
db.to_disk("training_data_cc.spacy")

# Train the NER model
ner = nlp.add_pipe("ner", last=True)
for _, annotations in TRAIN_DATA_CC:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])

# Number of training iterations
num_iterations = 1000  # Increase the number of iterations for better training

# Adjust to avoid training warnings
optimizer = nlp.begin_training()
for iteration in range(num_iterations):
    print(f"Training iteration {iteration + 1}/{num_iterations}")
    random.shuffle(TRAIN_DATA_CC)  # Shuffle training data to improve training
    losses = {}
    for text, annotations in TRAIN_DATA_CC:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        nlp.update([example], drop=0.35, sgd=optimizer, losses=losses)
    print(f"Iteration {iteration + 1} - Losses: {losses}")

# Save the trained model
model_path_cc = "ner_model_cc"
nlp.to_disk(model_path_cc)

print("Model training completed.")

# Load the trained model
nlp = spacy.load(model_path_cc)

# Extract text from the PDF (reuse the text_data from the first script)
extracted_data_cc = {"Centro de Custo": []}
for text in text_data:
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "CENTRO_CUSTO":
            # Validate length for "Centro de Custo"
            if ent.text.isdigit() and len(ent.text) in [7, 8]:
                extracted_data_cc["Centro de Custo"].append(ent.text.strip())

# Calculate accuracy
# Change this value according to your expected total for "Centro de Custo"
expected_total = 16
total_extracted = len(extracted_data_cc["Centro de Custo"])
accuracy = (total_extracted / expected_total) * \
    100 if expected_total > 0 else 0

# Save the results to a JSON file
results = {
    "Centro de Custo": extracted_data_cc["Centro de Custo"],
    "Metrics": {
        "Total Extracted": total_extracted,
        "Expected Total": expected_total,
        # Ensure accuracy is not more than 100%
        "Accuracy (%)": min(accuracy, 100.0)
    }
}
with open('extracted_data_cc.json', 'w') as file:
    json.dump(results, file, indent=4)

print("Data extraction for Centro de Custo completed and saved to JSON.")

# Print the results
print(json.dumps(results, indent=4))
