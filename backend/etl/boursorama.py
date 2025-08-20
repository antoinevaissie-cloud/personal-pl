import io
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from .common import parse_amount, ensure_windows_1252, extract_merchant

def load_boursorama_csv(file_content: bytes) -> List[Dict[str, Any]]:
    """Load Boursorama CSV with deterministic parsing."""
    # Decode with cp1252
    content_str = ensure_windows_1252(file_content)
    
    try:
        # Read with semicolon separator
        df = pd.read_csv(
            io.StringIO(content_str),
            sep=';',
            encoding=None,  # Already decoded
            dtype=str  # Keep everything as string for manual parsing
        )
        
        # Clean column names (remove BOM and whitespace)
        df.columns = df.columns.str.strip()
        # Remove BOM character if present
        df.columns = [col.replace('\ufeff', '').replace('ï»¿', '') for col in df.columns]
        
        # Expected columns
        required_cols = ['dateOp', 'label', 'amount']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            # Try alternative column names
            alt_mapping = {
                'dateOp': 'dateOp',
                'label': 'label', 
                'amount': 'amount'
            }
            # More flexible column detection
            available_cols = df.columns.tolist()
            print(f"Available Boursorama columns: {available_cols}")
        
        rows = []
        for _, row in df.iterrows():
            # Skip empty rows
            if pd.isna(row.get('dateOp')) or row.get('dateOp', '').strip() == '':
                continue
            
            try:
                # Parse date - detect format
                date_str = str(row['dateOp']).strip()
                ts = None
                
                # Try different date formats
                date_formats = ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y']
                for fmt in date_formats:
                    try:
                        ts = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                
                if ts is None:
                    print(f"Warning: Could not parse date '{date_str}', skipping row")
                    continue
                
                # Parse amount (may have comma decimals)
                amount_raw = str(row['amount']).strip()
                amount = parse_amount(amount_raw, decimal_comma=True)
                
                # Description and merchant
                description = str(row['label']).strip()
                merchant = extract_merchant(description)
                
                # Category information (store in extra for now)
                category_parent = row.get('categoryParent', '')
                category = row.get('category', '')
                
                # Account information
                account_label = row.get('accountLabel', 'Boursorama Account')
                if pd.isna(account_label):
                    account_label = 'Boursorama Account'
                
                # Balance if available
                balance = None
                if 'accountbalance' in row and not pd.isna(row['accountbalance']):
                    try:
                        balance = parse_amount(str(row['accountbalance']), decimal_comma=True)
                    except:
                        pass
                
                rows.append({
                    'ts': ts,
                    'description': description,
                    'merchant': merchant,
                    'amount_raw': amount_raw,
                    'amount': amount,
                    'currency': 'EUR',
                    'account_label': str(account_label).strip(),
                    'extra': {
                        'category_parent': str(category_parent).strip(),
                        'category': str(category).strip(),
                        'balance': balance,
                        'supplier_found': row.get('supplierFound', ''),
                        'comment': row.get('comment', ''),
                        'account_num': row.get('accountNum', ''),
                        'raw_row': dict(row)
                    }
                })
                
            except Exception as e:
                print(f"Warning: Skipping Boursorama row due to parsing error: {e}")
                continue
        
        return rows
        
    except Exception as e:
        raise ValueError(f"Error parsing Boursorama CSV: {e}")

def validate_boursorama_format(file_content: bytes) -> bool:
    """Validate that file appears to be Boursorama format."""
    try:
        content_str = ensure_windows_1252(file_content)
        
        # Look for Boursorama-specific patterns
        if ';' in content_str and ('dateOp' in content_str or 'label' in content_str):
            return True
        
        return False
        
    except Exception:
        return False