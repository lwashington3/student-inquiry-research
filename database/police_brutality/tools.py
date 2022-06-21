from datetime import datetime as dt, date
from enum import Enum
from numpy import isnan
from warnings import warn


class Gender(Enum):
	M = "Male"
	F = "Female"
	U = "Unknown"
	T = "Transgender"


class Race(Enum):
	B = "Black"
	W = "White"
	A = "Asian"
	N = "Native American"
	H = "Hispanic"
	O = "Other"
	U = "Unknown"
	P = "Pacific Islander"
	UR = "Unknown Race"


class ThreatLevel(Enum):
	Attack = "Attack"
	Other = "Other"
	Undetermined = "Undetermined"
	none = "None"
	Used_Weapon = "Used Weapon"
	Unclear = "Unclear"
	Brandished_Weapon = "Brandished Weapon"
	STM = "Sudden Threatening Movement"


class Flee(Enum):
	Car = "Car"
	Foot = "Foot"
	Other = "Other"
	Unknown = "Unknown"
	Not_fleeing = "Not fleeing"
	Car_and_Foot = "Car,Foot"


class Armed(Enum):
	Allegedly_Armed = "Allegedly Armed"
	Unclear = "Unclear"
	Vehicle = "Vehicle"
	Unarmed = "Unarmed"
	No_Actual_Weapon = "Unarmed/Did Not Have Actual Weapon"


class PopulationDensity(Enum):
	Suburban = "Suburban"
	Urban = "Urban"
	Rural = "Rural"
	Undetermined = "Undetermined"


def get_true_value(obj):
	if isinstance(obj, date):
		return obj.strftime("%Y-%m-%d")
	return obj if not isinstance(obj, Enum) else obj.value


def check_is_nan(value) -> bool:
	if isinstance(value, float):
		return isnan(value)
	return False


def check_is_none(value) -> bool:
	if check_is_nan(value):
		return True
	elif value is None:
		return True
	return False


def correct_dictionary_types(raw_dct, correct_type_dct:dict[str,type], **kwargs) -> dict:
	leave_dates_as_date = kwargs.get("leave_dates_as_date", False)

	for key, correct_type in correct_type_dct.items():
		raw_value = raw_dct[key]
		match correct_type.__name__:
			case "str":
				if not raw_value:
					raw_dct[key] = None
			case "int":
				try:
					new_value = int(raw_value)
				except (ValueError, TypeError):
					new_value = None
				raw_dct[key] = new_value
			case "float":
				try:
					new_value = float(raw_value)
					if isnan(new_value):
						new_value = None
				except (ValueError, TypeError):
					new_value = None
				raw_dct[key] = new_value
			case "bool":
				raw_dct[key] = convert_to_boolean(raw_value)
			case "date":
				if not isinstance(raw_value, date):
					try:
						day = dt.strptime(raw_value, "%m/%d/%Y")
					except ValueError:
						day = dt.strptime(raw_value, "%Y-%m-%d")  # CSV Reader may change the format
				else:
					day = raw_value
				raw_dct[key] = day if leave_dates_as_date else day.strftime("%Y-%m-%d")
			case "Gender":
				try:
					raw_dct[key] = convert_to_gender(raw_value)
				except ValueError as e:
					raw_dct[key] = Gender.U
					warn(f"ValueError: {e}, assigning default value: {Gender.U} to row id: {raw_dct['id']}, name: {raw_dct['name']}")
			case "Race":
				try:
					raw_dct[key] = convert_to_race(raw_value)
				except ValueError as e:
					raw_dct[key] = Race.U
					warn(f"ValueError: {e}, assigning default value: {Race.U} to row id: {raw_dct['id']}, name: {raw_dct['name']}")
			case "ThreatLevel":
				try:
					raw_dct[key] = convert_to_threat_level(raw_value)
				except ValueError as e:
					raw_dct[key] = ThreatLevel.Undetermined
					warn(f"ValueError: {e}, assigning default value: {ThreatLevel.Undetermined} to row id: {raw_dct['id']}, name: {raw_dct['name']}")
			case "Flee":
				try:
					raw_dct[key] = convert_to_flee(raw_value)
				except ValueError as e:
					raw_dct[key] = Flee.Unknown
					warn(f"ValueError: {e}, assigning default value: {Flee.Unknown} to row id: {raw_dct['id']}, name: {raw_dct['name']}")
			case "Armed":
				try:
					raw_dct[key] = convert_to_armed(raw_value)
				except ValueError as e:
					raw_dct[key] = Armed.Unclear
					warn(f"ValueError: {e}, assigning default value: {Armed.Unclear} to row id: {raw_dct['id']}, name: {raw_dct['name']}")
			case "PopulationDensity":
				try:
					raw_dct[key] = convert_to_population_density(raw_value)
				except ValueError as e:
					raw_dct[key] = PopulationDensity.Undetermined
					warn(f"ValueError: {e}, assigning default value: {PopulationDensity.Undetermined} to row id: {raw_dct['id']}, name: {raw_dct['name']}")
	return raw_dct


def generate_placeholders(number:int) -> str:
	return ("%s," * number).rstrip(",")


def convert_to_boolean(value:str|int) -> bool:
	if isinstance(value, float):
		if isnan(value):
			return False
		return bool(value)
	if isinstance(value, int):
		return bool(value)
	value = value.lower()
	return value == "true" or value == "yes"


def convert_to_custom_enum(value:str, enum, none_value):
	if isinstance(value, enum):
		return value
	if check_is_none(value):
		return none_value
	value = value.upper()
	for attribute in ("name", "value"):
		for e in enum:
			if value == getattr(e, attribute).replace("_", ' ').upper():
				return e
	return None


def convert_to_gender(value:str) -> Gender:
	gender = convert_to_custom_enum(value, Gender, none_value=Gender.U)
	if gender is not None:
		return gender
	raise ValueError(f"Unknown gender value: {value}")


def convert_to_race(value:str) -> Race:
	race = convert_to_custom_enum(value, Race, none_value=Race.U)
	if race is not None:
		return race
	raise ValueError(f"Unknown race value: {value}")


def convert_to_threat_level(value:str) -> ThreatLevel:
	threat_level = convert_to_custom_enum(value, ThreatLevel, none_value=ThreatLevel.Undetermined)
	if threat_level is not None:
		return threat_level
	raise ValueError(f"Unknown threat level value: {value}")


def convert_to_flee(value:str) -> Flee:
	fleeing = convert_to_custom_enum(value, Flee, none_value=Flee.Unknown)
	if fleeing is not None:
		return fleeing
	raise ValueError(f"Unknown flee value: {value}")


def convert_to_armed(value:str) -> Armed:
	armed = convert_to_custom_enum(value, Armed, none_value=Armed.Unclear)
	if armed is not None:
		return armed
	raise ValueError(f"Unknown armed value: {value}")


def convert_to_population_density(value:str) -> PopulationDensity:
	popden = convert_to_custom_enum(value, PopulationDensity, none_value=PopulationDensity.Undetermined)
	if popden is not None:
		return popden
	raise ValueError(f"Unknown population density value: {value}")


def check_similarity(cursor, new_record:dict, type_map, table_name) -> dict:
	key_order = new_record.keys()
	cursor.execute(f"SELECT {','.join(key_order).rstrip(',')} FROM {table_name} WHERE id = {new_record['id']}")
	original = cursor.fetchone()
	original = correct_dictionary_types({key: value for key, value in zip(key_order, original)}, type_map, leave_dates_as_date=False)
	return {key: (original[key], new_record[key]) for key in key_order if original[key] != new_record[key]}
