import os
import json
import fitz
from extract_utils import (
    classify_document_type, 
    extract_text_heavy_outline,
    extract_transactional_outline,
    extract_visual_outline
)

def main():
    input_dir = "input"
    output_dir = "output"

    if not os.path.isdir(input_dir):
        print(f"ERROR: Input directory not found: {input_dir}")
        return
    os.makedirs(output_dir, exist_ok=True)

    for fname in sorted(os.listdir(input_dir)):
        if not fname.lower().endswith('.pdf'):
            continue
        
        in_pdf = os.path.join(input_dir, fname)
        out_json = os.path.join(output_dir, fname[:-4] + '.json')
        print(f"INFO: Processing {fname}...")

        try:
            doc = fitz.open(in_pdf)
            doc_type = classify_document_type(doc)
            print(f"  -> Classified as: {doc_type}")
            
            if doc_type == "transactional":
                result = extract_transactional_outline(doc)
            elif doc_type == "visual":
                result = extract_visual_outline(doc)
            else: # "text_heavy" is the default
                result = extract_text_heavy_outline(doc)
            
            doc.close()
            
            with open(out_json, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"OK: Wrote outline to {out_json}")

        except Exception as e:
            print(f"ERROR on {fname}: {e}")

if __name__ == '__main__':
    main()
