import ccxt
import numpy as np
from scipy.stats import norm
import time

# Define the exchange and symbol
exchange = ccxt.binance()
symbol = 'BTC/USDT'

# Store previous Greeks values for comparison
previous_delta = None
previous_vega = None

# Define the Greeks calculations


def calculate_delta(S, K, T, r, q, sigma):
    d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    delta = np.exp(-q * T) * norm.cdf(d1)
    return delta


def calculate_gamma(S, K, T, r, q, sigma):
    d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    gamma = (np.exp(-q * T) * norm.pdf(d1)) / (S * sigma * np.sqrt(T))
    return gamma


def calculate_vega(S, K, T, r, q, sigma):
    d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    vega = S * np.exp(-q * T) * norm.pdf(d1) * np.sqrt(T)
    return vega

# Calculate the sigma value


def calculate_sigma(data):
    mean = np.mean(data)
    sigma = np.sqrt(np.sum((data - mean)**2) / (len(data) - 1))
    return sigma

# Function to fetch data and calculate Greeks


def fetch_and_calculate():
    global previous_delta, previous_vega

    try:
        # Fetch the 1-minute data
        data = exchange.fetch_ohlcv(symbol, timeframe='1m')

        # Extract close prices for volatility calculation
        close_prices = [x[4] for x in data]
        S = close_prices[-1]  # current price
        K = 1  # strike price (for calculation purposes)
        T = 1/1440  # time to expiration (1 minute)
        r = 0.05  # risk-free interest rate
        q = 0  # dividend yield (not applicable for crypto)
        sigma = calculate_sigma(close_prices)  # calculate sigma value

        # Calculate Greeks
        delta = calculate_delta(S, K, T, r, q, sigma)
        gamma = calculate_gamma(S, K, T, r, q, sigma)
        vega = calculate_vega(S, K, T, r, q, sigma)

        # Print the Greeks values and sigma
        print(f"Delta: {delta}")
        print(f"Gamma: {gamma}")
        print(f"Vega: {vega}")
        print(f"Sigma: {sigma}")

        # Calculate and print the percentage change for Delta and Vega if previous values exist
        if previous_delta is not None:
            delta_change = ((delta - previous_delta) / previous_delta) * 100
            print(f"Delta Change: {delta_change:.2f}%")
        else:
            print("Delta Change: N/A (first calculation)")

        if previous_vega is not None:
            vega_change = ((vega - previous_vega) / previous_vega) * 100
            print(f"Vega Change: {vega_change:.2f}%")
        else:
            print("Vega Change: N/A (first calculation)")

        # Update the previous values for the next calculation
        previous_delta = delta
        previous_vega = vega

    except Exception as e:
        print(f"Error fetching data or calculating Greeks: {e}")


# Run the fetch and calculate function continuously with a pause between checks
while True:
    fetch_and_calculate()
    time.sleep(60)  # Pause for 60 seconds before fetching the next set of data
