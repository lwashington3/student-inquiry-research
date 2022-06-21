from sys import platform
from os.path import join
import pandas as pd
import numpy as np
from datetime import datetime as dt
from enum import Enum

if platform.lower() == "win32":
    data_dir = "D:\\data\\SIR"
else:
    data_dir = "./data/"

add_data_dir = lambda file: join(data_dir, file)

remove_data_dir = lambda file: file.replace(data_dir, "")


def map_to_boolean(df: pd.DataFrame, columns: list):
    for string in columns:
        df[string] = df[string].replace({"Yes": True, "No": False, "yes": True, "no": False})
    return df


def tuple_to_hex(tup: tuple) -> str:
    colors = [hex(color).replace("0x", "").zfill(2) for color in tup]
    return "#" + "".join(colors)


def mpv_formatting(file_name: str, output_file: str, index=False):
    df1 = pd.read_excel(file_name, sheet_name="2013-2021 Police Killings")
    df1 = df1.filter([i for i in df1.columns if not i.startswith("Unnamed: ")], axis=1)
    df1["Victim's race"] = df1["Victim's race"].replace("white", "White").replace("Hispanic ", "Hispanic").replace(
        "Unknown race", "Unknown Race")
    df1["Victim's gender"] = df1["Victim's gender"].replace("Male ", "Male").replace(np.nan, "Unknown")
    df1["Symptoms of mental illness?"] = df1["Symptoms of mental illness?"].replace("Unkown", "Unknown").replace(
        "unknown", "Unknown").replace("Unknown ", "Unknown").replace("Yes", True).replace("No", False).replace(np.nan,
        "Unknown").replace("Drug or alcohol use", "Drug or Alcohol use").replace("Drug of Alcohol Use", "Drug or Alcohol Use")\
        .replace("Drug or Alcohol use", "Drug or Alcohol Use").replace("Yes/Drug or alcohol use", "True, Alcohol").replace("Unclear",
        "Unknown")
    df1["Alleged Threat Level (Source: WaPo)"] = df1["Alleged Threat Level (Source: WaPo)"].replace("other", "Other")\
        .replace("attack", "Attack").replace("undetermined", "Undetermined").replace("none", "None").replace(np.nan, "Undetermined")\
        .replace("other ", "Other")
    df1["Armed/Unarmed Status"] = df1["Armed/Unarmed Status"].replace("unclear", "Unclear").replace("Allegedly armed",
        "Allegedly Armed").replace("Unclear ", "Unclear").replace("unarmed/Did Not Have Actual Weapon", "Unarmed/Did Not Have Actual Weapon")
    df1["Fleeing (Source: WaPo)"] = df1["Fleeing (Source: WaPo)"].replace("car", "Car").replace("not fleeing",
        "Not Fleeing").replace("other", "Other").replace("foot", "Foot").replace("Not fleeing", "Not Fleeing")\
        .replace("not fleeing ", "Not Fleeing").replace(np.nan, "Unknown").replace("car, foot", "Car and Foot")
    df1['Date of Incident (month/day/year)'] = pd.to_datetime(df1['Date of Incident (month/day/year)']).dt.date
    df1["Alleged Weapon (Source: WaPo and Review of Cases Not Included in WaPo Database)"] = df1[
        "Alleged Weapon (Source: WaPo and Review of Cases Not Included in WaPo Database)"].replace("gun ", "gun") \
        .replace("Gun", "gun").replace("vehicle ", "vehicle").replace("wood stick ", "wood stick").replace(
        "wooden stick", "wood stick")
    df1["Date of Incident (month/day/year)"] = df1["Date of Incident (month/day/year)"].replace("Yes", True).replace(
        "No", False).replace("yes", True).replace("no", False)
    df1 = map_to_boolean(df1, ["Call for Service? (DRAFT)", "Body Camera (Source: WaPo)"])
    df1["Body Camera (Source: WaPo)"] = df1["Body Camera (Source: WaPo)"].replace("surveillance video", "Surveillance Video")\
        .replace("Surveillance video", "Surveillance Video").replace("Dashcam video", "Dashcam Video")\
        .replace(np.nan, "Unknown").replace("cell phone video", "Cell Phone Video")
    df1["City"] = df1["City"].replace("Kansas CIty", "Kansas City").replace("Lagrange", "LaGrange")\
        .replace("Havre de Grace", "Havre De Grace").replace("Deland", "DeLand").replace("Dekalb", "DeKalb").replace(
        "Bellfower", "Bellflower").apply(lambda string: string.strip().replace("  ", " ") if isinstance(string, str) else string)
    df1["Call for Service? (DRAFT)"] = df1["Call for Service? (DRAFT)"].replace("No ", False).replace(np.nan, "Unavailable")
    df1["Off-Duty Killing?"] = df1["Off-Duty Killing?"].replace(np.nan, "False").replace("Off-Duty", "True").replace("Off-duty", "True").replace("off-duty", "True")
    df1["Cause of death"] = df1["Cause of death"].replace("Tasered", "Taser").replace("/", ",")
    df1["Criminal Charges?"] = df1["Criminal Charges?"].apply(lambda row: row.strip().replace("Year", "year").replace("Life", "life").replace("Prison", "prison").replace("Charged with crime", "Charged with a crime"))
    df1.columns = ["Date of Incident" if i == "Date of Incident (month/day/year)" else i for i in df1.columns]

    df2 = pd.read_excel(file_name, sheet_name="2013-2020 Killings by PD")
    df3 = pd.read_excel(file_name, sheet_name="2013-2020 Killings by State")
    df4 = pd.read_excel(file_name, sheet_name="Police Killings of Black Men")

    with pd.ExcelWriter(output_file, date_format="m/d/YYYY") as writer:
        df1.to_excel(writer, sheet_name="2013-2021 Police Killings", index=index)
        df2.to_excel(writer, sheet_name="2013-2020 Killings by PD", index=index)
        df3.to_excel(writer, sheet_name="2013-2020 Killings by State", index=index)
        df4.to_excel(writer, sheet_name="Police Killings of Black Men", index=index)


