import init
import pandas as pd
import numpy as np
import random

    
def matchupdt(player1, player2, df):
    winner = init.predict(player1, player2, df)
    if winner == player1:
        return player1, player2
    else:
        return player2, player1

def random_shuffling(df):
    players = df["Names"].to_list()
    random.shuffle(players)

    return players

def seeded_shuffling(df):
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
        1
        ]

    df = df.loc[bracket]

    players = df["Names"].to_list()
    
    return players

def dualtournamentsetup(df, player_list):
    players = player_list.copy()
    winner = [None] * 62
    loser = [None] * 62
    losers_df = pd.DataFrame()

    #first bracket
    adjustment = 0 
    for i in range(0, 16, 1):
        winner[i], loser[i] = matchupdt(players[i + adjustment], players[i + adjustment + 1], df)
        adjustment += 1
    
    #losers bracket round 1
    adjustment = 0
    for i in range(16, 24, 1):
        winner[i], loser[i] = matchupdt(loser[i+adjustment-16], loser[i+adjustment+1-16], df)
        loser_index = df.index[df["Names"] == loser[i]]
        losers_df = pd.concat([losers_df, df.loc[loser_index]])
        losers_df.loc[loser_index, "Post-Rankings"] = 25
        adjustment += 1

    #winners bracket round 1
    adjustment = 0
    for i in range(24, 32, 1):
        winner[i], loser[i] = matchupdt(winner[i+adjustment-24], winner[i+adjustment+1-24], df)
        adjustment += 1

    #losers bracket round 2
    for i in range(32, 36, 1):
        winner[i], loser[i] = matchupdt(winner[i-16], loser[i-4], df)
        loser_index = df.index[df["Names"] == loser[i]]
        losers_df = pd.concat([losers_df, df.loc[loser_index]])
        losers_df.loc[loser_index, "Post-Rankings"] = 17
    
    for i in range(36, 40, 1):
        winner[i], loser[i] = matchupdt(winner[i-16], loser[i-12], df)
        loser_index = df.index[df["Names"] == loser[i]]
        losers_df = pd.concat([losers_df, df.loc[loser_index]])
        losers_df.loc[loser_index, "Post-Rankings"] = 17

    #winners bracket round 2
    adjustment = 0
    for i in range(40, 44, 1):
        winner[i], loser[i] = matchupdt(winner[i+adjustment-16], winner[i+adjustment+1-16], df)
        adjustment += 1

    #losers bracket round 3
    adjustment = 0
    for i in range(44, 48, 1):
        winner[i], loser[i] = matchupdt(winner[i+adjustment-12], winner[i+1+adjustment-12], df)
        loser_index = df.index[df["Names"] == loser[i]]
        losers_df = pd.concat([losers_df, df.loc[loser_index]])
        losers_df.loc[loser_index, "Post-Rankings"] = 13
        adjustment += 1

    for i in range(48, 52, 1):
        winner[i], loser[i] = matchupdt(winner[i-4], loser[i-8], df)
        loser_index = df.index[df["Names"] == loser[i]]
        losers_df = pd.concat([losers_df, df.loc[loser_index]])
        losers_df.loc[loser_index, "Post-Rankings"] = 9

    #winners bracket round 3
    adjustment = 0
    for i in range(52, 54, 1):
        winner[i], loser[i] = matchupdt(winner[i+adjustment-12], winner[i+adjustment+1-12], df)
        adjustment +=1

    #losers bracket round 4
    winner[54], loser[54] = matchupdt(winner[48], winner[49], df)
    loser_index = df.index[df["Names"] == loser[54]]
    losers_df = pd.concat([losers_df, df.loc[loser_index]])
    losers_df.loc[loser_index, "Post-Rankings"] = 7

    winner[55], loser[55] = matchupdt(winner[50], winner[51], df)
    loser_index = df.index[df["Names"] == loser[55]]
    losers_df = pd.concat([losers_df, df.loc[loser_index]])
    losers_df.loc[loser_index, "Post-Rankings"] = 7

    winner[56], loser[56] = matchupdt(winner[54], loser[53], df)
    loser_index = df.index[df["Names"] == loser[56]]
    losers_df = pd.concat([losers_df, df.loc[loser_index]])
    losers_df.loc[loser_index, "Post-Rankings"] = 5

    winner[57], loser[57] = matchupdt(winner[55], loser[52], df)
    loser_index = df.index[df["Names"] == loser[57]]
    losers_df = pd.concat([losers_df, df.loc[loser_index]])
    losers_df.loc[loser_index, "Post-Rankings"] = 5

    #winners bracket round 4
    winner[58], loser[58] = matchupdt(winner[52], winner[53], df)

    #loser bracket round 5
    winner[59], loser[59] = matchupdt(winner[56], winner[57], df)
    loser_index = df.index[df["Names"] == loser[59]]
    losers_df = pd.concat([losers_df, df.loc[loser_index]])
    losers_df.loc[loser_index, "Post-Rankings"] = 4

    #semfinal
    winner[60], loser[60] = matchupdt(winner[59], loser[58], df)
    loser_index = df.index[df["Names"] == loser[60]]
    losers_df = pd.concat([losers_df, df.loc[loser_index]])
    losers_df.loc[loser_index, "Post-Rankings"] = 3

    #final
    winner[61], loser[61] = matchupdt(winner[60], winner[58], df)
    loser_index = df.index[df["Names"] == loser[61]]
    losers_df = pd.concat([losers_df, df.loc[loser_index]])
    losers_df.loc[loser_index, "Post-Rankings"] = 2

    winner_index = df.index[df["Names"] == winner[61]]
    losers_df = pd.concat([losers_df, df.loc[winner_index]])
    losers_df.loc[winner_index, "Post-Rankings"] = 1

    return losers_df

def dualtournament(df, seeded = False):
    if seeded:
        players = seeded_shuffling(df)
    else:
        players = random_shuffling(df)

    df = dualtournamentsetup(df, players)

    weighted_inversions, number_inversions, Top1, Top8 = init.calculate_metrics(df)

    return weighted_inversions, number_inversions, Top1, Top8


def main():
    df = init.load()
    inversion_metrics, number_inversions, Top1, TopK = dualtournament(df)
    print("Unseeded")
    print(f"The weighted inversions were {inversion_metrics:.2f}")
    print(f"The number of inversions were {number_inversions:.2f}")
    print(f"The Top Player Finished at {Top1} position")
    print(f"The average finishing position of the Top 8 was {TopK: .2f}")

    print()
    print("Seeded")
    print()

    inversion_metrics, number_inversions, Top1, TopK = dualtournament(df, seeded = True)
    print(f"The weighted inversions were {inversion_metrics:.2f}")
    print(f"The number of inversions were {number_inversions:.2f}")
    print(f"The Top Player Finished at {Top1} position")
    print(f"The average finishing position of the Top 8 was {TopK: .2f}")


if __name__ == "__main__":
    main()