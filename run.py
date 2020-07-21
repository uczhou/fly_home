'''
五个一政策下的回国航班查询器
Flights to Mainland China Checker during COVID-19 situation
Version:0.3
Author: uchzhou
'''

import streamlit as st
import pandas as pd
import functools
import time
import datetime
from flights_resource import flights
from utils import search_flight
import numpy as np


def make_clickable(url, text):
    return f'<a target="_blank" href="{url}">{text}</a>'


def cache_on_button_press(label, **cache_kwargs):
    """Function decorator to memoize function executions.
    Parameters
    ----------
    label : str
        The label for the button to display prior to running the cached funnction.
    cache_kwargs : Dict[Any, Any]
        Additional parameters (such as show_spinner) to pass into the underlying @st.cache decorator.
    Example
    -------
    This show how you could write a username/password tester:
        @cache_on_button_press('Authenticate')
    ... def authenticate(username, password):
    ...     return username == "buddha" and password == "s4msara"
    ...
    ... username = st.text_input('username')
    ... password = st.text_input('password')
    ...
    ... if authenticate(username, password):
    ...     st.success('Logged in.')
    ... else:
    ...     st.error('Incorrect username or password')
    """
    internal_cache_kwargs = dict(cache_kwargs)
    internal_cache_kwargs['allow_output_mutation'] = True
    internal_cache_kwargs['show_spinner'] = False

    def function_decorator(func):
        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            @st.cache(**internal_cache_kwargs)
            def get_cache_entry(func, args, kwargs):
                class ButtonCacheEntry:
                    def __init__(self):
                        self.evaluated = False
                        self.return_value = None

                    def evaluate(self):
                        self.evaluated = True
                        self.return_value = func(*args, **kwargs)

                return ButtonCacheEntry()

            cache_entry = get_cache_entry(func, args, kwargs)
            if not cache_entry.evaluated:
                if st.button(label):
                    cache_entry.evaluate()
                else:
                    raise st.ScriptRunner.StopException
            return cache_entry.return_value

        return wrapped_func

    return function_decorator


# Searching function
@cache_on_button_press('Search')
def get_flights(start, end, region, cur):
    print('Start.....................')
    dates = [start]
    if start.year != end.year or start.month != end.month:
        dates.append(end)

    df_records = pd.DataFrame(columns=['日期', '星期', '始发国家', '始发城市', '始发机场', '到达城市', '到达机场', '航空公司', '航班号', '票价', '官网购票链接'])

    origin_destination = {}
    for flight_num, schedule in flights.items():
        if schedule['region'] != region:
            continue
        origin = schedule['origin']
        destination = schedule['destination']
        if destination not in origin_destination:
            origin_destination[destination] = set()
            origin_destination[destination].add(origin)
        else:
            origin_destination[destination].add(origin)

    for destination, origins in origin_destination.items():
        for origin in origins:
            for date in dates:
                df = search_flight(origin, destination, cur, date)
                for idx, row in df.iterrows():
                    for flight_num, schedule in flights.items():
                        if row['航班号'] in flight_num and row['始发机场'] == schedule['origin'] \
                                and row['到达机场'] == schedule['destination'] and row['星期'] in schedule['date']:
                            df_records = df_records.append({
                                '日期': row['日期'],
                                '星期': row['星期'],
                                '始发国家': schedule['country'],
                                '始发城市': schedule['origin_city'],
                                '始发机场': row['始发机场'],
                                '到达城市': schedule['destination_city'],
                                '到达机场': row['到达机场'],
                                '航空公司': row['航空公司'],
                                '航班号': flight_num,
                                '票价': row['票价'],
                                '官网购票链接': row['官网购票链接']
                            }, ignore_index=True)
                            print(
                                '日期: {}/星期: {}/票价: ${}/始发机场: {}/到达机场： {}/航空公司: {}/航班号: {}'.format(row['日期'], row['星期'],
                                                                                                  row['票价'],
                                                                                                  row['始发机场'],
                                                                                                  row['到达机场'],
                                                                                                  row['航空公司'], flight_num))
                time.sleep(0.5)
    df_records['官网购票链接'] = df_records['官网购票链接'].apply(make_clickable, args=('点击前往',))
    print('End...............................')
    return df_records


