# DB Delays Web Application
This README outlines the main points that should be satisfied for our DB delays web application.

# Front End
## General thoughts and descriptions
We require the following fields:
- `start_timestamp` - when did the train start moving FROM THE FIRST STATION? It's a weird question, but our dataset requires this.
- `src_station` - from that, we can infer `src_eva_nr`, `src_category`. Requires `station:eva_nr` mappings dictionary (probably in the back-end) and `eva_nr:category` mapping.
- `line` - should already be somewhat filtered based on station; we probably need a dictionary of `eva_nr:{lines}` mappings for filtering (probably in the back-end).
- `dst_station` - from that, we can infer `dst_eva_nr`, `dst_category`. Requires `station:eva_nr` mappings dictionary (probably in the back-end) and `eva_nr:category` mapping.
- `src_arrival_plan` - when is/was the train supposed to arrive at the start station? This must be >= `start_timestamp`.
- `src_arrival_delay` - how late (in minutes) is the train right now?
- `dst_arrival_plan` - when is the train supposed to arrive at the destination station? This must be >= `src_arrival_plan`.
- `info` - is there any information text about the delay?

Then there are two more "weird" questions we'd probably want to get rid of, but we currently might have to ask:
- `src_path_length` - how far along the `line` is our start station?
- `dst_path_length` - how far along the `line` is the desination station?

The last two could be inferred from the `line` and also uniquely determine the direction that the line is going as the `src` station must be with a smaller `path_length` than `dst`. This means that from the `line` numbering fixes and the line cross-matches, we should be able to get all the `line:eva_nr:src_path_length:dst_path_length` mappings; here, `src_path_length` and `dst_path_length` denote the smaller and the larger location number on the line.

The mappings could probably be summarized by a Pandas table; then again, lookups are maybe quicker in a dictionary.



## Input field types
The input fields should function as follows:
- `start_timestamp` - separate date and time selectors. Date should be a calendar widget if possible (limit to +- 2 years from current date), time should be a numeric input field with values 0-23 and 0-59.
- `src_station` - dropdown with search; in other words, putting in "aac" should filter the results to show Aachen West and Aachen East and Aachen North. Since there are over 1000 stations, it might be reasonable to only show around 100 stations at a time. Sort by station category.
- `line` - dropdown with search. Sort alphanumerically.
- `dst_station` - dropdown with search; in other words, putting in "aac" should filter the results to show Aachen West and Aachen East and Aachen North. Since there are over 1000 stations, it might be reasonable to only show around 100 stations at a time. Sort by station category.
- `src_arrival_plan` - separate date and time selectors. Date should be a calendar widget if possible (limit to +- 2 years from current date), time should be a numeric field with values 0-23 and 0-59.
- `src_arrival_delay` - numeric input field between 0 and 159 (the max delay we have in the dataset).
- `dst_arrival_plan` - separate date and time selectors. Date should be a calendar widget if possible (limit to +- 2 years from current date), time should be a numeric field with values 0-23 and 0-59.
- `info` - dropdown with no search.

There will probably be some extra stuff we need to decide, such as "will we only allow going through the input fields one-by-one".


# Back End
This part will be a bit messier as I'm not quite certain what the endpoints should be. I'll try my best :)

## Establishing some base specs
Let's use Python Flask for the backend. It will be hosted on `localhost:5530` (the punctuality rate was 55.3%).

## General initial thoughts
We will use the following endpoints:
- `/` - just the web interface itself.
- `POST /predict` - for predictions. Takes a JSON request, processes it and feeds it to the models. Returns the prediction for some `x` minutes and the confidence. Here, `x in [5, 6, 10, 15, 20, 25, 30]`.
- `GET /stations` - get the list of stations.
- `GET /lines` - get the list of lines.

For the `GET` endpoints, add URL parameters. Examples:
- `GET /stations?name=aac` only returns the stations with name that include `aac` (fuzzy search?).
- `GET /lines?eva_nr=8000320` only returns the lines that correspond to that station.
