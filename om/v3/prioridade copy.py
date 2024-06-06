import json
import random

import fitz  # PyMuPDF
import spacy

from spacy.tokens import DocBin


# Define the input path
input_pdf_path = 'OM.pdf'

# Read the input PDF with PyMuPDF to extract text
input_pdf = fitz.open(input_pdf_path)
text_data = []
for page_num in range(input_pdf.page_count):
    page = input_pdf.load_page(page_num)
    text = page.get_text("text")
    text_data.append(text)

# Save the extracted text to a file (optional)
with open('extracted_text.txt', 'w') as file:
    file.write('\n'.join(text_data))

print("Text extraction completed.")


def train_ner_model(train_data, model_name):
    # Load a blank spaCy model
    nlp = spacy.blank("pt")

    # Define the training data
    db = DocBin()
    for text, annotations in train_data:
        doc = nlp.make_doc(text)
        ents = []
        for start, end, label in annotations.get("entities"):
            span = doc.char_span(start, end, label=label)
            ents.append(span)
        doc.ents = ents
        db.add(doc)
    db.to_disk(f"training_data_{model_name}.spacy")

    # Train the NER model
    ner = nlp.add_pipe("ner", last=True)
    for _, annotations in train_data:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    # Number of training iterations
    num_iterations = 300
    optimizer = nlp.begin_training()
    for iteration in range(num_iterations):
        print(f"Training iteration {iteration + 1}/{num_iterations}")
        random.shuffle(train_data)
        losses = {}
        for text, annotations in train_data:
            doc = nlp.make_doc(text)
            example = spacy.training.Example.from_dict(doc, annotations)
            nlp.update([example], drop=0.35, sgd=optimizer, losses=losses)
        print(f"Iteration {iteration + 1} - Losses: {losses}")

    # Save the trained model
    model_path = f"ner_model_{model_name}"
    nlp.to_disk(model_path)

    print(f"Model training for {model_name} completed.")
    return model_path


def extract_entities(model_path, text_data, label):
    # Load the trained model
    nlp = spacy.load(model_path)

    extracted_data = {label: []}
    for text in text_data:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == label:
                extracted_data[label].append(ent.text.strip())

    return extracted_data


# Define the training data for 'Prioridade'
TRAIN_DATA_PRIORIDADE = [
    ("Prioridade Alta", {"entities": [(11, 15, "PRIORIDADE")]}),
    ("Prioridade Média", {"entities": [(11, 16, "PRIORIDADE")]}),
    ("Prioridade Baixa", {"entities": [(11, 16, "PRIORIDADE")]}),
    # Add more training examples here
]

# Train model for Prioridade
model_path_prioridade = train_ner_model(TRAIN_DATA_PRIORIDADE, "prioridade")

# Extract entities
extracted_data_prioridade = extract_entities(
    model_path_prioridade, text_data, "PRIORIDADE")

# Calculate metrics
expected_total = 16  # Adjust this based on the expected total of each entity
total_extracted = len(extracted_data_prioridade["PRIORIDADE"])
accuracy = (total_extracted / expected_total) * 100

# Add metrics to the extracted data
extracted_data_prioridade["Metrics"] = {
    "Total Extracted": total_extracted,
    "Expected Total": expected_total,
    "Accuracy (%)": accuracy
}

# Save the results to a JSON file
with open('extracted_data_prioridade.json', 'w') as file:
    json.dump(extracted_data_prioridade, file, indent=4)

print("Data extraction for Prioridade completed and saved to JSON.")
print(json.dumps(extracted_data_prioridade, indent=4))
