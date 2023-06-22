import init
import pandas as pd
import numpy as np


def create_knockout_bracket(df):
    bracket = [
        0,
        31,
        16,
        15,
        8,
        23,
        24,
        7,
        4,
        27,
        20,
        11,
        12,
        19,
        28,
        3,
        2,
        29,
        18,
        13,
        10,
        21,
        26,
        5,
        6,
        25,
        22,
        9,
        14,
        17,
        30,
        1,
        9,
        22
    ]

    df = df.loc[bracket]
    df.reset_index(drop = True, inplace = True)

    return df

def knockout_stage(df, eliminated, rounds, rank_offset, seeded = False):
    winners = pd.DataFrame()
    if seeded:
        if rounds == 32:
            matchups = create_knockout_bracket(df)
        else:
            matchups = df.copy()
    else:
        matchups = init.random_draw(df)
    for i in range(0, rounds, 2):
        player1 = matchups.at[i, "Names"]
        player2 = matchups.at[i+1, "Names"]
        winner, loser, winner_wins, loser_wins = init.single_matchup(player1, player2, df)

        winner_index = matchups.index[matchups["Names"] == winner]
        loser_index = matchups.index[matchups["Names"] == loser]
        matchups.loc[winner_index, ['Wins', 'Matches Played']] += winner_wins, 1
        matchups.loc[loser_index, ['Wins', 'Matches Played']] += loser_wins, 1

        winners = pd.concat([winners, matchups.loc[winner_index]])
        eliminated = pd.concat([eliminated, matchups.loc[loser_index]])

    eliminated.reset_index(drop=True, inplace =True)
    eliminated.loc[eliminated["Post-Rankings"].isnull(), "Post-Rankings"] = eliminated["Wins"].rank(ascending=False, method = "dense") + rank_offset

    winners.reset_index(inplace = True, drop = True)

    return winners, eliminated    


def knockout(df, seeded = False):
    eliminated = pd.DataFrame()
    eliminated["Post-Rankings"] = np.nan
    df = df.copy()
    df[["Wins", "Matches Played"]] = 0
    winners, eliminated = knockout_stage(df, eliminated, 32, 16, seeded)
    winners, eliminated = knockout_stage(winners, eliminated, 16, 8, seeded)
    semifinalists, eliminated = knockout_stage(winners, eliminated, 8, 4, seeded)
    finalists, eliminated = knockout_stage(semifinalists, eliminated, 4, 2, seeded)
    winners, eliminated = knockout_stage(finalists, eliminated, 2, 0, seeded)
    eliminated = pd.concat([eliminated, winners])
    eliminated.loc[eliminated["Post-Rankings"].isnull(), "Post-Rankings"] = 1.0
    eliminated["Post-Rankings"] = eliminated["Post-Rankings"].astype(int)

    weighted_inversions, number_inversions, Top1, Top8 = init.calculate_metrics(eliminated)

    return weighted_inversions, number_inversions, Top1, Top8

def main():
    df = init.load()
    inversion_metrics, number_inversions, Top1, TopK = knockout(df)
    print("Unseeded")
    print(f"The weighted inversions were {inversion_metrics:.2f}")
    print(f"The number of inversions were {number_inversions:.2f}")
    print(f"The Top Player Finished at {Top1} position")
    print(f"The average finishing position of the Top 8 was {TopK: .2f}")

    print()
    print("Seeded")
    print()

    inversion_metrics, number_inversions, Top1, TopK = knockout(df, seeded = True)
    print(f"The weighted inversions were {inversion_metrics:.2f}")
    print(f"The number of inversions were {number_inversions:.2f}")
    print(f"The Top Player Finished at {Top1} position")
    print(f"The average finishing position of the Top 8 was {TopK: .2f}")


if __name__ == "__main__":
    main()
