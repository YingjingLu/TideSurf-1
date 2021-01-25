import sys 
import pathlib 
sys.path.append(pathlib.Path(__file__).parent.absolute())

from tidesurf.data_source.stock.easy_quotation_sina_real import main 

if __name__ == "__main__":
    main()
