| Field                          | Type             | Description                                                                 |
|-------------------------------|------------------|-----------------------------------------------------------------------------|
| ID                            | string           | Unique identifier for journey                                               |
| eva_nr                        | int              | Unique identifier for train stops                                          |
| category                      | 1-7              | 1-2: primary junction<br>3: main stations from big and medium cities<br>4: metropolitan areas (high regional traffic)<br>5-6: small train stations<br>7: small simple train stops |
| path                          | string           | List of all previous stops before the current                              |
| station                       | string           | Station name                                                                |
| state, city, zip              | string, string, int | Address                                                                  |
| long, lat                     | float            | Geolocation                                                                 |
| arrival_plan, departure_plan | datetime         | Timestamp for planned arrival and departure                                |
| arrival_change, departure_change | datetime     | Timestamp for changed arrival and departure                                |
| arrival/departure_delay_m     | int              | Resulting delay in minutes                                                  |
| arrival/departure_delay_check | string           | Categorical identifier if a delay is present (>6 min)                      |
| info                          | string           | Info about the change                                                       |