@st.cache
def load_data(data_url, nrows=None):
    df = pd.read_csv(data_url, nrows=nrows)
    df = df.replace(np.nan, '', regex=True)
    return df


def show_table(st, df_record):
    df_record.reset_index(drop=True, inplace=True)
    if len(df_record) == 0:
        st.write("<b>查询日期范围内该地区的机票可能已售罄，建议更改日期范围或前往航空公司官网申请候补</b>", unsafe_allow_html=True)
    else:
        df = df_record.to_html(escape=False)
        st.table(df, unsafe_allow_html=True)


if __name__ == '__main__':

    app_title = st.title("Fly Home 五个一航班查询APP")
    selection_state = st.text('''
        请选择相应服务进入下一步。\n
        ''')

    if st.checkbox("查询机票"):
        app_title.title("查询回国航班")
        selection_state.text('''
            \n
            ''')
        st.write('''请先在左侧选择出发区域，之后设置查询日期区间和票价货币选择，最大
            查询范围为三个月，查询间隔为1秒，北美出发一个月的航班大概查询时间为1分钟，
            请耐心等待。查询完毕后将会有列表显示有票结果以及官方购票链接''')
        event_list = ['请选择区域', '北美', '欧洲', '东亚', '东南亚', '中东', '非洲', '更多区域正在开发中']
        event_type = st.sidebar.selectbox(
            '选择出发区域',
            event_list
        )

        # set app width
        st.markdown(
            f"""
        <style>
            .reportview-container .main .block-container{{
                max-width: 1280px;
                padding-top: 3rem;
                padding-right: 3rem;
                padding-left: 3rem;
                padding-bottom: 3rem;
            }}
        </style>
        """,
            unsafe_allow_html=True,
        )

        start = st.date_input('起始日期', datetime.date.today())
        end = st.date_input('结束日期', start)
        cur_list = ['人民币', '美元', '欧元', '日元', '韩元']
        cur1 = st.selectbox(
            '选择货币',
            cur_list
        )

        intv = end.month - start.month

        if cur1 == '人民币':
            cur = 'CNY'
        elif cur1 == '美元':
            cur = 'USD'
        elif cur1 == '日元':
            cur = 'JPY'
        elif cur1 == '韩元':
            cur = 'KRW'
        else:
            cur = 'EUR'
        if intv >= 3:
            st.write('为了优化性能，间隔请勿超过三个月')
        elif event_type == '北美':
            df_record = get_flights(start, end, 'North America', cur)
            show_table(st, df_record)
        elif event_type == '欧洲':
            df_record = get_flights(start, end, 'Europe', cur)
            show_table(st, df_record)
        elif event_type == '东亚':
            df_record = get_flights(start, end, 'East Asia', cur)
            # df_record.to_csv('flight_search_east.csv', encoding="utf-8")
            show_table(st, df_record)
        elif event_type == '中东':
            df_record = get_flights(start, end, 'Middle East', cur)
            # df_record.to_csv('flight_search_middleeast.csv', encoding="utf-8")
            show_table(st, df_record)
        elif event_type == '东南亚':
            df_record = get_flights(start, end, 'South East Asia', cur)
            # df_record.to_csv('flight_search_southeast.csv', encoding="utf-8")
            show_table(st, df_record)
        elif event_type == '非洲':
            df_record = get_flights(start, end, 'Africa', cur)
            # df_record.to_csv('flight_search_africa.csv', encoding="utf-8")
            show_table(st, df_record)
        else:
            pass

        st.write("""
        \n
        谢谢使用Fly Home App，请刷新网页（或按F5）开始新的查询。\n
        部分高需求航班可能会被航空公司锁仓所以不会显示在这里，部分国内航司需要上官网预约登记购票。\n
        疫情之下并不是所有机场都允许转机，有些国家可能需要核酸证明等文件，具体注意事项可以参照<a href="https://www.uscreditcardguide.com/xinguanyiqingzhixiaruhehuiguo/">这篇文章</a>。
        10月24日是航空公司的换季日，之后的航班信息可能会有变动\n
        祝愿大家都能顺利回国，一路平安！\n
        由于时间仓促，该项目少部分代码来自<a href="https://github.com/Vincent-Cui/flights_checker">Vincent-Cui</a>的项目，谢谢。\n
        发布时间: 2020-07-20
        """, unsafe_allow_html=True)
    elif st.checkbox("查看五个一航班"):
        app_title.title("五个一航班")
        selection_state.text('''
            \n
            ''')
        st.write('''请先在左侧选择出发需要筛选的条件''')
        st.markdown(
            f"""
        <style>
            .reportview-container .main .block-container{{
                max-width: 1280px;
                padding-top: 3rem;
                padding-right: 3rem;
                padding-left: 3rem;
                padding-bottom: 3rem;
            }}
        </style>
        """,
            unsafe_allow_html=True,
        )

        data_url = 'resources/airlines.csv'

        data_columns = ['区域', '国家', '机场', '国内机场', '航司', '航班号', '周几', '备注']

        data = load_data(data_url)

        filter_string = st.sidebar.selectbox(
            '选择筛选条件',
            ('全部', '地区', '日期')
        )

        if filter_string == '全部':
            st.subheader('全部航班')
            st.table(data)
        elif filter_string == '日期':
            week_to_filter = st.selectbox("选择星期", ('周一', '周二', '周三', '周四', '周五', '周六', '周日'))
            week_of_days_mapping = {
                1: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六', 7: '周日'
            }
            filtered_data = data[data['周几'].str.contains(week_to_filter)]

            st.subheader('选择日期： %s' % week_to_filter)
            st.table(filtered_data)
        elif filter_string == '地区':
            regions = ['北美', '东亚', '东南亚', '中东', '欧洲', '非洲']
            region = st.selectbox(
                '选择区域',
                regions)
            filtered_data = data[data['区域'].str.contains(region)]
            st.subheader('选择区域： %s' % region)
            st.table(filtered_data)
        else:
            pass
        # elif filter_string == '始发国家':
        #     pass
        # elif filter_string == '始发城市':
        #     pass
        # elif filter_string == '航司':
        #     pass

        st.write(
            '''
            注1：柬埔寨入境或者转机都需要柬埔寨商务签证+核酸检测报告+5万美金的医疗保险。\n
            注2：阿联酋要求，如果出发地是美国，满足以下条件需要96小时内核酸阴性证明：DFW, IAH, LAX, SFO, FLL和MCO出发，\n
            以及所有来自CA, FL,和TX三州的旅客都需要核酸阴性证明。目前来看如果是其他州的旅客从纽约JFK出发，似乎是不用核酸证明的。\n
            注3：葡萄牙现在要求登机前往葡萄牙都必须提供核酸检测，TAP直飞葡萄牙已经被允4。柬埔寨\n
            注4：法国每周只允许一班中方航司执飞的中法航班，未来CA MU CZ三班会轮流执飞，但是随着AF加班，中方航司可能会恢复到每周两班或者三班。\n
            数据来源<a href="https://github.com/USCreditCardGuide/airlines-to-china-covid-19">USCreditCardGuide</a>
            ''', unsafe_allow_html=True
        )

    st.write(
       f"""
        <footer>
          <p>If you have any questions or comments, please <a href="mailto:uchzhou@gmail.com" target="blank"><b>contact me!</b></a></p>
        </footer>
        """, unsafe_allow_html=True
    )