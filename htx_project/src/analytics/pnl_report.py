"""
PnL Report Module
Provides analytics and reporting functionality for profit and loss calculations
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PnLReport:
    """Profit and Loss Report Generator"""
    
    def __init__(self):
        """Initialize PnL Report generator"""
        self.trades_df = None
        self.orders_df = None
    
    def load_trade_data(self, trades_df: pd.DataFrame) -> None:
        """
        Load trade data for analysis
        
        Args:
            trades_df: DataFrame containing trade data
        """
        self.trades_df = trades_df.copy()
        logger.info(f"Loaded {len(trades_df)} trades for analysis")
    
    def load_order_data(self, orders_df: pd.DataFrame) -> None:
        """
        Load order data for analysis
        
        Args:
            orders_df: DataFrame containing order data
        """
        self.orders_df = orders_df.copy()
        logger.info(f"Loaded {len(orders_df)} orders for analysis")
    
    def calculate_pnl_by_symbol(self, symbol: Optional[str] = None) -> pd.DataFrame:
        """
        Calculate PnL by symbol
        
        Args:
            symbol: Specific symbol to analyze (if None, analyze all symbols)
            
        Returns:
            DataFrame with PnL calculations
        """
        if self.trades_df is None:
            raise ValueError("No trade data loaded. Call load_trade_data() first.")
        
        df = self.trades_df.copy()
        
        if symbol:
            df = df[df['symbol'] == symbol]
        
        if df.empty:
            return pd.DataFrame()
        
        # Group by symbol and calculate PnL
        pnl_data = []
        
        for sym in df['symbol'].unique():
            symbol_trades = df[df['symbol'] == sym].copy()
            symbol_trades = symbol_trades.sort_values('timestamp')
            
            # Calculate running balance
            symbol_trades['cumulative_volume'] = symbol_trades['volume'].cumsum()
            symbol_trades['cumulative_value'] = (symbol_trades['volume'] * symbol_trades['price']).cumsum()
            
            # Calculate average price
            symbol_trades['avg_price'] = symbol_trades['cumulative_value'] / symbol_trades['cumulative_volume']
            
            # Calculate PnL
            symbol_trades['pnl'] = 0.0
            
            for i in range(1, len(symbol_trades)):
                prev_avg_price = symbol_trades.iloc[i-1]['avg_price']
                current_price = symbol_trades.iloc[i]['price']
                current_volume = symbol_trades.iloc[i]['volume']
                current_side = symbol_trades.iloc[i]['side']
                
                if current_side == 'sell':
                    # Calculate PnL for sell trades
                    pnl = (current_price - prev_avg_price) * current_volume
                    symbol_trades.iloc[i, symbol_trades.columns.get_loc('pnl')] = pnl
            
            # Calculate total PnL
            total_pnl = symbol_trades['pnl'].sum()
            total_volume = symbol_trades['volume'].sum()
            total_fees = symbol_trades.get('fee', pd.Series(0)).sum()
            
            pnl_data.append({
                'symbol': sym,
                'total_volume': total_volume,
                'total_pnl': total_pnl,
                'total_fees': total_fees,
                'net_pnl': total_pnl - total_fees,
                'trade_count': len(symbol_trades),
                'first_trade': symbol_trades['timestamp'].min(),
                'last_trade': symbol_trades['timestamp'].max()
            })
        
        return pd.DataFrame(pnl_data)
    
    def calculate_daily_pnl(self, symbol: Optional[str] = None) -> pd.DataFrame:
        """
        Calculate daily PnL
        
        Args:
            symbol: Specific symbol to analyze (if None, analyze all symbols)
            
        Returns:
            DataFrame with daily PnL calculations
        """
        if self.trades_df is None:
            raise ValueError("No trade data loaded. Call load_trade_data() first.")
        
        df = self.trades_df.copy()
        
        if symbol:
            df = df[df['symbol'] == symbol]
        
        if df.empty:
            return pd.DataFrame()
        
        # Add date column
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        
        # Calculate daily PnL
        daily_pnl = df.groupby('date').agg({
            'pnl': 'sum',
            'volume': 'sum',
            'fee': 'sum'
        }).reset_index()
        
        daily_pnl['net_pnl'] = daily_pnl['pnl'] - daily_pnl['fee']
        daily_pnl['cumulative_pnl'] = daily_pnl['net_pnl'].cumsum()
        
        return daily_pnl
    
    def calculate_win_loss_ratio(self, symbol: Optional[str] = None) -> Dict[str, float]:
        """
        Calculate win/loss ratio
        
        Args:
            symbol: Specific symbol to analyze (if None, analyze all symbols)
            
        Returns:
            Dictionary with win/loss statistics
        """
        if self.trades_df is None:
            raise ValueError("No trade data loaded. Call load_trade_data() first.")
        
        df = self.trades_df.copy()
        
        if symbol:
            df = df[df['symbol'] == symbol]
        
        if df.empty:
            return {}
        
        # Calculate PnL for each trade
        pnl_by_symbol = self.calculate_pnl_by_symbol(symbol)
        
        if pnl_by_symbol.empty:
            return {}
        
        # Get individual trade PnL
        df = self.trades_df.copy()
        if symbol:
            df = df[df['symbol'] == symbol]
        
        df = df.sort_values('timestamp')
        
        # Calculate running PnL for each trade
        df['cumulative_volume'] = df['volume'].cumsum()
        df['cumulative_value'] = (df['volume'] * df['price']).cumsum()
        df['avg_price'] = df['cumulative_value'] / df['cumulative_volume']
        df['trade_pnl'] = 0.0
        
        for i in range(1, len(df)):
            if df.iloc[i]['side'] == 'sell':
                prev_avg_price = df.iloc[i-1]['avg_price']
                current_price = df.iloc[i]['price']
                current_volume = df.iloc[i]['volume']
                pnl = (current_price - prev_avg_price) * current_volume
                df.iloc[i, df.columns.get_loc('trade_pnl')] = pnl
        
        # Calculate statistics
        winning_trades = df[df['trade_pnl'] > 0]
        losing_trades = df[df['trade_pnl'] < 0]
        
        total_trades = len(df[df['trade_pnl'] != 0])
        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        
        win_rate = win_count / total_trades if total_trades > 0 else 0
        loss_rate = loss_count / total_trades if total_trades > 0 else 0
        
        avg_win = winning_trades['trade_pnl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['trade_pnl'].mean() if len(losing_trades) > 0 else 0
        
        profit_factor = abs(avg_win * win_count / (avg_loss * loss_count)) if avg_loss != 0 and loss_count > 0 else float('inf')
        
        return {
            'total_trades': total_trades,
            'winning_trades': win_count,
            'losing_trades': loss_count,
            'win_rate': win_rate,
            'loss_rate': loss_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'total_pnl': df['trade_pnl'].sum(),
            'total_fees': df.get('fee', pd.Series(0)).sum(),
            'net_pnl': df['trade_pnl'].sum() - df.get('fee', pd.Series(0)).sum()
        }
    
    def calculate_drawdown(self, symbol: Optional[str] = None) -> pd.DataFrame:
        """
        Calculate drawdown analysis
        
        Args:
            symbol: Specific symbol to analyze (if None, analyze all symbols)
            
        Returns:
            DataFrame with drawdown calculations
        """
        if self.trades_df is None:
            raise ValueError("No trade data loaded. Call load_trade_data() first.")
        
        df = self.trades_df.copy()
        
        if symbol:
            df = df[df['symbol'] == symbol]
        
        if df.empty:
            return pd.DataFrame()
        
        # Calculate cumulative PnL
        daily_pnl = self.calculate_daily_pnl(symbol)
        
        if daily_pnl.empty:
            return pd.DataFrame()
        
        # Calculate running maximum and drawdown
        daily_pnl['running_max'] = daily_pnl['cumulative_pnl'].expanding().max()
        daily_pnl['drawdown'] = daily_pnl['cumulative_pnl'] - daily_pnl['running_max']
        daily_pnl['drawdown_pct'] = (daily_pnl['drawdown'] / daily_pnl['running_max']) * 100
        
        return daily_pnl
    
    def generate_summary_report(self, symbol: Optional[str] = None) -> Dict[str, any]:
        """
        Generate comprehensive summary report
        
        Args:
            symbol: Specific symbol to analyze (if None, analyze all symbols)
            
        Returns:
            Dictionary with comprehensive report data
        """
        if self.trades_df is None:
            raise ValueError("No trade data loaded. Call load_trade_data() first.")
        
        # Get basic statistics
        pnl_by_symbol = self.calculate_pnl_by_symbol(symbol)
        win_loss_stats = self.calculate_win_loss_ratio(symbol)
        daily_pnl = self.calculate_daily_pnl(symbol)
        drawdown_data = self.calculate_drawdown(symbol)
        
        # Calculate additional metrics
        df = self.trades_df.copy()
        if symbol:
            df = df[df['symbol'] == symbol]
        
        if df.empty:
            return {}
        
        # Time period analysis
        start_date = df['timestamp'].min()
        end_date = df['timestamp'].max()
        total_days = (end_date - start_date).days + 1
        
        # Volume analysis
        total_volume = df['volume'].sum()
        avg_volume_per_trade = df['volume'].mean()
        
        # Price analysis
        if 'price' in df.columns:
            avg_price = df['price'].mean()
            price_volatility = df['price'].std()
        else:
            avg_price = price_volatility = 0
        
        # Fee analysis
        total_fees = df.get('fee', pd.Series(0)).sum()
        avg_fee_per_trade = df.get('fee', pd.Series(0)).mean()
        
        # Drawdown analysis
        max_drawdown = drawdown_data['drawdown'].min() if not drawdown_data.empty else 0
        max_drawdown_pct = drawdown_data['drawdown_pct'].min() if not drawdown_data.empty else 0
        
        # Sharpe ratio (simplified)
        if not daily_pnl.empty and daily_pnl['net_pnl'].std() != 0:
            sharpe_ratio = daily_pnl['net_pnl'].mean() / daily_pnl['net_pnl'].std() * np.sqrt(252)
        else:
            sharpe_ratio = 0
        
        report = {
            'period': {
                'start_date': start_date,
                'end_date': end_date,
                'total_days': total_days
            },
            'volume': {
                'total_volume': total_volume,
                'avg_volume_per_trade': avg_volume_per_trade
            },
            'price': {
                'avg_price': avg_price,
                'price_volatility': price_volatility
            },
            'fees': {
                'total_fees': total_fees,
                'avg_fee_per_trade': avg_fee_per_trade
            },
            'performance': {
                'total_pnl': win_loss_stats.get('total_pnl', 0),
                'net_pnl': win_loss_stats.get('net_pnl', 0),
                'max_drawdown': max_drawdown,
                'max_drawdown_pct': max_drawdown_pct,
                'sharpe_ratio': sharpe_ratio
            },
            'trading_stats': win_loss_stats,
            'symbols': pnl_by_symbol.to_dict('records') if not pnl_by_symbol.empty else []
        }
        
        return report
    
    def export_report_to_csv(self, report_data: Dict[str, any], filename: str) -> None:
        """
        Export report data to CSV
        
        Args:
            report_data: Report data dictionary
            filename: Output filename
        """
        # Convert report data to DataFrame format
        export_data = []
        
        # Add summary metrics
        for category, metrics in report_data.items():
            if isinstance(metrics, dict):
                for metric, value in metrics.items():
                    export_data.append({
                        'category': category,
                        'metric': metric,
                        'value': value
                    })
        
        df = pd.DataFrame(export_data)
        df.to_csv(filename, index=False)
        logger.info(f"Report exported to {filename}")
    
    def plot_pnl_chart(self, symbol: Optional[str] = None, save_path: Optional[str] = None) -> None:
        """
        Plot PnL chart (requires matplotlib)
        
        Args:
            symbol: Specific symbol to plot
            save_path: Path to save the chart
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
        except ImportError:
            logger.warning("matplotlib not available. Cannot plot chart.")
            return
        
        daily_pnl = self.calculate_daily_pnl(symbol)
        
        if daily_pnl.empty:
            logger.warning("No data available for plotting")
            return
        
        plt.figure(figsize=(12, 8))
        
        # Plot cumulative PnL
        plt.subplot(2, 1, 1)
        plt.plot(daily_pnl['date'], daily_pnl['cumulative_pnl'], linewidth=2)
        plt.title(f'Cumulative PnL - {symbol if symbol else "All Symbols"}')
        plt.ylabel('Cumulative PnL')
        plt.grid(True, alpha=0.3)
        
        # Plot daily PnL
        plt.subplot(2, 1, 2)
        plt.bar(daily_pnl['date'], daily_pnl['net_pnl'], alpha=0.7)
        plt.title(f'Daily PnL - {symbol if symbol else "All Symbols"}')
        plt.ylabel('Daily PnL')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Chart saved to {save_path}")
        
        plt.show()
