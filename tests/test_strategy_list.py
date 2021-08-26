# ##################### CSV 만들어서 저장하는 파일 ####################
import pandas as pd
import csv
import strategy.Strategies as st
from strategy.Strategies import get_stocks
import time
from datetime import timedelta
from aistock.StockPrice import get_close_prices_by, get_volumes_by, StockPriceTable


def test():
    # print(str(StockPriceTable.date.name))
    # print(type(StockPriceTable.__tablename__))
    # print(str(StockPriceTable.close.name))
    # r = get_close_prices_by('060310', date='2021-08-05')
    # s = r[StockPriceTable.symbol.name]
    # print(s)
    # df = pd.DataFrame()
    # df['060310'] = get_close_prices_by('060310', begin_date='2021-07-01')['close']
    # df['265520'] = get_close_prices_by('265520', begin_date='2021-07-01')['close']
    # t = get_close_prices_by('265520', begin_date='2021-07-01')['close']
    # print(type(t))
    # df = df.pct_change(10)
    # print(type(df.index))
    # print(df)
    # df = df.pct_change(20)
    # rs = get_stocks()
    # print(rs)
    rs = get_volumes_by('265520', begin_date='2021-07-01')
    print(rs)


def test_all():
    test_mo1()
    test_mo3()


def test_mo1():
    """
    모멘텀 1개월
    """
    start = time.time()
    print("모멘텀 1 종목 리스트 만들기")

    df = st.momentum_1month()
    print(df.iloc[:10])
    momentum_1mo_assets = df.index

    # momentum_1mo_assets.to_csv('momentum_1mo_assets.csv')
    with open('momentum_1mo_assets.csv', 'w') as file:
        write = csv.writer(file)
        write.writerow(momentum_1mo_assets)

    print(timedelta(seconds=(time.time() - start)))


def test_mo3():
    # ################### 모멘텀 3개월 ##########################
    start = time.time()
    print("모멘텀 3 종목 리스트 만들기")
    df = st.momentum_3months()
    print(df.iloc[:10])
    momentum_3mos_assets = df.index

    with open('momentum_3mos_assets.csv', 'w') as file:
        write = csv.writer(file)
        write.writerow(momentum_3mos_assets)

    print(timedelta(seconds=(time.time() - start)))


def speedy():
    # ###################### 급등주 ############################
    start = time.time()
    print("급등주 csv")

    df = pd.DataFrame({'speedy_rising_volume_list': st.speedy_rising_volume()})
    # noinspection PyTypeChecker
    df.to_csv("speedy_rising_volume_list_df.csv")

    print(timedelta(seconds=(time.time() - start)))


def date_count():
    # #################### 하루 상승빈도 ########################
    start = time.time()
    print("하루 상승빈도 csv")
    up_down_zero_df = st.get_up_down_zero_df()
    # noinspection PyTypeChecker
    up_down_zero_df.to_csv("up_down_zero_df.csv")
    print(timedelta(seconds=(time.time() - start)))
    # # 대충 10분 혹은 그 이상 정도 걸림 ##


def dual_mo():
    # ################### Dual Momentum #######################
    start = time.time()
    print("Dual Momentum csv")
    # stock_dual = st.get_holding_list('KOSPI')
    stock_dual = get_stocks()
    prices = st.get_close_prices_all('2021-01-01')
    dualmomentumlist = st.dual_momentum(prices, lookback_period=20, n_selection=len(stock_dual) // 2)

    with open('dualmomentumlist.csv', 'w') as file:
        write = csv.writer(file)
        write.writerow(dualmomentumlist)
    print(timedelta(seconds=(time.time() - start)))


if __name__ == '__main__':
    test()
