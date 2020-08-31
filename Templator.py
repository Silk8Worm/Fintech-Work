from __future__ import print_function

from googleapiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
import requests
from datetime import datetime

# Doc IDs
DOCS_FILE_ID = "1H7vnOxkqeJdH-6OlHzexHf9O-q7taenaD2SX7wcTnrk"

CLIENT_ID_FILE = 'credentials.json'
TOKEN_STORE_FILE = 'token.json'
SCOPES = (
    'https://www.googleapis.com/auth/drive'
)

SOURCE = 'sheets'

institutional_ownership_name_tags = []
institutional_ownership_info_tags = []
institutional_ownership_date_tags = []

fund_ownership_name_tags = []
fund_ownership_info_tags = []
fund_ownership_date_tags = []

insider_trading_tags = []
insider_trading_date_tags = []

insider_roster_name_tags = []
insider_roster_info_tags = []
insider_roster_date_tags = []

ceo_info_tags = []

for i in range(9):
    ceo_info_tags.append("CEO_INFO"+str(i))

for i in range(10):
    institutional_ownership_name_tags.append('INSTITUTIONAL_OWNERSHIP_NAME'+str(i))
    institutional_ownership_info_tags.append('INSTITUTIONAL_OWNERSHIP_INFO'+str(i))
    institutional_ownership_date_tags.append('INSTITUTIONAL_OWNERSHIP_DATE'+str(i))

    fund_ownership_name_tags.append('FUND_OWNERSHIP_NAME'+str(i))
    fund_ownership_info_tags.append('FUND_OWNERSHIP_INFO'+str(i))
    fund_ownership_date_tags.append('FUND_OWNERSHIP_DATE'+str(i))

    insider_trading_tags.append('INSIDER_TRADING_NAME'+str(i))
    insider_trading_date_tags.append('INSIDER_TRADING_DATE'+str(i))

    insider_roster_name_tags.append('INSIDER_ROSTER_NAME'+str(i))
    insider_roster_info_tags.append('INSIDER_ROSTER_INFO'+str(i))
    insider_roster_date_tags.append('INSIDER_ROSTER_DATE'+str(i))


COLUMNS = ['COMPANY_NAME', 'TICKER', 'UPDATED_DATE', 'CURRENT_PRICE',
           '52_WEEK_HIGH', '52_WEEK_LOW', 'MARKET_CAP', 'PE_RATIO', 'BETA',
           'COMPANY_PROFILE', 'INDUSTRY_PEERS', 'CEO_COMPENSATION',
           'INSIDER_TRADES', 'INSIDER_ROSTER']

COLUMNS.extend(ceo_info_tags)
COLUMNS.extend(institutional_ownership_name_tags)
COLUMNS.extend(institutional_ownership_info_tags)
COLUMNS.extend(institutional_ownership_date_tags)
COLUMNS.extend(fund_ownership_name_tags)
COLUMNS.extend(fund_ownership_info_tags)
COLUMNS.extend(fund_ownership_date_tags)
COLUMNS.extend(insider_trading_tags)
COLUMNS.extend(insider_trading_date_tags)
COLUMNS.extend(insider_roster_name_tags)
COLUMNS.extend(insider_roster_info_tags)
COLUMNS.extend(insider_roster_date_tags)


def get_http_client():
    store = file.Storage(TOKEN_STORE_FILE)
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_ID_FILE, SCOPES)
        creds = tools.run_flow(flow, store)
    return creds.authorize(Http())


HTTP = get_http_client()
DRIVE = discovery.build('drive', 'v3', http=HTTP)
DOCS = discovery.build('docs', 'v1', http=HTTP)
SHEETS = discovery.build('sheets', 'v4', http=HTTP)


