"""
Data source crawler from Sina using easyquotation

Input Args:

sys.argv:
1 - logging_path
3 - number of process

Outputs:
Crawling results stored in a form of
.
+-- 2020-02-03
|   +-- 600001
|       +-- 0.pkl
|       +-- 1.pkl
"""
import easyquotation as eq 
import multiprocessing
from multiprocessing import Process, Queue
import sys 
from tidesurf.data_source.stock.get_stock_codes import StockCodeSHDJT
import json 
import math 
import logging 
import time
import pytz 
from datetime import datetime 
import requests 
import re 
import traceback
import pickle

def format_number(n):
    return str(n) if n >= 10 else "0" + str(n)


def get_stock_type(stock_code):
    """判断股票ID对应的证券市场
    匹配规则
    ['50', '51', '60', '90', '110'] 为 sh
    ['00', '13', '18', '15', '16', '18', '20', '30', '39', '115'] 为 sz
    ['5', '6', '9'] 开头的为 sh， 其余为 sz
    :param stock_code:股票ID, 若以 'sz', 'sh' 开头直接返回对应类型，否则使用内置规则判断
    :return 'sh' or 'sz'"""
    assert type(stock_code) is str, "stock code need str type"
    sh_head = ("50", "51", "60", "90", "110", "113",
            "132", "204", "5", "6", "9", "7")
    if stock_code.startswith(("sh", "sz", "zz")):
        return stock_code[:2]
    else:
        return "sh" if stock_code.startswith(sh_head) else "sz"

def is_in_trade_hour():
    """
    morning hours: 
        9:15 - 11:30
    Afternoon hours:
        13:00 - 15:05
    """
    new_dt = datetime.fromtimestamp(int(time.time()),
            pytz.timezone('Asia/Shanghai'))
    if (new_dt.hour < 9 or new_dt.hour > 15):
        return False 
    if (12 <= new_dt.hour < 13):
        return False 
    if (new_dt.hour == 9 and new_dt.minute < 15):
        return False 
    if (new_dt.hour == 11 and new_dt.minute > 30):
        return False 
    if (new_dt.hour == 15 and new_dt.minute > 5):
        return False 
    return True

class Getter(object):
    max_num = 800
    grep_detail = re.compile(
        r"(\d+)=[^\s]([^\s,]+?)%s%s"
        % (r",([\.\d]+)" * 29, r",([-\.\d:]+)" * 2)
    )
    grep_detail_with_prefix = re.compile(
        r"(\w{2}\d+)=[^\s]([^\s,]+?)%s%s"
        % (r",([\.\d]+)" * 29, r",([-\.\d:]+)" * 2)
    )
    del_null_data_stock = re.compile(
        r"(\w{2}\d+)=\"\";"
    )

    def __init__(self, stock_list): 
        self._session = requests.session()
        self.stock_list = self.gen_stock_list(stock_list)
        print(self.stock_list)

    def get_stocks_by_range(self, params):
        headers = {
            "Accept-Encoding": "gzip, deflate, sdch",
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/54.0.2840.100 "
                "Safari/537.36"
            ),
        }

        r = self._session.get(self.stock_api + params, headers=headers)
        return r.text
    
    def gen_stock_list(self, stock_codes):
        stock_with_exchange_list = self._gen_stock_prefix(stock_codes)

        if self.max_num > len(stock_with_exchange_list):
            request_list = ",".join(stock_with_exchange_list)
            return [request_list]

        stock_list = []
        for i in range(0, len(stock_codes), self.max_num):
            request_list = ",".join(
                stock_with_exchange_list[i : i + self.max_num]
            )
            stock_list.append(request_list)
        return stock_list

    def _gen_stock_prefix(self, stock_codes):
        return [
            get_stock_type(code) + code[-6:] for code in stock_codes
        ]

    def _fetch_stock_data(self, stock_list):
        """获取股票信息"""
        pool = multiprocessing.pool.ThreadPool(len(stock_list))
        try:
            res = pool.map(self.get_stocks_by_range, stock_list)
        finally:
            pool.close()
        return [d for d in res if d is not None]
    
    @property
    def stock_api(self) -> str:
        return f"http://hq.sinajs.cn/rn={int(time.time() * 1000)}&list="

    def format_response_data(self, rep_data, prefix=False):
        stocks_detail = "".join(rep_data)
        stocks_detail = self.del_null_data_stock.sub('', stocks_detail)
        stocks_detail = stocks_detail.replace(' ', '')
        grep_str = self.grep_detail_with_prefix if prefix else self.grep_detail
        result = grep_str.finditer(stocks_detail)
        stock_dict = dict()
        for stock_match_object in result:
            stock = stock_match_object.groups()
            stock_dict[stock[0]] = dict(
                name=stock[1],
                open=float(stock[2]),
                close=float(stock[3]),
                now=float(stock[4]),
                high=float(stock[5]),
                low=float(stock[6]),
                buy=float(stock[7]),
                sell=float(stock[8]),
                turnover=int(stock[9]),
                volume=float(stock[10]),
                bid1_volume=int(stock[11]),
                bid1=float(stock[12]),
                bid2_volume=int(stock[13]),
                bid2=float(stock[14]),
                bid3_volume=int(stock[15]),
                bid3=float(stock[16]),
                bid4_volume=int(stock[17]),
                bid4=float(stock[18]),
                bid5_volume=int(stock[19]),
                bid5=float(stock[20]),
                ask1_volume=int(stock[21]),
                ask1=float(stock[22]),
                ask2_volume=int(stock[23]),
                ask2=float(stock[24]),
                ask3_volume=int(stock[25]),
                ask3=float(stock[26]),
                ask4_volume=int(stock[27]),
                ask4=float(stock[28]),
                ask5_volume=int(stock[29]),
                ask5=float(stock[30]),
                date=stock[31],
                time=stock[32],
            )
        return stock_dict

    def get_stock_data(self, **kwargs):
        """获取并格式化股票信息"""
        res = self._fetch_stock_data(self.stock_list)
        return self.format_response_data(res, **kwargs)