class Spending(object):
    def __init__(self, file, dtype=np.float64):
        self.file = open(file, 'r')
        data = self.file.readlines()
        self.publisher = data[0].rstrip("\n").rstrip(",")
        self.file = file

        try:
            self.table_num, self.description = \
            self.standardStrip(data[2]).split("\"")[1].split("'")[0].lower().split("table")[1].lstrip().split(".")
            self.table_num = int(self.table_num)
            self.description = self.description.strip(" ")
        except ValueError:
            pass
        except IndexError:
            pass

        self.title = self.standardStrip(data[3]).split("  ")
        self.data_sources = self.standardStrip(data[4]).strip("\"").strip("Data Source: ")
        self.author = self.standardStrip(data[5]).strip("\"").lstrip("Author: ")
        self.contact_info = self.standardStrip(data[6])
        try:
            self.date = dt.strptime(self.standardStrip(data[7]), "Date of version: %m/%d/%Y").date()
        except ValueError:
            self.date = None

        start_index = [i for i in range(len(data)) if data[i].replace(",", "") == "\n"]
        data2 = data[start_index[0] + 2:start_index[1]]
        data2 = [i.strip("\n").split(",") for i in data2]
        for i in range(len(data2)):
            for j in range(len(data2[i])):
                if data2[i][j] == "NaN":
                    data2[i][j] = np.NaN
        columns = [i.pop(0) for i in data2]
        columns = np.array([i for i in columns if i != ""])
        self._set_data_frame(data2, columns, dtype)
        self._set_notes(data[start_index[1] + 1:])

    def _set_data_frame(self, data, row_index, dtype=np.float16):
        columns = data.pop(0)
        row_index = np.delete(row_index, 0)
        try:
            array = np.array(data, dtype=dtype)
        except:
            array = np.array(data, dtype=np.float16)
        self.df = pd.DataFrame(array, index=row_index, columns=columns)

    def _set_notes(self, data):
        if "Note" in data[0]:
            self.note = data.pop(0)
        self.source = data.pop(-1)
        for subnote in data:
            tag, content = self.standardStrip(subnote).strip("\"").split("/")
            content = f"Subnote {tag}: {content}"
            tag = f"subnote_{tag}"
            setattr(self, tag, content)

    def __str__(self) -> str:
        if hasattr(self, "description") and hasattr(self, "table_num"):
            return f"Dataset \"{self.title}\" published by {'the ' + self.publisher if 'the ' not in self.publisher.lower() else self.publisher} on {self.date:%B %d, %Y} by {self.author} has information about {self.description} from {self.data_sources}"
        else:
            return f"Dataset \"{self.title}\" published by {'the ' + self.publisher if 'the ' not in self.publisher.lower() else self.publisher} on {self.date:%B %d, %Y} by {self.author} has information from {self.data_sources}"

    def __int__(self) -> int:
        try:
            return self.table_num
        except AttributeError:
            raise ValueError("This specific object does not have the attribute that calculates the int")

    def __bool__(self) -> bool:
        return hasattr(self, "data")

    @staticmethod
    def standardStrip(string: str) -> str:
        return string.rstrip("\n").rstrip(",")