def get_data(ticker):
    """Gets data.
    """
    headers = {'Authorization': 'Token 922be03dda90a60ae9b569b9d73424e52350facf'}
    raw = requests.get('https://tranquil-beyond-74281.herokuapp.com/info/report/'+ticker, headers=headers)
    arr = []
    arr.append(str(raw.json()['stats']['companyName']))  # company name
    arr.append(str(raw.json()['price_target']['symbol']))  # symbol
    arr.append(str(raw.json()['price_target']['updatedDate']))  # update date
    arr.append('$'+str(raw.json()['charting_yearly_vals'][len(raw.json()['charting_yearly_vals'])-1]))  # current price
    arr.append('$'+str(raw.json()['stats']['week52high']))  # 52 week high
    arr.append('$'+str(raw.json()['stats']['week52low']))  # 52 week low
    arr.append('${:,.2f}'.format(raw.json()['stats']['marketcap']))  # market cap
    arr.append(str(raw.json()['stats']['peRatio']))  # p/e ratio
    arr.append(str(raw.json()['stats']['beta']))  # beta
    arr.append(str(raw.json()['company']['description']))  # company profile
    arr.append('\n'.join(raw.json()['peers']))
    arr.append(str(raw.json()['CeoCompensation']['name']))
    arr.append('{:,.0f}'.format(raw.json()['CeoCompensation']['salary']))
    arr.append('{:,.0f}'.format(raw.json()['CeoCompensation']['bonus']))
    arr.append(str(raw.json()['CeoCompensation']['stockAwards']))
    arr.append(str(raw.json()['CeoCompensation']['optionAwards']))
    arr.append(str(raw.json()['CeoCompensation']['nonEquityIncentives']))
    arr.append(str(raw.json()['CeoCompensation']['pensionAndDeferred']))
    arr.append(str(raw.json()['CeoCompensation']['otherComp']))
    arr.append('{:,.0f}'.format(raw.json()['CeoCompensation']['total']))
    for j in range(len(institutional_ownership_name_tags)):
        arr.append(str(raw.json()['istitutionalOwnership'][j]['entityProperName']))
    for j in range(len(institutional_ownership_info_tags)):
        arr.append(str(raw.json()['istitutionalOwnership'][j]['reportedHolding'])+'\n'+str(raw.json()['istitutionalOwnership'][j]['adjHolding']))
    for j in range(len(institutional_ownership_date_tags)):
        arr.append(str(raw.json()['istitutionalOwnership'][j]['reportDate']))
    for j in range(len(fund_ownership_name_tags)):
        arr.append(str(raw.json()['fundOwnership'][j]['entityProperName']))
    for j in range(len(fund_ownership_info_tags)):
        arr.append(str(raw.json()['fundOwnership'][j]['reportedHolding'])+'\n'+str(raw.json()['fundOwnership'][j]['adjHolding']))
    for j in range(len(fund_ownership_date_tags)):
        arr.append(str(raw.json()['fundOwnership'][j]['report_date']))
    #TODO figure out what the transaaction codes mean
    trans_name = 'Sold'
    for j in range(len(insider_trading_tags)):
        try:
            arr.append(str(raw.json()['insiderTransactions'][j]['fullName'])+', ' +
                       str(raw.json()['insiderTransactions'][j]['reportedTitle']) +
                       ('\n%s ' % trans_name) +
                       '{:,.0f}'.format(raw.json()['insiderTransactions'][j]['tranShares']) +
                       ' shares at ' + '${:,.2f}'.format(raw.json()['insiderTransactions'][j]['tranPrice']) +
                       ' per share.')
        except:
            print("error with formatting insider transactions")
    for j in range(len(insider_trading_date_tags)):
        arr.append(str(raw.json()['insiderTransactions'][j]['effectiveDate']))
    for j in range(len(insider_roster_name_tags)):
        arr.append(str(raw.json()['insiderRoster'][j]['entityName']))
    for j in range(len(insider_roster_info_tags)):
        arr.append('{:,.0f}'.format(raw.json()['insiderRoster'][j]['position']))
    for j in range(len(insider_roster_date_tags)):
        arr.append(str(raw.json()['insiderRoster'][j]['reportDate']))

    return arr


def _copy_template(tmpl_id, service, ticker):
    body = {'name': ticker+'_Merged (%s)' % datetime.now(tz=None)}
    return service.files().copy(body=body, fileId=tmpl_id,
                            fields='id').execute().get('id')


def merge_template(tmpl_id, service, ticker):
    """Copies template document and merges data into newly-minted copy then
        returns its file ID.
    """
    # copy template and set context data struct for merging template values
    copy_id = _copy_template(tmpl_id, service, ticker)
    context = merge.iteritems() if hasattr({}, 'iteritems') else merge.items()

    # "search & replace" API requests for mail merge substitutions
    reqs = [{'replaceAllText': {
        'containsText': {
            'text': '{{%s}}' % key.upper(), # {{VARS}} are uppercase
            'matchCase': True,
        },
        'replaceText': value,
    }} for key, value in context]

    # send requests to Docs API to do actual merge
    DOCS.documents().batchUpdate(body={'requests': reqs},
                                 documentId=copy_id, fields='').execute()
    return copy_id

if __name__ == '__main__':

    ticker = 'TSLA'
    merge = {}

    # get row data, then loop through & process each form letter
    data = get_data(ticker) # get data from data source
    merge.update(dict(zip(COLUMNS, data)))
    print('Merged doc: docs.google.com/document/d/%s/edit' % (
        merge_template(DOCS_FILE_ID, DRIVE, data[1])))
