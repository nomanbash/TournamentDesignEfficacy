# Assessing Efficacy of Different Tournament Designs Using a Monte Carlo Approach

This repository contains several files used to determine which tournament is the most efficacious in terms of placement of the Top 8, Top 1 players, as well as the number of inversions and total inversions when it comes to eSports.
The tournmanets to be assessed are the Global StarCraft II League Code S Season 1 tournaments from 2012 - 2019.
Data is gathered from liquipedia using a web scraped `import_players.py`. This file can be run simply running `python import_players.py` and then pasting the relevant liquipedia URL (works for 2012 -2019).
The script will ping the Aligulac API. Therefore, an API key needs to be setup in `config.py`. Simply put your API key from Aligulac there.

Each .py script contains a different tournament design. Running the scripts themselves will simply output the metrics for both the seeded and the unseeded tournament. You will be asked to input the tournament.
Tournaments can be entered as 2012GSL, 2013GSL and so on. The data is then gathered from the data folder, player ratings are assessed and the script outputs the metrics.

Running results.py runs a simulation 1000 times for each tournament (8000 times total, 16 tournaments) and creates a numpy array with the details of the metrics of each simulation. GSL_false.npy refers to whether seeding is true or false.

The code has already been run and output stored in results.
