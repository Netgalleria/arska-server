# State numbering - example schema
State numbers are between 0 to 65535, where 0 is undefined 

## Node specific states 1-999
Node specific states are  not replicated from node to node.
Currently in use:

| State      | Description  |
| ------------- |------------- |
| 1 | always on  |
| 100 | hour 00, local time 00:00-00:59 |
| 101 | hour 01|
| 102...122 | hour 02... hour |
| 123 | hour 23, local time|
| 130 | päiväsähkö, daytime 07-22:, every day|
| 131 | yösähkö, 22-07, every day|
| 140 | kausisähkö talvipäivä, Nov 1- Mar 31 07-22, Mon-Sat|
| 141 | kausisähkö, other time|


## Local states 1000-9999
Local  states can depend on local conditions, e.g. local power production/consumption and net purchase from grid within netting period, which are sensored or metered locally. Property specific states can be replicated between Arska Nodes.

| State      | Description  |
| ------------- |------------- |
| 1001 | buying, more purchase production in current netting period  |
| 1005 | selling, more production than purchase in current netting period|
| 1006 | selling (like 1005), but enabled only before solar noon|
| 1007 | selling (like 1005), but enabled only after solar noon|
| 1010 | extra production, more production (read from inverter) than defined base load|
| 1011 | extra production, before solar noon|
| 1012 | extra production, after solar noon|


## Regional states 10000-65535
Price area specific states  depend on spot prices on the specific price area. FI-Finland is one price are, e.g. Norway and Sweden are divided to several price areas. These states are maintained by   [Arska Server instance](https://github.com/Netgalleria/arska-server/)(local or cloud based). Day-ahead price data is loaded from EntsoE transparency platform https://transparency.entsoe.eu/. 

| State      | Description  | Rule |
|----------|--------- |----|
| **10100-**  | States solar power forecast |  |
| 10101 | dark day coming (heat the boilers, there will be no cheap energy today) | solar24h<5 and hhmm >= '0000' and hhmm <'0700' |
| 10105 | pretty sunny day coming | solar24h>5 and hhmm >= '0000' and hhmm <'0700' |
| 10111 | sunny coming (do not overheat the boilers) | solar24h>10 and hhmm >= '0000' and hhmm <'0700' |
| **11000-**  | States based on day-ahead spot prices, fixed limits |  |
| 11010 | spot very low < 2 c/kWh | energyPriceSpot<2 |
| 11012 | spot low < 4 c/kWh | energyPriceSpot<4 |
| 11014 | spot moderate < 6 c/kWh | energyPriceSpot<6 |
| 11020 | spot pretty expensive > 10 c/kWh | energyPriceSpot>10 |
| 11021 | spot expensive > 15 c/kWh | energyPriceSpot>15 |
| 11022 | spot very expensive > 30 c/kWh | energyPriceSpot>30 |
| **11100-**  | best spot price ranks in various windows |  |
| **11110-**  | best spot price ranks in 6 h window |  |
| 11111 | cheapest 1 hours in coming 6 h | spotPriceRank24h==1 |
| 11112 | cheapest 2 hours coming 6 h | spotPriceRank24h<=2 |
| 11113 | cheapest 3 hour in coming 6 h | spotPriceRank6h<=3 |
| **11120-**  | best spot price ranks in 12 h window |  |
| 11121 | cheapest 1 h in 12 h | spotPriceRank12h==1 |
| 11122 | cheapest 2 h in 12 h | spotPriceRank12h<=2 |
| 11123 | cheapest 3 h in 12 h | spotPriceRank12h<=3 |
| 11124 | cheapest 4 h in 12 h | spotPriceRank12h<=4 |
| 11141 | Cheapest spot price in 24 h window | spotPriceRank24h==1 |
| 11142 | Cheapest 2 hours in 24 h window | spotPriceRank24h<=2 |
| 11143 | Cheapest 3 hours in 24 h window | spotPriceRank24h<=3 |
| 11144 | Cheapest 4 hours in 24 h window | spotPriceRank24h<=4 |
| 11145 | Cheapest 5 hours in 24 h window | spotPriceRank24h<=5 |
| 11146 | Cheapest 6 hours in 24 h window | spotPriceRank24h<=6 |
| 11156 | Spot price is low and now it is one of 6 cheapest hour in 24 h | energyPriceSpot<4.0 and spotPriceRank24h<=6 |







