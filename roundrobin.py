import init

def roundrobin(df, seeded = False):
    """
    A tournament where every player plays every other player. Takes in a dataframe with ratings and Pre-Rank and outputs the metrics after every 
    player has played every other player
    """
    df = df.copy()
    df["Wins"] = 0
    df["Matches Played"] = 0


    #
    for i in range(31):
        for j in range(i+1, 32):
            player1 = df.at[i, "Names"]
            player2 = df.at[j, "Names"]

            #get the winner, loser
            winner, loser, winner_wins, loser_wins = init.single_matchup(player1, player2, df)
            
            #find their index in the original dataframe
            winner_index = df.index[df["Names"] == winner]
            loser_index = df.index[df["Names"] == loser]
            
            #update their results
            df.loc[winner_index, ['Wins', "Matches Played"]] += winner_wins, 1
            df.loc[loser_index, ['Wins', "Matches Played"]] += loser_wins, 1
    
    
    #simple sort by wins. Whoever has the most wins(points) is 1st
    df = df.sort_values(by = ["Wins", "ratings"], ascending = False, ignore_index = True)
    df["Post-Rankings"] = df.index + 1

    weighted_inversions, number_inversions, Top1, Top8 = init.calculate_metrics(df)

    return weighted_inversions, number_inversions, Top1, Top8

def main():
    df = init.load()
    inversion_metrics, number_inversions, Top1, TopK = roundrobin(df)
    print(f"The weighted inversions were {inversion_metrics:.2f}")
    print(f"The number of inversions were {number_inversions:.2f}")
    print(f"The Top Player Finished at {Top1} position")
    print(f"The average finishing position of the Top 8 was {TopK: .2f}")

if __name__ == "__main__":
    main()
