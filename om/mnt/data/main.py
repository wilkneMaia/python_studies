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

# Define the training data for both "Centro de Custo" and "Prioridade"
TRAIN_DATA = [
    ("Centro de Custo 1370392", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 11203035", {"entities": [(16, 24, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370390", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370391", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370066", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Prioridade Alta", {"entities": [(11, 15, "PRIORIDADE")]}),
    ("Prioridade Média", {"entities": [(11, 16, "PRIORIDADE")]}),
    ("Prioridade Baixa", {"entities": [(11, 16, "PRIORIDADE")]}),
    # Adicione mais exemplos de treinamento aqui
]

# Convert the training data to spaCy's format
db = DocBin()
for text, annotations in TRAIN_DATA:
    doc = nlp.make_doc(text)
    ents = []
    for start, end, label in annotations.get("entities"):
        span = doc.char_span(start, end, label=label)
        ents.append(span)
    doc.ents = ents
    db.add(doc)
db.to_disk("training_data.spacy")

# Train the NER model
ner = nlp.add_pipe("ner", last=True)
for _, annotations in TRAIN_DATA:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])

# Number of training iterations
num_iterations = 300  # Increase the number of iterations for better training

# Adjust to avoid training warnings
optimizer = nlp.begin_training()
for iteration in range(num_iterations):
    print(f"Training iteration {iteration + 1}/{num_iterations}")
    random.shuffle(TRAIN_DATA)  # Shuffle training data to improve training
    losses = {}
    for text, annotations in TRAIN_DATA:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        nlp.update([example], drop=0.35, sgd=optimizer, losses=losses)
    print(f"Iteration {iteration + 1} - Losses: {losses}")

# Save the trained model
model_path = "ner_model"
nlp.to_disk(model_path)

print("Model training completed.")

# Load the trained model
nlp = spacy.load(model_path)

# Extract text from the PDF (reuse the text_data from the first script)
extracted_data = {"Centro de Custo": [], "Prioridade": []}
for text in text_data:
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "CENTRO_CUSTO":
            # Validate length for "Centro de Custo"
            if ent.text.isdigit() and len(ent.text) in [7, 8]:
                extracted_data["Centro de Custo"].append(ent.text.strip())
        if ent.label_ == "PRIORIDADE":
            extracted_data["Prioridade"].append(ent.text.strip())

# Calculate accuracy
# Change this value according to your expected total for "Centro de Custo"
expected_total_cc = 16
total_extracted_cc = len(extracted_data["Centro de Custo"])
accuracy_cc = (total_extracted_cc / expected_total_cc) * \
    100 if expected_total_cc > 0 else 0

# Change this value according to your expected total for "Prioridade"
expected_total_prioridade = 16
total_extracted_prioridade = len(extracted_data["Prioridade"])
accuracy_prioridade = (total_extracted_prioridade / expected_total_prioridade) * \
    100 if expected_total_prioridade > 0 else 0

# Save the results to a JSON file
results = {
    "Centro de Custo": extracted_data["Centro de Custo"],
    "Prioridade": extracted_data["Prioridade"],
    "Metrics": {
        "Centro de Custo": {
            "Total Extracted": total_extracted_cc,
            "Expected Total": expected_total_cc,
            # Ensure accuracy is not more than 100%
            "Accuracy (%)": min(accuracy_cc, 100.0)
        },
        "Prioridade": {
            "Total Extracted": total_extracted_prioridade,
            "Expected Total": expected_total_prioridade,
            # Ensure accuracy is not more than 100%
            "Accuracy (%)": min(accuracy_prioridade, 100.0)
        }
    }
}

with open('extracted_data.json', 'w') as file:
    json.dump(results, file, indent=4)

print("Data extraction completed and saved to JSON.")

# Print the results
print(json.dumps(results, indent=4))
