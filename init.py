import pandas as pd
import numpy as np
import random
import math

def main():
    players_df = load()
    player1 = input("Enter Player 1: ")
    player2 = input("Enter Player 2: ")
    print(predict(player1, player2, players_df))


def load():
    file_path = "Data/" + input("Enter file name: ") + ".csv"
    players_df = pd.read_csv(file_path)
    return players_df


    
def logistic(rating_diff):
    return 1 / (1 + math.exp(-rating_diff))

    
def predict(player1, player2, df):
    player_a, player_b = df[df["Names"] == player1]["ratings"].values[0], df[df["Names"] == player2]["ratings"].values[0]
    #variance_a, variance_b = df[df["Names"] == player1]["deviation"].values, df[df["Names"] == player2]["deviation"].values

    #player_a += sample_logistic(variance_a)
    #player_b += sample_logistic(variance_b)

    rating_diff = (player_a  - player_b)
    winrate = logistic(rating_diff)
    
    return player1 if random.random() <= winrate else player2

    
def calculate_metrics(df):
    filtered_df = df.copy()
    prerank = round(filtered_df["Pre-Rank"],0).astype(int).to_list()
    postrank = round(filtered_df["Post-Rankings"],0).astype(int).to_list()
    result = 0
    number = 0
    for row in range(len(prerank)):
        if postrank[row] < prerank[row]:
            number += 1
            if prerank[row] > 1:
                ranks = range(prerank[row], postrank[row], -1)
                result += sum(1 / math.log(rank) for rank in ranks)
            else:
                result += 1 / math.log(postrank[row])

    Top1 = df[df["Pre-Rank"] == 1]["Post-Rankings"].values[0]
    TopK = df[df["Pre-Rank"] <= 8]["Post-Rankings"].mean()

    return result, number, Top1, TopK


    
def calculate_running_mean(arr):
    running_means = []
    current_sum = 0
    for i, num in enumerate(arr, 1):
        current_sum += num
        running_mean = current_sum / i
        running_means.append(running_mean)
    return running_means

    
        
def create_seeded_groups(df):
    groups = {}
    for i in range(8):
        group_id = f"Group_{i+1}"
        start_index = i
        middle_index1 = i + 8
        middle_index12 = i + 16
        last_index = i + 24
        groups[group_id] = df.iloc[[start_index, middle_index1, middle_index12, last_index]]
    return groups

    

def create_groups(df):
    df = df.sample(frac = 1)
    groups = {}
    for i in range(8):
        group_id = f"Group_{i+1}"
        start_index = i * 4
        end_index = start_index + 4
        groups[group_id] = df.iloc[start_index:end_index]
    return groups


def single_matchup(player1, player2, df):
    winner = predict(player1, player2, df)
    if winner == player1:
        return player1, player2, 1, 0
    else:
        return player2, player1, 1, 0


def random_draw(df):
    num_teams = len(df)
    
    # Create a copy of the DataFrame to store the draw results
    draw_df = df.copy()
    
    # Create a list to track the teams that have been drawn
    drawn_teams = []
    
    # Iterate through the group numbers
    for group_num in range(0, num_teams, 2):
        # Get the teams from the current group
        team1 = df.loc[group_num, 'Names']
        team2 = df.loc[group_num + 1, 'Names']
        
        # Check if any of the teams have already been drawn
        if team1 in drawn_teams or team2 in drawn_teams:
            # Find a replacement team that hasn't been drawn yet
            replacement_teams = df.loc[~df['Names'].isin(drawn_teams)]
            replacement_team = replacement_teams.sample(n=1)['Names'].values[0]
            
            # Update the draw DataFrame with the replacement team
            draw_df.loc[group_num, 'Names'] = replacement_team
        
        # Add the drawn teams to the list
        drawn_teams.extend([draw_df.loc[group_num, 'Names'], draw_df.loc[group_num + 1, 'Names']])
    
    # Shuffle the draw DataFrame
    draw_df = draw_df.sample(frac=1).reset_index(drop=True)
    
    return draw_df






if __name__ == "__main__":
    main()