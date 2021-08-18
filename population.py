from requests import get
from pandas import read_html
try:
    from tools import add_data_dir
except ModuleNotFoundError:
    from .tools import add_data_dir


def get_tables_from_web(link: str):
    return read_html(get(link).content)


def add_state_graduation_rates(states:list, link:str) -> list:
    df = get_tables_from_web(link)[-1]
    for index, row in df.iterrows():
        state_name = row["State"]
        grad_rate = row["High School or Higher"]
        for i in range(len(states)):
            if states[i].lower() == state_name.lower():
                states[i].graduation_rate = grad_rate
    return states


def states_to_csv(states:list, file_loc:str, singles=("state_name", "population_2021", "growth_2021", "population_2018", "census_2010", "growth_since_2010", "percent_of_US", "density", "graduation_rate")):
    with open(file_loc, 'w') as file:
        file.write(", ".join([i.replace('_', ' ').title() for i in singles]) + "\n")
        for i in states:
            string = ""
            for attr in singles:
                string += str(getattr(i, attr)) + ", "
            file.write(string.rstrip(", ") + "\n")


def states_to_xlsx(states:list, file_loc:str, singles=("state_name", "population_2021", "growth_2021", "population_2018", "census_2010", "growth_since_2010", "percent_of_US", "density", "graduation_rate"), dataframes=("General Info", "race_data", "household_families", "household_types", "education_attained", "education_attained_by_race", "earnings_by_educational_attainment", "poverty", "poverty_rate_by_education", "poverty_rate_by_employment_and_sex", "income_by_household_type", "veterans_by_war", "veterans_by_age", "veterans_by_race")):
    for sheet in dataframes:
        if sheet == "General Info":
            pass
        else:
            pass

    '''with open(file_loc, 'w') as file:
        file.write(", ".join([i.replace('_', ' ').title() for i in singles]) + "\n")
        for i in states:
            string = ""
            for attr in singles:
                string += str(getattr(i, attr)) + ", "
            file.write(string.rstrip(", ") + "\n")'''


def rearrange(lis:list) -> list:
    pass


class StatePopulation(object):
    def __init__(self, state_name: str, population_2021: int, growth_2021: float, population_2018: int, census_2010: int, growth_since_2010: float, percent_of_US: float, density: int):
        self.state_name = state_name
        self.population_2021 = population_2021
        self.growth_2021 = growth_2021
        self.population_2018 = population_2018
        self.census_2010 = census_2010
        self.growth_since_2010 = growth_since_2010
        self.percent_of_US = percent_of_US
        self.density = density
        self.link = f"https://worldpopulationreview.com/states/{self.state_name.replace(' ','-').lower()}-population"
        self.graduation_rate = None
        self._getData()

    def _getData(self):
        tables = get_tables_from_web(self.link)
        if len(tables) != 13:
            raise ValueError(f"{self.county_name}'s webpage: {self.link} does not have 14 tables")
        else:
            self.race_data = tables[0]
            self.household_families = tables[1]
            self.household_types = tables[2]
            self.education_attained = tables[3]
            self.education_attained_by_race = tables[4]
            self.earnings_by_educational_attainment = tables[5]
            self.poverty = tables[6]
            self.poverty_rate_by_education = tables[7]
            self.poverty_rate_by_employment_and_sex = tables[8]
            self.income_by_household_type = tables[9]
            self.veterans_by_war = tables[10]
            self.veterans_by_age = tables[11]
            self.veterans_by_race = tables[12]

    def lower(self):
        return self.state_name.lower()

    def upper(self):
        return self.state_name.upper()

    @staticmethod
    def from_web(link: str):
        df = get_tables_from_web(link)[-1]
        return [StatePopulation(row["State"], row["2021 Pop."], row["2021 Growth"], row["2018 Pop."], row["2010 Census"], row["Growth Since 2010"], row["% of US"], row["Density (p/mi²)"]) for index, row in df.iterrows()]


class CountyPopulation(object):
    STATE_DICTIONARY = {'Alabama': 'AL', 'Alaska': 'AK', 'American Samoa': 'AS','Arizona': 'AZ','Arkansas': 'AR','California': 'CA','Colorado': 'CO','Connecticut': 'CT','Delaware': 'DE','District of Columbia': 'DC','Florida': 'FL','Georgia': 'GA','Guam': 'GU','Hawaii': 'HI','Idaho': 'ID','Illinois': 'IL','Indiana': 'IN','Iowa': 'IA','Kansas': 'KS','Kentucky': 'KY','Louisiana': 'LA','Maine': 'ME','Maryland': 'MD','Massachusetts': 'MA','Michigan': 'MI','Minnesota': 'MN','Mississippi': 'MS','Missouri': 'MO','Montana': 'MT','Nebraska': 'NE','Nevada': 'NV','New Hampshire': 'NH','New Jersey': 'NJ','New Mexico': 'NM','New York': 'NY','North Carolina': 'NC','North Dakota': 'ND','Northern Mariana Islands': 'MP','Ohio': 'OH','Oklahoma': 'OK','Oregon': 'OR','Pennsylvania': 'PA','Puerto Rico': 'PR','Rhode Island': 'RI','South Carolina': 'SC','South Dakota': 'SD','Tennessee': 'TN','Texas': 'TX','Utah': 'UT','Vermont': 'VT','Virgin Islands': 'VI','Virginia': 'VA','Washington': 'WA','West Virginia': 'WV','Wisconsin': 'WI','Wyoming': 'WY'}

    def __init__(self, county_name:str, state:str, population_2021:int, population_2010:int, growth_since_2010:float):
        self.county_name = county_name
        self.state = state
        self.population_2021 = population_2021
        self.population_2010 = population_2010
        self.growth_since_2010 = growth_since_2010
        self.link = f"https://worldpopulationreview.com/us-counties/{self.STATE_DICTIONARY[state].lower()}/{county_name.replace(' ', '-').lower()}-population"
        self._getData()

    def _getData(self):
        tables = get_tables_from_web(self.link)
        if len(tables) != 14:
            raise ValueError(f"{self.county_name}'s webpage: {self.link} does not have 14 tables")
        else:
            self.growth_data = tables[0]
            self.race_data = tables[1]
            self.household_families = tables[2]
            self.household_types = tables[3]
            self.education_attained = tables[4]
            self.education_attained_by_race = tables[5]
            self.earnings_by_educational_attainment = tables[6]
            self.poverty = tables[7]
            self.poverty_rate_by_education = tables[8]
            self.poverty_rate_by_employment_and_sex = tables[9]
            self.income_by_household_type = tables[10]
            self.veterans_by_war = tables[11]
            self.veterans_by_age = tables[12]
            self.veterans_by_race = tables[13]

    @staticmethod
    def from_web(link:str):
        df = get_tables_from_web(link)[-1]
        return [CountyPopulation(row["County Name"], row["State"], row["2021 Population"], row["2010 Population"], row["Growth (since 2010)"]) for index, row in df.iterrows()]


if __name__ == "__main__":
    countypop = CountyPopulation.from_web("https://worldpopulationreview.com/us-counties")
    statepop = StatePopulation.from_web("https://worldpopulationreview.com/states")
    statepop = add_state_graduation_rates(statepop, "https://worldpopulationreview.com/state-rankings/high-school-graduation-rates-by-state")
    states_to_csv(statepop, add_data_dir("Education/state_data.csv"))
