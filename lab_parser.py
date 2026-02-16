"""PDF parser for lab test results."""
import os
import re
from datetime import datetime
from typing import List, Dict, Optional
import PyPDF2
import config


class LabDataParser:
    """Parser for extracting lab test results from PDF files."""
    
    def __init__(self, health_data_dir: str = None):
        self.health_data_dir = health_data_dir or config.HEALTH_DATA_DIR
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    
    def parse_date_from_filename(self, filename: str) -> Optional[str]:
        """
        Extract date from filename.
        
        Args:
            filename: PDF filename
            
        Returns:
            Date in YYYY-MM-DD format or None
        """
        # Pattern: "Feb 16, 2026.pdf" or similar
        date_pattern = r'([A-Za-z]+)\s+(\d+),?\s+(\d{4})'
        match = re.search(date_pattern, filename)
        
        if match:
            month_str, day, year = match.groups()
            try:
                date_obj = datetime.strptime(f"{month_str} {day} {year}", "%b %d %Y")
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                try:
                    date_obj = datetime.strptime(f"{month_str} {day} {year}", "%B %d %Y")
                    return date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    pass
        
        return None
    
    def parse_lab_values(self, text: str, test_type: str) -> List[Dict]:
        """
        Parse lab values from extracted text.
        
        Args:
            text: Extracted PDF text
            test_type: Type of lab test (e.g., "BASIC METABOLIC SET")
            
        Returns:
            List of lab result dictionaries
        """
        results = []
        
        # Common patterns for lab results
        # Pattern: "Test Name    Value   Reference Range   Units"
        # Example: "Glucose      95      70-100 mg/dL"
        
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Try to identify test name and value patterns
            # This is a simplified parser - may need adjustment based on actual PDF format
            
            # Pattern for numeric values with units
            value_pattern = r'(\d+\.?\d*)\s*(mg/dL|mmol/L|g/dL|%|K/uL|M/uL|fL|pg|g/dL|mEq/L|/'
            
            # Look for common test names
            test_names = [
                'Glucose', 'Sodium', 'Potassium', 'Chloride', 'CO2', 'BUN', 'Creatinine',
                'Calcium', 'WBC', 'RBC', 'Hemoglobin', 'Hematocrit', 'MCV', 'MCH', 'MCHC',
                'RDW', 'Platelet', 'Neutrophils', 'Lymphocytes', 'Monocytes', 'Eosinophils',
                'Basophils', 'eGFR'
            ]
            
            for test_name in test_names:
                if test_name.lower() in line.lower():
                    # Try to extract value and reference range
                    parts = line.split()
                    
                    # Simple heuristic: look for numeric value after test name
                    for j, part in enumerate(parts):
                        try:
                            value = float(part.replace(',', ''))
                            unit = parts[j + 1] if j + 1 < len(parts) else ''
                            
                            # Try to find reference range
                            ref_range = ''
                            for k in range(j + 1, min(j + 5, len(parts))):
                                if '-' in parts[k] or 'to' in parts[k].lower():
                                    ref_range = parts[k]
                                    break
                            
                            results.append({
                                'test_name': test_name,
                                'value': value,
                                'unit': unit,
                                'reference_range': ref_range,
                                'test_type': test_type
                            })
                            break
                        except (ValueError, IndexError):
                            continue
        
        return results
    
    def parse_pdf_file(self, pdf_path: str) -> Dict:
        """
        Parse a single PDF file for lab results.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with test date, test type, and results
        """
        filename = os.path.basename(pdf_path)
        
        # Extract test type from filename
        test_type = "Unknown"
        if "BASIC METABOLIC" in filename.upper():
            test_type = "Basic Metabolic Panel"
        elif "CBC" in filename.upper():
            test_type = "Complete Blood Count"
        elif "GLUCOSE" in filename.upper():
            test_type = "Glucose"
        
        # Extract date
        test_date = self.parse_date_from_filename(filename)
        
        # Extract text and parse values
        text = self.extract_text_from_pdf(pdf_path)
        lab_values = self.parse_lab_values(text, test_type)
        
        return {
            'file': filename,
            'test_date': test_date,
            'test_type': test_type,
            'results': lab_values,
            'raw_text': text[:500]  # Store first 500 chars for debugging
        }
    
    def parse_all_pdfs(self) -> List[Dict]:
        """
        Parse all PDF files in the health data directory.
        
        Returns:
            List of parsed lab result dictionaries
        """
        all_results = []
        
        if not os.path.exists(self.health_data_dir):
            print(f"Warning: Health data directory '{self.health_data_dir}' not found")
            return all_results
        
        pdf_files = [f for f in os.listdir(self.health_data_dir) if f.endswith('.pdf')]
        
        print(f"Found {len(pdf_files)} PDF files in {self.health_data_dir}")
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.health_data_dir, pdf_file)
            print(f"Parsing {pdf_file}...")
            
            try:
                result = self.parse_pdf_file(pdf_path)
                all_results.append(result)
                print(f"✓ Extracted {len(result['results'])} values from {pdf_file}")
            except Exception as e:
                print(f"✗ Error parsing {pdf_file}: {e}")
        
        return all_results
    
    def manual_entry_helper(self, pdf_path: str):
        """
        Helper function to display PDF text for manual data entry.
        Useful when automated parsing fails.
        
        Args:
            pdf_path: Path to PDF file
        """
        text = self.extract_text_from_pdf(pdf_path)
        print("=" * 80)
        print(f"PDF: {os.path.basename(pdf_path)}")
        print("=" * 80)
        print(text)
        print("=" * 80)


def create_manual_lab_data_template() -> Dict:
    """
    Create a template for manually entering lab data.
    Use this if PDF parsing doesn't work well.
    
    Returns:
        Template dictionary structure
    """
    return {
        'test_date': '2026-02-10',  # YYYY-MM-DD
        'test_type': 'Basic Metabolic Panel',
        'results': [
            {'test_name': 'Glucose', 'value': 95, 'unit': 'mg/dL', 'reference_range': '70-100'},
            {'test_name': 'Sodium', 'value': 140, 'unit': 'mEq/L', 'reference_range': '136-145'},
            # Add more results...
        ]
    }
