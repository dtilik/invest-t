# Invest-T: Tinkoff Invest Trading Bot

An automated trading bot for short-term trading using the Tinkoff Invest API.

## Features

- Integration with Tinkoff Invest API
- Support for two modes: production and sandbox
- Two trading strategies: momentum and mean reversion
- Customizable trading strategy parameters
- Continuous trading capability with configurable intervals
- Detailed operation logging

## Requirements

- Python 3.8+
- Tinkoff Invest API access token

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/invest-t.git
cd invest-t
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # for Linux/Mac
# or .venv\Scripts\activate for Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## User Interface

Invest-T includes a modern web-based dashboard built with Next.js to help you visualize and manage your trading operations.

### UI Features

- **Dashboard Overview**: View key performance metrics at a glance
- **Account Management**: View, create, and modify trading accounts
- **Strategy Management**: Configure and monitor your trading strategies
- **Performance Analytics**: Visualize your trading performance with interactive charts
- **Trading Journal**: Keep track of all your trades and their outcomes
- **Real-time Price Charts**: Monitor market prices using TradingView's Lightweight Charts

### UI Tech Stack

- **Next.js**: React framework for the frontend
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Recharts**: For data visualization
- **Lucide React**: Icon library

### UI Installation

1. Navigate to the UI directory:
```bash
cd invest-t-ui
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Start the development server:
```bash
npm run dev
# or
yarn dev
```

4. Open [http://localhost:3000](http://localhost:3000) to view the dashboard

## Configuration

1. Create a .env file and add your token:
```
TINKOFF_TOKEN=your_token
```

### Backend Configuration

The main settings are in the `config.py` file:

- `SANDBOX_MODE`: sandbox mode (True/False)
- `TICKER`: instrument ticker for trading
- `STRATEGY`: strategy to use ('simple_momentum' or 'mean_reversion')
- `CANDLE_INTERVAL`: candle interval ('1m', '5m', '15m', '1h')
- `LOOKBACK_PERIOD`: number of candles for analysis
- `BUY_THRESHOLD` and `SELL_THRESHOLD`: threshold values for buy/sell signals
- `POSITION_SIZE`: position size (fraction of available funds)

## Usage

### Basic Launch

To run the bot with default settings:

```bash
python main.py
```

### Advanced Options

The bot supports several command-line arguments:

```bash
python main.py --strategy mean_reversion --ticker AAPL --interval 5m --sandbox --continuous --cycle-minutes 30
```

Available parameters:
- `--strategy`: trading strategy ('simple_momentum' or 'mean_reversion')
- `--ticker`: instrument ticker
- `--interval`: candle interval ('1m', '5m', '15m', '1h')
- `--sandbox`: use sandbox mode
- `--continuous`: run in continuous mode
- `--cycle-minutes`: minutes between trading cycles (default 15)

## Project Structure

- `main.py`: main entry point with extended functionality
- `bot.py`: simplified bot version
- `config.py`: configuration parameters
- `strategies/`: trading strategy modules
  - `base_strategy.py`: base class for all strategies
  - `momentum_strategy.py`: price momentum-based strategy
  - `mean_reversion_strategy.py`: mean reversion-based strategy
- `utils/`: helper functions
  - `helpers.py`: utilities for data processing and indicators

## Process Flow Diagram

Below is a diagram of the main processes of the trading bot:

```mermaid
flowchart TD
    A[Bot Launch] --> B{Sandbox Mode?}
    B -->|Yes| C[Connect to Sandbox API]
    B -->|No| D[Connect to Production API]
    C --> E[Get Accounts]
    D --> E
    E --> F[Get Instrument by Ticker]
    F --> G[Get Historical Data]
    G --> H[Analyze Data with Selected Strategy]
    H --> I{Trading Signal?}
    I -->|Buy| J[Place Buy Order]
    I -->|Sell| K[Place Sell Order]
    I -->|No Signal| L[Wait for Next Cycle]
    J --> M{Continuous Mode?}
    K --> M
    L --> M
    M -->|Yes| N[Pause Between Cycles]
    N --> G
    M -->|No| O[Terminate]
```

## Architecture

### System Architecture

Invest-T consists of two main components:

1. **Python Backend**: Handles trading logic, API communication, and strategy execution
2. **Next.js Frontend**: Provides visualization and management of trading activities

```mermaid
graph TD
    A[Next.js Frontend] -->|API Requests| B[Python Backend]
    B -->|API Responses| A
    B -->|Requests| C[Tinkoff Invest API]
    C -->|Responses| B
    B -->|Trading Signals| D[Strategy Modules]
    D -->|Buy/Sell/Hold| B
    B -->|Store Data| E[Database]
    E -->|Retrieve Data| B
    A -->|Fetch Analytics| E
```

### UI-Backend Integration

The Next.js UI communicates with the Python backend via a REST API:

- **Account Management**: View account balances, create/update accounts
- **Strategy Configuration**: Update strategy parameters, activate/deactivate strategies
- **Performance Monitoring**: Fetch historical trade data and performance metrics
- **Real-time Updates**: WebSocket connection for live trade notifications and price updates

## Class Diagram

```mermaid
classDiagram
    class TradingBot {
        +token: str
        +sandbox_mode: bool
        +ticker: str
        +figi: str
        +account_id: str
        +strategy: BaseStrategy
        +run(continuous, interval_minutes)
        -_execute_trading_cycle()
        -_initialize_trading(client)
        -_get_historical_data(client)
        -_place_buy_order(client)
        -_place_sell_order(client)
    }
    
    class BaseStrategy {
        <<abstract>>
        +params: dict
        +generate_signal(data): int
    }
    
    class MomentumStrategy {
        +lookback_period: int
        +buy_threshold: float
        +sell_threshold: float
        +generate_signal(data): int
    }
    
    class MeanReversionStrategy {
        +window: int
        +std_dev_threshold: float
        +generate_signal(data): int
    }
    
    BaseStrategy <|-- MomentumStrategy
    BaseStrategy <|-- MeanReversionStrategy
    TradingBot *-- BaseStrategy
```

## Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Bot
    participant API
    participant Strategy
    
    User->>Bot: Launch (main.py)
    Bot->>API: Connect to API
    API-->>Bot: Successful Connection
    Bot->>API: Get Account List
    API-->>Bot: Account List
    Bot->>API: Get Instrument Data
    API-->>Bot: Instrument Data (FIGI)
    loop Trading Cycle
        Bot->>API: Request Historical Data
        API-->>Bot: Historical Data
        Bot->>Strategy: Analyze Data
        Strategy-->>Bot: Trading Signal
        alt Buy Signal
            Bot->>API: Place Buy Order
            API-->>Bot: Order Confirmation
        else Sell Signal
            Bot->>API: Place Sell Order
            API-->>Bot: Order Confirmation
        else No Signal
            Bot->>Bot: Wait
        end
        opt Continuous Mode
            Bot->>Bot: Pause Between Cycles
        end
    end
    Bot-->>User: Terminate
```
