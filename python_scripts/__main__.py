import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
try:
	from tools import *
except ModuleNotFoundError:
	from .tools import *


def _biggest_race_generator(row:pd.core.series.Series) -> int:
	races = (row["Black Population"], row["Hispanic Population"], row["Native American Population"], row["Asian Population"], row["Pacific Islander Population"], row["White Population"], row["Other Population"])
	return races.index(max(races))


def graduation_rate(file_name:str) -> pd.DataFrame:
	df = pd.read_csv(file_name)
	df["Biggest Race"] = df.apply(_biggest_race_generator, axis=1)
	return df


def state_education_spending(df:pd.DataFrame, x:str, scale=1):
	ax = sns.regplot(x=df[x].apply(lambda x: x / scale), y=df["Graduation Rate"])
	ax.set_title(f"{x} vs Graduation Rate by State")
	scale_label = f" (per ${scale:,})" if scale != 1 else ""
	ax.set_xlabel(f"{x}{scale_label if scale != 1 else ''}")
	ax.set_ylabel("Graduation Rate (%)")
	plt.show()


def racial_percentage_plot(df: pd.DataFrame, race: str):
	x = df.apply(lambda row: row[f"{race} Population"] / (
			row["Black Population"] + row["Hispanic Population"] + row["Native American Population"] + row["Asian Population"] + row["Pacific Islander Population"] + row["White Population"] + row[
		"Other Population"]), axis=1)
	x = x.to_numpy() * 100
	y = df["Graduation Rate"].to_numpy()

	sns.regplot(x=x, y=y, scatter=False)  # Scatter is true if the points need shadows

	plt.title("Racial Percentage vs Graduation Rate")
	plt.xlabel(f"{race.title()} Population Percentage per State (%)")
	plt.ylabel("Graduation Rate (%)")

	plt.scatter(x, y, c=x, cmap="autumn_r")
	plt.colorbar()
	plt.show()


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

	def __str__(self) -> str:
		"""Returns a human-readable linear equation"""
		if self.y_intercept == 0:
			intercept_str = ""
		elif self.y_intercept < 0:
			intercept_str = f" {round(self.y_intercept, 2)}"
		else:
			intercept_str = f" + {round(self.y_intercept, 2)}"
		return f"{round(self.slope[0], 2)}x" + intercept_str

	def __repr__(self):
		"""Returns a more specific linear equation"""
		if self.y_intercept == 0:
			intercept_str = ""
		elif self.y_intercept < 0:
			intercept_str = f" {self.y_intercept}"
		else:
			intercept_str = f" + {self.y_intercept}"
		return f"{self.slope[0]}x" + intercept_str

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
		return self.slope[0] * x + self.y_intercept

	def getNpLinspace(self, start=0, stop=1000, num=50) -> np.ndarray:
		return self.slope[0] * np.linspace(start, stop, num) + self.y_intercept

	def rounded_y_intercept(self, rounding) -> str:
		if self.y_intercept == 0:
			intercept_str = ""
		elif self.y_intercept < 0:
			intercept_str = f" {round(self.y_intercept, 4)}"
		else:
			intercept_str = f" + {round(self.y_intercept, 4)}"
		return f"{round(self.slope[0], rounding)}x" + intercept_str

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
		return cls.create(model.coef_, model.intercept_)


def spending_graph(df: pd.DataFrame, x: str, y: str, special="", color1="#000000", color2="#ff0000", x_scale=1, save="",
				   transparent=True):
	"""
		Creates a scatter plot from the provided dataframe.

		Parameters
		----------
		df : pd.DataFrame
			This is the DataFrame that the function will draw values from.
		x : str
			This label of the series in the dataframe that should be used as the independent variable.
		y : str
			This label of the series in the dataframe that should be used as the dependent variable.
		special : str, optional
			This will plot a specific data point found in both the independent and dependent series and plot it in a different color.
		color1 : str, optional
			The default color of all points plotted. This will not apply to the special data point if one is provided. Default is black.
		color2 : str, optional
			The default color of the special data point. Default is red.
		x_scale : float, optional
			A scale that will be applied to every data point for the independent, x, variables.
		save : float, optional
			The file location where the plot should be saved. Will be saved to the directory that is saved in outputDirectory. Default does not save.
		transparent : bool, optional
			If the graph background should be transparent when saving. Default is yes.

		Returns
		-------
		Matplotlib.pyplot

		Examples
		--------
		>>> df[y]
			Row1        1000.0
			Row2        2500.0
			Row3       15000.0
		>>> x_scale = 1_000
		>>> df[y]
			Row1        1.0000
			Row2        2.5000
			Row3       15.0000
		"""
	plt.scatter(df[x].apply(lambda x: x / x_scale), df[y], c=color1)
	if special:
		plt.scatter(df[x][special] / x_scale, df[y][special], c=color2, label=f"{special} {x} ($)")
	x_scale_label = f"(per ${x_scale:,})" if x_scale != 1 else "($)"
	plt.xlabel(f"{x} {x_scale_label}")
	plt.ylabel("Graduation Rate (%)")
	plt.title(f"{x} {x_scale_label} vs Graduation Rate (%)")
	if save:
		plt.savefig(f"{output_folder}/{save}", transparent=transparent)
	return plt


def generate_spending_model(x, y, model):
	x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.2, random_state=0)
	# sc = StandardScaler()
	# x_train = sc.fit_transform(x_train)
	# x_test = sc.transform(x_test)

	try:
		model = model.fit(x_train, y_train)
	except ValueError as e:
		raise ValueError(model, str(e))
	y_pred = model.predict(x_test)
	accuracy = {"Mean Absolute Error": mean_absolute_error(y_test, y_pred),
				"Mean Squared Error": mean_squared_error(y_test, y_pred),
				"Root Mean Squared Error": np.sqrt(mean_squared_error(y_test, y_pred))}

	return model, accuracy, (x_test, y_test), y_pred


if __name__ == "__main__":
	state_data = graduation_rate(add_data_dir("Education\\state_data.csv"))
	race_pop = state_data.filter(
		["State Name", "Biggest Race", "Black Population", "Hispanic Population", "Native American Population",
		 "Asian Population", "Pacific Islander Population", "White Population", "Other Population"])
	race_pop.head(len(race_pop))

	state_education_spending(state_data, "Instruction Spending Per Pupil", scale=1_000)
	racial_percentage_plot(state_data, "Black")
