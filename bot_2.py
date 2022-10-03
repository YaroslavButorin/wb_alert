#-*- coding: utf-8 -*-
import requests
import json
import datetime
from dateutil.relativedelta import relativedelta
from collections import Counter
import numpy as np

key = 'wb_key'
headers = {'Authorization': key}
method = 'https://suppliers-api.wildberries.ru/api/v2/orders'
date_end = datetime.datetime.today()
date_start = date_end - relativedelta(days=1)
cutoff_from = date_start.strftime("%Y-%m-%dT%T+03:00")
cutoff_to = date_end.strftime("%Y-%m-%dT%T+03:00")
current_date = datetime.date.today()

def what_good(barcode):
    method_2 = 'https://suppliers-api.wildberries.ru//api/v2/stocks'
    params = {'skip':0,
              'take':1,
              'search':barcode}
    r = requests.get(method_2,params=params,headers=headers)
    my_json = r.content.decode('utf8').replace("'", '"')
    response = json.loads(my_json)
    name = [x['article'] for x in response['stocks']]
    size = [x['size'] for x in response['stocks']]
    return [name,size]
def check_wb():


    with open('log.txt','r') as f:
        lines = f.readlines()
    print(lines)
    if len(lines) == 30:
        file = open("log.txt", "r+")
        file.truncate(0)
        file.close()
    skip_count = 0
    for line in lines:
        if len(line) != 0:
            skip_count +=1
    params = {'date_start':cutoff_from,
              'date_end':cutoff_to,
              'take':1,
	          'status':0,
              'skip':0}
    params['skip'] = skip_count
    r = requests.get(method,headers =headers,params=params)
    my_json = r.content.decode('utf8').replace("'", '"')
    response = json.loads(my_json)
    present = [item for sublist in [x['barcodes'] for x in response['orders']] for item in sublist]
    if len(present) !=0:
        order_id = [x['orderId'] for x in response['orders']][0]
        office =  [x['officeAddress'] for x in response['orders']]
        count = Counter(present)
        list_of_goods = [office[0],]
        for x in present:
            what_is_this = what_good(x)
            name = what_is_this[0]
            size = what_is_this[1]
            list_of_goods.append(name[0])
            list_of_goods.append(size[0])
        keys_values = count.items()

        if len(present)>0:
            return f'{current_date} Упал заказ на вб,вот что в нем: заказ№{order_id,str(list_of_goods)}\n'
        else:
            #return 'test'
            pass
            #print('ничего нет')
def check_last_msg(text):
    f = open('log.txt', "a")
    f.write(text)
    f.close()


def telegram_bot_sendtext(bot_message):
    bot_token = 'bot_token'
    #bot_chatID = '424368293'
    bot_chatID = '-765133080'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    save_msg = check_last_msg(bot_message)
    print(save_msg)
    response = requests.get(send_text)

    return response.json()

try:
    test = telegram_bot_sendtext(check_wb())
    print(test)
except TypeError:
    print('ничего нету')
