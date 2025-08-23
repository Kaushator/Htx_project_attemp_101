"""
HTX Project Main Entry Point
Main application for HTX trading analysis and reporting
"""

import argparse
import sys
import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.api.htx_client import HTXClient
from src.parsers.file_parser import FileParser
from src.analytics.pnl_report import PnLReport
from src.integrations.three_commas import ThreeCommasIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HTXProject:
    """Main HTX Project class"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize HTX Project
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self.load_config(config_path)
        self.htx_client = None
        self.file_parser = None
        self.pnl_report = None
        self.three_commas = None
        
        self.initialize_components()
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            logger.warning(f"Configuration file {config_path} not found. Using default config.")
            return self.get_default_config()
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'htx': {
                'api_key': '',
                'secret_key': '',
                'base_url': 'https://api.huobi.pro'
            },
            'three_commas': {
                'api_key': '',
                'secret_key': ''
            },
            'data': {
                'directory': 'data',
                'file_types': ['csv', 'xlsx', 'xls']
            },
            'analytics': {
                'default_currency': 'USD',
                'timezone': 'UTC'
            }
        }
    
    def initialize_components(self) -> None:
        """Initialize project components"""
        # Initialize HTX client
        if self.config.get('htx', {}).get('api_key'):
            self.htx_client = HTXClient(
                api_key=self.config['htx']['api_key'],
                secret_key=self.config['htx']['secret_key'],
                base_url=self.config['htx'].get('base_url', 'https://api.huobi.pro')
            )
            logger.info("HTX client initialized")
        
        # Initialize file parser
        data_dir = self.config.get('data', {}).get('directory', 'data')
        self.file_parser = FileParser(data_directory=data_dir)
        logger.info(f"File parser initialized with data directory: {data_dir}")
        
        # Initialize PnL report
        self.pnl_report = PnLReport()
        logger.info("PnL report generator initialized")
        
        # Initialize 3Commas integration
        if self.config.get('three_commas', {}).get('api_key'):
            self.three_commas = ThreeCommasIntegration(
                api_key=self.config['three_commas']['api_key'],
                secret_key=self.config['three_commas']['secret_key']
            )
            logger.info("3Commas integration initialized")
    
    def list_files(self) -> None:
        """List available data files"""
        try:
            files = self.file_parser.list_available_files()
            if files:
                print(f"\nAvailable data files ({len(files)}):")
                for i, filename in enumerate(files, 1):
                    file_info = self.file_parser.get_file_info(filename)
                    print(f"{i:2d}. {filename}")
                    print(f"     Size: {file_info.get('size', 0):,} bytes")
                    print(f"     Rows: {file_info.get('rows', 0):,}")
                    print(f"     Columns: {file_info.get('columns', 0)}")
                    print()
            else:
                print("No data files found in the data directory.")
        except Exception as e:
            logger.error(f"Error listing files: {e}")
    
    def analyze_file(self, filename: str, symbol: Optional[str] = None) -> None:
        """
        Analyze a specific file
        
        Args:
            filename: Name of the file to analyze
            symbol: Specific symbol to analyze (optional)
        """
        try:
            # Load and parse file
            if filename.endswith('.csv'):
                df = self.file_parser.load_csv_file(filename)
            elif filename.endswith(('.xlsx', '.xls')):
                df = self.file_parser.load_excel_file(filename)
            else:
                print(f"Unsupported file format: {filename}")
                return
            
            # Parse trade data
            df = self.file_parser.parse_trade_data(df)
            
            # Load data into PnL report
            self.pnl_report.load_trade_data(df)
            
            # Generate and display report
            report = self.pnl_report.generate_summary_report(symbol)
            
            if report:
                self.display_report(report, symbol)
            else:
                print("No data available for analysis.")
                
        except Exception as e:
            logger.error(f"Error analyzing file {filename}: {e}")
    
    def display_report(self, report: Dict[str, Any], symbol: Optional[str] = None) -> None:
        """
        Display analysis report
        
        Args:
            report: Report data
            symbol: Symbol being analyzed
        """
        print(f"\n{'='*60}")
        print(f"ANALYSIS REPORT - {symbol if symbol else 'ALL SYMBOLS'}")
        print(f"{'='*60}")
        
        # Period information
        period = report.get('period', {})
        print(f"\n📅 PERIOD:")
        print(f"   Start Date: {period.get('start_date', 'N/A')}")
        print(f"   End Date:   {period.get('end_date', 'N/A')}")
        print(f"   Total Days: {period.get('total_days', 0)}")
        
        # Volume information
        volume = report.get('volume', {})
        print(f"\n📊 VOLUME:")
        print(f"   Total Volume: {volume.get('total_volume', 0):,.2f}")
        print(f"   Avg Volume per Trade: {volume.get('avg_volume_per_trade', 0):,.2f}")
        
        # Performance information
        performance = report.get('performance', {})
        print(f"\n💰 PERFORMANCE:")
        print(f"   Total PnL: {performance.get('total_pnl', 0):,.2f}")
        print(f"   Net PnL:   {performance.get('net_pnl', 0):,.2f}")
        print(f"   Max Drawdown: {performance.get('max_drawdown', 0):,.2f}")
        print(f"   Max Drawdown %: {performance.get('max_drawdown_pct', 0):,.2f}%")
        print(f"   Sharpe Ratio: {performance.get('sharpe_ratio', 0):,.2f}")
        
        # Trading statistics
        trading_stats = report.get('trading_stats', {})
        if trading_stats:
            print(f"\n📈 TRADING STATISTICS:")
            print(f"   Total Trades: {trading_stats.get('total_trades', 0)}")
            print(f"   Winning Trades: {trading_stats.get('winning_trades', 0)}")
            print(f"   Losing Trades: {trading_stats.get('losing_trades', 0)}")
            print(f"   Win Rate: {trading_stats.get('win_rate', 0)*100:.1f}%")
            print(f"   Loss Rate: {trading_stats.get('loss_rate', 0)*100:.1f}%")
            print(f"   Avg Win: {trading_stats.get('avg_win', 0):,.2f}")
            print(f"   Avg Loss: {trading_stats.get('avg_loss', 0):,.2f}")
            print(f"   Profit Factor: {trading_stats.get('profit_factor', 0):,.2f}")
        
        # Symbol breakdown
        symbols = report.get('symbols', [])
        if symbols:
            print(f"\n🔍 SYMBOL BREAKDOWN:")
            for symbol_data in symbols:
                sym = symbol_data.get('symbol', 'Unknown')
                print(f"   {sym}:")
                print(f"     PnL: {symbol_data.get('net_pnl', 0):,.2f}")
                print(f"     Volume: {symbol_data.get('total_volume', 0):,.2f}")
                print(f"     Trades: {symbol_data.get('trade_count', 0)}")
        
        print(f"\n{'='*60}")
    
    def sync_from_3commas(self, account_id: Optional[int] = None) -> None:
        """
        Sync data from 3Commas
        
        Args:
            account_id: Specific account ID to sync
        """
        if not self.three_commas:
            print("3Commas integration not configured. Please add API keys to config.yaml")
            return
        
        try:
            print("Syncing trades from 3Commas...")
            trades = self.three_commas.sync_trades_from_3commas(account_id)
            
            if trades:
                # Convert to DataFrame and save
                import pandas as pd
                df = pd.DataFrame(trades)
                
                # Save to CSV
                filename = f"3commas_trades_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
                self.file_parser.export_to_csv(df, filename)
                
                print(f"Synced {len(trades)} trades and saved to {filename}")
                
                # Analyze the synced data
                self.pnl_report.load_trade_data(df)
                report = self.pnl_report.generate_summary_report()
                self.display_report(report)
            else:
                print("No trades found to sync.")
                
        except Exception as e:
            logger.error(f"Error syncing from 3Commas: {e}")
    
    def export_report(self, filename: str, symbol: Optional[str] = None) -> None:
        """
        Export analysis report to file
        
        Args:
            filename: Output filename
            symbol: Specific symbol to export
        """
        try:
            if not self.pnl_report.trades_df is not None:
                print("No trade data loaded. Please analyze a file first.")
                return
            
            report = self.pnl_report.generate_summary_report(symbol)
            self.pnl_report.export_report_to_csv(report, filename)
            print(f"Report exported to {filename}")
            
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
    
    def get_htx_data(self, symbol: str, period: str = '1day', size: int = 200) -> None:
        """
        Get data from HTX API
        
        Args:
            symbol: Trading symbol
            period: Time period
            size: Number of data points
        """
        if not self.htx_client:
            print("HTX client not configured. Please add API keys to config.yaml")
            return
        
        try:
            print(f"Fetching {symbol} data from HTX...")
            data = self.htx_client.get_klines(symbol, period, size)
            
            if data and 'data' in data:
                # Convert to DataFrame
                import pandas as pd
                df = pd.DataFrame(data['data'], columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume', 'amount'
                ])
                
                # Convert timestamp
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                
                # Save to CSV
                filename = f"htx_{symbol}_{period}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
                self.file_parser.export_to_csv(df, filename)
                
                print(f"Downloaded {len(df)} data points and saved to {filename}")
            else:
                print("No data received from HTX API.")
                
        except Exception as e:
            logger.error(f"Error getting HTX data: {e}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='HTX Trading Analysis Tool')
    parser.add_argument('--config', default='config.yaml', help='Configuration file path')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List files command
    subparsers.add_parser('list', help='List available data files')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a data file')
    analyze_parser.add_argument('filename', help='File to analyze')
    analyze_parser.add_argument('--symbol', help='Specific symbol to analyze')
    
    # Sync from 3Commas command
    sync_parser = subparsers.add_parser('sync', help='Sync data from 3Commas')
    sync_parser.add_argument('--account-id', type=int, help='Specific account ID to sync')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export analysis report')
    export_parser.add_argument('filename', help='Output filename')
    export_parser.add_argument('--symbol', help='Specific symbol to export')
    
    # Get HTX data command
    htx_parser = subparsers.add_parser('htx', help='Get data from HTX API')
    htx_parser.add_argument('symbol', help='Trading symbol')
    htx_parser.add_argument('--period', default='1day', help='Time period')
    htx_parser.add_argument('--size', type=int, default=200, help='Number of data points')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # Initialize project
        project = HTXProject(args.config)
        
        # Execute command
        if args.command == 'list':
            project.list_files()
        elif args.command == 'analyze':
            project.analyze_file(args.filename, args.symbol)
        elif args.command == 'sync':
            project.sync_from_3commas(args.account_id)
        elif args.command == 'export':
            project.export_report(args.filename, args.symbol)
        elif args.command == 'htx':
            project.get_htx_data(args.symbol, args.period, args.size)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
