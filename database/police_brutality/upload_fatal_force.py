from tabulate import tabulate
from tools import Gender, Race, ThreatLevel, Flee, get_true_value, correct_dictionary_types, generate_placeholders, convert_to_boolean, convert_to_gender, convert_to_race, convert_to_threat_level, convert_to_flee, check_similarity
from warnings import warn


def upload_wapo_fatal_force_data(cursor, dct:dict[str,str], type_map:dict[str,type], update:bool=True):
	"""
	Uploads a record into the Washington Post Fatal Force's MySQL database
	:param dict dct: The dictionary of the record. The key should be the column name, and the value should be a string holding the value. The string must be able to be converted using the convert_to... methods for the custom enumerations
	:param dict type_map: A dictionary holding the correct type for each column. The column is the key and the type is the value.
	:param bool update: if the database should update the record if the id is already being used.
	"""
	dct = correct_dictionary_types(dct, type_map)

	# Check if the id is already in the table
	cursor.execute(f"SELECT COUNT(id) FROM police_brutality.wapo_fatal_force WHERE id = {dct['id']}")
	if cursor.fetchone()[0]:
		update_dict = check_similarity(cursor, dct, type_map, "police_brutality.wapo_fatal_force")
		if not update_dict:
			return

		warn(f"The record with id: '{dct['id']}', currently known as '{update_dict['name'] if 'name' in update_dict.keys() else dct['name']}', needs to, and will{' NOT' if not update else ''} be updated. The values that will be updated are: ")
		print(tabulate([[key, value[0], value[1]] for key, value in update_dict.items()],  headers=("Column", "Current", "New"), tablefmt="fancy_grid"))
		if update:
			for key, (original, new) in update_dict.items():
				print(f"UPDATE police_brutality.wapo_fatal_force SET {key} = %s WHERE {key} = %s AND id = {dct['id']}", (get_true_value(new), get_true_value(original)))
				cursor.execute(f"UPDATE police_brutality.wapo_fatal_force SET {key} = %s WHERE {key} = %s AND id = {dct['id']}", (get_true_value(new), get_true_value(original)))
	else:
		non_null_keys = []
		non_null_values = []
		for header in type_map.keys():
			val = dct[header]
			if val is not None:
				non_null_keys.append(header)
				non_null_values.append(get_true_value(val))

		command = f"INSERT INTO police_brutality.wapo_fatal_force({','.join(non_null_keys)}) VALUES({generate_placeholders(len(non_null_values))})"
		cursor.execute(command, non_null_values)


if __name__ == "__main__":
	from csv import DictReader
	from datetime import date
	from mysql.connector import connect
	from ..tools import get_host_kwargs

	db = connect(**get_host_kwargs())
	cursor = db.cursor(buffered=True)

	database_file = r"D:\data\SIR\Police\data-police-shootings\fatal-police-shooting-data.csv"
	has_header_in_file = True
	type_map = {"id": int, "name": str, "date": date, "manner_of_death": str, "weapon": str, "age": int, "gender": Gender,
				"race": Race, "city": str, "state": str, "mental_illness_symptoms": bool, "threat_level": ThreatLevel,
				"fleeing": Flee, "body_camera": bool, "longitude": float, "latitude": float, "exact_geocoding": bool}
	update = True

	with open(database_file, 'r') as csvfile:
		reader = DictReader(csvfile, type_map.keys(), delimiter=',', quotechar='"')
		iterator = iter(reader)
		if has_header_in_file:
			next(iterator)
		for row in iterator:
			print(f"ID: {row['id']:>5} started")
			upload_wapo_fatal_force_data(cursor, row, type_map, update=update)
	print("Finished")
	# if update:
	# 	input("Ready to commit?")
	db.commit()
