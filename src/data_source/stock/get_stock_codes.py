import json 
import re 
import os 
import requests 

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
        res = []
        for item in raw_list:
            if item.startsiwth("~"):
                single_stock_split = item[1:].split("`")
                assert(len(single_stock_split) == 3, "Stock split should have three items")
                res.append(single_stock_split)
        return res
