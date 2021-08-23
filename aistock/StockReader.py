import datetime
# from datetime import timedelta
import FinanceDataReader as fdr
import pandas as pd
from deprecated import deprecated
from pandas import DataFrame, json_normalize
from pykrx import stock
import requests
import json


COL_TICKER = 'Symbol'
COL_CLOSE = 'Close'
COL_OPEN = 'Open'
COL_HIGH = 'High'
COL_LOW = 'Low'
COL_VOLUME = 'Volume'
COL_CHANGE = 'Change'
COL_DATE = 'Date'


def read_tickerlist_to_list() -> list:
    """
    종목을 조회하는 함수. pykrx를 통해서 로드함.
    :return: list 종목 코드 목록
    """
    return read_tickerlist_to_list_pykrx()


def read_tickerlist_to_list_pykrx() -> list:
    """
    종목을 조회하는 함수.
    'pykrx' 사용
    :return: list 종목 코드 목록
    """
    today = datetime.datetime.today().strftime("%Y%m%d")
    tickers = stock.get_market_ticker_list(today, market='KOSDAQ')
    tickers2 = stock.get_market_ticker_list(today, market='KOSPI')
    tickers.extend(tickers2)
    return list(tickers)


class StockKrxCols:
    FULL_CODE = 'FullCode'
    CODE = 'Code'
    SYMBOL = 'Symbol'
    NAME = 'Name'
    MARKET = 'Market'
    MARKET_NAME = 'MarketName'
    MARKET_CODE = 'MarketCode'


def read_stocklist_by_market() -> DataFrame:
    """
    라이브러리 없이 바로 주식 종목을 가져오는 기능 구현
    FinanceDataReader/krx/listing.py 을 참조해서 개선
    왠지 갯수가 안 맞는데?

    :return: 종목 목록 데이터프레임<br>
        FullCode	Code	Name	MarketCode	MarketName	Market	Symbol<br>
    0	KR7060310000	060310	3S	KSQ	코스닥	KOSDAQ	060310<br>
    1	KR7095570008	095570	AJ네트웍스	STK	유가증권	KOSPI	095570<br>
    2	KR7006840003	006840	AK홀딩스	STK	유가증권	KOSPI	006840
    """
    bld = 'dbms/comm/finder/finder_stkisu'
    r = requests.post('http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd', data={'bld': bld})
    jo = json.loads(r.text)
    """
    (KRX에서 로드된 데이터)
        full_code	short_code	codeName	marketCode	marketName	marketEngName	ord1	ord2
    0	KR7060310000	060310	3S	KSQ	코스닥	KOSDAQ		16
    1	KR7095570008	095570	AJ네트웍스	STK	유가증권	KOSPI		16
    2	KR7006840003	006840	AK홀딩스	STK	유가증권	KOSPI		16
    """
    df = json_normalize(jo, 'block1')
    df = df.rename(columns={
        'full_code': StockKrxCols.FULL_CODE,
        'short_code': StockKrxCols.CODE,
        'codeName': StockKrxCols.NAME,
        'marketCode': StockKrxCols.MARKET_CODE,
        'marketName': StockKrxCols.MARKET_NAME,
        'marketEngName': StockKrxCols.MARKET,
    })
    df[StockKrxCols.SYMBOL] = df[StockKrxCols.CODE]
    df.drop(['ord1', 'ord2'], inplace=True, axis=1)
    return df


def read_stock_list_pykrx_fundamental() -> list:
    """
    종목을 조회하는 함수. pykrx를 통해서 로드함.
    :return: 종목 코드 목록 (DataFrame)
    """
    today = datetime.datetime.today().strftime("%Y%m%d")
    kospi = stock.get_market_fundamental_by_ticker(today, market="KOSPI").index
    kosdaq = stock.get_market_fundamental_by_ticker(today, market="KOSDAQ").index
    stocks = kospi.append(kosdaq)
    # df_tickers = pd.DataFrame(tickers, columns=['ticker'])
    return list(stocks)


def read_stock_details(market: str = None) -> DataFrame:
    """
    상장 종목 전체를 조회
    """
    if market is None:
        return read_stock_details_fdr()
    else:
        return read_stock_details_fdr(market)


def read_stock_details_fdr(market: str = 'KRX') -> DataFrame:
    """
    상장 종목 전체를 조회 [FinanceDataReader 이용]
    :param market: 마켓 구분 (KRX는 KOSPI,KOSDAQ,KONEX 모두 포함)
    """
    df = fdr.StockListing(market)  # KRX는 KOSPI,KOSDAQ,KONEX 모두 포함
    # print(df.head())
    return df


def read_prices_by_ticker(ticker: str, start_date: str, end_date: str = None) -> DataFrame:
    """
    한 종목의 가격 정보를 조회
    :param ticker: 종목코드
    :param start_date: 조회 시작일자 (yyyy-mm-dd)
    :param end_date: 조회 끝일자 (yyyy-mm-dd)
    :return: DataFrame
    """
    return read_prices_by_ticker_fdr(ticker, start_date, end_date)
    # return read_prices_by_ticker_pykrx(ticker, start_date, end_date)


def read_prices_by_ticker_fdr(ticker: str, start_date: str, end_date=None) -> DataFrame:
    """
    한 종목의 가격 정보를 조회 [FinanceDataReader 이용]
    :param ticker: 종목코드
    :param start_date: 조회 시작일자 (yyyy-mm-dd)
    :param end_date: 조회 끝일자 (yyyy-mm-dd)
    :return: DataFrame
    """
    df = fdr.DataReader(ticker, start_date, end_date)
    df.rename(
        columns={'Open': COL_OPEN, 'High': COL_HIGH, 'Low': COL_LOW, 'Close': COL_CLOSE, 'Volume': COL_VOLUME,
                 'Change': COL_CHANGE},
        inplace=True)
    df.index.name = COL_DATE
    df.insert(0, COL_TICKER, ticker)
    return df


def read_prices_by_ticker_pykrx(ticker: str, start_date: str, end_date=None) -> DataFrame:
    """
    한 종목의 가격 정보를 조회 [PyKrx 이용]
    :param ticker: 종목코드
    :param start_date: 조회 시작일자 (yyyy-mm-dd)
    :param end_date: 조회 끝일자 (yyyy-mm-dd)
    :return: DataFrame
    """
    start_date = f'{start_date[:4]}{start_date[5:7]}{start_date[8:10]}'
    if end_date is not None:
        end_date = f'{end_date[:4]}{end_date[5:7]}{end_date[8:10]}'

    if end_date is not None:
        df = stock.get_market_ohlcv_by_date(start_date, end_date, ticker)
    else:
        today = datetime.datetime.today().strftime("%Y%m%d")
        df = stock.get_market_ohlcv_by_date(start_date, today, ticker)
    df.rename(
        columns={'시가': COL_OPEN, '고가': COL_HIGH, '저가': COL_LOW, '종가': COL_CLOSE, '거래량': COL_VOLUME},
        inplace=True)
    df.index.name = COL_DATE
    df.insert(0, COL_TICKER, ticker)
    return df


@deprecated
def read_stock_close_prices(ticker='095570', date='2021-01-01'):
    """
    통신으로 외부에서 stock_close_price를 읽어들임.
    :param ticker: 
    :param date: 
    :return: DataFrame
    """
    df = pd.DataFrame()
    # ticker, date = '095570', '2021-08-01'
    # df['Close'] = fdr.DataReader(ticker, date)['Close']
    df[COL_CLOSE] = fdr.DataReader(ticker, date)['Close']
    df[COL_TICKER] = ticker
    return df
