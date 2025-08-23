"""
Tests for file parsers
"""

import pytest
import pandas as pd
from pathlib import Path
from app.services.parser_csv import FileParser


@pytest.fixture
def parser():
    """Create parser instance"""
    return FileParser()


@pytest.fixture
def sample_csv_data():
    """Create sample CSV data"""
    return pd.DataFrame({
        'Date': ['2023-01-01', '2023-01-02'],
        'Symbol': ['BTCUSDT', 'ETHUSDT'],
        'Side': ['buy', 'sell'],
        'Amount': [0.1, 0.5],
        'Price': [50000, 3000],
        'Fee': [0.001, 0.001]
    })


def test_parser_initialization(parser):
    """Test parser initialization"""
    assert parser.supported_extensions == ['.csv', '.xlsx', '.xls']
    assert 'exchange' in parser.column_mappings


def test_detect_sheet_type(parser):
    """Test sheet type detection"""
    columns = pd.Index(['Date', 'Symbol', 'Side', 'Amount', 'Price'])
    sheet_type = parser._detect_sheet_type(columns)
    assert sheet_type == 'exchange'


def test_standardize_columns(parser, sample_csv_data):
    """Test column standardization"""
    standardized = parser._standardize_columns(sample_csv_data, 'exchange')
    assert 'date' in standardized.columns
    assert 'symbol' in standardized.columns
    assert 'side' in standardized.columns


def test_clean_data(parser, sample_csv_data):
    """Test data cleaning"""
    cleaned = parser._clean_data(sample_csv_data, 'exchange')
    assert pd.api.types.is_datetime64_any_dtype(cleaned['date'])
    assert pd.api.types.is_numeric_dtype(cleaned['amount'])
    assert pd.api.types.is_numeric_dtype(cleaned['price'])


def test_get_summary(parser, sample_csv_data):
    """Test summary generation"""
    data = {'exchange': sample_csv_data}
    summary = parser.get_summary(data)
    assert summary['total_sheets'] == 1
    assert 'exchange' in summary['sheets']
    assert summary['sheets']['exchange']['rows'] == 2
