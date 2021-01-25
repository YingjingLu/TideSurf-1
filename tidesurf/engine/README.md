# Design of the Engine

The engine process the raw data and dump into some form of the data for analytics

There are different types of data engine depending on the algorithm for assist trading


## IO Engine
* Receive real time data from the data server
* Process historic raw data and dump the data
* load processed data to the calculation

## Computation Engine

**Also holds states for all the data being processed**

* Perform computation for displayed and selected stocks
* Perform computation for newly received real time data
* Perform computation for buy and stock indicators
* Perform computation for stock selection & rankings
* Perform computation for notifications
* Notify the middleware to push to clients

## Back test Engine

* Perform testing on profit/loss on historic data from computation
* Perform testing on effectiveness of indicators
* Perform testing on trade histories

## Server Middleware
**Hold server states for serving clients**

* Generate response for client requests
* Generate push for client page
* Maintainning online clients states



# Engine file 

```
.
picked_stocks.json
+-- 2020-12-23
|   +-- stock_list_2020-12-23.json
|   +-- 000001.pkl
|   +-- 000002.pkl
|   +-- 000003.pkl
|   +-- 000004.pkl
```



### Config file
picked_stocks.json
```json
[
    "000001",
    "000002",
    "000003",
    "000004"
]
```

# Data file
```
.
+-- 2020-12-23
|   +-- stock_list_2020-12-23.json
|   +-- 000001.pkl
|   +-- 000002.pkl
|   +-- 000003.pkl
|   +-- 000004.pkl

```

