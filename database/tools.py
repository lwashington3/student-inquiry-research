def get_host_kwargs(host=None, user=None, password=None, database=None, port="3306") -> dict[str,str]:
	from os import getenv
	return {"host": getenv("host", host),
			"user": getenv("user", user),
			"password": getenv("password", password),
			"database":"police_brutality" if database is None else database,
			"port":getenv("port", port)}


def generate_placeholders(number:int) -> str:
	return ("%s," * number).rstrip(",")
