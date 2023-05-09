import re
import spacy
import argparse
import csv
from tqdm import tqdm

nlp = spacy.load("en_core_web_sm")

def remove_pii(text):
    # Use spaCy NER to identify entities
    doc = nlp(text)
    entity_types_to_remove = {"FAC", "PERSON", "GPE", "DATE", "ORG"}
    text_parts = []
    start = 0

    for ent in doc.ents:
        if ent.label_ in entity_types_to_remove:
            text_parts.append(text[start:ent.start_char])
            text_parts.append("[REDACTED]")
            start = ent.end_char

    text_parts.append(text[start:])
    text = "".join(text_parts)

    # Use regex patterns for other PII fields
    pii_patterns = [
        # Email address
        r"[\w\.-]+@[\w\.-]+\.\w+",
        # Phone number
        r"\+?(\d[\s-]?){10,15}",
        # Social Security Number (SSN)
        r"\d{3}-\d{2}-\d{4}",
        # Passport number (generic pattern, passport numbers vary by country)
        r"[A-Z]{1,2}\d{6,10}",
        # Credit card number
        r"\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}",
        # IP address
        r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)",
        # Date of birth
        r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}",
    ] 

    for pattern in pii_patterns:
        text = re.sub(pattern, "[REDACTED]", text)

    return text

def process_csv(input_file, output_file):
    with open(input_file, newline='', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        total_lines = sum(1 for _ in open(input_file, 'r', encoding='utf-8'))

        for row in tqdm(reader, total=total_lines, desc="Processing rows"):
            sanitized_row = [remove_pii(cell) for cell in row]
            writer.writerow(sanitized_row)

def main():
    parser = argparse.ArgumentParser(description="Remove PII from a CSV file.")
    parser.add_argument("input_file", help="Path to the input CSV file.")
    parser.add_argument("output_file", help="Path to the output CSV file.")
    args = parser.parse_args()

    process_csv(args.input_file, args.output_file)

if __name__ == "__main__":
    main()
