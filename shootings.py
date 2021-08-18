__author__ = "Len Washington III"

from datetime import datetime as dt
from matplotlib import pyplot as plt
from requests import get
import numpy as np
try:
    from converter import Converter, add_data_dir
except ModuleNotFoundError:
    from .converter import Converter, add_data_dir


class Shootings(object):
    """This class was made for analyzing data from the Washington Post's Fatal Force Github repository about shootings from 1/1/2015"""
    def __init__(self, ID: int, name: str, date: dt, shot: bool, shot_and_tasered: bool,
                 arm_undetermined: bool, arm_unknown: bool, unarmed: bool, age: int,
                 male: bool, female: bool, unknown_gender: bool, is_white_non_hispanic: bool, is_black_non_hispanic: bool,
                 is_asian: bool, is_native_american: bool, is_hispanic: bool, other_race: bool, unknown_race: bool, city: str,
                 state: str, signs_of_mental_illness: bool, threat_level_attack: bool, threat_level_other, threat_level_undetermined: bool,
                 fled_by_foot: bool, fled_by_car: bool, not_fleeing: bool, body_camera: bool, longitude: float, latitude: float,
                 is_geocoding_exact: bool):
        """

        :param int ID: The unique integer identifier for each victim.
        :param str name: The name of the victim.
        :param datetime.datetime date: The date of the fatal shooting as a datetime.datetime object.

        The next two parameters deal with the manner of death of the victim. Only one of these parameters will be true.
        :param bool shot: If the victim was only shot when they died. This will be the opposite of shot_and_tasered.
        :param bool shot_and_tasered: If the victim was both shot and tasered when they died. This will be the opposite of shot.

        The next three parameters indicates whether or not the victim was armed. Only one parameter can be true
        :param bool arm_undetermined: This is true if it is not known whether or not the victim was armed
        :param bool arm_unknown: This is true if the victim was armed. This also includes not knowing what the object was
        :param bool unarmed: Indicates that the victim was not armed.

        :param int age: The age of the victim

        The next three parameters regard the gender that the victim IDENTIFIES with if the report says the victim didn't identify there biological sex
        :param bool male: Indicates whether or not the victim identified as male
        :param bool female: Indicates whether or not the victim identified as female
        :param bool unknown_gender: Indicates if the gender of the victim could not be determined

        The next seven parameters regard the race of the victim.
        :param bool is_white_non_hispanic: True if the victim was white, non-hispanic
        :param bool is_black_non_hispanic: True if the victim was black, non-hispanic
        :param bool is_asian: True if the victim was asian
        :param bool is_native_american: True if the victim was Native American
        :param bool is_hispanic: True if the victim was Hispanic
        :param bool other_race: True if the victim was race not previously listed
        :param bool unknown_race: True if the victim's race couldn't be determined

        :param str city: The municipality where the shooting took places. In some counties, this field is the county if a specific municipality if unavailable or unknown
        :param str state: The two-letter postal code abbreviation of the state.

        :param bool signs_of_mental_illness:

        :param bool threat_level_attack:
        :param bool threat_level_other:
        :param bool threat_level_undetermined:

        :param bool fled_by_foot:
        :param bool fled_by_car:
        :param bool not_fleeing:

        :param bool body_camera: Whether or not the police were wearing a functional body camera at the time of the shooting

        :param float longitude:
        :param float latitude:
        :param bool is_geocoding_exact:
        """
        self.id = ID
        self.name = name.strip(" ")
        self.date = date
        self.shot = shot
        self.shot_and_tasered = shot_and_tasered
        self.arm_undetermined = arm_undetermined
        self.arm_unknown = arm_unknown
        self.unarmed = unarmed
        self.age = age
        self.male = male
        self.female = female
        self.unknown_gender = unknown_gender
        self.is_white_non_hispanic = is_white_non_hispanic
        self.is_black_non_hispanic = is_black_non_hispanic
        self.is_asian = is_asian
        self.is_native_american = is_native_american
        self.is_hispanic = is_hispanic
        self.other_race = other_race
        self.unknown_race = unknown_race
        self.city = city
        self.state = state
        self.signs_of_mental_illness = signs_of_mental_illness
        self.threat_level_attack = threat_level_attack
        self.threat_level_other = threat_level_other
        self.threat_level_undetermined = threat_level_undetermined
        self.fled_by_foot = fled_by_foot
        self.fled_by_car = fled_by_car
        self.not_fleeing = not_fleeing
        self.body_camera = body_camera
        self.longitude = longitude
        self.latitude = latitude
        self.is_geocoding_exact = is_geocoding_exact

    def shotIn(self, date:int) -> bool:
        """This method takes a date, whether it's a year or a datetime object, and checks to see if the person was killed in that time. This can be used for filtering shootings between a specific set of dates."""
        if isinstance(date, int):
            try:
                return date == self.date.year
            except AttributeError:
                print(self.id, self.date)
        elif isinstance(date, dt):
            return date == self.date

    def wasFleeing(self) -> bool:
        """Returns whether or not the victim was fleeing"""
        return not self.not_fleeing

    def bodyCamera(self) -> bool:
        """
        Returns whether or not the police had body camera function when the shooting happened
        """
        return self.body_camera

    def getRace(self) -> str:
        """
        Returns the race of the person
        """
        if self.is_white_non_hispanic:
            return "White"
        elif self.is_black_non_hispanic:
            return "Black"
        elif self.is_asian:
            return "Asian"
        elif self.is_native_american:
            return "Native American"
        elif self.is_hispanic:
            return "Hispanic"
        elif self.unknown_race:
            return "UNKNOWN RACE"
        else:
            return ""

    def getGender(self) -> str:
        """
        Returns the gender of the person
        """
        if self.male:
            return "Male"
        elif self.female:
            return "Female"
        elif self.unknown_gender:
            return "UNKNOWN GENDER"

    def getCity(self) -> str:
        return f"{self.city}, {self.state}"

    def getGeoCoordinates(self) -> tuple:
        return self.latitude, self.longitude

    def __str__(self) -> str:
        return f"{self.name}, a {self.age} year-old {self.getRace()} {self.getGender()} was killed on {self.date:%B %#d, %Y} in {self.city}, {self.state}, {'exactly at' if self.is_geocoding_exact else 'close to'} ({self.latitude}, {self.longitude}). They {'showed' if self.signs_of_mental_illness else 'did not show'} signs of mental illness. The police {'were' if self.body_camera else 'were not'} wearing a body camera at the time of the shooting."

    def __int__(self) -> int:
        return self.id

    @staticmethod
    def from_web(url="https://raw.githubusercontent.com/washingtonpost/data-police-shootings/master/fatal-police-shootings-data.csv", full_file="fatal-police-shooting-web.csv", bin_file="binary-fatal-police-shooting-web.csv", delimiter=",", hasHeader=True) -> list:
        data = get(url).text.replace("  ", " ").split("\r\n")
        with open(full_file, "w") as file:
            file.write("\n".join(data))
        convert = Converter(full_file, bin_file)

        convert.setInputHeaders(Converter.STANDARD_INPUT_HEADERS)
        convert.setOutputHeaders(Converter.STANDARD_OUTPUT_HEADERS)
        convert.setConversionHeaders(Converter.STANDARD_CONVERSION_HEADERS)

        for (inp, output, conv) in zip(convert.input_headers, convert.output_headers, convert.conversion_headers):
            print(f"{inp} : {output} : {conv}")

        convert.convert_binary()
        return Shootings.from_csv(bin_file, delimiter=delimiter, hasHeader=hasHeader)

    @staticmethod
    def from_csv(file, delimiter=",", hasHeader=True) -> list:
        data = open(file).readlines()
        if hasHeader:
            data.pop(0)
        data = [[i.title() for i in person.split(delimiter)] for person in data]
        everything = []
        for person in data:
            tmp = []
            for detail in person:
                try:
                    detail = float(detail)
                    if int(detail) == detail:
                        detail = int(detail)
                        if detail == 1 or detail == 0:
                            detail = bool(detail)
                except ValueError:
                    try:
                        detail = dt.strptime(detail.strip(" "), "%Y-%m-%d")
                    except ValueError:
                        pass
                tmp.append(detail)

            obj = Shootings(tmp[0], tmp[1], tmp[2], tmp[3], tmp[4], tmp[5], tmp[6], tmp[7], tmp[8], tmp[9], tmp[10], tmp[11], tmp[12], tmp[13], tmp[14], tmp[15], tmp[16], tmp[17], tmp[18], tmp[19].strip(" "), tmp[20].upper().strip(" "), tmp[21], tmp[22], tmp[23], tmp[24], tmp[25], tmp[26], tmp[27], tmp[28], tmp[29], tmp[30], tmp[31])
            everything.append(obj)
        return everything