class LinearEquation(object):
    def __init__(self, x: list, y: list):
        if len(x) != len(y):
            raise ValueError(
                f"The length of the first list does not match the length of the second list: {len(x)} != {len(y)}")

        self.x = x
        self.y = y

        self._x_standard_deviation = self._getStandardDeviation(x)
        self._y_standard_deviation = self._getStandardDeviation(y)
        self.r = self._getR()
        self.slope = self.r * (self._y_standard_deviation / self._x_standard_deviation)
        self.y_intercept = self._average(y) - self.slope * self._average(x)

    def __itruediv__(self, other):
        if isinstance(other, [int, float]):
            self.slope /= other

    def __str__(self) -> str:
        """Returns a human-readable linear equation"""
        if self.y_intercept == 0:
            intercept_str = ""
        elif self.y_intercept < 0:
            intercept_str = f" {round(self.y_intercept, 2)}"
        else:
            intercept_str = f" + {round(self.y_intercept, 2)}"
        return f"{round(self.slope, 2)}x" + intercept_str

    def __repr__(self):
        """Returns a more specific linear equation"""
        if self.y_intercept == 0:
            intercept_str = ""
        elif self.y_intercept < 0:
            intercept_str = f" {self.y_intercept}"
        else:
            intercept_str = f" + {self.y_intercept}"
        return f"{self.slope}x" + intercept_str

    def __len__(self) -> int:
        return len(self.x)

    def _getR(self):
        standardDeviationSums = self._standardDeviationSums(self.x, self.y)
        r = standardDeviationSums / ((len(self.x) - 1) * self._x_standard_deviation * self._y_standard_deviation)
        return r

    def _standardDeviationSums(self, x_lis, y_lis):
        summation = 0
        for x, y in zip(x_lis, y_lis):
            x_diff = x - self._average(x_lis)
            y_diff = y - self._average(y_lis)
            summation += (x_diff * y_diff)
        return summation

    def _getStandardDeviation(self, lis) -> float:
        standardDeviation = sum([(point - self._average(lis)) ** 2 for point in lis])
        standardDeviation /= (len(lis) - 1)
        return np.sqrt(standardDeviation)

    @staticmethod
    def _average(lis) -> float:
        return sum(lis) / len(lis)

    def predict(self, x) -> float:
        return self.slope * x + self.y_intercept

    def getNpLinspace(self, start=0, stop=1000, num=50) -> np.ndarray:
        return self.slope * np.linspace(start, stop, num) + self.y_intercept

    def rounded_y_intercept(self, rounding) -> str:
        if self.y_intercept == 0:
            intercept_str = ""
        elif self.y_intercept < 0:
            intercept_str = f" {round(self.y_intercept, 4)}"
        else:
            intercept_str = f" + {round(self.y_intercept, 4)}"
        return f"{round(self.slope, rounding)}x" + intercept_str

    @classmethod
    def create(cls, slope: float, y_intercept: float):
        obj = cls([i for i in range(9)], [2 * i for i in range(9)])
        obj.slope = slope
        obj.y_intercept = y_intercept
        return obj

    @classmethod
    def from_model(cls, model):
        if not hasattr(model, "coef_"):
            raise ValueError(f"Given model {model} does not have the required attribute 'coef_' to be used.")
        if not hasattr(model, "intercept_"):
            raise ValueError(f"Given model {model} does not have the required attribute 'intercept_' to be used.")
        return cls.create(model.coef_[0], model.intercept_)

    @classmethod
    def removal(cls, df: pd.DataFrame, x: str, y: str, remove=()):
        for extra in remove:
            df = df.drop(extra)
        return cls(df[x], df[y])


class Race(object):
    def __init__(self, name:str, color:str):
        self.name = name
        self.color = color

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, Race):
            return self.name == other.name
        elif isinstance(other, str):
            return self.name == other
        return False

    def __ne__(self, other):
        return not self == other


class Races(Enum):
    Black = Race("Black", "#784B2F")
    White = Race("White", "#8a8a8a")  # "#EDE4C8")
    Asian = Race("Asian", "#ff00ff")  # Pink
    Hispanic = Race("Hispanic", "#0000ff")
    Native_American = Race("Native American", "#00ff00")
    Pacific_Islander = Race("Pacific Islander", "#cccc00")
    Other = Race("Other", "000000")
    Races = (Black, Hispanic, Native_American, Asian, Pacific_Islander, White, Other)


if __name__ == "__main__":
    mpv_formatting(join("~", r"Downloads\MPVDatasetDownload.xlsx"), "tools.xlsx")
