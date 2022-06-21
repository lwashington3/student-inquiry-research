from mysql.connector.cursor_cext import CMySQLCursorBuffered
from tabulate import tabulate
from tools import Armed, Gender, Race, ThreatLevel, Flee, PopulationDensity, get_true_value, correct_dictionary_types, generate_placeholders, check_is_none, check_similarity
from warnings import warn


def upload_mpv_data(cursor:CMySQLCursorBuffered, dct:dict[str,str], type_map:dict[str,type], update:bool=True):
	"""
	Uploads a record into the Mapping Police Violence database
	:param dict dct: The dictionary of the record. The key should be the column name, and the value should be a string holding the value. The string must be able to be converted using the convert_to... methods for the custom enumerations
	:param dict type_map: A dictionary holding the correct type for each column. The column is the key and the type is the value.
	:param bool update: if the database should update the record if the id is already being used.
	"""
	dct = correct_dictionary_types(dct, type_map)
	if dct["race"] == Race.UR:
		dct["race"] = Race.U

	# Check if the id is already in the table
	cursor.execute(f"SELECT COUNT(id) FROM police_brutality.mapping_police_violence WHERE id = {dct['id']}")
	if cursor.fetchone()[0]:
		update_dict = check_similarity(cursor, dct, type_map, "police_brutality.mapping_police_violence")
		if not update_dict:
			return

		warn(f"The record with id: '{dct['id']}', currently known as '{update_dict['name'] if 'name' in update_dict.keys() else dct['name']}', needs to, and will{' NOT' if not update else ''} be updated. The values that will be updated are: ")
		print(tabulate([[key, value[0], value[1]] for key, value in update_dict.items()],  headers=("Column", "Current", "New"), tablefmt="fancy_grid"))
		if update:
			for key, (original, new) in update_dict.items():
				print(f"UPDATE police_brutality.mapping_police_violence SET {key} = %s WHERE {key} = %s AND id = {dct['id']}", (get_true_value(new), get_true_value(original)))
				cursor.execute(f"UPDATE police_brutality.mapping_police_violence SET {key} = %s WHERE {key} = %s AND id = {dct['id']}", (get_true_value(new), get_true_value(original)))
	else:
		non_null_keys = []
		non_null_values = []
		for header in type_map.keys():
			val = dct[header]
			if not check_is_none(val):
				non_null_keys.append(header)
				non_null_values.append(get_true_value(val))

		command = f"INSERT INTO police_brutality.mapping_police_violence({','.join(non_null_keys)}) VALUES({generate_placeholders(len(non_null_values))})"
		cursor.execute(command, non_null_values)


if __name__ == "__main__":
	from datetime import date
	from mysql.connector import connect
	from pandas import read_csv
	from ..tools import get_host_kwargs
	from mysql.connector.errors import IntegrityError

	db = connect(**get_host_kwargs())
	cursor = db.cursor(buffered=True)
	print(type(cursor))
	database_file = r"D:\data\SIR\Police\Mapping Police Violence.csv"
	type_map = {"name":str, "age":int, "gender":Gender, "race":Race,"date":date, "address":str, "city":str, "state":str,
				"zipcode":int, "county":str, "responsible_agency":str, "ori_agency_identifier":str, "cause_of_death":str,
				"official_disposition_of_death":str, "mental_illness_symptoms":bool, "armed":Armed, "alleged_weapon":str,
				"alleged_threat_level":ThreatLevel, "fleeing":Flee, "body_camera":bool, "wapo_id":int, "off_duty_killing":bool,
				"population_density":PopulationDensity, "id":int, "fatal_encounters_id":int, "encounter_type":str,
				"call_for_service":bool, "census_tract":int, "census_tract_median_household_income":int, "longitude":float, "latitude":float}
	update = False
	df = read_csv(database_file)
	df = df.filter(("name", "age", "gender", "race", "date", "street_address", "city", "state", "zip", "county", "agency_responsible",
					"ori", 'cause_of_death', 'disposition_official', 'signs_of_mental_illness', 'allegedly_armed',
					'wapo_armed', 'wapo_threat_level', 'wapo_flee', 'wapo_body_camera', 'wapo_id', 'off_duty_killing',
					'geography', 'mpv_id', 'fe_id', 'encounter_type', 'call_for_service', 'tract', 'hhincome_median_census_tract',
					'latitude', 'longitude'), axis=1)

	df.columns = type_map.keys()
	missing_ids = 0
	for row_index, row in df.iterrows():
		row_index += 2
		print(f"Row: {row_index:>6}/10,206 ID: {row['id']:>5} started")
		dct = row.to_dict()
		if check_is_none(dct['id']):
			warn(f"The person in row: {row_index}, named: {dct['name']}, is being skipped because they do not have an MPV ID")
			missing_ids += 1
			continue
		try:
			upload_mpv_data(cursor, dct, type_map, update=update)
		except IntegrityError as e:
			if "Cannot add or update a child row: a foreign key constraint fails" in str(e):
				print(f"The Washington Post ID for {dct['name']} ({dct['id']}) does not exist in the Washington Post database.")

	print(f"Finished. People missing ids: {missing_ids}")
	# if update:
	# 	input("Ready to commit?")
	db.commit()


#  TODO: Off Duty isn't saved as a boolean, the column will say "Off-Duty", create an enum to rectify is
