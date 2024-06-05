import spacy

from spacy.tokens import DocBin

# Load the trained model
nlp = spacy.load("ner_model")

# Extract text from the PDF (reuse the text_data from the first script)
extracted_priorities = []
for text in text_data:
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PRIORIDADE":
            extracted_priorities.append(ent.text)

# Save the extracted priorities to a file (optional)
with open('extracted_priorities.txt', 'w') as file:
    file.write('\n'.join(extracted_priorities))

print("Priority extraction completed.")
