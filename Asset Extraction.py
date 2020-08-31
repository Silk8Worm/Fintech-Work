import csv
import alpaca_trade_api as tradeapi

api = tradeapi.REST('PKUS0ETTC3JPNXVN22SO', 'CIoX5VE0GfazzTbrZGF3PLpliwJxs3Zob8q3lK9I', base_url='https://paper-api.alpaca.markets')
account = api.get_account()

# Read in tickers from 'Valid-Tickers.csv'
with open('Valid-Tickers.csv', newline='') as csvfile:
    tickerreader = csv.reader(csvfile, delimiter=' ')
    tickers = []
    for row in tickerreader:
        tickers.append(row[0][5:])
    tickers.pop(0)

assets = api.list_assets()

asset_out = []

for asset in assets:
    if asset.symbol in tickers:
        asset_out.append(asset)

with open('Asset-Info.csv', 'w', newline='') as csvfile:
    assetwriter = csv.writer(csvfile)
    assetwriter.writerow(['Asset Class', 'Easy to Borrow', 'Exchange', 'ID', 'Marginable', 'Name', 'Shortable', 'Status', 'Symbol', 'Tradable'])
    for asset in asset_out:
        assetwriter.writerow([asset.__class__, asset.easy_to_borrow, asset.exchange, asset.id, asset.marginable, asset.name, asset.shortable, asset.status, asset.symbol, asset.tradable])
