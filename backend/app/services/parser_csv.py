"""
CSV and Excel file parser service
Handles parsing of trading data files
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class FileParser:
    """Parser for CSV and Excel files with trading data"""
    
    def __init__(self):
        self.supported_extensions = ['.csv', '.xlsx', '.xls']
        self.column_mappings = {
            'exchange': {
                'date': ['Date', 'Time', 'DateTime'],
                'symbol': ['Symbol', 'Pair', 'Market'],
                'side': ['Side', 'Type', 'Order Type'],
                'amount': ['Amount', 'Quantity', 'Size'],
                'price': ['Price', 'Rate'],
                'fee': ['Fee', 'Commission'],
                'total': ['Total', 'Value']
            },
            'deposit': {
                'date': ['Date', 'Time', 'DateTime'],
                'currency': ['Currency', 'Coin'],
                'amount': ['Amount', 'Quantity'],
                'txid': ['TxID', 'Transaction ID', 'Hash']
            },
            'withdraw': {
                'date': ['Date', 'Time', 'DateTime'],
                'currency': ['Currency', 'Coin'],
                'amount': ['Amount', 'Quantity'],
                'fee': ['Fee', 'Withdrawal Fee'],
                'txid': ['TxID', 'Transaction ID', 'Hash']
            },
            'transfer': {
                'date': ['Date', 'Time', 'DateTime'],
                'currency': ['Currency', 'Coin'],
                'amount': ['Amount', 'Quantity'],
                'from_account': ['From', 'From Account'],
                'to_account': ['To', 'To Account']
            }
        }
    
    async def parse_csv_file(self, file_path: str) -> Dict[str, pd.DataFrame]:
        """Parse CSV file and return structured data"""
        try:
            df = pd.read_csv(file_path)
            return await self._process_dataframe(df, file_path)
        except Exception as e:
            logger.error(f"Failed to parse CSV file {file_path}: {e}")
            raise
    
    async def parse_excel_file(self, file_path: str) -> Dict[str, pd.DataFrame]:
        """Parse Excel file and return structured data"""
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(file_path)
            result = {}
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                if not df.empty:
                    processed_df = await self._process_dataframe(df, file_path, sheet_name)
                    if processed_df:
                        result[sheet_name] = processed_df
            
            return result
        except Exception as e:
            logger.error(f"Failed to parse Excel file {file_path}: {e}")
            raise
    
    async def _process_dataframe(self, df: pd.DataFrame, file_path: str, sheet_name: str = None) -> Optional[pd.DataFrame]:
        """Process dataframe and standardize columns"""
        if df.empty:
            return None
        
        # Determine sheet type based on column names
        sheet_type = self._detect_sheet_type(df.columns)
        if not sheet_type:
            logger.warning(f"Could not determine sheet type for {file_path} sheet: {sheet_name}")
            return None
        
        # Standardize column names
        df = self._standardize_columns(df, sheet_type)
        
        # Clean and validate data
        df = self._clean_data(df, sheet_type)
        
        # Add metadata
        df['source_file'] = Path(file_path).name
        df['sheet_name'] = sheet_name or 'main'
        df['parsed_at'] = datetime.utcnow()
        
        return df
    
    def _detect_sheet_type(self, columns: pd.Index) -> Optional[str]:
        """Detect sheet type based on column names"""
        columns_lower = [col.lower() for col in columns]
        
        for sheet_type, mappings in self.column_mappings.items():
            for field, possible_names in mappings.items():
                if any(name.lower() in columns_lower for name in possible_names):
                    return sheet_type
        
        return None
    
    def _standardize_columns(self, df: pd.DataFrame, sheet_type: str) -> pd.DataFrame:
        """Standardize column names based on sheet type"""
        df_copy = df.copy()
        mappings = self.column_mappings[sheet_type]
        
        for standard_name, possible_names in mappings.items():
            for possible_name in possible_names:
                if possible_name in df_copy.columns:
                    df_copy = df_copy.rename(columns={possible_name: standard_name})
                    break
        
        return df_copy
    
    def _clean_data(self, df: pd.DataFrame, sheet_type: str) -> pd.DataFrame:
        """Clean and validate data"""
        df_copy = df.copy()
        
        # Convert date columns
        if 'date' in df_copy.columns:
            df_copy['date'] = pd.to_datetime(df_copy['date'], errors='coerce')
        
        # Convert numeric columns
        numeric_columns = ['amount', 'price', 'fee', 'total']
        for col in numeric_columns:
            if col in df_copy.columns:
                df_copy[col] = pd.to_numeric(df_copy[col], errors='coerce')
        
        # Remove rows with invalid dates
        if 'date' in df_copy.columns:
            df_copy = df_copy.dropna(subset=['date'])
        
        return df_copy
    
    async def save_to_database(self, data: Dict[str, pd.DataFrame], db: AsyncSession):
        """Save parsed data to database"""
        # TODO: Implement database saving logic
        # This will be implemented when models are created
        logger.info(f"Saving {len(data)} sheets to database")
        
        for sheet_name, df in data.items():
            logger.info(f"Processing sheet: {sheet_name} with {len(df)} rows")
            # await self._save_sheet_to_db(sheet_name, df, db)
    
    def export_to_csv(self, data: Dict[str, pd.DataFrame], output_dir: str):
        """Export processed data to CSV files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for sheet_name, df in data.items():
            output_file = output_path / f"{sheet_name}.csv"
            df.to_csv(output_file, index=False)
            logger.info(f"Exported {sheet_name} to {output_file}")
    
    def get_summary(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Get summary statistics for parsed data"""
        summary = {
            "total_sheets": len(data),
            "sheets": {}
        }
        
        for sheet_name, df in data.items():
            sheet_summary = {
                "rows": len(df),
                "columns": len(df.columns),
                "date_range": None,
                "currencies": []
            }
            
            if 'date' in df.columns:
                sheet_summary["date_range"] = {
                    "start": df['date'].min().isoformat() if not df['date'].isna().all() else None,
                    "end": df['date'].max().isoformat() if not df['date'].isna().all() else None
                }
            
            if 'currency' in df.columns:
                sheet_summary["currencies"] = df['currency'].unique().tolist()
            
            summary["sheets"][sheet_name] = sheet_summary
        
        return summary
