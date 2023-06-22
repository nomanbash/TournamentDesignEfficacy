import init
import pandas as pd
import numpy as np
import random
import swiss
import tripleknockouts


def csgo_swissround(df):
    players = df["Names"].to_list()
    random.shuffle(players)

    tournament_df = df.copy()

    pairings = [(players[i], players[i+1]) for i in range(0, len(players), 2) if players[i+1] not in df["Opponents"]]

    for pair in pairings:
        winner, loser, onewins, twowins = init.single_matchup(pair[0], pair[1], df)

        winner_index = tournament_df.index[tournament_df["Names"] == winner]
        loser_index = tournament_df.index[tournament_df["Names"] == loser]

        tournament_df.loc[winner_index, ["Points", "Opponent Wins", "Matches", "Opponents"]] += onewins, twowins, 1, ", " + loser
        tournament_df.loc[loser_index, ["Points", "Opponent Wins", "Matches", "Opponents"]] += twowins, onewins, 1, ", " + winner

        tournament_df.loc[winner_index, "OMW%"] = tournament_df["Opponent Wins"] / tournament_df["Matches"]
        tournament_df.loc[loser_index, "OMW%"] = tournament_df["Opponent Wins"] / tournament_df["Matches"]

    tournament_df["Opponents"] = tournament_df["Opponents"].astype(str)

    return tournament_df

def csgoswiss_roundtwo(df):
    df = df.sort_values(by = "Points")
    top_bracket = df.head(16).copy()
    bottom_bracket = df.tail(16).copy()

    top_bracket = csgo_swissround(top_bracket)
    bottom_bracket = csgo_swissround(bottom_bracket)

    df = pd.concat([top_bracket, bottom_bracket])

    return df

def csgo_swissround3(df):
    eliminator = df[df["Points"] == 0].copy()
    middle = df[df["Points"] == 1].copy()
    top = df[df["Points"] == 2].copy()

    top = csgo_swissround(top)
    middle = csgo_swissround(middle)
    eliminator = csgo_swissround(eliminator)

    df = pd.concat([top, middle, eliminator])

    return df

def csgo_swissroundfour(df):
    qualified = df[df["Points"] == 3].copy()
    eliminated = df[df["Points"] == 0].copy()
    top = df[df["Points"] == 2].copy()
    bottom = df[df["Points"] == 1].copy()

    top = csgo_swissround(top)
    bottom = csgo_swissround(bottom)

    df = pd.concat([qualified, eliminated, top, bottom])

    return df

def csgo_swissroundfive(df):
    qualified = df[df["Points"] == 3].copy()
    eliminated = df[df["Points"] <= 1].copy()
    top = df[df["Points"] == 2].copy()

    top = csgo_swissround(top)

    df = pd.concat([qualified, eliminated, top])

    return df

