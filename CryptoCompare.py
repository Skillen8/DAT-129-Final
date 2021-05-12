import requests
import pandas as pd
import csv
import datetime
import key as api_key
# key
API_KEY = api_key
# global list containing the name of each coin
coin_name_list = []


# fetches the top 10 coins by volume per day
def get_top10_coins_by_volume():
    get_list_of_coins = 'https://min-api.cryptocompare.com/data/top/totalvolfull?limit=10&tsym=USD'
    response = requests.get(get_list_of_coins, API_KEY)
    coin_dict = response.json()
    dict = coin_dict['Data']
    print(coin_dict)
    # enters the json nested dict to get coin names
    for i in range(len(dict)):
        nested_dict = dict[i]
        more_nested = nested_dict['CoinInfo']
        coin_name = more_nested['Name']
        coin_name_list.append(coin_name)
    print(*coin_name_list)


# fetches the price, time and date of each coin for (limit) number of days
def coin_data():
    master_data = {'Coin': []}
    day_limit = '200'
    # first gets the name from coin list
    for name in coin_name_list:
        count = 0
        coin = 'https://min-api.cryptocompare.com/data/v2/histoday?fsym=' + name + '&tsym=USD&limit=' + day_limit
        response = requests.get(coin, API_KEY)
        data_dict = response.json()
        # nested dict for each coin name
        coin_dict = {name: {'Price': [], 'Date': []}}
        # nested loop extracts the time price and date from the json dict for each day per coin
        for j in range(0, int(day_limit)):
            extract = data_dict['Data']['Data'][count]
            epoch_time = extract['time']
            date = datetime.datetime.utcfromtimestamp(epoch_time).strftime('%Y-%m-%d')
            coin_dict[name]['Date'].append(date)
            coin_dict[name]['Price'].append(extract['high'])
            count += 1
        master_data['Coin'].append(coin_dict)

    return master_data, day_limit


# gets the percentage of coins by comparing the side by side indexes
def coin_percent():
    data, limit = coin_data()
    date_list = []
    # dict for the top 10 coins
    # the key is the name the value will be the percentage, either increased or decreased from the day before
    perc_dict = {coin_name_list[0]: [], coin_name_list[1]: [], coin_name_list[2]: [],
                 coin_name_list[3]: [], coin_name_list[4]: [], coin_name_list[5]: [],
                 coin_name_list[6]: [], coin_name_list[7]: [], coin_name_list[8]: [],
                 coin_name_list[9]: []
                 }

    count = 0
    # extracts the date and appends it to a list
    # starts at one because the loop below compares the 0 and 1st index, so this matches up the dates
    for i in range(1, int(limit)):
        coin = 'https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=' + limit
        response = requests.get(coin, API_KEY)
        data_dict = response.json()
        extract = data_dict['Data']['Data'][i]
        epoch_time = extract['time']
        date = datetime.datetime.utcfromtimestamp(epoch_time).strftime('%Y-%m-%d')
        date_list.append(date)
    # starts loop for each coin in the list
    for name in coin_name_list:
        # nested loop extracts data from the dictionary created in the method above
        for j in range (1, int(limit)):
            # 1st index
            extract = data['Coin'][count][name]['Price'][j]
            # 0th index (always one behind ^)
            extract_index_back = data['Coin'][count][name]['Price'][j - 1]
            # checks which index is higher, then calculates the percentage between them
            # then appends to perc_dict (percentage_dictionary)
            if extract >= extract_index_back:
                increase = extract - extract_index_back
                perc = increase / extract_index_back * 100
                format_perc = "{:.2f}".format(perc)
                perc_up = '+' + '%' + str(format_perc)
                perc_dict[coin_name_list[count]].append(perc_up)
            else:
                decrease = extract_index_back - extract
                perc_d = decrease / extract * 100
                format_perc = "{:.2f}".format(perc_d)
                perc_down = '-' + '%' + str(format_perc)
                perc_dict[coin_name_list[count]].append(perc_down)
        count += 1

    return perc_dict, date_list


