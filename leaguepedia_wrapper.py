# ./leaguepedia_wrapper.py
# A tool class to process things with the Leaguepedia API
import mwclient, json

class LeaguePediaWrapper:
    """This class is a container for functions and stuff
    related to the LeaguePedia API such as requests, parsing, etc
    """

    def __init__(self):
        self.site = mwclient.Site('lol.fandom.com', path='/')

    def get_league_names(self, is_official=True, limit='max'):
        """Requests all leagues

        Args:
            is_official (bool, optional): only requests leagues that are official if true, unofficial if false. 
            limit (str, optional): max number of responses

        Returns:
            Parsed JSON with all leagues names
        """
        
        response = self.site.api('cargoquery',
            limit = limit, 
            tables = "Leagues",
            fields = "League_Short",
            where = "IsOfficial='Yes'" if is_official else "IsOfficial='No'"
        )

        return json.dumps(response)

    def parse(self, unparsed):
        """Parses the raw response of the Leaguepedia API
        It deletes the  ""limits": {"cargoquery": 500}" and "title" parts of the response

        Args:
            unparsed (str): and API reponse string

        Returns:
            (list) : a list with all the strings 
        """
        
        # List with parsed data
        # Example : [{"a":"b"}, {"c":"d"}] 
        parsed_list = list()

        # Converting to a list of JSON sets
        uncompleted_parse = json.loads(unparsed)['cargoquery']

        for item in uncompleted_parse:
            for value in item.values():
                parsed_list.append(json.loads(json.dumps(value)))

        return parsed_list
    
    def get_tournaments_names(self, date, limit='max'):
        """Returns every tournament name where there was games 
        after the required date
        

        Args:
            date (DateTime): Minimum date for a tournament
            limit (str, optional): Max responses. Defaults to 'max'.

        Returns:
            Parsed JSON with all tournament names, ordered by date
        """

        response = self.site.api('cargoquery', 
            limit = 'max',
            tables = "ScoreboardGames=SG",
            fields = "SG.Tournament",
            where = f'SG.DateTime_UTC >= "{date}"' ,
            group_by = "SG.Tournament",
            order_by = "SG.DateTime_UTC"
        )

        return json.dumps(response)


    def get_match_history_by_tournament(self, tournament, limit='max'):
        """Returns informatinos and a match history link for every
        match held in the tournament

        Args:
            tournament (str): the Leaguepedia tournament name
            limit (str, optional): Max responses. Defaults to 'max'.

        Returns:
            Parsed JSON with every match held in the tournament
        """
        
        response = self.site.api('cargoquery',
            limit = limit,
            tables = "ScoreboardGames=SG",
            fields = "SG.Team1, SG.Team2, SG.Patch, SG.DateTime_UTC, SG.MatchHistory",
            where = f'SG.Tournament="{tournament}"'
        )
        # ne marche pas parce que LCK CL contient LCK par exemple 
        
        return json.dumps(response)