def main():
    lower, upper = 13, 19
    lis = Shootings.from_csv(add_data_dir("data-police-shootings/binary-data.csv"))
    plotting = [person for person in lis if person.is_black_non_hispanic and (lower <= (0 if person.age == "" else person.age) <= upper) and (person.getGender() == "Male")]
    # chi = [person for person in plotting if person.is_black_non_hispanic and person.state == "IL"]
    # x = [person.age for person in plotting]
    # y = [(person.date.date() - date(2015, 1, 1)).days for person in plotting]

    x1 = [person.age for person in plotting if person.signs_of_mental_illness]
    x2 = [person.age for person in plotting if not person.signs_of_mental_illness]

    y1 = [(person.date.date() - date(2015, 1, 1)).days for person in plotting if person.signs_of_mental_illness]
    y2 = [(person.date.date() - date(2015, 1, 1)).days for person in plotting if not person.signs_of_mental_illness]
    plt.scatter(x2, y2, c=["red"], label="Shows Signs of Mental Illness")
    plt.scatter(x1, y1, c=["blue"], label="Don't show signs of Mental Illness")
    plt.xticks(np.arange(lower, upper+1, step=1))
    plt.yticks(np.arange(0, (365*5.5), step=365//2), ["Jan 2015", "July 2015", "Jan 2016", "July 2016", "Jan 2017", "July 2017", "Jan 2018", "July 2018", "Jan 2019", "July 2019", "Jan 2020", "July 2020"])  # , rotation=345)
    plt.xlabel("Age (Years)")
    plt.ylabel("Date")
    plt.title(f"Black Males Between the Ages of {lower} and {upper} Killed in Chicago, IL")
    plt.legend(loc="upper left")
    plt.show()


if __name__ == "__main__":
    # main()
    lis = Shootings.from_web(full_file=add_data_dir("Police\\data-police-shootings\\fatal-police-shooting-data.csv"), bin_file=add_data_dir("Police\\data-police-shootings/binary-data.csv"))
    print(len(lis))
    print(lis[0])
