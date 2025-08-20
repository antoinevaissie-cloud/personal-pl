import io
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from .common import parse_amount, ensure_windows_1252, extract_merchant

def load_bnp_csv(file_content: bytes) -> List[Dict[str, Any]]:
    """Load BNP CSV with deterministic parsing."""
    # Decode with cp1252
    content_str = ensure_windows_1252(file_content)
    
    # Split lines and skip first 2 lines
    lines = content_str.split('\n')
    if len(lines) < 3:
        raise ValueError("BNP CSV must have at least 3 lines (2 header lines + data)")
    
    # Skip first 2 lines, then treat line 3 as header
    csv_content = '\n'.join(lines[2:])
    
    try:
        # Read with semicolon separator
        df = pd.read_csv(
            io.StringIO(csv_content), 
            sep=';',
            encoding=None,  # Already decoded
            dtype=str  # Keep everything as string for manual parsing
        )
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Expected columns (may vary by BNP export format)
        required_cols = ['Date operation', 'Libelle', 'Montant']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns in BNP CSV: {missing_cols}")
        
        rows = []
        for _, row in df.iterrows():
            # Skip empty rows
            if pd.isna(row.get('Date operation')) or row.get('Date operation', '').strip() == '':
                continue
            
            try:
                # Parse date (dd-mm-yyyy format)
                date_str = str(row['Date operation']).strip()
                ts = datetime.strptime(date_str, '%d-%m-%Y')
                
                # Parse amount (comma decimals)
                amount_raw = str(row['Montant']).strip()
                amount = parse_amount(amount_raw, decimal_comma=True)
                
                # Description and merchant
                description = str(row['Libelle']).strip()
                merchant = extract_merchant(description)
                
                # Additional fields
                account_label = row.get('Compte', 'Compte de chèques')
                if pd.isna(account_label):
                    account_label = 'Compte de chèques'
                
                rows.append({
                    'ts': ts,
                    'description': description,
                    'merchant': merchant,
                    'amount_raw': amount_raw,
                    'amount': amount,
                    'currency': 'EUR',
                    'account_label': str(account_label).strip(),
                    'extra': {
                        'categorie': row.get('Categorie operation', ''),
                        'sous_categorie': row.get('Sous Categorie', ''),
                        'raw_row': dict(row)
                    }
                })
                
            except Exception as e:
                print(f"Warning: Skipping BNP row due to parsing error: {e}")
                continue
        
        return rows
        
    except Exception as e:
        raise ValueError(f"Error parsing BNP CSV: {e}")

def validate_bnp_format(file_content: bytes) -> bool:
    """Validate that file appears to be BNP format."""
    try:
        content_str = ensure_windows_1252(file_content)
        lines = content_str.split('\n')
        
        # Should have at least 3 lines
        if len(lines) < 3:
            return False
        
        # Look for BNP-specific patterns in headers or content
        header_line = lines[2] if len(lines) > 2 else lines[0]
        
        # Check for semicolon separator and common BNP columns
        if ';' in header_line and ('Date operation' in header_line or 'Libelle' in header_line):
            return True
        
        return False
        
    except Exception:
        return False