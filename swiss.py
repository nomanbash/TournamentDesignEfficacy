import init
import random
import pandas as pd

def no_seeding(player_list):
    random.shuffle(player_list)
    pairings = pairings = [(player_list[i], player_list[i+1]) for i in range(0, len(player_list), 2)]

    return pairings

def seeding(player_list):
    pairings = [(player_list[i], player_list[31-i]) for i in range(0, 16, 1)]
    return pairings

def swissroundone(df, seeded = False):
    players = df["Names"].to_list()

    tournament_df = df.copy()
    tournament_df["Matches"] = 0
    tournament_df["Points"] = 0
    tournament_df["Opponent Wins"] = 0
    tournament_df["Opponent Matches"] = 0

    if seeded:
        pairings = seeding(players)
    else:
        pairings = no_seeding(players)

    for pair in pairings:                                    
        winner, loser, wins1, wins2 = init.single_matchup(pair[0], pair[1], df)
        
        winner_index = tournament_df.index[tournament_df["Names"] == winner]
        loser_index = tournament_df.index[tournament_df["Names"] == loser]

         
        tournament_df.at[winner_index[0], "Opponents"] = loser
        tournament_df.at[loser_index[0], "Opponents"] = winner

        tournament_df.loc[winner_index, [
            "Points",
            "Matches",
            "Opponent Wins",
            "Opponent Matches"
        ]] += wins1, 1, tournament_df.at[loser_index[0], "Points"], tournament_df.at[loser_index[0], "Matches"]
        
        tournament_df.loc[loser_index, [
            "Points",
            "Matches",
            "Opponent Wins",
            "Opponent Matches"
        ]] += wins2, 1, tournament_df.at[winner_index[0], "Points"], tournament_df.at[winner_index[0], "Matches"]

        tournament_df.loc[winner_index, "OMW%"] = tournament_df["Opponent Wins"] / tournament_df["Opponent Matches"]
        tournament_df.loc[loser_index, "OMW%"] = tournament_df["Opponent Wins"] / tournament_df["Opponent Matches"]


    tournament_df["Opponents"] = tournament_df["Opponents"].astype(str)

    return tournament_df


def split_dataframe(df):
    df = df.sort_values(by = "Points")
    num_rows = df.shape[0]
    split_point1 = num_rows // 4
    split_point2 = split_point1 * 2
    split_point3 = split_point1 * 3

    df_dict = {
        "Group1": df.iloc[:split_point1, :],
        "Group2": df.iloc[split_point1:split_point2, :],
        "Group3": df.iloc[split_point2:split_point3, :],
        "Group4": df.iloc[split_point3:, :]
    }

    return df_dict


def swissround2(df):
    players = df["Names"].to_list()
    random.shuffle(players)

    tournament_df = df.copy()

    pairings = [(players[i], players[i+1]) for i in range(0, len(players), 2) if players[i+1] not in df.at[df.index[df["Names"] == players[i]][0], "Opponents"]]

    for pair in pairings:
        winner, loser, wins1, wins2 = init.single_matchup(pair[0], pair[1], df)        
        
        winner_index = tournament_df.index[tournament_df["Names"] == winner]
        loser_index = tournament_df.index[tournament_df["Names"] == loser]

        tournament_df.loc[winner_index, ["Opponents", "Points", "Matches", "Opponent Wins", "Opponent Matches"]] += ", " + str(loser), wins1, 1, tournament_df.at[loser_index[0], "Points"], tournament_df.at[loser_index[0], "Matches"]

        tournament_df.loc[loser_index, ["Opponents", "Points", "Matches", "Opponent Wins", "Opponent Matches"]] += ", " + str(winner), wins2, 1, tournament_df.at[winner_index[0], "Points"], tournament_df.at[winner_index[0], "Matches"]


        tournament_df.loc[winner_index, "OMW%"] = tournament_df.at[winner_index[0], "Opponent Wins"] / tournament_df.at[winner_index[0],"Opponent Matches"]
        tournament_df.loc[loser_index, "OMW%"] = tournament_df.at[loser_index[0], "Opponent Wins"] / tournament_df.at[loser_index[0], "Opponent Matches"]

    return tournament_df

def simulate_swiss_round2(df):
    dictionary = split_dataframe(df)
    exit_df = pd.DataFrame()
    for group in dictionary:
        exit_df = pd.concat([exit_df, swissround2(dictionary[group])])
    
    return exit_df

def simulate_rest_of_tourney(df, number_of_rounds):
    for _ in range(number_of_rounds):
        df = simulate_swiss_round2(df)
    
    return df

def swiss(df, seeded = False):
    roundone = swissroundone(df, seeded)
    df = simulate_rest_of_tourney(roundone, 5)

    df["Post-Rankings"] = df[["Points", "OMW%"]].apply(tuple,axis=1).rank(method='dense',ascending=False).astype(int)

    weighted_inversions, number_inversions, Top1, Top8 = init.calculate_metrics(df)

    return weighted_inversions, number_inversions, Top1, Top8


def main():
    df = init.load()
    df, inversion_metrics, number_inversions, Top1, TopK = swiss(df)
    print("Unseeded")
    print(f"The weighted inversions were {inversion_metrics:.2f}")
    print(f"The number of inversions were {number_inversions:.2f}")
    print(f"The Top Player Finished at {Top1} position")
    print(f"The average finishing position of the Top 8 was {TopK}")

    print()
    print("Seeded")
    print()

    df, inversion_metrics, number_inversions, Top1, TopK = swiss(df, seeded = True)
    print(f"The weighted inversions were {inversion_metrics:.2f}")
    print(f"The number of inversions were {number_inversions:.2f}")
    print(f"The Top Player Finished at {Top1} position")
    print(f"The average finishing position of the Top 8 was {TopK}")


if __name__ == "__main__":
    main()