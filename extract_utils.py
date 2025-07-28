import fitz
import re
import statistics

def classify_document_type(doc):
    scores = {"text_heavy": 0, "transactional": 0, "visual": 0}
    page_count = len(doc)
    full_text_lower = "".join(page.get_text("text").lower() for page in doc)
    total_words = len(full_text_lower.split())
    avg_words_per_page = total_words / page_count if page_count > 0 else 0

    if "application form" in full_text_lower: scores["transactional"] = 10
    if page_count <= 2 and avg_words_per_page < 200: scores["visual"] = 5
    if page_count > 3 or avg_words_per_page > 250: scores["text_heavy"] = 5
    if any(k in full_text_lower for k in ["table of contents", "references", "appendix"]): scores["text_heavy"] += 10
    
    if max(scores.values()) == 0: return "text_heavy"
    return max(scores, key=scores.get)

def extract_text_heavy_outline(doc):
    """
    Final specialist function that now identifies and skips processing
    the content of the Table of Contents pages.
    """
    # --- New Logic: Find and store the page numbers of the Table of Contents ---
    toc_pages = set()
    for page_num, page in enumerate(doc):
        # Only search the first few pages for a TOC
        if page_num > 4:
            break
        if "table of contents" in page.get_text("text").lower():
            toc_pages.add(page_num + 1)

    # 1. Precise line-by-line extraction, skipping TOC pages
    all_lines = []
    for page_num, page in enumerate(doc):
        # --- New Logic: Skip the page if it's part of the TOC ---
        if (page_num + 1) in toc_pages:
            continue
            
        page_height = page.rect.height
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b.get("type") == 0:
                for l in b.get("lines", []):
                    if l["bbox"][1] > page_height * 0.9: continue # Filter footers
                    if not l.get("spans"): continue
                    text = " ".join(s.get("text", "") for s in l["spans"]).strip()
                    if not text: continue
                    first_span = l["spans"][0]
                    all_lines.append({
                        "text": text, "size": round(first_span["size"], 2),
                        "is_bold": "bold" in first_span["font"].lower(),
                        "page_num": page_num + 1, "y0": l["bbox"][1], "x0": l["bbox"][0]
                    })
    
    # Manually add a single entry for the Table of Contents to the outline
    outline = []
    for page_num in sorted(list(toc_pages)):
         outline.append({"level": "H1", "text": "Table of Contents", "page": page_num})

    if not all_lines: return {"title": "", "outline": outline}

    # (The rest of the logic remains the same)
    logical_blocks = []
    if all_lines:
        current_block = [all_lines[0]]
        for i in range(1, len(all_lines)):
            if abs(all_lines[i]["y0"] - all_lines[i-1]["y0"]) < 5 and \
               all_lines[i]["page_num"] == all_lines[i-1]["page_num"] and \
               abs(all_lines[i]["size"] - all_lines[i-1]["size"]) < 1:
                current_block.append(all_lines[i])
            else:
                logical_blocks.append(current_block)
                current_block = [all_lines[i]]
        logical_blocks.append(current_block)

    processed_blocks = []
    for block in logical_blocks:
        full_text = " ".join(b["text"] for b in block).strip()
        avg_size = sum(b["size"] for b in block) / len(block)
        processed_blocks.append({
            "text": full_text, "size": round(avg_size, 2),
            "is_bold": any(b["is_bold"] for b in block),
            "page_num": block[0]["page_num"], "word_count": len(full_text.split()),
            "x0": block[0]["x0"]
        })

    body_size = statistics.median([b['size'] for b in processed_blocks if b['word_count'] > 10]) if any(b['word_count'] > 10 for b in processed_blocks) else 10.0
    title_candidates = [b for b in processed_blocks if b['page_num'] == 1 and b['size'] > body_size * 1.8]
    title = " ".join(b['text'] for b in title_candidates) if title_candidates else ""

    for block in processed_blocks:
        if block['text'] in title and block['page_num'] == 1: continue
        text, size, is_bold, wc, x0 = block['text'], block['size'], block['is_bold'], block['word_count'], block['x0']
        level = None
        
        if re.match(r'^\s*\d\.\d\s+\d{1,2}\s+[A-Z]+\s+\d{4}', text): continue

        match = re.match(r'^\s*(\d+(\.\d+)*)\.?\s+', text)
        if match and wc < 15 and x0 < 100:
            dots = match.group(1).count('.')
            if dots == 0: level = "H1"
            elif dots == 1: level = "H2"
            else: level = "H3"
        
        elif wc < 15 and is_bold and size > body_size * 1.25:
             if "Revision History" in text: level = "H1"
             elif size > body_size * 1.6: level = "H1"
             else: level = "H2"
        
        if level:
            outline.append({"level": level, "text": text, "page": block["page_num"]})
    
    final_outline = []
    seen = set()
    outline.sort(key=lambda x: (x['page'], x['text']))
    for item in outline:
        if item['text'] not in seen:
            final_outline.append(item)
            seen.add(item['text'])
            
    return {"title": title, "outline": final_outline}

def extract_transactional_outline(doc):
    title_block = sorted([b for b in doc[0].get_text("blocks", sort=True) if b[6] == 0], key=lambda x: x[1])
    title = title_block[0][4].replace("\n", " ").strip() if title_block else ""
    return {"title": title, "outline": []}

def extract_visual_outline(doc):
    """
    A general specialist extractor for visual documents that uses font size
    and position to identify the most prominent text as headings.
    """
    lines = []
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b.get("type") == 0:
                for l in b.get("lines", []):
                    if not l.get("spans"): continue
                    text = " ".join(s.get("text", "") for s in l["spans"]).strip()
                    if not text: continue
                    first_span = l["spans"][0]
                    lines.append({
                        "text": text, 
                        "size": round(first_span["size"], 2),
                        "page_num": page_num + 1
                    })
    
    if not lines:
        return {"title": "", "outline": []}
        
    # Find the median font size to use as a baseline for "normal" text
    all_sizes = [line['size'] for line in lines]
    median_size = statistics.median(all_sizes) if all_sizes else 10.0
    
    # Identify candidates that are significantly larger than the median
    heading_candidates = []
    for line in lines:
        if line['size'] > median_size * 1.5: # Must be at least 50% larger
            heading_candidates.append(line)
            
    # Sort the most prominent text by size to determine title and H1
    heading_candidates.sort(key=lambda x: x['size'], reverse=True)
    
    title = ""
    outline = []
    
    if heading_candidates:
        # Assume the largest text is the title
        title = heading_candidates[0]['text']
        # Assume the second largest is the main heading
        if len(heading_candidates) > 1:
            outline.append({
                "level": "H1",
                "text": heading_candidates[1]['text'],
                "page": heading_candidates[1]['page_num']
            })

    return {"title": title, "outline": outline}
