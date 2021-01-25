"""
The manager process that maintains the shared states among different processes 

"""
from multiprocessing import Queue, Array, Value, Process, Lock
from multiprocessing.managers import SyncManager, BaseManager
import pandas as pd 
import os, sys 
import json
from tidesurf.lib.stock import Stock
from tidesurf.engine.stock_data_process import StockDataProcess

class EngineManager(SyncManager):
    def __init__(self, config_file_path, *args, **kwargs):
        self._code_to_stock_dict = dict() 
        self._stock_data_process_list = self.list()
        self.load_config(config_file_path)
        
        picked_stock_path = self.get_picked_stock_path()
        self.load_picked_stock(picked_stock_path)
        self.load_all_stocks()
        """ Locks """
        self._picked_stock_lock = self.RLock()

        super().__init__(args, kwargs)

    def load_config(self, config_file_path):
        config = None 
        with open(config_file_path, "r") as in_f:
            config = json.load(in_f)

        self._engine_folder_path = config["engine_data_folder_path"]
        self._data_folder_path = config["data_folder_path"]
        self._num_stock_data_process = int(config["num_stock_data_process"])
    
    def load_all_stocks(self):
        """
        load the most recent stock list from data folder, assign the stock lists into processes
        stock list json format:
        {
            "stocks":[
                [
                    "000001",
                    "\u5e73\u5b89\u94f6\u884c",
                    "payh"
                ]
            ]
        }
        """
        
        for _ in range(self.num_stock_data_process):
            self.stock_data_process_list.append(StockDataProcess(self.code_to_stock_dict))


        # distribute the stocks evenly among different StockDataProcess
        with open(self.get_stock_list_path(), "r") as in_f:
            cur_process = 0
            stock_list = json.load(in_f)["stocks"]
            for stock_item in stock_list:
                self.code_to_stock_dict[stock_item[0]] = Stock(stock_item[0], stock_item[2], stock_item[1])
                self.stock_data_process_list[cur_process % self.num_stock_data_process].add_stock_from_code(stock_item[0])

    @property
    def code_to_stock_dict(self):
        """
        Dict<str, Stock>
        """
        return self._code_to_stock_dict

    @property
    def num_stock_data_process(self):
        return self._num_stock_data_process
    
    @property 
    def stock_data_process_list(self):
        return self._stock_data_process_list
    
    @property
    def engine_folder_path(self):
        return self._engine_folder_path
    
    @property 
    def data_folder_path(self):
        return self._data_folder_path 
    

    """ >>> Start Picked Stock List and Dict """
    def load_picked_stock(self, picked_stock_path):
        """
        load stocks into a shared list
        """
        lst = None
        try:
            with open(picked_stock_path, "r") as in_f:
                lst = json.load(in_f)
        except:
            raise ValueError("Picked Stock path cannot be opened")
        
        self._picked_stock_lock.acquire()
        self.picked_stock_list(self.list(lst))
        self._picked_stock_index_dict = self.dict()
        for i in range(len(self.picked_stock_list)):
            self._picked_stock_index_dict[i] = self.picked_stock_list[i]
        self._picked_stock_lock.release()

    @property
    def picked_stock_list(self):
        return self._picked_stock_list
    
    @picked_stock_list.setter
    def picked_stock_list(self, lst):
        self._picked_stock_list = lst

    @property 
    def picked_stock_index_dict(self):
        return self._picked_stock_index_dict

    def add_picked_stock(self, code):
        self._picked_stock_lock.acquire()
        self.picked_stock_list.append(code)
        self._picked_stock_index_dict[len(self.picked_stock_list) - 1] = code
        self._picked_stock_lock.release()

        self.dump_picked_stock()
    
    def dump_picked_stock(self):
        with open(self.get_picked_stock_path, "w")as out_f:
            json.dump(self.picked_stock_list, out_f)
    
    """ >>> End Picked Stock List and Dict """

    """ >>> Start file path """
    def get_picked_stock_path(self):
        return os.path.join(self.engine_folder_path, "picked_stocks.json")
    
    def get_stock_list_path(self):
        return os.path.join(self.data_folder_path, "stock_list.json")
    """ >>> End file path """

def main():
    pass
