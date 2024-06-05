import json
import random

import fitz  # PyMuPDF
import spacy

from spacy.tokens import DocBin


# Define the input path
input_pdf_path = 'SEMANA_01.pdf'

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
TRAIN_DATA = [
    ("Centro de Custo 1370392", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 11203035", {"entities": [(16, 24, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370390", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370391", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370066", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370393", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370394", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370395", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370396", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370397", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370398", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370399", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370400", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370401", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370402", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    ("Centro de Custo 1370403", {"entities": [(16, 23, "CENTRO_CUSTO")]}),
    # Adicione mais exemplos de treinamento aqui conforme necessário
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
num_iterations = 100

for iteration in range(num_iterations):
    print(f"Training iteration {iteration + 1}/{num_iterations}")
    optimizer = nlp.begin_training()
    for i in range(50):  # Aumentando o número de iterações para um melhor treinamento
        random.shuffle(TRAIN_DATA)  # Shuffle training data to improve training
        for text, annotations in TRAIN_DATA:
            doc = nlp.make_doc(text)
            example = spacy.training.Example.from_dict(doc, annotations)
            nlp.update([example], drop=0.35, sgd=optimizer)

# Save the trained model
model_path = "ner_model"
nlp.to_disk(model_path)

print("Model training completed.")

# Load the trained model
nlp = spacy.load(model_path)

# Extract text from the PDF (reuse the text_data from the first script)
extracted_centro_custo = []
for text in text_data:
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "CENTRO_CUSTO":
            # Additional validation: Ensure the extracted value is numeric
            if ent.text.isdigit() and len(ent.text) == 7:
                extracted_centro_custo.append(ent.text.strip())

# Create a JSON structure for the results
results = {
    "Centro de Custo": extracted_centro_custo,
    "Total Extracted": len(extracted_centro_custo),
    "Expected Total": 16,
    "Accuracy (%)": (len(extracted_centro_custo) / 16) * 100
}

# Save the results to a JSON file
with open('extracted_centro_custo.json', 'w') as file:
    json.dump(results, file, indent=4)

print("Centro de Custo extraction completed and saved to JSON.")

# Print the results
print(json.dumps(results, indent=4))
