import numpy as np
from neupy import algorithms
from neupy.layers import *
import os as os
import requests as request
from bs4 import BeautifulSoup
from xlrd import open_workbook
import pickle as pickle
import tkinter as tk
from tkinter import *

class neural_network:
    def __init__(self, inputs, outputs):
        #Initialsies a gradient descent neural net, reshaping inputs and outputs        
        self.neural_network = algorithms.MinibatchGradientDescent((10, 20, 2), verbose = True, step = 0.1)
        inputs = np.array(inputs)
        outputs = np.array(outputs)
        self.X = np.reshape(inputs, (len(inputs), 10))
        self.Y = np.reshape(outputs, (len(outputs), 2))

    def train_network(self):
        #Trains the neural network
        self.neural_network.train(self.X, self.Y, epochs = 10000)

    def make_prediction(self, inputs):
        #Allows predictions to be made from user input. Returns result
        predictions = self.neural_network.predict(inputs)
        return predictions

class data_scraper:
    def __init__(self):
        self.elo_scores = []
        self.team_names = []
        self.team_and_elo = {}
        self.ratings_attack = {}
        self.ratings_midfield = {}
        self.ratings_defence = {}
        self.ratings_overall = {}
        self.match_teams = []
        self.match_records = []
        self.scores_as_classifications = []
        
        self.elo_url ="https://sinceawin.com/data/elo/league/div/e0"
        self.elo_page = request.get(self.elo_url)
        self.elo_soup = BeautifulSoup(self.elo_page.content, "html.parser")
        self.elo_soup.prettify()
        self.elo_tables = self.elo_soup.findChildren("tbody")
        self.elo_rows = self.elo_tables[0].findAll("tr")

        self.ratings_url = "https://www.fifaindex.com/teams/?league=13&order=desc"
        self.ratings_page = request.get(self.ratings_url)
        self.ratings_soup = BeautifulSoup(self.ratings_page.content, "html.parser")
        self.ratings_soup.prettify()
        self.ratings_tables = self.ratings_soup.findChildren("tbody")
        self.ratings_rows = self.ratings_tables[0].findAll("tr")

    def get_team_names(self):
        for row in self.elo_rows:
            cells = row.findAll("td")
            count = 0
            team_name = ""
            for cell in cells:
                if count == 1:
                    team_name = cell.text
                    team_name = self.team_name_normaliser(team_name)
                    self.team_and_elo[team_name] = 0
                if count == 2:
                    self.team_and_elo[team_name] = float(cell.text) / 10000
                count = count + 1

    def get_team_ratings(self):
        for row in self.ratings_rows:
            cells = row.findAll("td")
            count = 0
            team_name = ""
            for cell in cells:
                if count == 1:
                    team_name = cell.text
                    self.team_name_normaliser(team_name)
                    self.ratings_attack[team_name] = 0
                    self.ratings_midfield[team_name] = 0
                    self.ratings_defence[team_name] = 0
                    self.ratings_overall[team_name] = 0
                if count == 3:
                    self.ratings_attack[team_name] = float(cell.text) / 100
                if count == 4:
                    self.ratings_midfield[team_name] = float(cell.text) / 100
                if count == 5:
                    self.ratings_defence[team_name] = float(cell.text) / 100
                if count == 6:
                    self.ratings_overall[team_name] = float(cell.text) / 100
                count = count + 1
        return self.ratings_attack, self.ratings_midfield, self.ratings_defence, self.ratings_overall

    def get_match_history(self):
        wb = open_workbook('C:/Users/Jack/Documents/2017Results.xlsx')
        self.match_records = []
        self.match_teams = []
        for s in wb.sheets():
            for row in range(1, s.nrows - 1):
               col_names = s.row(1)
               teamPair = []
               count = 0
               for name, col in zip(col_names, range(2, 4)):
                   team_name  = (s.cell(row, col).value)
                   try :
                       team_name = str(team_name)
                   except : pass
                   
                   teamPair.append(team_name)
                   if count % 2 != 0:
                       self.match_teams.append(teamPair)
                   count = count + 1
               scorePair = []
               count = 0
               for name, col in zip(col_names, range(4, 6)):
                    score  = (s.cell(row, col).value)
                    try :
                        score = float(score) / 10
                    except : pass
                    scorePair.append((score))
                    if count % 2 != 0:
                        self.match_records.append(scorePair)
                    count = count + 1
            return self.match_records, self.match_teams

    def classify_scores(self):
        count = 0
        for record in self.match_records:
            if record[0] > record[1]:
                self.scores_as_classifications.append([0.99, 0.0])
            if record[0] == record[1]:
                self.scores_as_classifications.append([0.5, 0.5])
            if record[0] < record[1]:
                self.scores_as_classifications.append([0.0, 0.99])
            count = count + 1
        return self.scores_as_classifications

    def teams_present(self, first_team, second_team):
        found = 0
        for team in list(self.team_and_elo.keys()):
            if team == first_team or team == second_team:
                found = found + 1
            if found == 2:
                return True
        return False

    def generate_inputs(self):
        inputs = []
        outputs = []
        count = 0 
        for matches in self.match_teams:
                first_team = self.match_teams[count][0]
                second_team = self.match_teams[count][1]
                if self.teams_present(first_team, second_team):
                    first_team = self.team_name_normaliser(matches[0])
                    second_team = self.team_name_normaliser(matches[1])
                    match_data = []
                    match_data.append(self.team_and_elo[first_team])
                    match_data.append(self.ratings_attack[first_team])
                    match_data.append(self.ratings_midfield[first_team])
                    match_data.append(self.ratings_defence[first_team])
                    match_data.append(self.ratings_overall[first_team])

                    match_data.append(self.team_and_elo[second_team])
                    match_data.append(self.ratings_attack[second_team])
                    match_data.append(self.ratings_midfield[second_team])
                    match_data.append(self.ratings_defence[second_team])
                    match_data.append(self.ratings_overall[second_team])

                    inputs.append(match_data)
                    outputs.append(self.scores_as_classifications[count])
                count = count + 1
        return inputs, outputs

    def team_name_normaliser(self, team_name):
        if team_name == "Man City":
            team_name = "Manchester City"
        if team_name == "Tottenham":
            team_name = "Spurs"
        if team_name == "Man United":
            team_name = "Manchester Utd"
        if team_name == "Newcastle":
            team_name = "Newcastle Utd"
        if team_name == "Cardiff":
            team_name = "Cardiff City"
        if team_name == "Leicester":
            team_name = "Leicester City"
        return team_name

