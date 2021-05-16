# ./leaguepedia_scraping.py 
# This program requests information on every competitive games played on the patches 11.1 to 11.9 
from leaguepedia_wrapper import LeaguePediaWrapper
from acs_wrapper import ACSWrapper
import pymongo
import time, sys, json

# "Wrapper" to request on LeaguePedia 
lpedia_wrapper = LeaguePediaWrapper()
acs_wrapper = ACSWrapper()

def clone_matches_stats(lpedia_match_list, match_stats_db):
    """Cloning matches from the match list 
    returned by the function "clone_leaguepedia_matches()
    into a MongoDB database

    Args:
        lpedia_match_list (Leaguepedia match list): [description]
        match_stats_db ([type]): [description]
    """
    
    i = 0
    for tournament in lpedia_match_list.keys():
        for match in lpedia_match_list[tournament]:
            # Parsing URL
            parsed_url = acs_wrapper.parse_mh_url(match["MatchHistory"])
            
            if parsed_url != "not_valid":
                # Match data
                match_stats = acs_wrapper.get_match_stats(parsed_url, tournament)
                match_timeline = acs_wrapper.get_match_timeline(parsed_url, tournament)
                
                # Merging dict 
                to_insert = {}
                to_insert["match_id"], to_insert["match_stats"], to_insert["match_timeline"] = parsed_url["gameId"], match_stats, match_timeline

                # Inserting in database
                collection = match_stats_db[str(tournament)]
                x = collection.update_one({"match_id":parsed_url["gameId"]}, {"$set":to_insert}, upsert=True)

                # Console 
                print('Cloning ACS data ... [{0:.4f}%][{1: ^60}]'.format(i/len(lpedia_match_list)*100, tournament), end="\r", flush=True)
        i += 1
    
    sys.stdout.flush()
    print("\n[Match statistics and timeline successfully cloned !")

def clone_leaguepedia_matches():
    """Creates a special list of JSON objects of matches
    with match history links

    Returns:
        A list of JSON Objects containing matches list 
        It looks like this : 
            [{'Team1': 'Team 7AM', 'Team2': 'KV Mechelen Esports', 'Patch': '11.1', 'DateTime UTC': '2021-01-18 19:16:00', \
            'MatchHistory': 'https://matchhistory...', 'DateTime UTC__precision': '0'}, {another one}, ...]
    """
    # Getting leagues names 
    tournaments_names = lpedia_wrapper.get_tournaments_names(date='2021-01-01 00:00:00', limit='max')
    tournaments_names = lpedia_wrapper.parse(tournaments_names)

    # Cargoquery bug : "#" character can't be used in a query (results in a error)
    # so the Tournament "OTBLX..." must be removed from the tournament names list 
    for t in tournaments_names:
        if "OTBLX 2021 Spring Community Cup #1" in t["Tournament"]:
            tournaments_names.remove(t)
 
    leaguepedia_matches = {}
    # Cloning Leaguepedia data
    for index, t in enumerate(tournaments_names):
        # Console 
        print('Getting match list ... [{0:.2f}%][{1: ^60}]'.format(index/len(tournaments_names)*100, t["Tournament"]), end="\r", flush=True)

        # Getting the match list 
        match_list = lpedia_wrapper.get_match_history_by_tournament(t["Tournament"], limit='max')
        # Parsing match list 
        match_list = lpedia_wrapper.parse(match_list)

        leaguepedia_matches[t["Tournament"]] = match_list 
    
    sys.stdout.flush()
    print("\n[Matches list completed]")

    return leaguepedia_matches

def main():

    # Initializing MongoDB Client 
    mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
    matches_stats_db = mongo_client["ClonedACS"]

    # Getting back every match history link
    leaguepedia_matches = clone_leaguepedia_matches()
    # Cloning stats & timeline for each match
    clone_matches_stats(leaguepedia_matches, matches_stats_db)
    

if __name__ == "__main__":
    main()

