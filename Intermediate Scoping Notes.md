# Data to initially leave in
- `timestamp` from ID (for XGBoost, needs to probably be split to day - hours - minutes)
- `path_length` from ID (I think 1 will be a better start point than 0)
- `line` (categorical)
- `eva_nr` (categorical)
- `category` (categorical)
- `arrival_plan` (for XGBoost, day - hours - minutes)
- `arrival_delay_m` (how many minutes is it currently late to my station)
- ***MAYBE*** `info` (categorical based on the text)
- ***dst_eva_nr*** - check section [[#FORK IN THE ROAD]]
- ***dst_arrival_plan*** - check section [[#FORK IN THE ROAD]]
- ***dst_arrival_delay_over_6_minutes*** - check text below and [[#FORK IN THE ROAD]]

**A dictionary that maps every eva_nr to a station name**

And what we will be predicting is:
*here, do one at a time. maybe start with 6 minutes as it is already done*
- `dst_arrival_delay_over_6_minutes`

- `dst_arrival_delay_over_5_minutes`
- `dst_arrival_delay_over_10_minutes`
- `dst_arrival_delay_over_15_minutes`
- `dst_arrival_delay_over_20_minutes`
- `dst_arrival_delay_over_25_minutes`
- `dst_arrival_delay_over_30_minutes`

## QUESTIONS
It seems as if ID_part_1 is able to change when the train arrives to another county. So... oops.

## FORK IN THE ROAD
**Sticking with XGBoost requires us to do a bit of data manipulation**. 
**Option 1**: We could create (initially, a toy set of) a database with **ALL cross-matched values**. Say for the example line with Aachen West at 2024-07-08 00:20:00. From that line, we could create a separate line for each pair of START-DESTINATION station. 
**Example:**
Aachen West	2024-07-08 00:20:00	2024-07-08 00:21:00 ... Herzogenrath	2024-07-08 00:29:00
***AND ALSO***
Aachen West	2024-07-08 00:20:00	2024-07-08 00:21:00 ... Lauffen (Neckar)	2024-07-08 00:50:00
***AND ALSO***
Aachen West	2024-07-08 00:20:00	2024-07-08 00:21:00 ... Plochingen	2024-07-08 01:06:00

**Option 2**: Alternatively, we could find all the end stops of the train lines and say whether the train will be late to **that end stop**. So in the above example, we would only include the line with **Aachen West** and **Plochingen**. This would be a bit easier, but still a bit tedious as we first have to figure out which way the train is going. And it wouldn't be as useful and cool.

# Model experimentation plan
Train a model that predicts whether delay will be over 6 minutes.

Initially, take a subset (not a random sample, but just, say, only one days' worth of datapoints) of the data and train the model on that. 
Do that for both Option 1 where we have all cross-matched stations and for Option 2 where we only consider late arrival at the end stop.

Then, move on to other models:
- Train a model that predicts whether delay will be over 5 minutes.
- Train a model that predicts whether delay will be over 10 minutes.
- Train a model that predicts whether delay will be over 15 minutes.
- Train a model that predicts whether delay will be over 20 minutes.
- Train a model that predicts whether delay will be over 25 minutes.
- Train a model that predicts whether delay will be over 30 minutes.

# Tasks
## Task 1
For each line in the dataset, create columns
- `dst_arrival_delay_over_6_minutes`
- `dst_arrival_delay_over_5_minutes`
- `dst_arrival_delay_over_10_minutes`
- `dst_arrival_delay_over_15_minutes`
- `dst_arrival_delay_over_20_minutes`
- `dst_arrival_delay_over_25_minutes`
- `dst_arrival_delay_over_30_minutes`
That have a boolean value (`True/False`).

This can just be done by checking the `arrival_delay_m` value.

For every stop on some train line in some departure schedule, leaving only one line per stop (the latest one; get from the ID timestamp) is sufficient.


## Task 2
The difficult task.

**Accurately** fetch the full train line for some departure. The base for this can be found in Emile's solution of Task 1.25 [here](/data/cleanUp_dataDBQuestion.ipynb). Note that the existing solution may not yet be fully accurate -- sort by the timestamps in the ID instead of just the `arrival_plan`.

Check the `ID` value of those lines in the dataset. From my checking, it seemed as if the ID changes when the train reaches a new state. Is that true?

Now comes the fun part.

- Figure out the direction the train is heading.
- Figure out the last stop the train was at.
- For every stop the train has not yet been at (defined by some dataset line `x`):
    - Create a line in the dataset. This line consists of all the info in `x` as well as the `dst_eva_nr` of the destination station, the `dst_arrival_plan` of the destination station and all the `dst_arrival_delay_over_N_minutes` boolean values.

***Ensure that no stops are missed and that the stops are truly in correct order. This can be checked also by the path length in the ID**