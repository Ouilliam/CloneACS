# ./leaguepedia_wrapper.py
# A tool class to process things with the ACS API
import requests, json, simplejson

class ACSWrapper:
    """This class is a container for functions and stuff
    related to the LeaguePedia API such as requests, parsing, etc
    """
    
    def __init__(self):
        self.acs_stats_url = "https://acs.leagueoflegends.com/v1/stats/game/{}/{}?gameHash={}"
        self.acs_timeline_url = "https://acs.leagueoflegends.com/v1/stats/game/{}/{}/timeline?gameHash={}"
        
        # Loading & formating cookie
        cookies_file = open("cookies.txt", "r")
        self.cookies = cookies_file.read()
        self.cookies = {c.split("=")[0]:c.split("=")[1] for c in self.cookies.split(";")}

        # Files used to investigate when there is an error on request
        # or the Leaguepedia match history URL is not correct
        self.wrong_url = open("url_error_log.txt", "a+")
        self.wrong_request = open("response_error_log.txt", "a+")
    
    def parse_mh_url(self, mh_url):
        """Parses a match history URL to a dictionnary
        with relevant informations for a query on the ACS/Riot API

        Args:
            mh_url (str): a match history URL

        Returns:
            A dictionary containing the region, gameId and gameHash
        """
        # Preventing from LPL match history link and ensuring there is a gameHash
        if "lpl" not in mh_url and "?gameHash=" in mh_url:
            parsed_data = {}
            parsed_data["region"] = mh_url.split("/")[5]
            parsed_data["gameId"] = mh_url.split("/")[6].split("?gameHash=")[0]
            
            if "&amp" in mh_url:
                parsed_data["gameHash"] = mh_url.split("/")[6].split("?gameHash=")[1].split("&amp;tab=overview")[0]
            else:
                parsed_data["gameHash"] = mh_url.split("/")[6].split("?gameHash=")[1].split("tab=overview")[0]

            return parsed_data
        else:
            self.wrong_url.write(str(mh_url)+",\n")
            return "not_valid"

    def get_match_stats(self, parsed_url, tournament):
        """Requests match statistics from
        the parsed url

        Args:
            parsed_url (dict): a parsed URL dictionary (parsed with "parse_mh_url")
            tournament (str): the tournament name, used in case of error

        Returns:
            A JSON dictionnary with every stat
        """
        json_data = ""
        # Formating URL
        url = self.acs_stats_url.format(str(parsed_url["region"]), str(parsed_url["gameId"]), str(parsed_url["gameHash"]))
        
        try:
            response = requests.get(url ,cookies=self.cookies, timeout=10)
        except requests.exceptions.RequestException:
            print("Error when requesting")
        
        try:
            json_data = response.json()
        except simplejson.errors.JSONDecodeError:
            self.wrong_request.write("Match statistics response error : " + str(response) + " || " + "Tournament : " + tournament + " || " + "URL : " + str(parsed_url) + ",\n")

        return json_data

    def get_match_timeline(self, parsed_url, tournament):
        """Requests a match timeline from
        the parsed url
        
        Args:
            parsed_url (dict): a parsed URL dictionary (parsed with "parse_mh_url")
            tournament (str): the tournament name used in case of error

        Returns:
            A JSON dictionary with the timeline of the game    
        """
        json_data = ""
        # Formating URL
        url = self.acs_timeline_url.format(str(parsed_url["region"]), str(parsed_url["gameId"]), (str(parsed_url["gameHash"])))
        
        try:
            response = requests.get(url ,cookies=self.cookies, timeout=10)
        except requests.exceptions.RequestException:
            print("Error when requesting")
        
        try:
            json_data = response.json()
        except simplejson.errors.JSONDecodeError:
            self.wrong_request.write("Match timeline response error : " + str(response) + " || " + "Tournament : " + tournament + " || " + "URL : " + str(parsed_url) + ",\n")

        return json_data
        
