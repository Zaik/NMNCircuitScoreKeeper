#Given a CSV with format:
#entrant_id, recent_tag, points
#and a tourament and event slug
#Calculates an updated CSV in the same format

import math
import csv
import argparse
import SREUinterface

#The pool of points winnable for placing in a tournament is = players * v
point_multiplier = 4

#The multiplier for how much you win if you beat an opponent = their_score * v
win_multiplier = 0.25

#Prize split
#Described as a list of decimal numbers, should add up to ~1
#each item in the list is how many players, counting from 1st place to last, get that fraction of the pot
#if the number of players is smaller than the prize split list, then the remainder of the list is applied again
#from the top of the list. (example, if your prize split goes to 32 people with only 16 people in the tournament
#1st place would win 1st + 17th prize)
prize_list = []

#we'll cheat though because this is annoying to do manually
first_price = 0.2

#The algorithm: first place gets first prize
#The placing after that gets half the price
#and so ons
def generate_prize_list(start_price, start_placing, start_placers, start_pool):
	placing = start_placing
	placers = start_placers
	price = start_price
	total_pool = start_pool
	result_list = []
	while (total_pool < 0.99):
		if (placing > 3 and placing % 2 == 0):
			placers *= 2
		result_list += [price] * placers
		total_pool += price * placers
		price /= 2
		placing += 1
	#Check how close to 1 we are
	return result_list

prize_list = [0.25, 0.20, 0.15, 0.10] + generate_prize_list(0.05, 4, 1, 0.7)

def obtain_placing_points(placing, num_players):
	placing -= 1
	pool = num_players * point_multiplier
	points = 0
	while placing < num_players:
		points += prize_list[placing % len(prize_list)] * pool
		placing += len(prize_list)
	return points

def calculate_new_csv(old_dict, players_info, sets_info):
	print("Calculating new scores...")
	player_dict = {}
	for player in players_info:
		player_dict[player['id']] = player
		if not player['id'] in old_dict:
			#pretend the player existed all along
			old_dict[player['id']] = {'score' : 0.0, 'tag' : player['tag']}
	new_dict = old_dict.copy()
	for set in sets_info:
		if set['no_contest']:
			continue
		winner = old_dict[set['winner']]
		loser = old_dict[set['loser']]
		loser_score = loser['score']
		loser_score_minimum = obtain_placing_points(player_dict[set['loser']]['seed'], len(players_info)) / 4.0
		if loser_score < loser_score_minimum:
			loser_score = loser_score_minimum
		winner_gains = loser_score * win_multiplier
		if winner_gains > loser_score_minimum * 4:
			winner_gains = loser_score_minimum * 2
		new_dict[set['winner']]['score'] += winner_gains
	for player in players_info:
		placing_gains = obtain_placing_points(player['placing'], len(players_info))
		new_dict[player['id']]['score'] += placing_gains
	print("Done")
	return new_dict

def read_csv_file(file):
	csv_dict = {}
	if file == "":
		return csv_dict
	print("Reading CSV file...")
	with open(file) as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			csv_dict[row['id']] = {'score' : float(row['score']), 'tag' : row['tag']}
	print("Done")
	return csv_dict

def write_csv_file(file, dict):
	print("Writing CSV file")
	if file != "":
		with open(file, 'w') as csvfile:
			csvfile.write("id,score,tag\n")
			for player in dict:
				csvfile.write(player + "," + str(dict[player]['score']) + "," + dict[player]['tag'] + "\n")
	else:
		for player in dict:
			print(player + "," + str(dict[player]['score']) + "," + dict[player]['tag'] + "\n")
	print("Done")
			
def execute(old_csv, new_csv, tournament_slug, event_name):
	old_dict = read_csv_file(old_csv)
	(set_infos, player_infos) = SREUinterface.get_tournament_info(tournament_slug, event_name)
	new_dict = calculate_new_csv(old_dict, player_infos, set_infos)
	write_csv_file(new_csv, new_dict)

argparse = argparse.ArgumentParser(description = "Generate an updated CSV of player scores based on a tournament event and an old CSV")
argparse.add_argument('tournament_slug', nargs ='?', default=None, help = "Tournament slug to analyze")
argparse.add_argument('event_name', nargs ='?', default=None, help = "slug of event in tournament to analyze")
argparse.add_argument('old_csv', nargs ='?', default=None, help = "The CSV containing the previous player IDs and scores and tags")
argparse.add_argument('new_csv', nargs ='?', default=None, help = "The CSV that will contain the newly calculated player IDs and scores and tags (if omitted, outputs to stdout)")

args = argparse.parse_args()
old_csv = args.old_csv
new_csv = args.new_csv
slug = args.tournament_slug
event = args.event_name

if old_csv == None:
	old_csv = input("Enter old_csv file (blank for no file): ")
if new_csv == None:
	new_csv = input("Enter name of new csv file to create (blank to print to stdout): ")
if slug == None:
	slug = input("Enter the tournament slug: ")
if event == None:
	event = input("Enter the event slug: ")

print("Running...")
execute(old_csv, new_csv, slug, event)
			  