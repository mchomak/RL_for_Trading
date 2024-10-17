import pandas as pd
import requests
from datetime import datetime
import time
import os
import logging
from model_config import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GTDF:
    def __init__(self, tokens, full_path, timeframe="hour", aggregate=1, year=None, month=None, day=None, network="ton", currency="usd", token="base", limit=1000):
        """
        Initializes the GTDF class with provided parameters.
        Args:
            tokens (dict): Dictionary containing token names and their corresponding addresses.
            data_num (int): Number used for defining the data path.
            timeframe (str): Timeframe for data aggregation (default is "hour").
            aggregate (int): Aggregation level for data (default is 1).
            year (int): Year for data retrieval (default is current year).
            month (int): Month for data retrieval (default is current month).
            day (int): Day for data retrieval (default is current day).
            network (str): Network name (default is "ton").
            currency (str): Currency type (default is "usd").
            token (str): Token type (default is "base").
            limit (int): Limit for number of data points to retrieve (default is 1000).
        """
        self.tokens = tokens
        self.timeframe = timeframe
        self.aggregate = aggregate

        now = datetime.now()
        self.year = year if year is not None else now.year
        self.month = month if month is not None else now.month
        self.day = day if day is not None else now.day

        self.network = network
        self.currency = currency
        self.token = token
        self.limit = limit

        self.full_path = full_path

    def _process_response(self, response):
        """
        Processes the response from the API.

        Args:
            response (requests.Response): The response object from the API request.

        Returns:
            pd.DataFrame: DataFrame containing processed OHLCV data.
        """
        data = response.json()
        ohlcv_data = data["data"]["attributes"]["ohlcv_list"]

        processed_data = []
        for day in ohlcv_data:
            date = datetime.utcfromtimestamp(day[0]).strftime('%Y-%m-%d %H:%M')
            processed_data.append([date, day[1], day[2], day[3], day[4], day[5]])

        df = pd.DataFrame(processed_data, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df = df.sort_values(by='Date')
        df['Average'] = (df['High'] + df['Low']) / 2
        df['Change'] = df['Close'].pct_change().fillna(0) * 100
        df['Volume Change'] = df['Volume'].pct_change().fillna(0) * 100
        df = df[['Date', 'Open', 'High', 'Low', 'Average', 'Close', 'Change', 'Volume', 'Volume Change']]
        return df


    def _get_dex_data(self, address, timestamp=None):
        """
        Retrieves DEX data from the geckoterminal API.

        Args:
            address (str): Address of the token pool.
            timestamp (int): Unix timestamp for the data retrieval point (default is None).

        Returns:
            pd.DataFrame: DataFrame containing processed OHLCV data.
        """
        if not timestamp:
            dt = datetime(self.year, self.month, self.day)
            timestamp = round(dt.timestamp())

        url = f"https://api.geckoterminal.com/api/v2/networks/{self.network}/pools/{address}/ohlcv/{self.timeframe}?aggregate={self.aggregate}&before_timestamp={timestamp}&limit={self.limit}&currency={self.currency}&token={self.token}"

        try:
            response = requests.get(url=url)
            response.raise_for_status()
            df = self._process_response(response)

            if df.shape[0] >= 1000:
                last_day = df["Date"].iloc[24]
                new_timestamp = round(datetime.strptime(last_day, '%Y-%m-%d %H:%M').timestamp())
                old_df = self._get_dex_data(address, timestamp=new_timestamp)
                merged_df = pd.concat([df, old_df], ignore_index=True)
                merged_df = merged_df.sort_values(by='Date')
                df = merged_df.drop_duplicates(subset=["Date"])

            return df
        
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            return None
        
        except Exception as e:
            logging.error(f"Data processing failed: {e}")
            return None


    def _save_to_csv(self, df, name):
        """
        Saves the DataFrame to a CSV file.

        Args:
            df (pd.DataFrame): The DataFrame to save.
            name (str): The token name.
        """
        try:
            # Clean and convert data types
            for column in ['Open', 'High', 'Low', 'Average', 'Close', 'Change', 'Volume', "Volume Change"]:
                df[column] = df[column].replace({'\$': '', ',': '', ' ': ''}, regex=True).astype(float)

            df.sort_values('Date', ascending=True, inplace=True)
            df.set_index('Date', inplace=True)
            df_cleaned = df.round(9)

            # Form the filename and save the DataFrame to a CSV file
            filename = os.path.join(self.full_path, f"{name}_per_{self.timeframe}_{self.aggregate}_{self.year}_{self.month:02d}_{self.day:02d}.csv")
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            df_cleaned.to_csv(filename)
            logging.info(f"Data for {name} saved to {filename}")

        except Exception as e:
            logging.error(f"Failed to save data for {name}: {e}")


    def get_tokens(self):
        """
        Main method to retrieve data for all tokens and save it to CSV files.
        """
        for name in self.tokens:
            df = self._get_dex_data(address=self.tokens[name])
            if df is not None:
                logging.info(f"Data for {name} retrieved successfully with shape {df.shape}")
                self._save_to_csv(df, name)
                time.sleep(5)
            else:
                logging.error(f"DataFrame for {name} is None")


if __name__ == "__main__":
    tokens = {
        # "NOT":"EQCaY8Ifl2S6lRBMBJeY35LIuMXPc8JfItWG4tl7lBGrSoR2",
        "PEPE":"0xa43fe16908251ee70ef74718545e4fe6c5ccec9f",
        "BANANA":"0x43de4318b6eb91a7cf37975dbb574396a7b5b5c6",
        "TRUMP":"0xe4b8583ccb95b25737c016ac88e539d0605949e8",
        "NEIRO":"0xc555d55279023e732ccd32d812114caf5838fd46",
        "ILV":"0x6a091a3406e0073c3cd6340122143009adac0eda",
        "FLOKI":"0xca7c2771d248dcbe09eabe0ce57a62e18da178c0",
        "MOG":"0xc2eab7d33d3cb97692ecb231a5d0e4a649cb539d",
        "FET":"0x744159757cac173a7a3ecf5e97adb10d1a725377",
        "ONDO":"0x7b1e5d984a43ee732de195628d20d05cfabc3cc7",
        "PEPECOIN":"0xddd23787a6b80a794d952f5fb036d0b31a8e6aff",
        "SHIB":"0xcf6daab95c476106eca715d48de4b13287ffdeaa",
        "ATH":"0xd31d41dffa3589bb0c0183e46a1eed983a5e5978",
        "PAAL":"0x2a6c340bcbb0a79d3deecd3bc5cbc2605ea9259f",
        "WTAO":"0x2982d3295a0e1a99e6e88ece0e93ffdfc5c761ae",
        "PRIME":"0x16588709ca8f7b84829b43cc1c5cb7e84a321b16",
        "WQUIL":"0x43e7ade137b86798654d8e78c36d5a556a647224",
        "ENA":"0xc3db44adc1fcdfd5671f555236eae49f4a8eea18",
        "ANDY":"0xa1bf0e900fb272089c9fd299ea14bfccb1d1c2c0",
        "NPC":"0x69c7bd26512f52bf6f76fab834140d13dda673ca",
        "BASEDAI":"0x8d58e202016122aae65be55694dbce1b810b4072",
        "BOBO":"0xe945683b3462d2603a18bdfbb19261c6a4f03ad1",
        "SPX":"0x52c77b0cb827afbad022e6d6caf2c44452edbc39",
        "APU":"0x5ced44f03ff443bbe14d8ea23bc24425fb89e3ed",
        "PEIPEI":"0xbf16540c857b4e32ce6c37d2f7725c8eec869b8b",
        "NEURAL":"0x1112956589a2bea1b038732db4ea6b0c416ef130",
        "MAGA":"0x0c3fdf9c70835f9be9db9585ecb6a1ee3f20a6c7",
    }
    print(len(tokens))
    gtdf = GTDF(tokens=tokens, full_path = os.path.join(os.getcwd(), "data", "raw"), network= "eth", aggregate= 1)
    gtdf.get_tokens()
