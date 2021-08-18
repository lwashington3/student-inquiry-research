from pandas import DataFrame
import numpy as np
from datetime import datetime as dt
try:
    from tools import add_data_dir
except ModuleNotFoundError:
    from .tools import add_data_dir


class Inmates(object):
    def __init__(self, file, set_metadata=True, index=False, dtype=np.int32):
        self.file = open(file, 'r')
        data = self.file.readlines()
        self.publisher = data[0].rstrip("\n").rstrip(",")
        self.file = file

        if set_metadata:
            try:
                self.table_num, self.description = self.standardStrip(data[2]).split("\"")[1].split("'")[0].lower().split("table")[1].lstrip().split(".")
                self.table_num = int(self.table_num)
                self.description = self.description.strip(" ")
            except ValueError:
                pass
            except IndexError:
                pass

            try:
                self.title, self.location = self.standardStrip(data[3]).split("  ")
                self.location = self.location.strip(" ")
            except ValueError:
                pass
            self.data_sources = self.standardStrip(data[4]).strip("\"").strip("Data Source: ")
            self.author = self.standardStrip(data[5]).strip("\"").lstrip("Author: ")
            self.contact_info = self.standardStrip(data[6])
            self.date = dt.strptime(self.standardStrip(data[7]), "Date of version: %m/%d/%Y").date()

        start_index = [i for i in range(len(data)) if data[i].replace(",", "") == "\n"]
        data2 = data[start_index[0]+2:start_index[1]]
        data2 = [i.strip("\n").split(",") for i in data2]
        for i in range(len(data2)):
            for j in range(len(data2[i])):
                if data2[i][j] == "NaN":
                    data2[i][j] = np.NaN
        columns = [i.pop(0) for i in data2]
        columns = np.array([i for i in columns if i != ""])
        if "" in data2[0]:
            self._set_multiple_data_frames(data2, columns, dtype)
        else:
            self._set_data_frame(data2, columns, index, dtype)
        self._set_notes(data[start_index[1]+1:])

    def _set_data_frame(self, data, row_index, index, dtype=np.float16):
        columns = data.pop(0)
        # row_index = np.delete(row_index, 0)
        try:
            array = np.array(data, dtype=dtype)
        except:
            array = np.array(data, dtype=np.float16)
        # self.df = DataFrame(array, index=row_index, columns=columns)
        self.df = DataFrame(array, columns=columns)
        self.dataframes = ["df"]
        self.df[row_index[0]] = row_index[1:]
        if index:
            self.df = self.df.set_index(row_index[0])

    def _set_multiple_data_frames(self, data, row_index, dtype=np.float16):
        lis = []
        split_index = [data[0].index(i) for i in data[0] if i != ""]
        split_index.append(-1)
        self.dataframes = []
        for current in split_index[:-1]:
            next_index = split_index[split_index.index(current) + 1]
            if next_index == -1:
                tmp = [i[current:] for i in data]
            else:
                tmp = [i[current:next_index] for i in data]
            for i in range(len(tmp)):
                if tmp[i][0] == "":
                    tmp[i] = tmp[i][1:]
            lis.append(np.array(tmp))
        for i in lis:
            tag = i[0][0].lower()
            if "/" in tag:
                tag = tag.split("/")[0]
            lis2 = i[1:]
            columns = lis2[0]
            lis2 = lis2[1:]
            lis2 = np.array([i for i in lis2], dtype=dtype)
            try:
                df = DataFrame(lis2, index=row_index, columns=columns)
                setattr(self, tag, df)
                self.dataframes.append(tag)
            except ValueError as e:
                raise ValueError(f"{tag}, {e}")

    def _set_notes(self, data):
        if "Note" in data[0]:
            self.note = data.pop(0)
        try:
            self.source = data.pop(-1)
        except IndexError:
            pass
        for subnote in data:
            tag, content = self.standardStrip(subnote).strip("\"").split("/")
            content = f"Subnote {tag}: {content}"
            tag = f"subnote_{tag}"
            setattr(self, tag, content)

    def __len__(self):
        if hasattr(self, "df"):
            return len(self.df)
        elif len(self.dataframes) > 1:
            if all([len(getattr(self, i)) for i in self.dataframes]):
                return len(getattr(self, self.dataframes[0]))
        else:
            return len(super())

    def __str__(self) -> str:
        if hasattr(self, "description") and hasattr(self, "table_num"):
            return f"Dataset \"{self.title}\" published by {'the ' + self.publisher if 'the ' not in self.publisher.lower() else self.publisher} in {self.location} on {self.date:%B %d, %Y} by {self.author} has information about {self.description} from {self.data_sources}"
        else:
            return f"Dataset \"{self.title}\" published by {'the ' + self.publisher if 'the ' not in self.publisher.lower() else self.publisher} in {self.location} on {self.date:%B %d, %Y} by {self.author} has information from {self.data_sources}"

    def __int__(self) -> int:
        try:
            return self.table_num
        except AttributeError:
            raise ValueError("This specific object does not have the attribute that calculates the int")

    def __bool__(self) -> bool:
        return hasattr(self, "data")

    @staticmethod
    def standardStrip(string: str) -> str:
        string = string.rstrip("\n")
        while string.endswith(","):
            string = string.rstrip(",")
        return string.strip("'")


if __name__ == "__main__":
    inmates = Inmates(add_data_dir("Prison/jail_inmates_2018/ji18at01.csv"))
    print(inmates.race.head())
    # print(inmates.df.head(len(inmates)))
