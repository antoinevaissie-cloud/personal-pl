import io
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from .common import parse_amount, extract_merchant

def load_revolut_csv(file_content: bytes) -> List[Dict[str, Any]]:
    """Load Revolut CSV with deterministic parsing."""
    # Revolut uses UTF-8 encoding
    try:
        content_str = file_content.decode('utf-8')
    except UnicodeDecodeError:
        # Fallback to latin-1
        content_str = file_content.decode('latin-1')
    
    try:
        # Read with comma separator (standard CSV)
        df = pd.read_csv(
            io.StringIO(content_str),
            sep=',',
            dtype=str  # Keep everything as string for manual parsing
        )
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Expected columns
        required_cols = ['Completed Date', 'Description', 'Amount', 'Currency']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            # Print available columns for debugging
            print(f"Available Revolut columns: {df.columns.tolist()}")
            raise ValueError(f"Missing required columns in Revolut CSV: {missing_cols}")
        
        rows = []
        for _, row in df.iterrows():
            # Skip empty rows
            if pd.isna(row.get('Completed Date')) or row.get('Completed Date', '').strip() == '':
                continue
            
            # Only process completed transactions
            state = row.get('State', '').strip().upper()
            if state and state != 'COMPLETED':
                continue
            
            try:
                # Parse completed date
                date_str = str(row['Completed Date']).strip()
                ts = None
                
                # Try different datetime formats
                date_formats = [
                    '%Y-%m-%d %H:%M:%S',
                    '%d-%m-%Y %H:%M:%S', 
                    '%Y-%m-%d',
                    '%d-%m-%Y'
                ]
                
                for fmt in date_formats:
                    try:
                        ts = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                
                if ts is None:
                    print(f"Warning: Could not parse date '{date_str}', skipping row")
                    continue
                
                # Parse amount (no comma decimals, standard decimal point)
                amount_raw = str(row['Amount']).strip()
                amount = parse_amount(amount_raw, decimal_comma=False)
                
                # Parse fee if present and merge into amount
                fee_raw = row.get('Fee', '0').strip()
                if fee_raw and fee_raw != '0':
                    fee = parse_amount(fee_raw, decimal_comma=False)
                    # Subtract fee from amount (making it more negative for expenses)
                    amount = amount - abs(fee)
                
                # Description and merchant
                description = str(row['Description']).strip()
                merchant = extract_merchant(description)
                
                # Currency (expect GBP but could be others)
                currency = str(row['Currency']).strip().upper()
                
                # Account information
                product = row.get('Product', 'Revolut Card')
                if pd.isna(product):
                    product = 'Revolut Card'
                
                # Balance if available
                balance = None
                if 'Balance' in row and not pd.isna(row['Balance']):
                    try:
                        balance = parse_amount(str(row['Balance']), decimal_comma=False)
                    except:
                        pass
                
                rows.append({
                    'ts': ts,
                    'description': description,
                    'merchant': merchant,
                    'amount_raw': amount_raw,
                    'amount': amount,
                    'currency': currency,
                    'account_label': str(product).strip(),
                    'extra': {
                        'type': row.get('Type', ''),
                        'started_date': row.get('Started Date', ''),
                        'state': row.get('State', ''),
                        'fee_raw': fee_raw,
                        'balance': balance,
                        'raw_row': dict(row)
                    }
                })
                
            except Exception as e:
                print(f"Warning: Skipping Revolut row due to parsing error: {e}")
                continue
        
        return rows
        
    except Exception as e:
        raise ValueError(f"Error parsing Revolut CSV: {e}")

def validate_revolut_format(file_content: bytes) -> bool:
    """Validate that file appears to be Revolut format."""
    try:
        content_str = file_content.decode('utf-8')
        
        # Look for Revolut-specific patterns
        if ',' in content_str and ('Completed Date' in content_str or 'Description' in content_str):
            return True
        
        return False
        
    except Exception:
        return False