def csgo_swissroundsix(df):
    eliminated = df[df["Points"] < 3].copy()

    eliminated.reset_index(inplace = True, drop = True)

    eliminated.loc[:3, "Post-Rankings"] = 29
    eliminated.loc[4:10, "Post-Rankings"] = 23
    eliminated.loc[10:,"Post-Rankings"] = 17

    roundone = df[df["Points"] == 3].copy()

    roundone.reset_index(inplace = True, drop = True)

    matchups = init.random_draw(roundone)
    winners = pd.DataFrame()
    for i in range(0, 16, 2):
        player1 = matchups.at[i, "Names"]
        player2 = matchups.at[i+1, "Names"]
        winner, loser, winner_wins, loser_wins = tripleknockouts.triple_matchup(player1, player2, df)

        winner_index = matchups.index[matchups["Names"] == winner]
        loser_index = matchups.index[matchups["Names"] == loser]
        
        matchups.loc[winner_index, ['Points', "Matches"]] += winner_wins * 3, 3
        matchups.loc[loser_index, ['Points', "Matches"]] += loser_wins * 3, 3

        winners = pd.concat([winners, matchups.loc[winner_index]])
        eliminated = pd.concat([eliminated, matchups.loc[loser_index]])

    eliminated.reset_index(drop=True, inplace =True)
    eliminated.loc[eliminated["Post-Rankings"].isnull(), "Post-Rankings"] = eliminated["Points"].rank(ascending=False, method = "dense") + 8

    winners.reset_index(inplace = True, drop = True)

    matchups = init.random_draw(winners)
    semifinalists = pd.DataFrame()
    for i in range(0, 8, 2):
        player1 = matchups.at[i, "Names"]
        player2 = matchups.at[i+1, "Names"]
        winner, loser, winner_wins, loser_wins = tripleknockouts.triple_matchup(player1, player2, df)

        winner_index = matchups.index[matchups["Names"] == winner]
        loser_index = matchups.index[matchups["Names"] == loser]

        matchups.loc[winner_index, ['Points', "Matches"]] += winner_wins * 3, 3
        matchups.loc[loser_index, ['Points', "Matches"]] += loser_wins * 3, 3

        semifinalists = pd.concat([semifinalists, matchups.loc[winner_index]])
        eliminated = pd.concat([eliminated, matchups.loc[loser_index]])

    eliminated.reset_index(drop=True, inplace =True)
    eliminated.loc[eliminated["Post-Rankings"].isnull(), "Post-Rankings"] = eliminated["Points"].rank(ascending=False, method = "dense") + 4

    semifinalists.reset_index(inplace = True, drop = True)

    matchups = init.random_draw(semifinalists)
    finalists = pd.DataFrame()
    for i in range(0, 4, 2):
        player1 = matchups.at[i, "Names"]
        player2 = matchups.at[i+1, "Names"]
        winner, loser, winner_wins, loser_wins = tripleknockouts.triple_matchup(player1, player2, df)

        winner_index = matchups.index[matchups["Names"] == winner]
        loser_index = matchups.index[matchups["Names"] == loser]
        matchups.loc[winner_index, ['Points', "Matches"]] += winner_wins * 3, 3
        matchups.loc[loser_index, ['Points', "Matches"]] += loser_wins * 3, 3

        finalists = pd.concat([finalists, matchups.loc[winner_index]])
        eliminated = pd.concat([eliminated, matchups.loc[loser_index]])

    eliminated.reset_index(drop=True, inplace =True)
    eliminated.loc[eliminated["Post-Rankings"].isnull(), "Post-Rankings"] = eliminated["Points"].rank(ascending=False, method = "dense") + 2

    champion, runnerup, champwins, runwins = tripleknockouts.triple_matchup(finalists['Names'].iloc[0], finalists['Names'].iloc[1], df)
    winner_index = finalists.index[finalists["Names"] == champion]
    loser_index = finalists.index[finalists["Names"] == runnerup]
    finalists.loc[winner_index, ['Points', 'Matches']] += champwins * 3, 3
    finalists.loc[loser_index, ['Points', 'Matches']] += runwins * 3, 3
    finalists.loc[winner_index, "Post-Rankings"] = 1.0
    finalists.loc[loser_index, "Post-Rankings"] = 2.0

    eliminated = pd.concat([eliminated, finalists.loc[loser_index]])
    eliminated = pd.concat([eliminated, finalists.loc[winner_index]])

    eliminated["Post-Rankings"] = eliminated["Post-Rankings"].astype("int")

    return eliminated
        
def csgoswiss(df, seeded = False):
    df = swiss.swissroundone(df, seeded)
    df = csgoswiss_roundtwo(df)
    df = csgo_swissround3(df)
    df = csgo_swissroundfour(df)
    df = csgo_swissroundfive(df)
    df = csgo_swissroundsix(df)

    weighted_inversions, number_inversions, Top1, Top8 = init.calculate_metrics(df)

    return weighted_inversions, number_inversions, Top1, Top8


def main():
    df = init.load()
    inversion_metrics, number_inversions, Top1, TopK = csgoswiss(df)
    print("Unseeded")
    print(f"The weighted inversions were {inversion_metrics:.2f}")
    print(f"The number of inversions were {number_inversions:.2f}")
    print(f"The Top Player Finished at {Top1} position")
    print(f"The average finishing position of the Top 8 was {TopK}")

    print()
    print("Seeded")
    print()

    inversion_metrics, number_inversions, Top1, TopK = csgoswiss(df, seeded = True)
    print(f"The weighted inversions were {inversion_metrics:.2f}")
    print(f"The number of inversions were {number_inversions:.2f}")
    print(f"The Top Player Finished at {Top1} position")
    print(f"The average finishing position of the Top 8 was {TopK}")


if __name__ == "__main__":
    main()