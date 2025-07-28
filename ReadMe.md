# Challenge 1A: Hierarchical PDF Outline Extractor

## Overview
This repository contains our solution for **Challenge 1A of the Adobe India Hackathon 2025**.  

The project automatically **processes PDF documents**, intelligently **classifies their type**, and **extracts a structured hierarchical outline** (Title, H1, H2, H3).  
The final output for each PDF is a **clean, well-formatted JSON file**.  

The entire solution is **containerized using Docker**, ensuring consistent execution across environments and compliance with all challenge constraints, including **offline operation** and **specific resource limits**.

---

## Approach and Methodology

Our solution uses a **multi-stage pipeline** designed to adapt to different document layouts for maximum accuracy.

### **1. Document Classification**
Each PDF is first analyzed using the `classify_document_type` function, which determines the document category using these heuristics:
- **Word Count & Page Density**: Calculates average words per page. High-density documents are flagged as `text_heavy`.
- **Keyword Detection**: Detects key phrases:
  - `"table of contents"` or `"appendix"` → likely `text_heavy`.
  - `"application form"` → likely `transactional`.
- **Page Count**: Very short documents (≤2 pages) with low word counts are classified as `visual`.

This triage system ensures the **most effective extraction strategy** is applied per document type.

---

### **2. Specialized Extraction Functions**
Based on classification, one of three specialized functions is used:

#### **a) extract_text_heavy_outline**
Designed for **complex reports and articles**:
- **TOC Skipping**: Skips over "Table of Contents" pages to avoid redundant entries.
- **Detailed Text Analysis**: Uses PyMuPDF’s `get_text("dict")` to extract **text with metadata**:
  - Font size
  - Font name (for boldness detection)
  - Coordinates (for spatial analysis)
- **Footer Filtering**: Removes text in the **bottom 10%** of pages (likely footers/page numbers).
- **Logical Block Grouping**: Groups adjacent text lines with similar **font properties** and **vertical positions** into coherent blocks (e.g., paragraphs, multi-line headings).
- **Dual-Heuristic Heading Detection**:
  - **Structural Analysis**: Uses `re.match` for common numbered patterns (e.g., `1.`, `2.1`, `3.1.1`).
  - **Stylistic Analysis**: Computes **median body font size** and flags short lines with **significantly larger/bolder text** as headings.
- **Title Detection**: Identifies the **most prominent text on the first page** as the document title.

#### **b) extract_visual_outline & extract_transactional_outline**
For **simpler documents**:
- Identifies the **largest text block on the first page** as the document title.
- Extracts 1–2 major headings using **font size heuristics**.

---

### **3. Final Output**
All extracted information is compiled into a **clean hierarchical JSON structure**:
- **Title**
- **H1, H2, H3 headings**
- Ensures all keys/values follow the **required schema** before saving the `.json` file.

---

## Libraries Used
- **[PyMuPDF](https://pymupdf.readthedocs.io/)**
- **Standard Python Libraries**:  
  - `re` – Regular expressions  
  - `statistics` – Font size analysis  
  - `os` – File management  
  - `json` – Output generation  

---

## Building and Running with Docker

> **Note:** A **Dockerfile is already provided in the root directory**.

### **1. Build the Docker Image**
Navigate to the project’s root directory and run:
```bash
# Build the container
docker build -t adobe1a .

# Run the container
docker run --rm adobe1a

