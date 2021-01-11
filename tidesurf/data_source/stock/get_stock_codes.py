import json 
import re 
import os 
import requests 
import sys 

"""
Get stock code through shdjt.com
"""

class StockCodeSHDJT(object):

    """
    Response format:
        var astock_suggest="{}"
        each in the {} is of form: ~000001`平安银行`payh
    """

    def __init__(self):
        pass

    def get_list(self):
        """
        returns <list>:
        [
            ['002024', '贵州百灵', 'gzbl']
        ]
        """
        
        response_text = requests.get("http://www.shdjt.com/js/lib/astock.js").text 
        raw_list = response_text.split("~")
        raw_list[-1] = raw_list[-1][:-1]
        res = []
        for i in range(1, len(raw_list)):
            item = raw_list[i]
            single_stock_split = item.split("`")
            assert len(single_stock_split) == 3, "Stock split should have three items" 
            res.append(single_stock_split)
        return res