def job(index, stock_list, date, path, queue):
    code_list = []
    for i in stock_list:
        code_list.append(i[0])
    getter = Getter(code_list)
    cur_index = 0
    cur = 0
    cur_buf_list = []
    while (True):
        if is_in_trade_hour():
            try:
                res = getter.get_stock_data()
                cur_buf_list.append(res)
                cur += 1
                if (cur == 300):
                    with open ("{}/{}_{}-{}.pkl".format(path, date, index, cur_index), "wb") as file:
                        pickle.dump(cur_buf_list, file)
                    cur_buf_list.clear()
                    cur = 0
                    cur_index += 1
            except:
                queue.put(traceback.format_exc())
        else:
            if len(cur_buf_list) != 0:
                with open ("{}/{}_{}-{}.pkl".format(path, date, index, cur_index), "wb") as file:
                        pickle.dump(cur_buf_list, file)
                cur_buf_list.clear()
                cur = 0
                cur_index += 1

        time.sleep(1.5)

def main():
    """
    Driver function that establishes connection and report failures
    """
    assert len(sys.argv) == 3, "Sys args must have 3 arguments"
    [_, logging_path, num_process] = sys.argv 
    num_process = int(num_process)
    stock_list = StockCodeSHDJT().get_list()

    num_stock_per_process = math.ceil(len(stock_list) / num_process)
    dt = datetime.fromtimestamp(int(time.time()),
            pytz.timezone('Asia/Shanghai'))

    date = "{}-{}-{}".format(dt.year, format_number(dt.month), format_number(dt.day))

    with open("{}/stock_list_{}.json".format(logging_path, date), "w", encoding="utf-8") as f:
        json.dump(dict(stocks=stock_list), f)

    failure_queue = Queue()
    p_list = []
    for cur_index in range(num_process):
        np = Process(target=job, args=(
            cur_index,
            stock_list[cur_index * num_stock_per_process: (cur_index + 1) * num_stock_per_process ], 
            date, 
            logging_path,
            failure_queue))
        p_list.append(np)
        np.start()
    
    # start logging
    logging.basicConfig(filename=("{}/{}.log".format(logging_path, date)))

    while (True):
        
        while not failure_queue.empty():
            logging.error(failure_queue.get())
        
        new_dt = datetime.fromtimestamp(int(time.time()),
            pytz.timezone('Asia/Shanghai'))
        if (new_dt.hour == 15 and new_dt.minute > 5):
            for p in p_list:
                p.terminate()
            sys.exit()

        time.sleep(20)

if __name__ == "__main__":
    main()
