import pandas as pd
from tools import add_data_dir


class Causes(object):
    def __init__(self, cause: str, percent: float):
        self.cause = cause
        self.percent = percent

    def __repr__(self):
        return f"{self.cause} {self.percent * 100:#.1f}%"

    def __str__(self):
        return repr(self)

    def __float__(self):
        return self.percent

    @staticmethod
    def from_csv(file: str) -> pd.DataFrame:
        with open(file) as f:
            lines = [i.strip().split(",") for i in f.readlines()]
        length = len(lines[0])
        for i in lines:
            if length != len(i):
                raise ValueError(f"Row `{i}` does not match the length of the other lines.")
        index = [line[0] for line in lines]
        data = {index[0]: index[1:]}
        for i in range(1, length):
            col = [line[i] for line in lines]
            key = col.pop(0)

            try:
                col[0] = int(col[0])
            except ValueError:
                pass
            for j in range(1, len(col)):
                cause, percent = col[j].split("/")
                col[j] = Causes(cause, float(percent))
            data[key] = col
        return pd.DataFrame(data)


if __name__ == "__main__":
    print(Causes.from_csv(add_data_dir("Health/leading_causes_of_death.csv")).head())