class data_handler:
    def save_data_streams(self, inputs, outputs, nn):
        with open('inputs.pickle', 'wb') as file:
            pickle.dump(inputs, file, protocol = 3)
        with open('outputs.pickle', 'wb') as file:
            pickle.dump(outputs, file, protocol = 3)
        with open('neuralNetwork.pickle', 'wb') as file:
            pickle.dump(nn, file, protocol = 3)
        
    def check_data_streams(self):
        if not os.path.isfile("inputs.pickle"):
            return True
        if not os.path.isfile("outputs.pickle"):
            return True
        if not os.path.isfile("neuralNetwork.pickle"):
            return True
        else:
            return False

    def load_data_streams(self):
        input_file = open("inputs.pickle", "rb")
        output_file = open("outputs.pickle", "rb")
        neural_file = open("neuralNetwork.pickle", "rb")
        inputs = pickle.load(input_file)
        input_file.close()
        outputs = pickle.load(output_file)
        output_file.close()
        nn = pickle.load(neural_file)
        neural_file.close()
        return inputs, outputs, nn

class gui:
    def __init__(self, ds, nn):     
        self.root = tk.Tk()
        self.root.title("Scorify v2.2.0")
        self.main = Frame(self.root)
        self.main.grid(column = 0, row = 0, sticky = (N, W, E, S))
        self.main.columnconfigure(0, weight = 1)
        self.main.rowconfigure(0, weight = 1)

        self.ds = ds
        self.nn = nn

    def interface_handler(self, choices):
        self.home_dropdown(choices)
        self.away_dropdown(choices)
        button = Button(self.main, text='Done', command = self.start_prediction).grid(row = 1, column = 2)
        
        mainloop()

    def home_dropdown(self, choices):
        self.first_menu_value = StringVar(self.root)
        self.first_menu_value.set(list(choices.keys())[0])
        menu = OptionMenu(self.main, self.first_menu_value, *choices)
        menu.grid(row = 1, column = 0)
        menu.configure(width = 30)
        Label(self.main, text = "Select a Home Team").grid(row = 0, column = 0)

    def away_dropdown(self, choices):
        self.second_menu_value = StringVar(self.root)
        self.second_menu_value.set(list(choices.keys())[0])
        menu = OptionMenu(self.main, self.second_menu_value, *choices)
        menu.grid(row = 1, column = 1)
        menu.configure(width = 30)
        Label(self.main, text = "Select an Away Team").grid(row = 0, column = 1)

    def start_prediction(self):
        self.ds.get_team_names()
        self.ds.get_team_ratings()
        
        match_data = []
        match_data.append(self.ds.team_and_elo[self.first_menu_value.get()])
        match_data.append(self.ds.ratings_attack[self.first_menu_value.get()])
        match_data.append(self.ds.ratings_midfield[self.first_menu_value.get()])
        match_data.append(self.ds.ratings_defence[self.first_menu_value.get()])
        match_data.append(self.ds.ratings_overall[self.first_menu_value.get()])

        match_data.append(self.ds.team_and_elo[self.second_menu_value.get()])
        match_data.append(self.ds.ratings_attack[self.second_menu_value.get()])
        match_data.append(self.ds.ratings_midfield[self.second_menu_value.get()])
        match_data.append(self.ds.ratings_defence[self.second_menu_value.get()])
        match_data.append(self.ds.ratings_overall[self.second_menu_value.get()])

        predictions = self.nn.make_prediction([match_data])
        self.display_results(predictions)

    def display_results(self, predictions):
        results = "Results: " + str(round(predictions[0][0], 3)) + " - " + str(round(predictions[0][1], 3))
        
        result = Label(self.main, text = results).grid(row = 3, column = 0)
        
def main():
    ds = data_scraper()
    dh = data_handler()
    print("Checking if program is running for the first time . . .")
    if not dh.check_data_streams():
        print("Loading data from last use . . .")
        inputs, outputs, nn = dh.load_data_streams()
        ds.get_team_names()
        
        g = gui(ds, nn)
        g.interface_handler(ds.team_and_elo)
    else:
        print("Loading data from the web. Please wait . . .")
        ds.get_team_names()
        ds.get_team_ratings()
        ds.get_match_history()
        ds.classify_scores()
        inputs, outputs = ds.generate_inputs()
        print("Initialising neural network . . .")
        nn = neural_network(inputs, outputs)
        print("Training neural network. Please Wait . . .")
        nn.train_network()
        print("Saving data . . .")
        dh.save_data_streams(inputs, outputs, nn)
        print("Making prediction . . .")
        g = gui(ds, nn)
        g.interface_handler(ds.team_and_elo)

main()

