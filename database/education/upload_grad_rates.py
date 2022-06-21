def upload_graduation_rates(cursor, state, graduation_rate):
	cursor.execute(f"SELECT COUNT(graduation_rate) FROM sir_education.state_data WHERE state = '{state}'")
	if cursor.fetchone()[0]:
		cursor.execute(f"UPDATE sir_education.state_data SET graduation_rate = {graduation_rate} WHERE state = '{state}'")
	else:
		cursor.execute(f"INSERT INTO sir_education.state_data(state,graduation_rate) VALUES ({state},{graduation_rate})")


def upload_grad_rates(db, file:str, skip_headers=True):
	from csv import reader
	cursor = db.cursor(buffered=True)
	with open(file, 'r') as csvfile:
		csv = reader(csvfile, delimiter=",", quotechar='"')
		iterator = iter(csv)
		if skip_headers:
			next(iterator)
		for row in iterator:
			upload_graduation_rates(cursor, row[0], float(row[1]))


def upload_wpr_state_data(cursor, dct:dict):
	cursor.execute(f"SELECT COUNT(state) FROM sir_education.state_data WHERE state = '{dct['state']}'")
	if cursor.fetchone()[0]:
		pass
	else:
		cursor.execute()


def upload_education(db):
	upload_grad_rates(db, r"D:\data\SIR\Education\wpr_graduation_rate.csv")


if __name__ == "__main__":
	from ..tools import get_host_kwargs
	from mysql.connector import connect
	upload_education(connect(**get_host_kwargs()))
