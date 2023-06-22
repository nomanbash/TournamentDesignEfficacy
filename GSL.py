import init
import numpy as np

def gsl_matchup(player1, player2, df):
    winner_count = [0, 0]
    for _ in range(3):
        winner = init.predict(player1, player2, df)
        winner_count[winner == player1] += 1
    if winner_count[True] > winner_count[False]:
        return player1, player2
    else:
        return player2, player1

def gsl_matchupknockouts(player1, player2, df):
    winner_count = [0, 0]
    for _ in range(5):
        winner = init.predict(player1, player2, df)
        winner = init.predict(player1, player2, df)
        winner_count[winner == player1] += 1
    if winner_count[True] > winner_count[False]:
        return player1, player2
    else:
        return player2, player1
    
def gsl_matchupfinals(player1, player2, df):
    winner_count = [0, 0]
    for _ in range(7):
        winner = init.predict(player1, player2, df)
        winner_count[winner == player1] += 1
    if winner_count[True] > winner_count[False]:
        return player1, player2
    else:
        return player2, player1

def update_rankings_after_stage(eliminated_list, dataframe, stage_number):
    new_list = [item for sublist in eliminated_list for item in sublist[2:4]]

    conditions = [
        stage_number == 1,
        stage_number == 2,
        stage_number == 3,
        stage_number == 4
    ]
    values = [
        17,
        9,
        5,
        3
    ]
    filt = dataframe["Names"].isin(new_list)
    dataframe.loc[filt, "Post-Rankings"] = np.select(conditions, values, default = 0)

    return dataframe

def simulate_group(df):
    df = df.sample(frac = 1)
    winner1, loser1 = gsl_matchup(df.iloc[0,2], df.iloc[1,2], df)
    winner2, loser2 = gsl_matchup(df.iloc[2,2], df.iloc[3,2], df)
    champion1, playoff1 = gsl_matchup(winner1, winner2, df)
    playoff2, eliminated1 = gsl_matchup(loser1, loser2, df)
    champion2, eliminated2 = gsl_matchup(playoff1, playoff2, df)
    return [champion1, champion2, eliminated2, eliminated1]

def simulate_group_round(groups):
    next_round = []
    for group_id in groups:
        simulation_group = groups[group_id]
        next_round.append(simulate_group(simulation_group))
    return next_round

def next_round_list(next_round_list):
    new_list = []
    for i in range(len(next_round_list)):
        new_list.append(next_round_list[i][0])
        new_list.append(next_round_list[i][1])
    return new_list

def create_new_groups(shuffled_list):
    groups = {}
    for i in range(4):
        group_id = f"Group_{i+1}"
        start_index = i * 4
        end_index = start_index + 4
        groups[group_id] = shuffled_list[start_index:end_index]
    return groups

def simulate_round2_groups(groups_list, df):
    winner1, loser1 = gsl_matchup(groups_list[0], groups_list[1], df)
    winner2, loser2 = gsl_matchup(groups_list[2], groups_list[3], df)
    champion1, playoff1 = gsl_matchup(winner1, winner2, df)
    playoff2, eliminated1 = gsl_matchup(loser1, loser2, df)
    champion2, eliminated2 = gsl_matchup(playoff1, playoff2, df)
    return [champion1, champion2, eliminated2, eliminated1]

def simulate_group_round2(groups, df):
    next_round = []
    for group_id in groups:
        simulation_group = groups[group_id]
        next_round.append(simulate_round2_groups(simulation_group, df))
    return next_round

def simulate_knockouts(new_list, df):
    import random
    knockout_list = []
    for i in range(len(new_list)):
        knockout_list.append(new_list[i][0])
        knockout_list.append(new_list[i][1])
    random.shuffle(knockout_list)
    winners = []
    for i in range(0, 8, 2):
        winners.append(gsl_matchupknockouts(knockout_list[i], knockout_list[i+1], df)[0])

    filt_list = [player for player in knockout_list if player not in winners]
    filt = df["Names"].isin(filt_list)
    df.loc[filt, "Post-Rankings"] = 5 

    finalist = []
    for i in range(0, 4, 2):
        finalist.append(gsl_matchupknockouts(winners[i], winners[i+1], df)[0])
    filt_list = [player for player in winners if player not in finalist]
    filt = df["Names"].isin(filt_list)
    df.loc[filt, "Post-Rankings"] = 3

    champion, runner_up = gsl_matchupfinals(finalist[0], finalist[1], df)
    filt = df["Names"] == champion
    df.loc[filt, "Post-Rankings"] = 1
    filt = df["Names"] == runner_up
    df.loc[filt, "Post-Rankings"] = 2

    return df

def GSL(dataframe, seeded = False):
    tournament_df = dataframe.copy()
    if seeded:
        results = simulate_group_round(init.create_seeded_groups(dataframe))
    else:
        results = simulate_group_round(init.create_groups(dataframe))
    tournament_df = update_rankings_after_stage(results, tournament_df, 1)
    new_list = simulate_group_round2(create_new_groups(next_round_list(results)), dataframe)
    tournament_df = update_rankings_after_stage(new_list, tournament_df, 2)
    final_df = simulate_knockouts(new_list, tournament_df)
    final_df.sort_values(by = 'Post-Rankings', ascending = True)

    inversion_metrics, number_inversions, Top1, TopK = init.calculate_metrics(final_df)

    return inversion_metrics, number_inversions, Top1, TopK

def main():
    df = init.load()
    inversion_metrics, number_inversions, Top1, TopK = GSL(df)
    print("Unseeded")
    print(f"The weighted inversions were {inversion_metrics:.2f}")
    print(f"The number of inversions were {number_inversions:.2f}")
    print(f"The Top Player Finished at {Top1} position")
    print(f"The average finishing position of the Top 8 was {TopK}")

    print()
    print("Seeded")
    print()

    inversion_metrics, number_inversions, Top1, TopK = GSL(df, seeded=True)
    print(f"The weighted inversions were {inversion_metrics:.2f}")
    print(f"The number of inversions were {number_inversions:.2f}")
    print(f"The Top Player Finished at {Top1} position")
    print(f"The average finishing position of the Top 8 was {TopK}")


if __name__ == "__main__":
    main()

