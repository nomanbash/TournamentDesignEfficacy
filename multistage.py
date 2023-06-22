import init
import pandas as pd

def simulate_onegroup(df):
    df = df.copy()
    df["Wins"] = 0
    df["Matches Played"] = 0

    df.reset_index(drop=True, inplace=True)

    for i in range(3):
        for j in range(i + 1, 4):
            player1 = df.at[i, "Names"]
            player2 = df.at[j, "Names"]

            winner, loser, winner_wins, loser_wins = init.single_matchup(player1, player2, df)

            df.loc[df["Names"] == winner, ["Wins", "Matches Played"]] += winner_wins, 1
            df.loc[df["Names"] == loser, ["Wins", "Matches Played"]] += loser_wins, 1

    df.sort_values(by=["Wins", "ratings"], ascending=False, inplace=True, ignore_index=True)

    return df


def simulate_group_stage(df, seeded=False):
    if seeded:
        groups = init.create_seeded_groups(df)
    else:
        groups = init.create_groups(df)

    next_round = pd.DataFrame()
    eliminated = pd.DataFrame()

    for group_id in groups:
        simulation_group = groups[group_id]
        results = simulate_onegroup(simulation_group)
        next_round = pd.concat([next_round, results.head(2)], ignore_index=True)
        eliminated = pd.concat([eliminated, results.tail(2)], ignore_index=True)

    eliminated = eliminated.sort_values(by="Wins", ascending=False, ignore_index=False)
    eliminated["Post-Rankings"] = eliminated["Wins"].rank(ascending=False, method="dense") + 16

    return next_round, eliminated

def knockout_stage(df, eliminated, rounds, rank_offset):
    winners = pd.DataFrame()
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

def simulate_knockout_stage(df, eliminated):
    winners, eliminated = knockout_stage(df, eliminated, 16, 8)
    semifinalists, eliminated = knockout_stage(winners, eliminated, 8, 4)
    finalists, eliminated = knockout_stage(semifinalists, eliminated, 4, 2)
    winners, eliminated = knockout_stage(finalists, eliminated, 2, 0)
    eliminated = pd.concat([eliminated, winners])
    eliminated.loc[eliminated["Post-Rankings"].isnull(), "Post-Rankings"] = 1.0
    eliminated["Post-Rankings"] = eliminated["Post-Rankings"].astype(int)

    return eliminated


def multistage(df, seeded = False):
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


