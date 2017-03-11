#This is the file responsible for reading data from smash.gg

#You should be able to obtain a COMPLETE list of simplified matches
#and a COMPLETE list of simplified final standings

import sys
import pysmash

smash = pysmash.SmashGG()

#Given a the slug for a tournament, obtain the IDs for each phase_group (bracket)
#in that tournament
def get_sets_info(tournament_name, event_name):
	print("Obtaining set info...")
	sets = smash.tournament_show_sets(tournament_name, event_name)
	print("Done")
	return [{'winner'     : str(set['winner_id']),
			 'loser'      : str(set['loser_id']),
			 'no_contest' : set['entrant_1_score'] < 0 or set['entrant_2_score'] < 0}
			 for set in sets if set['entrant_1_score'] != None]
	
#Given a phase_group ID, obtain the sets, entrants, standings and seeding for that group
def get_players_info(tournament_name, event_name):
	print("Obtaining player info...")
	players = smash.tournament_show_players(tournament_name, event_name)
	print("Done")
	return [{'id'      : str(player['entrant_id']),
			 'tag'     : player['tag'],
			 'seed'    : player['seed'],
			 'placing' : player['final_placement']}
			 for player in players]

def get_tournament_info(tournament_name, event_name):
	return (get_sets_info(tournament_name, event_name),
			get_players_info(tournament_name, event_name))
