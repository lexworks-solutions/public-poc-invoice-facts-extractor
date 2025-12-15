"""
Invoice Synthesis Module

This module handles the synthesis step of the Invoice Facts Extractor pipeline:
using Gemini AI to extract structured invoice data from OCR text.
"""

import json
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from google import genai
from google.genai import errors as genai_errors

# Model configuration
GEMINI_MODEL = "gemini-2.5-flash"


@dataclass
class LineItem:
    description: str
    quantity: float
    unit_price: float
    total_price: float


@dataclass
class Digest:
    invoice_number: str
    invoice_date: str
    due_date: str
    total_amount: float
    line_items: list[LineItem]


EXTRACTION_PROMPT = """You are an invoice data extraction assistant. Your task is to extract structured data from OCR text of an invoice.

The OCR text is provided in TSV (tab-separated values) format with columns:
level, page_num, block_num, par_num, line_num, word_num, left, top, width, height, conf, text

Focus on the "text" column to understand the invoice content. The positional data can help you understand the document structure.

Extract the following information and return it as valid JSON:

{
  "invoice_number": "string - the invoice number/ID",
  "invoice_date": "string - the date the invoice was issued (format: YYYY-MM-DD if possible)",
  "due_date": "string - the payment due date (format: YYYY-MM-DD if possible)", 
  "total_amount": number - the final total amount to pay (as a number, not string),
  "line_items": [
    {
      "description": "string - description of the item/service",
      "quantity": number - quantity ordered,
      "unit_price": number - price per unit,
      "total_price": number - total for this line item
    }
  ]
}

Rules:
- Return ONLY valid JSON, no markdown formatting or explanation
- If a field cannot be determined, use null for strings and 0 for numbers
- For amounts, extract the numeric value only (no currency symbols)
- Include all line items found in the invoice

Here is the OCR TSV data:

"""


def get_extract_dir() -> Path:
    """Get the path to the extraction output directory."""
    return Path(__file__).parent.parent.parent / "examples" / ".poc" / "extract"


def get_synthesis_dir() -> Path:
    """Get the path to the synthesis output directory."""
    output_dir = Path(__file__).parent.parent.parent / "examples" / ".poc" / "synthesis"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def load_env() -> None:
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    value = value.strip()
                    # Remove surrounding quotes if present
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    os.environ[key.strip()] = value


def create_client() -> genai.Client:
    """Create and return a Gemini client."""
    load_env()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    return genai.Client(api_key=api_key)


def extract_digest_from_tsv(client: genai.Client, tsv_content: str, max_retries: int = 5) -> Digest:
    """
    Use Gemini to extract invoice data from TSV OCR output.
    
    Args:
        client: Gemini client instance
        tsv_content: Raw TSV content from OCR extraction
        max_retries: Maximum number of retry attempts for rate limits
        
    Returns:
        Digest object with extracted invoice data
    """
    prompt = EXTRACTION_PROMPT + tsv_content
    
    # Retry loop for handling rate limits
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )
            break
        except genai_errors.ClientError as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                wait_time = (2 ** attempt) * 5  # Exponential backoff: 5, 10, 20, 40, 80 seconds
                print(f"    Rate limited, waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                if attempt == max_retries - 1:
                    raise
            else:
                raise
    
    # Parse the JSON response
    response_text = response.text.strip()
    
    # Handle potential markdown code blocks in response
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        # Remove first and last lines (```json and ```)
        response_text = "\n".join(lines[1:-1])
    
    data = json.loads(response_text)
    
    # Convert to dataclass objects
    line_items = [
        LineItem(
            description=item.get("description", ""),
            quantity=float(item.get("quantity", 0)),
            unit_price=float(item.get("unit_price", 0)),
            total_price=float(item.get("total_price", 0)),
        )
        for item in data.get("line_items", [])
    ]
    
    return Digest(
        invoice_number=data.get("invoice_number", ""),
        invoice_date=data.get("invoice_date", ""),
        due_date=data.get("due_date", ""),
        total_amount=float(data.get("total_amount", 0)),
        line_items=line_items,
    )


def process_tsv_file(client: genai.Client, tsv_path: Path, output_dir: Path) -> Path:
    """
    Process a single TSV file and write the extracted digest to JSON.
    
    Args:
        client: Gemini client instance
        tsv_path: Path to the input TSV file
        output_dir: Directory to write the output JSON file
        
    Returns:
        Path to the created JSON file
    """
    print(f"Processing: {tsv_path.name}")
    
    # Read TSV content
    tsv_content = tsv_path.read_text(encoding="utf-8")
    
    # Extract digest using Gemini
    digest = extract_digest_from_tsv(client, tsv_content)
    
    # Convert to JSON-serializable dict
    digest_dict = asdict(digest)
    
    # Write to output file
    output_path = output_dir / f"{tsv_path.stem}.json"
    output_path.write_text(
        json.dumps(digest_dict, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    
    print(f"  -> Written to: {output_path}")
    return output_path


def synthesize_all_extracts() -> list[Path]:
    """
    Process all TSV files in the extract directory.
    
    Iterates through each TSV file in the .poc/extract directory,
    uses Gemini to extract structured data, and writes the results
    to JSON files in the .poc/synthesis subdirectory.
    
    Returns:
        List of paths to the created JSON files
    """
    extract_dir = get_extract_dir()
    output_dir = get_synthesis_dir()
    
    print(f"Extract directory: {extract_dir}")
    print(f"Output directory: {output_dir}")
    print("-" * 50)
    
    # Find all TSV files
    tsv_files = sorted(extract_dir.glob("*.tsv"))
    
    if not tsv_files:
        print("No TSV files found in extract directory.")
        return []
    
    print(f"Found {len(tsv_files)} TSV file(s) to process.\n")
    
    # Create Gemini client
    client = create_client()
    
    output_paths = []
    for i, tsv_path in enumerate(tsv_files):
        try:
            output_path = process_tsv_file(client, tsv_path, output_dir)
            output_paths.append(output_path)
            # Add delay between files to avoid rate limits
            if i < len(tsv_files) - 1:
                print("    Waiting 5s before next file...")
                time.sleep(5)
        except Exception as e:
            print(f"  -> Error processing {tsv_path.name}: {e}")
    
    print("-" * 50)
    print(f"Synthesis complete. {len(output_paths)} file(s) processed.")
    
    return output_paths


if __name__ == "__main__":
    synthesize_all_extracts()
