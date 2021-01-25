"""
Child process that is responsible for retrieving data from data source and update stock score


"""

from multiprocessing import Process 
from time import sleep 

class StockDataProcess(Process):
    def __init__(self, stock_dict, data_socket, data_process_name, update_per_second = 3):
        self._stock_dict = stock_dict 
        self._stock_list = list()
        self._data_process_name = data_process_name
        self._update_per_second = update_per_second
        
        super().__init__()
    
    def run(self):
        """
        When running the program we should consistently perform the following calculation
        Update the current score
        Update today's position
        """
        
        update_dict = self.perform_update()
        update_string = self.generate_response_string(update_dict)
        print(update_string)
        # self.push_socket.send(update_string)

        sleep(self.update_per_second)

    def perform_update(self):
        """
        Update the score delta, and return the delta dict
        """
        return {"hi":1}

    def generate_response_string(self, delta_dict):
        return '{"hi": 1}'
    
    def add_stock_from_code(self, code):
        self._stock_list.append(self.stock_list[code])

    @property
    def stock_list(self):
        return self._stock_list

    @property
    def stock_dict(self):
        return self._stock_dict

    @property
    def data_process_name(self):
        return self._data_process_name

    @property 
    def update_per_second(self):
        return self._update_per_second
    
