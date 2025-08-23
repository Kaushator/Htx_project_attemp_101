"""
File Parser Module
Handles loading and parsing CSV and Excel files from HTX exchange
"""

import pandas as pd
import os
from typing import Dict, List, Optional, Union
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileParser:
    """Parser for CSV and Excel files from HTX exchange"""
    
    def __init__(self, data_directory: str = "data"):
        """
        Initialize file parser
        
        Args:
            data_directory: Directory containing CSV and Excel files
        """
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(exist_ok=True)
    
    def list_available_files(self) -> List[str]:
        """List all available CSV and Excel files in the data directory"""
        files = []
        for ext in ['*.csv', '*.xlsx', '*.xls']:
            files.extend([f.name for f in self.data_directory.glob(ext)])
        return sorted(files)
    
    def load_csv_file(self, filename: str) -> pd.DataFrame:
        """
        Load and parse CSV file
        
        Args:
            filename: Name of the CSV file
            
        Returns:
            Parsed DataFrame
        """
        file_path = self.data_directory / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # Try different encodings
            for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    logger.info(f"Successfully loaded {filename} with encoding {encoding}")
                    return self._standardize_columns(df)
                except UnicodeDecodeError:
                    continue
            
            raise ValueError(f"Could not decode {filename} with any supported encoding")
            
        except Exception as e:
            logger.error(f"Error loading CSV file {filename}: {e}")
            raise
    
    def load_excel_file(self, filename: str, sheet_name: Optional[Union[str, int]] = 0) -> pd.DataFrame:
        """
        Load and parse Excel file
        
        Args:
            filename: Name of the Excel file
            sheet_name: Sheet name or index to load (default: first sheet)
            
        Returns:
            Parsed DataFrame
        """
        file_path = self.data_directory / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            logger.info(f"Successfully loaded {filename}")
            return self._standardize_columns(df)
            
        except Exception as e:
            logger.error(f"Error loading Excel file {filename}: {e}")
            raise
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names for consistency
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with standardized column names
        """
        # Create a copy to avoid modifying the original
        df = df.copy()
        
        # Common column name mappings
        column_mappings = {
            # Time columns
            'time': 'timestamp',
            'date': 'timestamp',
            'datetime': 'timestamp',
            'Time': 'timestamp',
            'Date': 'timestamp',
            'DateTime': 'timestamp',
            
            # Price columns
            'price': 'price',
            'Price': 'price',
            'close': 'price',
            'Close': 'price',
            
            # Volume columns
            'volume': 'volume',
            'Volume': 'volume',
            'amount': 'volume',
            'Amount': 'volume',
            
            # Symbol columns
            'symbol': 'symbol',
            'Symbol': 'symbol',
            'pair': 'symbol',
            'Pair': 'symbol',
            
            # Side columns
            'side': 'side',
            'Side': 'side',
            'type': 'side',
            'Type': 'side',
            
            # Order ID columns
            'order_id': 'order_id',
            'Order ID': 'order_id',
            'orderid': 'order_id',
            'OrderId': 'order_id',
        }
        
        # Rename columns if they exist
        df.columns = [column_mappings.get(col, col) for col in df.columns]
        
        return df
    
    def parse_trade_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Parse and clean trade data
        
        Args:
            df: Raw trade data DataFrame
            
        Returns:
            Cleaned trade data DataFrame
        """
        df = df.copy()
        
        # Convert timestamp to datetime if it exists
        if 'timestamp' in df.columns:
            try:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            except Exception as e:
                logger.warning(f"Could not convert timestamp column: {e}")
        
        # Convert numeric columns
        numeric_columns = ['price', 'volume', 'amount', 'fee']
        for col in numeric_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except Exception as e:
                    logger.warning(f"Could not convert {col} to numeric: {e}")
        
        # Clean up side column
        if 'side' in df.columns:
            df['side'] = df['side'].str.lower().str.strip()
            df['side'] = df['side'].map({
                'buy': 'buy',
                'sell': 'sell',
                'b': 'buy',
                's': 'sell'
            })
        
        return df
    
    def parse_order_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Parse and clean order data
        
        Args:
            df: Raw order data DataFrame
            
        Returns:
            Cleaned order data DataFrame
        """
        df = df.copy()
        
        # Convert timestamp to datetime if it exists
        if 'timestamp' in df.columns:
            try:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            except Exception as e:
                logger.warning(f"Could not convert timestamp column: {e}")
        
        # Convert numeric columns
        numeric_columns = ['price', 'volume', 'amount', 'filled_amount', 'remaining_amount']
        for col in numeric_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except Exception as e:
                    logger.warning(f"Could not convert {col} to numeric: {e}")
        
        # Clean up status column
        if 'status' in df.columns:
            df['status'] = df['status'].str.lower().str.strip()
        
        return df
    
    def get_file_info(self, filename: str) -> Dict[str, any]:
        """
        Get information about a file
        
        Args:
            filename: Name of the file
            
        Returns:
            Dictionary with file information
        """
        file_path = self.data_directory / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        info = {
            'filename': filename,
            'size': file_path.stat().st_size,
            'modified': pd.Timestamp(file_path.stat().st_mtime, unit='s'),
            'extension': file_path.suffix.lower()
        }
        
        # Try to get basic DataFrame info
        try:
            if info['extension'] == '.csv':
                df = self.load_csv_file(filename)
            elif info['extension'] in ['.xlsx', '.xls']:
                df = self.load_excel_file(filename)
            else:
                return info
            
            info.update({
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns),
                'memory_usage': df.memory_usage(deep=True).sum()
            })
            
        except Exception as e:
            logger.warning(f"Could not analyze file {filename}: {e}")
        
        return info
    
    def export_to_csv(self, df: pd.DataFrame, filename: str) -> None:
        """
        Export DataFrame to CSV file
        
        Args:
            df: DataFrame to export
            filename: Output filename
        """
        file_path = self.data_directory / filename
        df.to_csv(file_path, index=False)
        logger.info(f"Exported data to {file_path}")
    
    def export_to_excel(self, df: pd.DataFrame, filename: str, sheet_name: str = 'Sheet1') -> None:
        """
        Export DataFrame to Excel file
        
        Args:
            df: DataFrame to export
            filename: Output filename
            sheet_name: Sheet name
        """
        file_path = self.data_directory / filename
        df.to_excel(file_path, sheet_name=sheet_name, index=False)
        logger.info(f"Exported data to {file_path}")
