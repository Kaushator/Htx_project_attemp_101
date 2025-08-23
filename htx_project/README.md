# HTX Project

A comprehensive trading analysis and reporting tool for HTX exchange, with support for CSV/Excel file parsing, PnL calculations, and 3Commas integration.

## Features

- **HTX API Integration**: Direct access to HTX exchange data
- **File Parser**: Load and parse CSV/Excel files from HTX exchange
- **PnL Analytics**: Comprehensive profit and loss analysis with detailed reports
- **3Commas Integration**: Sync data from 3Commas trading platform
- **Data Export**: Export analysis results to CSV/Excel formats
- **Chart Generation**: Visualize trading performance with charts

## Project Structure

```
htx_project/
│── data/                  # CSV и excel файлы с биржи
│── src/
│   │── api/               # модуль работы с HTX API
│   │   └── htx_client.py
│   │── parsers/           # загрузка и парсинг csv/xlsx
│   │   └── file_parser.py
│   │── analytics/         # аналитика и отчёты
│   │   └── pnl_report.py
│   │── integrations/      # связка с 3commas или другими площадками
│   │   └── three_commas.py
│   │── main.py            # входная точка
│── tests/                 # юнит-тесты
│── requirements.txt
│── README.md
│── config.yaml            # настройки (api keys, пути к файлам, валюты)
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd htx_project
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the project**:
   - Copy `config.yaml` and update with your API keys
   - Add your CSV/Excel files to the `data/` directory

## Configuration

Edit `config.yaml` to add your API keys and settings:

```yaml
# HTX Exchange API Configuration
htx:
  api_key: "your_htx_api_key"
  secret_key: "your_htx_secret_key"
  base_url: "https://api.huobi.pro"

# 3Commas Integration Configuration
three_commas:
  api_key: "your_3commas_api_key"
  secret_key: "your_3commas_secret_key"
```

## Usage

### Command Line Interface

The project provides a command-line interface for various operations:

#### List available data files
```bash
python src/main.py list
```

#### Analyze a data file
```bash
python src/main.py analyze your_file.csv
python src/main.py analyze your_file.csv --symbol BTCUSDT
```

#### Sync data from 3Commas
```bash
python src/main.py sync
python src/main.py sync --account-id 12345
```

#### Export analysis report
```bash
python src/main.py export report.csv
python src/main.py export report.csv --symbol BTCUSDT
```

#### Get data from HTX API
```bash
python src/main.py htx BTCUSDT
python src/main.py htx BTCUSDT --period 1day --size 500
```

### Python API

You can also use the project as a Python library:

```python
from src.main import HTXProject

# Initialize the project
project = HTXProject("config.yaml")

# List available files
project.list_files()

# Analyze a file
project.analyze_file("trades.csv", symbol="BTCUSDT")

# Sync from 3Commas
project.sync_from_3commas()

# Get HTX data
project.get_htx_data("BTCUSDT", period="1day", size=200)
```

## Data Format

The project expects CSV/Excel files with the following columns:

### Trade Data
- `timestamp`: Trade timestamp
- `symbol`: Trading pair (e.g., BTCUSDT)
- `side`: Trade side (buy/sell)
- `price`: Trade price
- `volume`: Trade volume
- `fee`: Trading fee (optional)
- `order_id`: Order ID (optional)

### Order Data
- `timestamp`: Order timestamp
- `symbol`: Trading pair
- `side`: Order side
- `price`: Order price
- `volume`: Order volume
- `status`: Order status
- `filled_amount`: Filled amount (optional)
- `remaining_amount`: Remaining amount (optional)

## Analytics Features

### PnL Calculations
- Realized and unrealized PnL
- Average cost basis calculation
- Win/loss ratio analysis
- Profit factor calculation

### Performance Metrics
- Sharpe ratio
- Maximum drawdown
- Daily PnL tracking
- Symbol-wise breakdown

### Risk Analysis
- Drawdown analysis
- Volatility calculations
- Risk-adjusted returns

## 3Commas Integration

The project includes full integration with 3Commas:

- Sync trades and deals
- Bot management
- Account balance monitoring
- Automated trading strategies

### Supported Bot Types
- Grid bots
- DCA (Dollar Cost Averaging) bots
- Custom bot configurations

## Testing

Run the test suite:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=src tests/
```

## Development

### Code Style
The project uses:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking

### Running Development Tools
```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the example configurations

## Disclaimer

This software is for educational and research purposes. Trading cryptocurrencies involves risk, and you should never invest more than you can afford to lose. The authors are not responsible for any financial losses incurred through the use of this software.
