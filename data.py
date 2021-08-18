from tools import add_data_dir
from pandas import DataFrame


class DataGrabber(object):
    def __init__(self, file_location: str, set_metadata=True):
        self.file_location = file_location
        self.set_metadata = set_metadata

    def process_data(self):
        with open(self.file_location) as file:
            data = [i.strip().split(",") for i in file.readlines()]
        if self.set_metadata:
            pass

        table_start_row = 10
        table_end_row = None

        # Finds the last row of data
        for row in range(10, len(data)):
            if all(data[row]) == "":
                table_end_row = row
                break

        if table_end_row is None:
            table_end_row = len(data)

        data = data[table_start_row:table_end_row]

        index_column = [i.pop(0) for i in data]
        index_column_name = index_column.pop(0)
        index_column = [i for i in index_column if i]

        table_split_indexes = []
        for i in range(len(data[1])):
            if not data[1][i]:
                table_split_indexes.append(i)
        table_split_indexes.append(len(data[1]))
        
        raw_tables = []
        for i in range(len(table_split_indexes)-1):
            split = [row[table_split_indexes[i]:table_split_indexes[i+1]] for row in data]
            raw_tables.append(split)

        tables = {}
        for table in raw_tables:
            name = table[0][0]
            table.pop(0)
            table = [i[1:] for i in table]
            columns = [index_column_name] + table.pop(0)
            counter = 0
            for index, dat in zip(index_column, table):
                dat.insert(0, index)
                table[counter] = dat
                counter += 1
            df = DataFrame(table, columns=columns).set_index(index_column_name)
            drops = [i for i in range(len(df)) if not all(df.iloc[i])]           
            df = df.drop(df.index[drops])
            tables[name] = df

        return tables

    def _extra(self):
        pass


class LifeExpectancy(DataGrabber):
    @property
    def black(self):
        return self._black

    @black.setter
    def black(self, value):
        if isinstance(value, DataFrame) or issubclass(value, DataFrame):
            self._black = value

    @property
    def white(self):
        return self._white

    @white.setter
    def white(self, value):
        if isinstance(value, DataFrame) or issubclass(value, DataFrame):
            self._white = value

    @property
    def hispanic(self):
        return self._hispanic

    @hispanic.setter
    def hispanic(self, value):
        if isinstance(value, DataFrame) or issubclass(value, DataFrame):
            self._hispanic = value

    @property
    def non_hispanic_black(self):
        return self._non_hispanic_black

    @non_hispanic_black.setter
    def non_hispanic_black(self, value):
        if isinstance(value, DataFrame) or issubclass(value, DataFrame):
            self._non_hispanic_black = value

    @property
    def non_hispanic_white(self):
        return self._non_hispanic_white

    @non_hispanic_white.setter
    def non_hispanic_white(self, value):
        if isinstance(value, DataFrame) or issubclass(value, DataFrame):
            self._non_hispanic_white = value

    def __init__(self, file_location: str, set_metadata=False):
        super().__init__(file_location, set_metadata)
        self.tables = self.process_data()

        for key in self.tables.keys():
            table = self.tables[key]
            for column in table.columns:
                table[column] = table[column].apply(lambda string: float(string))

        self._black = self.tables["Black"]
        self._white = self.tables["White"]
        self._hispanic = self.tables["Hispanic"]
        self._non_hispanic_white = self.tables["Non-Hispanic White"]
        self._non_hispanic_black = self.tables["Non-Hispanic Black"]

    def __getitem__(self, item):
        return self.tables[item]


if __name__ == "__main__":
    DataGrabber(add_data_dir("Health/life_expectancy.csv")).process_data()
