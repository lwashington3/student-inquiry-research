__author__ = "Len Washington III"

try:
    from tools import add_data_dir
except ModuleNotFoundError:
    from .tools import add_data_dir


class Converter(object):
    STANDARD_INPUT_HEADERS = ("id", "name", "date", "manner_of_death", "armed", "age", "gender", "race", "city", "state", "signs_of_mental_illness", "threat_level", "flee", "body_camera", "longitude", "latitude", "is_geocoding_exact")
    STANDARD_OUTPUT_HEADERS = (("Id"), ("Name"), ("Date"), ("Shot", "Shot_and_Tasered"), ("Arm_Undetermined", "Arm_Unknown", "Unarmed"), ("Age"),
         ("Male", "Female", "Unknown_Gender"), ("White_non_Hispanic", "Black_non_Hispanic", "Asian", "Native_American",
         "Hispanic", "Other_Race", "Unknown_Race"), ("City"), ("State"), ("Signs_of_Mental_Illness"),
         ("Threat_Level_Attack", "Threat_Level_Other", "Threat_Level_Undetermined"), ("Fled_by_Foot", "Fled_by_Car", "Not_Fleeing"),
         ("Body_Camera"), ("Longitude"), ("Latitude"), ("Is_Geocoding_Exact"))
    STANDARD_CONVERSION_HEADERS = ((), (), (), ("Shot", "Shot And Tasered"), (('Gun', 'Toy Weapon', 'Nail Gun', 'Knife', 'Shovel', 'Vehicle', 'Hammer', 'Hatchet', 'Sword', 'Machete', 'Box Cutter', 'Metal Object', 'Screwdriver', 'Lawn Mower Blade', 'Flagpole', 'Guns And Explosives', 'Cordless Drill', 'Crossbow', 'Metal Pole', 'Taser', 'Metal Pipe', 'Metal Hand Tool', 'Blunt Object', 'Metal Stick', 'Sharp Object', 'Meat Cleaver', 'Carjack', 'Chain', "Contractor's Level", 'Unknown Weapon', 'Stapler', 'Beer Bottle', 'Bean-Bag Gun', 'Baseball Bat and Fireplace Poker', 'Straight Edge Razor', 'Gun And Knife', 'Ax', 'Brick', 'Baseball Bat', 'Hand Torch', 'Chain Saw', 'Garden Tool', 'Scissors', 'Pole', 'Pick-Axe', 'Flashlight', 'Baton', 'Spear', 'Chair', 'Pitchfork', 'Hatchet And Gun', 'Rock', 'Piece Of Wood', 'Bayonet', 'Pipe', 'Glass Shard', 'Motorcycle', 'Pepper Spray', 'Metal Rake', 'Crowbar', 'Oar', 'Machete And Gun', 'Tire Iron', 'Air Conditioner', 'Pole And Knife', 'Baseball Bat And Bottle', 'Fireworks', 'Pen', 'Chainsaw', 'Gun And Sword', 'Gun And Car', 'Pellet Gun', 'Claimed To Be Armed', 'Bb gun', 'Incendiary Device', 'Samurai Sword', 'Bow and Arrow', 'Gun And Vehicle', 'Vehicle And Gun', 'Wrench', 'Walking Stick', 'Barstool', 'Grenade', 'BB Gun And Vehicle', 'Wasp Spray', 'Air Pistol', 'Airsoft Pistol', 'Baseball Bat And Knife', 'Vehicle And Machete', 'Ice Pick', 'Car, Knife And Mace', 'Bottle', 'Gun and Machete'), "", "Unarmed"), (),
         ("M", "F", ("None", "")), ("W", "B", "A", "N", "H", "O", ("None", "")),
         (), (), ("False", "True"), ("Attack", "Other", "Undetermined"), ("Foot", "Car", "Not Fleeing"),
         ("False", "True"), (), (), ("False", "True"))

    def __init__(self, input_file: str, output_file: str, input_headers=(), output_headers=(), conversion_headers=(), insertion="/&*"):
        """

        :param str input_file: The csv file that has human readable data
        :param str output_file: The file where you want to send the binary data
        :param tuple input_headers:
        :param tuple output_headers:
        :param tuple conversion_headers:
        :param str insertion:
        """
        self.input_file = input_file
        self.output_file = output_file
        self.input_headers = input_headers
        self.output_headers = output_headers
        self.conversion_headers = conversion_headers
        self.insertion = insertion
        self._index = 0
        self.lis = []

    def __len__(self) -> int:
        return len(self.lis)

    def __str__(self) -> str:
        return f"Converting raw data about {len(self):,} police shootings and converting them for use with SIR project"

    def __bool__(self) -> bool:
        try:
            return bool(self.input_headers) and bool(self.output_headers) and bool(self.conversion_headers)
        except AttributeError:
            return False

    def __int__(self) -> int:
        return len(self)

    def __float__(self) -> float:
        return float(len(self))

    def __iter__(self):
        return self

    def __next__(self):
        if len(self) == 0:
            raise ValueError("A conversion has not been run. Conversions are required for object methods.")
        if self._index < len(self):
            result = self.lis[self._index]
            self._index += 1
            return result
        self._index = 0
        raise StopIteration

    def setOutputHeaders(self, headers: tuple):
        self.output_headers = headers

    def setInputHeaders(self, headers: tuple):
        self.input_headers = headers

    def setConversionHeaders(self, headers:tuple):
        self.conversion_headers = headers

    def convert_binary(self):
        lis = open(self.input_file).readlines()
        text = ""
        for item in self.output_headers:
            text += f"{item}, "
        text += "\n"
        lis.pop(0)
        # lis = [row for row in lis if f"{2020}-" not in row]
        output = open(self.output_file, 'w')
        output.writelines(self.write_headers())
        for row in lis:
            # Took out `.replace(", ", self.insertion)` because it was screwing up when there was a comma in Junior
            row = row.replace(", Jr.", " Jr.").replace("  ", " ").split(",")  # There's a typo in the name for 820 Austin where there is a space before his name and the system autocorrects that assuming it's something like Junior. I could contact WP to have them change this is their file
            row = [i.strip().lstrip(' ').title() for i in row]
            app = []
            for (cell, inp, conv) in zip(row, self.input_headers, self.conversion_headers):
                if len(conv) == 0:
                    app.append(cell)
                elif "False" in conv and "True" in conv:
                    app.append("1" if "True" in cell else "0")
                else:
                    for i in conv:
                        if isinstance(i, tuple):
                            app.append("1" if cell in i else "0")
                        else:
                            app.append("1" if cell == i else "0")
            output.writelines(", ".join(app).rstrip(", ").replace(self.insertion, ", ") + "\n")
        self.lis = lis

    def write_headers(self) -> str:
        string = ""
        for i in self.output_headers:
            if isinstance(i, str):
                string += f"{i}, "
            elif isinstance(i, tuple):
                for y in i:
                    if isinstance(y, str):
                        string += f"{y}, "
        return string.rstrip(", ") + "\n"


if __name__ == "__main__":
    convert = Converter(add_data_dir("data-police-shootings/fatal-police-shooting-data.csv"), add_data_dir("data-police-shootings/binary-data.csv"))
    convert.setInputHeaders(Converter.STANDARD_INPUT_HEADERS)
    convert.setOutputHeaders(Converter.STANDARD_OUTPUT_HEADERS)
    convert.setConversionHeaders(Converter.STANDARD_CONVERSION_HEADERS)

    for (inp, output, conv) in zip(convert.input_headers, convert.output_headers, convert.conversion_headers):
        print(f"{inp} : {output} : {conv}")
    convert.convert_binary()
