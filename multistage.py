import init
import pandas as pd

def simulate_onegroup(df):
    """
    Simulates one group. Takes in a dataframe of 4 players. All players play each other, outputs a dataframe sorted by most wins, or if a tie, by their ratings
    """

    #initialize
    df = df.copy()
    df["Wins"] = 0
    df["Matches Played"] = 0

    df.reset_index(drop=True, inplace=True)

    #make sure everyone plays each other
    for i in range(3):
        for j in range(i + 1, 4):
            player1 = df.at[i, "Names"]
            player2 = df.at[j, "Names"]

            #predict winner
            winner, loser, winner_wins, loser_wins = init.single_matchup(player1, player2, df)

            #update winner and loser in original df
            df.loc[df["Names"] == winner, ["Wins", "Matches Played"]] += winner_wins, 1
            df.loc[df["Names"] == loser, ["Wins", "Matches Played"]] += loser_wins, 1

    #sort df by points (wins) or their ratings if a tie
    df.sort_values(by=["Wins", "ratings"], ascending=False, inplace=True, ignore_index=True)

    return df


def simulate_group_stage(df, seeded=False):
    """
    Simulates the group stage for all groups. Takes in a dataframe, splits it into 8 groups depending on seeded bool value, runs simulate_group function for all groups
    """
    
    #check if seeded and seeded groups need to be made or random draw groups
    if seeded:
        groups = init.create_seeded_groups(df)
    else:
        groups = init.create_groups(df)

    #initialize output dataframes
    next_round = pd.DataFrame()
    eliminated = pd.DataFrame()

    #for each group, simulate the results. Take the top 2 and add them to the winners, take the bottom two and add them to eliminated
    for group_id in groups:
        simulation_group = groups[group_id]
        results = simulate_onegroup(simulation_group)
        next_round = pd.concat([next_round, results.head(2)], ignore_index=True)
        eliminated = pd.concat([eliminated, results.tail(2)], ignore_index=True)

    
    #update rankings of players who got eliminated.
    eliminated = eliminated.sort_values(by="Wins", ascending=False, ignore_index=False)
    eliminated["Post-Rankings"] = eliminated["Wins"].rank(ascending=False, method="dense") + 16

    return next_round, eliminated

def knockout_stage(df, eliminated, rounds, rank_offset):
    """
    Simulates the knockout stage. Takes in a dataframe of winners from group stage, the eliminated dataframe, the number of matches to be played and the rank_offset
    which is imply the best rating a player knocked out in this round can achieve. Outputs two dataframes, those who advance, and those who are eliminated
    """
    
    #initialize
    winners = pd.DataFrame()

    #create a random draw
    matchups = init.random_draw(df)

    #play matches
    for i in range(0, rounds, 2):
        player1 = matchups.at[i, "Names"]
        player2 = matchups.at[i+1, "Names"]

        #predict winner
        winner, loser, winner_wins, loser_wins = init.single_matchup(player1, player2, df)


        #update winner and loser's stats
        winner_index = matchups.index[matchups["Names"] == winner]
        loser_index = matchups.index[matchups["Names"] == loser]
        matchups.loc[winner_index, ['Wins', 'Matches Played']] += winner_wins, 1
        matchups.loc[loser_index, ['Wins', 'Matches Played']] += loser_wins, 1

        #add winners and losers to relevant dataframes
        winners = pd.concat([winners, matchups.loc[winner_index]])
        eliminated = pd.concat([eliminated, matchups.loc[loser_index]])

    #update rankings of those who were eliminated in this round.
    eliminated.reset_index(drop=True, inplace =True)
    eliminated.loc[eliminated["Post-Rankings"].isnull(), "Post-Rankings"] = eliminated["Wins"].rank(ascending=False, method = "dense") + rank_offset

    winners.reset_index(inplace = True, drop = True)

    return winners, eliminated

def simulate_knockout_stage(df, eliminated):
    """
    Simulates the entire knockout stage
    """
    winners, eliminated = knockout_stage(df, eliminated, 16, 8)
    semifinalists, eliminated = knockout_stage(winners, eliminated, 8, 4)
    finalists, eliminated = knockout_stage(semifinalists, eliminated, 4, 2)
    winners, eliminated = knockout_stage(finalists, eliminated, 2, 0)
    eliminated = pd.concat([eliminated, winners])
    eliminated.loc[eliminated["Post-Rankings"].isnull(), "Post-Rankings"] = 1.0
    eliminated["Post-Rankings"] = eliminated["Post-Rankings"].astype(int)

    return eliminated


def multistage(df, seeded = False):
    """
    Simulates the entire tournament. Takes in a dataframe, returns the metrics to be measured
    """
    knockouts, eliminated = simulate_group_stage(df, seeded)
    final_df = simulate_knockout_stage(knockouts, eliminated)
    weighted_inversions, number_inversions, Top1, Top8 = init.calculate_metrics(final_df)

    return weighted_inversions, number_inversions, Top1, Top8


def main():
    df = init.load()
    inversion_metrics, number_inversions, Top1, TopK = multistage(df)
    print("Unseeded")
    print(f"The weighted inversions were {inversion_metrics:.2f}")
    print(f"The number of inversions were {number_inversions:.2f}")
    print(f"The Top Player Finished at {Top1} position")
    print(f"The average finishing position of the Top 8 was {TopK: .2f}")

    print()
    print("Seeded")
    print()

    inversion_metrics, number_inversions, Top1, TopK = multistage(df, seeded = True)
    print(f"The weighted inversions were {inversion_metrics:.2f}")
    print(f"The number of inversions were {number_inversions:.2f}")
    print(f"The Top Player Finished at {Top1} position")
    print(f"The average finishing position of the Top 8 was {TopK: .2f}")


if __name__ == "__main__":
    main()


