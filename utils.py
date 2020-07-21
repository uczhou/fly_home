import pandas as pd
import dateutil.parser
from config import rapidapi_host, rapidapi_key, base_url
import requests
import json


def getDateTimeFromISO8601String(s):
    d = dateutil.parser.parse(s)
    return d


def search_flight(origin, destination, currency, date):
    with open("resources/carriers_mapping.json", "r") as read_file:
        carriers_mapping = json.load(read_file)

    # print('{}/{}'.format(origin,destination))
    date_string = date.strftime("%Y-%m-%d")
    url = "{}/{}/en-US/{}/{}/{}".format(base_url, currency, origin, destination, date_string)

    headers = {
        'x-rapidapi-host': rapidapi_host,
        'x-rapidapi-key': rapidapi_key
    }

    # df_record = pd.DataFrame(columns=['日期', '星期', '始发国家', '始发城市', '始发机场', '到达城市', '到达机场', '航空公司', '航班号', '票价', '官网购票链接'])
    df_record = pd.DataFrame(columns=['日期', '星期', '始发机场', '到达机场', '航空公司', '航班号', '票价', '官网购票链接'])

    response = requests.request("GET", url, headers=headers)

    response = response.json()

    quotes = response.get("Quotes", [])
    carriers = response.get("Carriers", [])
    carrier_map = {}

    for carrier in carriers:
        carrier_map[carrier["CarrierId"]] = carrier["Name"]

    tmp = {}
    for quote in quotes:
        carrier_id = quote["OutboundLeg"]["CarrierIds"][0]
        carrier_name = carrier_map.get(carrier_id, 'NA')
        if carrier_name not in carriers_mapping:
            if carrier_name == 'United':
                tmp[carrier_name] = carriers_mapping['United Airlines']
            elif carrier_name == 'ANA':
                tmp[carrier_name] = carriers_mapping['All Nippon Airways']
            else:
                for key, value in carriers_mapping.items():
                    if carrier_name in key:
                        tmp[carrier_name] = value
        for key, value in tmp.items():
            carriers_mapping[key] = value
        if quote['Direct'] is True:
            datetime_string = quote['OutboundLeg']['DepartureDate']
            datetime_dt = getDateTimeFromISO8601String(datetime_string)
            price = quote['MinPrice']
            week_of_day = datetime_dt.strftime("%A")
            # print(quote)
            df_record = df_record.append(
                {'日期': datetime_dt.strftime("%m/%d/%Y"),
                 '星期': week_of_day,
                 '始发机场': origin,
                 '到达机场': destination,
                 '航空公司': carrier_name,
                 '航班号': carriers_mapping.get(carrier_name, 'NA'),
                 '票价': '{} {}'.format(currency, price),
                 '官网购票链接': get_link(origin, destination, datetime_dt, carriers_mapping.get(carrier_name, 'NA'), currency)},
                ignore_index=True)
            
    # if not bool(tmp):
    #     with open("resources/carriers_mapping.json", "w") as read_file:
    #         json.dump(carriers_mapping, read_file)

    return df_record


def get_link(origin, destination, departure_date, iata_code, cur):
    url = 'https://www.google.com/flights?hl=zh-CN#'
    if departure_date.month < 10:
        mo = '0' + str(departure_date.month)
    else:
        mo = str(departure_date.month)
    if departure_date.day < 10:
        da = '0' + str(departure_date.day)
    else:
        da = str(departure_date.day)

    date_string = departure_date.strftime("%Y-%m-%d")

    url1 = url + 'flt=' + origin + '.' + destination + '.' + date_string + ';c:' + cur + ';e:1' + ';s:0;a:' + iata_code + ';sd:1;t:f;tt:o'

    if iata_code == 'UA':
        link = 'https://www.united.com/ual/en/US/flight-search/book-a-flight/results/rev?f=' + origin + '&t=' + destination + '&d=' + date_string + '&tt=1&sc=7&px=1&taxng=1&newHP=True&idx=1'
    elif iata_code == 'MU':
        link = 'http://www.ceair.com/booking/' + origin + '-' + destination + '-' + date_string + '_CNY.html'
    elif iata_code == 'CZ':
        link = 'https://oversea.csair.com/new/us/zh/flights?m=0&p=100&flex=1&t=' + origin + '-' + destination + '-' + date_string
    elif iata_code == 'MF':
        link = 'https://www.xiamenair.com/zh-cn/nticket.html?tripType=OW&orgCodeArr%5B0%5D=' + origin + '&dstCodeArr%5B0%5D=' + destination + '&orgDateArr%5B0%5D=' + date_string + '&dstDate=&isInter=true&adtNum=1&chdNum=0&JFCabinFirst=false&acntCd=&mode=Money&partner=false&jcgm=false'
    elif iata_code == 'HU':
        link = 'https://new.hnair.com/hainanair/ibe/deeplink/ancillary.do?DD1=' + date_string + '&DD2=&TA=1&TC=0&TI=0&TM=&TP=&ORI=' + origin + '&DES=' + destination + '&SC=A&ICS=F&PT=F&FLC=1&CKT=&DF=&NOR=&PACK=T&HC1=&HC2=&NA1=&NA2=&NA3=&NA4=&NA5=&NC1=&NC2=&NC3=&NC4='
    elif iata_code == '3U':
        link = 'http://www.sichuanair.com/'
    elif iata_code == 'JD':
        link = 'https://new.jdair.net/jdair/?tripType=OW&originCode=' + origin + '&destCode=' + destination + '&departureDate=' + date_string + '&returnDate=&cabinType=ECONOMY&adtNum=1&chdNum=0&const_id=5f0a8017p2ZZg9hvG7URRHemkpAMhpvwRfIFTPm1&token=#/ticket/tripList'
    elif iata_code == 'LH':
        link = 'https://www.lufthansa.com/cn/zh/homepage'
    elif iata_code == 'TK':
        link = 'https://www.turkishairlines.com/zh-cn/index.html'
    elif iata_code == 'CA':
        link = 'http://et.airchina.com.cn/InternetBooking/AirLowFareSearchExternal.do?&tripType=OW&searchType=FARE&flexibleSearch=false&directFlightsOnly=false&fareOptions=1.FAR.X&outboundOption.originLocationCode=' \
               + origin + '&outboundOption.destinationLocationCode=' + destination + '&outboundOption.departureDay=' \
               + str(da) + '&outboundOption.departureMonth=' + str(mo) + '&outboundOption.departureYear=' \
               + str(departure_date.year) + '&outboundOption.departureTime=NA&guestTypes%5B0%5D.type=ADT&guestTypes%5B0%5D.amount=1&guestTypes%5B1%5D.type=CNN&guestTypes%5B1%5D.amount=0&guestTypes%5B3%5D.type=MWD&guestTypes%5B3%5D.amount=0&guestTypes%5B4%5D.type=PWD&guestTypes%5B4%5D.amount=0&pos=AIRCHINA_CN&lang=zh_CN&guestTypes%5B2%5D.type=INF&guestTypes%5B2%5D.amount=0'
    else:
        link = url1

    return link
