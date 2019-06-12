from src.tools.Data import Data


class Description:
    lib = None
    @staticmethod
    def init():
        Description.lib = Data.process_raw(Data.get_cache_file('data/raw/descriptions.txt.txt'))
