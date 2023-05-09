import re
import spacy
import argparse
import csv
from tqdm import tqdm

nlp = spacy.load("en_core_web_sm")

def remove_pii(text):
    # Use spaCy NER to identify entities
    doc = nlp(text)
    entity_types_to_remove = {"FAC" : "MASKED_FAC", "PERSON" : "MASKED_PERSON", "GPE" : "MASKED_GPE", "DATE" : "MASKED_DATE", "ORG" : "MASKED_ORG"}
    text_parts = []
    start = 0

    for ent in doc.ents:
        if ent.label_ in entity_types_to_remove.keys():
            text_parts.append(text[start:ent.start_char])
            text_parts.append(f"[{entity_types_to_remove[ent.label_]}]")
            start = ent.end_char

    text_parts.append(text[start:])
    text = "".join(text_parts)

    # Use regex patterns for other PII fields
    pii_patterns = {
        # Email address
        r"[\w\.-]+@[\w\.-]+\.\w+" : "MASKED_EMAIL_ADDRESS",
        # Phone number 
        r"\+?(\d[\s-]?){10,15}" : "MASKED_PHONE_NUMBER",
        # Social Security Number (SSN)
        r"\d{3}-\d{2}-\d{4}" : "MASKED_SOCIAL_SECIRITY_NUMBER",
        # Passport number (generic pattern, passport numbers vary by country)
        r"[A-Z]{1,2}\d{6,10}" : "MASKED_PASSPORT_NUMBER",
        # Credit card number
        r"\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}" : "MASKED_CREDIT_CARD_NUMBER",
        # IP address
        r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)" : "MASKED_IP_ADDRESS",
        # Date of birth
        r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}" : "MASKED_DATE",
    } 

    for pattern in pii_patterns.keys():
        text = re.sub(pattern, f"[{pii_patterns[pattern]}]", text)

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
