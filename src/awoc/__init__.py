"""
--------------------------------------------------------
*** A WORLD OF COUNTRIES ***
--------------------------------------------------------
A comprehensive library API to retrieve collections of data
about continents & countries,as defined by the ISO Standard 3166-1.

Author: Luca Grandicelli <https://github.com/lucagrandicelli>
Version: 1.0.0
Released under MIT license <https://github.com/lucagrandicelli/a-world-of-countries-py/blob/master/LICENSE>
Heavily based on pydash <https://github.com/dgilland/pydash>
"""

# Importing the standard library os module.
import os.path

# Importing the standard library json module.
import json

# Importing the pydash module.
import pydash

# Sys
import sys
"""
--------------------------------------------------------
The AWOC (A World of Countries) class.

This library relies on a central world.json (Global World Object Data)
file which includes all the informations about continents and countries.
All the several methods included in this class just perform dynamic
filtering of such data.
--------------------------------------------------------

Index
- CONTINENTS METHODS
- COUNTRIES METHODS
"""


class AWOC:
    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)


    # The class constructor.
    # Here we set up some basic properties and import the main Global World Object Data json file (GWOD).
    def __init__(self):

        # Absolute dir the script is in
        self._script_dir = os.path.dirname(__file__)

        # The path to the Global World Object Data file.
        self._relative_GWOD_path = 'data/world.json'

        # Building GWOD full relative path.
        self._GWOD_path = self.resource_path(self._relative_GWOD_path)

        # Km2 to Ml2 Conversion Factor: 1km2 = 0.621371 ml2
        self._km2_to_ml2_conv_fac = 0.621371

        # Ml2 to Km2 Conversion Factor: 1Ml2 = 2.58999 Km2
        self._ml2_to_km2_conv_fac = 2.58999

        # Setting up the limit of units after which a float number must be truncated.
        self._decimal_floor = 2

        try:
            # Reading & parsing the Global World Object Data json file.
            with open(self._GWOD_path, "r") as json_file:
                self._GWOD = json.load(json_file)

        except:

            # Raise exception.
            raise FileNotFoundError(
                'Unable to initialize the AWOC class. Global World Data Object json file not found.')

    """
    --------------------------------------------------------
    CONTINENTS METHODS
    List of all AWOC methods about world continents.
    --------------------------------------------------------
    Index
    1. get_continents_list(): a list of continent names.
    2. get_continents(): a list of continent objects.
    --------------------------------------------------------
    """

    # 1. This method returns a list of continent names as strings.
    def get_continents_list(self):

        # Filter list of continents from the GWOD
        continents_list = list(set(
            [cn['Continent Name'] for cn in self._GWOD]))

        # Sort it alphabetically
        continents_list.sort()

        # Return list
        return continents_list

    # 2. This method returns a list of continent objects.
    # A single continent is described as: {"Continent Code": [String], "Continent Name": [String]}
    def get_continents(self):

        # 1. Map the GWOD to extract only the continents data.
        # 2. Make the results unique by continent code.
        # 3. Sort the resulting collection by continents code.

        continents = pydash.sort_by(
            pydash.uniq_by(
                pydash.map_(self._GWOD, lambda i: pydash.pick(
                    i, ['Continent Code', 'Continent Name'])),
                'Continent Code'),
            'Continent Name')

        # Return continent objects.
        return continents

    """
    --------------------------------------------------------
    COUNTRIES
    List of all AWOC methods about world countries.
    --------------------------------------------------------
    Index
    1. get_countries(): all countries data.
    2. get_country_data(country_name): the whole data package for a specified country.
       It can also return a specific key field, if exists, returning a list /w a single value.
    3. get_countries_list(): a list of country names.
    4. get_countries_list_of(continent_name): a list of country names for a specific continent.
    5. get_countries_data_of(continent_name): a list of country objects for a specific continent.
    6. get_country_ISO2(country_name): the ISO2 code for the specified country.
    7. get_country_ISO3(country_name): the ISO3 code for the specified country.
    8. get_country_TLD(country_name): the Top Level Domain (TLD) for the specified country.
    9. get_country_FIPS(country_name): the FIPS country code for the specified country.
    10. get_country_ISO_numeric(country_name): the ISO Numeric code for the specified country.
    11. get_country_geo_name_ID(country_name): the GEO Name ID for the specified country.
    12. get_country_E164(country_name): the E164 code for the specified country.
    13. get_country_phone_code(country_name): the Phone Code for the specified country.
    14. get_country_continent_name(country_name): the continent data the specified country belongs to.
    15. get_country_continent_code(country_name): the continent code the specified country belongs to.
    16. get_country_capital_city(country_name): the capital city of the specified country.
    17. get_country_time_zone(country_name): a time zone value for the specific country.
    18. get_country_currency_name(country_name): the currency name for the specified country.
    19. get_countries_list_by_currency(currency_name, continent_name = false):
        a list of countries filtered by a specific currency.
    20. get_countries_data_by_currency(currency_name, continent_name = false):
        one or multiple country object data for a specific currency.
    21. get_country_languages(country_name): a list of languages for the specific country.
    22. get_country_area(country_name, unit = 'km2'): a non formatted value for the country area in km2 or mi2.
    --------------------------------------------------------

    1. get_countries()
    This method extracts all the countries data from the GWOD.
    It performs an additional sort to ensure the correct result alphabetical order,
    regardless of the GWOD json objects order (which might fail).
    """

    def get_countries(self):
        return pydash.sort_by([c for c in self._GWOD], ['Country Name'])

    """
    2. get_country_data(country_name, field=False)
    This method returns a single country object data.
    If a 'field' parameter is specified, then the method will return its value.
    For a list of available fields, please check the example below:

    "Country Name": "Italy",
    "ISO2": "IT",
    "ISO3": "ITA",
    "TLD": "it",
    "FIPS": "IT",
    "ISO Numeric": 380,
    "GeoNameID": 3175395,
    "E164": 39,
    "Phone Code": 39,
    "Continent Name": "Europe",
    "Continent Code": "eu",
    "Capital": "Rome",
    "Time Zone in Capital": "Europe/Rome",
    "Currency Name": "Euro",
    "Languages": "Italian (official), German (parts of Trentino-Alto Adige region are predominantly German-speaking), French (small French-speaking minority in Valle d'Aosta region), Slovene (Slovene-speaking minority in the Trieste-Gorizia area)",
    "Area KM2": 301230
    """

    def get_country_data(self, country_name, field=False):

        # Parameters validation.
        if (not country_name):
            raise NameError('You must provide a country name.')

        # Sanitizing input fields.
        country_name = self._sanitize_country_name(country_name)

        # Fetching full country data.
        country_data = pydash.find(self._GWOD, [
            'Country Name',
            country_name.strip()
        ])

        # Let's make sure the country_data isn't empty.
        if (not country_data):

            # Build error message.
            error_msg = ('The specified Country Name "{}" does not exist.').format(
                country_name)

            # Raise error.
            raise NameError(error_msg)

        # If no key field has been provided, return the whole data object.
        if (not field or not isinstance(field, str)):
            return country_data

        # If the provided field exists, return it. Otherwise throw an error.
        if (field in country_data):

            # The language field must be returned as a list.
            return country_data[field].split(',') if 'Languages' == field else country_data[field]

        else:

            # Raise error.
            raise ValueError('The specified field key does not exists.')

    """
    3. get_countries_list()
    This method returns a list of country names sorted alphabetically.
    """

    def get_countries_list(self):

        # Let's build a list of country names.
        countries = [c['Country Name'] for c in self._GWOD]

        # Let's sort the list regardless of the GWOD order.
        countries.sort()

        # Return the list.
        return countries

    """
    4. get_countries_list_of(continent_name)
    This method returns a list of country names sorted alphabetically for a specific continent.
    """

    def get_countries_list_of(self, continent_name):

        # Parameters validation.
        if (not continent_name):
            raise NameError(
                'You must provide a continent name in order to use the get_countries_list_of() method.')

        # Sanitizing continent name
        continent_name = self._sanitize_continent_name(continent_name)

        # Filtering country objects for the specified continent.
        country_list = [
            country['Country Name'] for country in self._GWOD if country['Continent Name'] == continent_name.strip()]

        # If the returned data is an empty list, a wrong continent name has been provided.
        if (not country_list):

            # Build error message.
            error_msg = '"{}" is not a valid continent name'.format(
                continent_name)

            # Raise error.
            raise ValueError(error_msg)

        # Sort resulting list by Country Name.
        country_list.sort()

        # Return list.
        return country_list

    # 5. get_countries_data_of(continent_name)
    # This method returns a list of country objects alphabetically sorted per each country name for a specific continent.
    def get_countries_data_of(self, continent_name):

        # Parameters validation.
        if (not continent_name):
            raise NameError(
                'You must provide a continent name in order to use the get_countries_data_of() method.')

        # Sanitizing continent name
        continent_name = self._sanitize_continent_name(continent_name)

        country_data_list = [
            country for country in self._GWOD if country['Continent Name'] == continent_name.strip()]

        # Returning data.
        return pydash.sort_by(country_data_list, ['Country Name'])

    # 6. This method returns the ISO2 code for the specified country.
    def get_country_ISO2(self, country_name):
        return self.get_country_data(country_name, 'ISO2')

    # 7. This method returns the ISO3 code for the specified country.
    def get_country_ISO3(self, country_name):
        return self.get_country_data(country_name, 'ISO3')

    # 8. This method returns the Top Level Domain code for the specified country.
    def get_country_TLD(self, country_name):
        return self.get_country_data(country_name, 'TLD')

    # 9. This method returns the FIPS (Federal Information Processing Standard Publication) code for the specified country.
    def get_country_FIPS(self, country_name):
        return self.get_country_data(country_name, 'FIPS')

    # 10. This method returns the ISO Numeric code for the specified country.
    def get_country_ISO_numeric(self, country_name):
        return self.get_country_data(country_name, 'ISO Numeric')

    # 11. This method returns the E164 code for the specified country.
    def get_country_geo_name_ID(self, country_name):
        return self.get_country_data(country_name, 'GeoNameID')

    # 12. This method returns the E164 code for the specified country.
    def get_country_E164(self, country_name):
        return self.get_country_data(country_name, 'E164')

    # 13. This method returns the Phone Coden code for the specified country.
    def get_country_phone_code(self, country_name):
        return self.get_country_data(country_name, 'Phone Code')

    # 14. This method returns the continent name the specified country belongs to.
    def get_country_continent_name(self, country_name):
        return self.get_country_data(country_name, 'Continent Name')

    # 15. This method returns the continent code the specified country belongs to.
    def get_country_continent_code(self, country_name):
        return self.get_country_data(country_name, 'Continent Code')

    # 16. This method returns the Capital City for the specified country.
    def get_country_capital_city(self, country_name):
        return self.get_country_data(country_name, 'Capital')

    # 17. This method returns the time zone value for a specific country.
    def get_country_time_zone(self, country_name):
        return self.get_country_data(country_name, 'Time Zone in Capital')

    # 18. This method returns the currency name for the specified country.
    def get_country_currency_name(self, country_name):
        return self.get_country_data(country_name, 'Currency Name')

    # 19. This function return a list of countries filtered by the specific currency value.
    # An additional parameter 'continent_name' is available to limit the search to a specific continent.
    def get_countries_list_by_currency(self, currency_name, continent_name=False):

        # Parameters validation.
        if (not currency_name):
            raise NameError(
                'You must provide a currency name in order to use the get_countries_data_of() method.')

        # Setting up conditions.
        conditions = {'Currency Name': currency_name.strip()}

        # Checking if a continent name has been provided.
        if continent_name:

            # Sanitizing input fields.
            continent_name = self._sanitize_continent_name(continent_name)

            # Trimming and assigning value to the conditions object.
            conditions['Continent Name'] = continent_name.strip()

        # Filtering GWOD and return.
        countries = pydash.filter_(self._GWOD, conditions)
        countries = [country['Country Name'] for country in countries]
        countries.sort()

        # Returning data.
        return countries

    """
    20. This function return a list of country data filtered by the specific currency value.
    An additional parameter 'continent_name' is available to limit the search to a specific continent.
    """

    def get_countries_data_by_currency(self, currency_name, continent_name=False):

        # Parameters validation.
        if (not currency_name):
            raise NameError(
                'You must provide a currency name in order to use the get_countries_data_by_currency() method.')

        # Setting up conditions.
        conditions = {'Currency Name': currency_name.strip()}

        # Checking if a continent name has been provided.
        if continent_name:

            # Sanitizing input fields.
            continent_name = self._sanitize_continent_name(continent_name)

            # Trimming and assigning value to the conditions object.
            conditions['Continent Name'] = continent_name.strip()

        # Filtering GWOD and return.
        countries = pydash.filter_(self._GWOD, conditions)
        countries = pydash.sort_by(countries, ['Country Name'])

        return countries

    # 21. This method returns a verbose string of languages for the specified country.
    def get_country_languages(self, country_name):

        # Parameters validation.
        if (not country_name):
            raise NameError('You must provide a country name.')

        # Sanitizing input fields.
        country_name = self._sanitize_country_name(country_name)

        # Get country language code(s)
        languages = [country['Languages']
                     for country in self._GWOD if country['Country Name'] == country_name.strip()]

        # If the returned data is an empty array, a wrong country name has been provided.
        if not languages:

            # Build error message.
            error_msg = '"{}" is not a valid country name.'.format(
                country_name)

            # Return error message.
            raise ValueError(error_msg)

        # Return languages.
        return ''.join(languages)

   # 22. This method returns the geographic area in km2 || mi2 for the specified country.
   # The return value is unformatted. Parse it as you wish.
    def get_country_area(self, country_name, unit='km2'):

        # Parameters validation.
        if (not country_name):
            raise NameError('You must provide a country name.')

        # Sanitizing input fields.
        country_name = self._sanitize_country_name(country_name)

        # Get country Area in Km2
        country_area = [country['Area KM2']
                        for country in self._GWOD if country['Country Name'] == country_name.strip()]

        # If the returned data is an empty array, a wrong country name has been provided.
        if not country_area:

            # Build error message.
            error_msg = '"{}" is not a valid country name.'.format(
                country_name)

            # Return error message.
            raise ValueError(error_msg)

        # Convert returned Area to float.
        country_area = float(''.join(country_area))

        # Return converted value if needed.
        return self._km2_to_ml2(country_area) if unit == 'mi2' else round(country_area, self._decimal_floor)

    """
    --------------------------------------------------------
    HELPERS
    A list of methods used to perform internal operations.
    --------------------------------------------------------
    Index
    1. _km2_to_ml2(km2_val): convert square kilometers to square miles.
    2. _miles2_to_km2(ml2_val): convert square miles to square kilometers.
    3. _sanitize_continent_name(input_field): sanitizes input values for continent names.
    4. _sanitize_country_name(input_field): sanitizes input values for country names.
    --------------------------------------------------------
    """

    # 1. This helper converts square kilometers to square miles
    def _km2_to_ml2(self, km2_val):
        return round(float(km2_val * self._km2_to_ml2_conv_fac), self._decimal_floor)

    # 2. This helper convert square miles to square kilometers
    def _ml2_to_km2(self, ml2_val):
        return round(float(ml2_val * self._ml2_to_km2_conv_fac), self._decimal_floor)

    # 3. This method sanitizes any string used as continent name.
    def _sanitize_continent_name(self, input_field):

        # Let's break down the input data into a list of words.
        words_list = str(input_field).split(' ')

        # Let's lowercase all words.
        words_list = [word.lower() for word in words_list]

        # Let's capitalize all words.
        words_list = [word.capitalize() for word in words_list]

        # Return sanitized string.
        return ' '.join([word for word in words_list])

    # 4. This method sanitizes any string used as country name.
    def _sanitize_country_name(self, input_field):

        # Some words must not be included in any kind of string transformation.
        excluded_words = ['of', 'and', 'the', '.', 'U.S.']

        # Let's break down the input data into a list of words.
        words_list = str(input_field).split(' ')

        # Looping each word
        for (index, word) in enumerate(words_list):

            # Check whether the current word is in the excluded list.
            if word not in excluded_words:

                # Let's lowercase the current word.
                words_list[index] = word.lower()

                # Check if the current word is a multi-word with the '-' char in it.
                if ('-' in word):

                    # Let's split the inner word into multiple chunks.
                    inner_words = word.split('-')

                    # Let's capitalize each part of the multi-word.
                    inner_words = [i.capitalize() for i in inner_words]

                    # Let's rebuild the splitted inner word.
                    words_list[index] = '-'.join([i for i in inner_words])

                else:
                    # Let's capitalize the current word.
                    words_list[index] = word.capitalize()

        # Return sanitized string.
        return ' '.join([word for word in words_list])
