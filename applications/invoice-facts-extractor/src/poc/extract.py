"""
Invoice Text Extraction Module

This module handles the first step of the Invoice Facts Extractor pipeline:
converting PDF invoices to TSV format using Tesseract OCR.
"""

import os
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from PIL import Image


def get_examples_dir() -> Path:
    """Get the path to the examples directory."""
    return Path(__file__).parent.parent.parent / "examples"


def get_output_dir() -> Path:
    """Get the path to the extraction output directory."""
    output_dir = get_examples_dir() / ".poc" / "extract"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def extract_text_from_image(image: Image.Image) -> str:
    """
    Extract text from a single image using Tesseract OCR.
    
    Returns TSV-formatted string with the following columns:
    level, page_num, block_num, par_num, line_num, word_num, 
    left, top, width, height, conf, text
    
    Args:
        image: PIL Image object to process
        
    Returns:
        TSV-formatted string of OCR results
    """
    tsv_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.STRING)
    return tsv_data


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract text from all pages of a PDF using Tesseract OCR.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        TSV-formatted string containing OCR results from all pages
    """
    # Convert PDF pages to images
    images = convert_from_path(str(pdf_path))
    
    all_tsv_lines = []
    header = None
    
    for page_num, image in enumerate(images, start=1):
        tsv_data = extract_text_from_image(image)
        lines = tsv_data.strip().split('\n')
        
        if page_num == 1:
            # Keep header from first page
            header = lines[0]
            all_tsv_lines.append(header)
            all_tsv_lines.extend(lines[1:])
        else:
            # Skip header for subsequent pages, just add data rows
            all_tsv_lines.extend(lines[1:])
    
    return '\n'.join(all_tsv_lines)


def process_invoice(pdf_path: Path, output_dir: Path) -> Path:
    """
    Process a single invoice PDF and write the extracted text to a TSV file.
    
    Args:
        pdf_path: Path to the input PDF file
        output_dir: Directory to write the output TSV file
        
    Returns:
        Path to the created TSV file
    """
    print(f"Processing: {pdf_path.name}")
    
    # Extract text from PDF
    tsv_content = extract_text_from_pdf(pdf_path)
    
    # Write to output file
    output_path = output_dir / f"{pdf_path.stem}.tsv"
    output_path.write_text(tsv_content, encoding='utf-8')
    
    print(f"  -> Written to: {output_path}")
    return output_path


def extract_all_examples() -> list[Path]:
    """
    Process all PDF examples in the examples directory.
    
    Iterates through each PDF file in the examples directory,
    extracts text using OCR, and writes the results to TSV files
    in the .poc/extract subdirectory.
    
    Returns:
        List of paths to the created TSV files
    """
    examples_dir = get_examples_dir()
    output_dir = get_output_dir()
    
    print(f"Examples directory: {examples_dir}")
    print(f"Output directory: {output_dir}")
    print("-" * 50)
    
    # Find all PDF files in the examples directory
    pdf_files = sorted(examples_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in examples directory.")
        return []
    
    print(f"Found {len(pdf_files)} PDF file(s) to process.\n")
    
    output_paths = []
    for pdf_path in pdf_files:
        try:
            output_path = process_invoice(pdf_path, output_dir)
            output_paths.append(output_path)
        except Exception as e:
            print(f"  -> Error processing {pdf_path.name}: {e}")
    
    print("-" * 50)
    print(f"Extraction complete. {len(output_paths)} file(s) processed.")
    
    return output_paths


if __name__ == "__main__":
    extract_all_examples()

