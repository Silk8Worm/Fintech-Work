import requests
import csv
from typing import List
import numpy
import math


def rolling_sharpe(port_vals: List[float], starting: float) -> float:
    """
    It does what the spreadsheet does, so if the spreadsheet can do it, so can
    this.

    >>> rolling_sharpe([100.4, 100.2, 100.21, 99.21, 100, 100.8, 99.79, 100.79, 100.45, 100.84, 100.4, 100.89], 100)
    """

    RFR = .02
    D_RFR = (math.pow((1+RFR), (4/365))-1)
    daily_r = []
    avg_r_ann = []
    st_dev_ann = []

    if len(port_vals) <= 10:
        print("not enough portfolio values")
        return None

    daily_r.append((port_vals[0]-starting)/starting)

    for i in range(1, len(port_vals)):
        daily_r.append((port_vals[i]-port_vals[i-1])/port_vals[i-1])

    for i in range(9, len(port_vals)):
        avg_r_ann.append(numpy.mean(daily_r[0:i+1])*252)

    for i in range(9, len(port_vals)):
        st_dev_ann.append(numpy.std(daily_r[0:i+1], ddof=1)*math.sqrt(252))

    return (avg_r_ann[-1]-D_RFR)/st_dev_ann[-1]


def partition_based_on(arr, low, high, what):
    i = (low-1)
    pivot = arr[high][what]

    for j in range(low, high):
        if arr[j][what] >= pivot:
            i = i+1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i+1], arr[high] = arr[high], arr[i+1]
    return i+1


def quick_sort_traders(arr, low, high, what):
    if len(arr) == 1:
        return arr
    if low < high:
        pi = partition_based_on(arr, low, high, what)
        quick_sort_traders(arr, low, pi-1, what)
        quick_sort_traders(arr, pi+1, high, what)


def score_and_write_traders(traders: List):

    quick_sort_traders(traders, 0, len(traders)-1, "equity")

    for k in range(len(traders)):
        traders[k]["equity_score"] = len(traders)-k

    quick_sort_traders(traders, 0, len(traders)-1, "sharpe")

    for k in range(len(traders)):
        traders[k]["sharpe_score"] = len(traders) - k
        traders[k]["total_score"] = traders[k]["sharpe_score"] + \
                                    traders[k]["equity_score"]

    quick_sort_traders(traders, 0, len(traders)-1, "total_score")

    with open('final_standings.csv', mode='w') as final_standings_file:
        file_writer = csv.writer(final_standings_file, delimiter=',',
                                 quotechar='"', lineterminator='\n')
        file_writer.writerow(["Final Rank", "Team Name", "Sharpe Ratio",
                              "Sharpe Score", "Equity", "Equity Score",
                              "Total Score"])
        for k in range(len(traders)):
            file_writer.writerow([k+1,
                                  traders[k]["name"],
                                  traders[k]["sharpe"],
                                  traders[k]["sharpe_score"],
                                  traders[k]["equity"],
                                  traders[k]["equity_score"],
                                  traders[k]["total_score"]])


if __name__ == '__main__':

    headers = {'Authorization': 'Token 922be03dda90a60ae9b569b9d73424e52350facf'}
    raw = requests.get('https://tranquil-beyond-74281.herokuapp.com/info/getsecretvals/', headers=headers)

    TRADERS_LIST = {"BlurpleBears": 1521719.96, "Grace,MichelleandEmilia": 1720748.54,
                    "MagnificentMustardMooses": 1415065.54, "GordonGekko": 2489310, "IndigoIguanas": 1335991.61,
                    "AngelinaGuo": 1231875.7, "WU": 1143551.53, "DenimDolphins": 1149905.7, "Martin": 1197395.57, "leaf": 1327140.27,
                    "RaspberryRoseRhinos": 1103132.84, "Fred": 1257318.33, "BrownInvestors": 1348680.59,
                    "RCInvestors": 1133597.27, "EmeraldEagles": 1186078.13, "hi": 1113938.32, "Iamnotboris": 1284608.06,
                    "WittyAtom": 1119924.65, "11MDM11": 1068602, "GalacticGreenGiraffes": 1027284.68}

    traders = []

    for trader in raw.json():
        if trader["name"] in TRADERS_LIST.keys():
            traders.append(trader)

    for trader in traders:
        trader["values"].append(TRADERS_LIST[trader["name"]])
        trader["sharpe"] = rolling_sharpe(trader["values"][1:len(trader["values"])], trader["values"][0])

    for trader in traders:
        trader["equity"] = trader["values"][len(trader["values"])-1]

    score_and_write_traders(traders)
