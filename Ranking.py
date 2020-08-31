import requests, csv


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


if __name__ == '__main__':
    headers = {'Authorization': 'Token 922be03dda90a60ae9b569b9d73424e52350facf'}
    raw = requests.get('https://tranquil-beyond-74281.herokuapp.com/info/standings/', headers=headers)

    traders = []

    for trader in raw.json():
        if trader["name"] != "rcftaTeam":
            traders.append(trader)

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


