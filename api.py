import requests
from requests.structures import CaseInsensitiveDict
from CONF import COORDS_KEY, COORDS_KEY_WEATHER
from utilities import rename_country


class API(object):
    """
    management class for the API functionality of the app
    """
    def __init__(self):
        self.loc_list = []
        self.max_temp = {}
        self.min_temp = {}
        self.humidity = {}
        self.status = {}
        self.location = ""
        self.op = -1

    def get_loc(self, location):
        """
        get coords for the provided location
        :param location: a string describing the searched location
        :return:
        """
        self.location = location

        # api url
        url = "https://www.mapquestapi.com/geocoding/v1/" \
              "address?key=%s" % COORDS_KEY

        # setting up headers
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"

        # setting up requested data for the program
        data = '{"location": "%s","options": {"thumbMaps": true}}' % location

        # request
        try:
            resp = requests.post(url, headers=headers, data=data.encode('utf-8'))
        except ConnectionError:
            return False

        if resp.status_code != 200:
            return False

        resp_dict = resp.json()
        self._filter_relevant_locations(resp_dict["results"][0]["locations"],
                                        location)

        return len(self.loc_list) != 0

    def _filter_relevant_locations(self, location_list, location):
        """
        Isolate only the relevant results that return from the api
        :param location_list: the list of returned values
        :param location: the location received by the user
        :return: filtered list
        """
        locations = [[loc["adminArea5"], loc["adminArea1"],
                      loc["adminArea3"], loc["adminArea4"], loc["displayLatLng"]]
                     for loc in location_list]

        # Isolating the valid locations
        for loc in locations:
            for attr in loc[:-1]:
                if attr.lower() == location.lower():
                    self.loc_list.append(loc)
                    break
                elif rename_country(attr).lower() == location.lower():
                    loc[1] = rename_country(location).title()
                    self.loc_list.append(loc)
                    break

        return self.loc_list

    def choose_city(self, index):
        """
        Given the chosen location by the user, get the weather data
        :param index: the chosen location from self.loc_list
        :return: self after data added.
        """
        self.op = index
        if len(self.loc_list) == 0:
            raise Exception("no valid location available")

        lat = self.loc_list[index][4]["lat"]
        lon = self.loc_list[index][4]["lng"]
        url = "https://api.openweathermap.org/data/2.5/" \
              "onecall?lat=%s&lon=%s&appid=" \
              "%s" % (lat, lon, COORDS_KEY_WEATHER)

        try:
            resp = requests.post(url, timeout=3)
        except ConnectionError:
            return False

        if resp.status_code != 200:
            return resp.status_code

        data_dict = resp.json()
        self._process_weather_response(data_dict)

        return self

    def _process_weather_response(self, data_dict):
        self.max_temp = {day: round(data["temp"]["max"] - 273.1, 2) for
                         day, data in enumerate(data_dict["daily"])}
        self.min_temp = {day: round(data["temp"]["min"] - 273.1, 2) for
                         day, data in enumerate(data_dict["daily"])}
        self.humidity = {day: data["humidity"] for
                         day, data in enumerate(data_dict["daily"])}
        self.status = {day: data["weather"][0]["main"] for
                       day, data in enumerate(data_dict["daily"])}


if __name__ == "__main__":
    api = API()
