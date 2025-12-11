# Task 1

Check the data description in `data_description.md`or on [Kaggle](https://www.kaggle.com/datasets/nokkyu/deutsche-bahn-db-delays/data). Do some data explaration to answer the following questions:

- Is it possible to extract information from the ID column? Does the ID column stay constant during the one entire train line?
- What’s the relationship between path, eva_nr and station?  Can a stop be on the path when it’s still the station?
- When does “city” change — is city the destination, the nearest city, the town name?
- Find examples and outliers etc. in the columns `arrival_plan` and `departure_plan`,  `arrival_change` and `departure_change`,
- Check whether `arrival_delay_m`  and `departure_delay_m` columns match up with the `plan`  and `change` columns by running some checking function.
- Check whether the `arrival_delay_check` and `departure_delay_check` have an *accidental* mistake — is there a row where the delay is over 6 minutes, but check returns `on_time` ? Use pandas to check all rows.
- Check all the info values (perhaps by using `.unique` ) — do they contain something useful? If yes, then explain; if no, could we consider removing that?
- Check weird times — do trains also run at night? What happens to them at night?

Based on those questions, try to decide which columns are worth dropping.



# Task 1.25

try to find the data points for a specific train ride. In other words, say that you picked `line` 18 that was supposed to arrive in Aachen West at 2024-07-08 00:20:00 — gather ALL data points that are related to that one train ride. This might just mean fetching all the lines with the same ID value and then sorting them by arrival time ascending.



# Task 1.5

Visualize the following data for exploration and cleanup reasons:

- number of rows per train line
- if the ID stays constant during the entire train ride (if more than 1 line corresponds to an ID value): visualize the number of lines per ID
- highest-traffic stations (if ID values are unique, then just x = eva_nr and y = count(eva_nr); if not, then consider grouping x = ID&eva_nr, y=count(ID&eva_nr)
- number of data points per category (remember that `category` is a categorical field)
- number of data points per state
- arrival_delay distribution (exclude all 0 values, maybe)
- departure_delay distribution (exclude all 0 values, maybe)
- arrival_delay and/or departure_delay distribution for trains that have a corresponding delay of more than 6 minutes
- arrival_delay and/or departure_delay distribution for trains that have a corresponding delay of more than … 15 minutes (arbitrary value; could also do 10 minutes or 30 minutes)
- the number of trains per some given time
    - first, just show the number of trains or data lines in any given hour (so, make “buckets” of 1 hour).
    - then, make visualizations that combine some days — the plot should be able to answer the question “on every workday, how many trains are on the train lines at 17.00-18.00”? have a line plot with 5 lines that visualize each workday. Then, do the same for the weekend.
    - This visualization might highly depend on whether the Germans have different schedules on weekends as we do
- for trains that are not “on_time”, show the distribution for:
    - the state that they are in
    - the stop (eva_nr or station) they are at
    - the line they are taking
    - the time they are supposed to arrive/depart



# Task 2

Transform and/or figure out what to do with the following columns:

- `line`
    - make sure that the values are considered categorical strings
- `path`
    - should this be made into a list/set/collection object that has all the `eva_nr`values of the stations?
    - Should this be made into a numeric value (just a `count`  on the number of stops on the path)