# checks if the percentage of each coin went up or down that day
# both %5 and %10
def coin_change_together():
    perc_dict, date_list = coin_percent()
    # lists for the number of times its above or below 5 or 10 percent
    high_perc_5 = []
    low_perc_5 = []
    high_perc_10 = []
    low_perc_10 = []
    five_perc = 5.00
    ten_perc = 10.00
    # dict for +%5 +%10 and -%5 -%10
    percents_up_down = {'Up %5': high_perc_5, 'Down %5': low_perc_5, 'Up 10%': high_perc_10, 'Down %10': low_perc_10}
    # puts 0 in for every list above
    for i in range(0, len(date_list)):
        high_perc_5.append(0)
        low_perc_5.append(0)
        high_perc_10.append(0)
        low_perc_10.append(0)
    # loop the iterates through the percentage dict from coin_percent()
    for key, val in perc_dict.items():
        index = 0
        # each element in the list that is a value of the dict
        for perc in val:
            # ex. +%5 splits to [+, 5]
            split_num = perc.split('%')
            # checks either a + - string to determine if went up or down from the previous day
            if split_num[0] == '+':
                # checks if it is >= to 5 or 10, if so, adds 1 to that element, elements start at 0
                if float(split_num[1]) >= five_perc:
                    high_perc_5[index] = high_perc_5[index] + 1
                if float(split_num[1]) >= ten_perc:
                    high_perc_10[index] = high_perc_10[index] + 1
            elif split_num[0] == '-':
                # checks percents again but this time for decreasing
                if float(split_num[1]) >= five_perc:
                    low_perc_5[index] = low_perc_5[index] + 1
                if float(split_num[1]) >= ten_perc:
                    low_perc_10[index] = low_perc_10[index] + 1
            index += 1

    return high_perc_5, high_perc_10, low_perc_5, low_perc_10, percents_up_down


# displays the information on how many coins that increased or decreased %5 and %10 and how many days they did
def print_coins_match(perc_list, perc_list_down, percent):

    count3 = 0
    count5 = 0
    # goes through each element in the lists containing the number of coins each day were above %5 or %10
    for val in perc_list:
        # the element is above 3 or 5 it adds to the count
        # the count is the number of days
        # its checking if 3 or 5 coins per day were above 5 or 10 percent
        if val >= 3:
            count3 += 1
        if val >= 5:
            count5 += 1
    print()
    print("There is", count3, 'day(s), were 3 or more coins were', percent, 'above the previous day')
    print("There is", count5, 'day(s), were 5 or more coins were', percent, 'above the previous day')
    count3 = 0
    count5 = 0
    # goes through each element in the lists containing the number of coins each day were below %5 or %10
    for val in perc_list_down:
        # the element is above 3 or 5 it adds to the count
        # the count is the number of days
        # its checking if 3 or 5 coins per day were below 5 or 10 percent
        if val >= 3:
            count3 += 1
        if val >= 5:
            count5 += 1
    print()
    print("There is", count3, 'day(s), were 3 or more coins where', percent, 'below the previous day')
    print("There is", count5, 'day(s), were 5 or more coins where', percent, 'below the previous day')


# creates csv from the dicts
def csv_write():
    dict, date = coin_percent()
    x, c, v, b, percent_dict = coin_change_together()
    date_dict = {'Date': date}
    # creates "coins.csv"
    with open("coinss.csv", 'w') as csv_file:
        writer = csv.writer(csv_file)
        # adds the date dict to it
        for key, value in date_dict.items():
            writer.writerow([key, value])
        # adds the coin name and the percent increase or decrease
        for key, value in dict.items():
            writer.writerow([key, value])
        # the number of coins per day to increase or decrease collectively
        for key, value in percent_dict.items():
            writer.writerow([key, value])
    # merges the collectively increased or decreased coin dict to the dict containing the date and coin percentages
    dict.update(percent_dict)
    # data frame displaying the merged dictionaries
    df = pd.DataFrame(dict, index=date, )
    df.name = 'Date'
    print('=================================================================================')
    print('Now displaying all historical data')
    print('=================================================================================')
    print(df)


def main():
    print('Here are the top 10 coins today by volume')
    get_top10_coins_by_volume()
    coin_change_together()
    csv_write()
    list5, list10, list_down5, list_down10, perc_dict = coin_change_together()
    print_coins_match(list5, list_down5, '%5')
    print_coins_match(list10, list_down10, '%10')


if __name__ == '__main__':
    main()




