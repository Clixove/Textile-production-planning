# Textile production planning

Decision making of textile production in H company: customer management and production tasks distribution

## Database

This database includes records of textile (chemical fiber) production in H company.

**customers**

The quality of the customers measured by H company.

| Name        | Type | Description                                                  |
| ----------- | ---- | ------------------------------------------------------------ |
| customer_id | text | customer's identifier                                        |
| parts       | text | the production that the customer buys; one company can have multiple records if buying multiple parts from H company |
| score       | text | the score of the customer, ranges 1\~5                       |

**factories**

The factories managed by H company.

Each factory manages multiple batches. Each batch has the same production settings. Production tasks assigned to the same batch number must produce the same type of textile. I don't know the relationship between batch, factory, parts and specification in advance, but look up them from orders. (See the view "batches".)

| Name         | Type | Description                                                |
| ------------ | ---- | ---------------------------------------------------------- |
| factory_id   | text | Factory's identifier                                       |
| factory_name | text | Factory's name (processed in consider of business privacy) |

**orders**

The orders placed by customers. 

When an order is placed, H company will allocate a batch according to the specification. Then, H company checks whether there is stocked production. If there is, it will ship; if not, it will start producing. The batches distributed to 5 of the factories recorded efficiency. Among which, there are 40 batches in 2 factories records efficiency of spinning, and 218 batches in 3 factories records efficiency of texturing. The records of efficiency in spinning and texturing don't have common batches or factories. Other batches don't record efficiency.

| Name          | Type | Description                                     |
| ------------- | ---- | ----------------------------------------------- |
| order_id      | text | the order's identifier                          |
| created_time  | text | datetime when the order is received             |
| customer_id   | text | the customer's identifier who placed the order  |
| batch_id      | text | the batch's identifier                          |
| factory_id    | text | the factory's identifier who works on the order |
| weight        | real | the weight of ordered textile (KG)              |
| parts         | text | the production type of ordered textile          |
| specification | text | the specification of ordered textile            |
| price         | real | the price of 1KG ordered production (CNY 2020)  |
| voucher       | real | the discount amount of this order (CNY 2020)    |
| quality       | real | the quality of ordered textile, ranged 1\~5     |

**spinning**

Spinning produces FDY and POY from melted polyester, and wind the fibers on the bobbin. 

This table tracks to 40 batches in orders. **If one shift has multiple records, I have summarized the production and scrap rate. In this dataset, it's guaranteed `(batch_id, date, night)` is unique.**

| Name       | Type    | Description                                                  |
| ---------- | ------- | ------------------------------------------------------------ |
| batch_id   | text    | the batch's identifier                                       |
| date       | text    | the date of shift                                            |
| night      | integer | whether the night shift                                      |
| production | real    | the mass of total production (KG)                            |
| scrap_rate | real    | the mass of abandoned bobbin over total mass of bobbins, in percentage ranged 0\~100 |

**texturing**

Texturing produces DTY from the output of spinning. 

This table tracks to 218 batches in orders. The efficiency of the same batch may change in different weather. **I have manually adjusted with concerns to correct the mistakes of workers recording the time range (from `start_time` to `end_time`). In this dataset, it's guaranteed the time ranges for each `batch_id` don't overlap.**

| Name       | Type | Description                                                  |
| ---------- | ---- | ------------------------------------------------------------ |
| batch_id   | text | the batch's identifier                                       |
| start_time | text | datetime when the record starts                              |
| end_time   | text | datetime when the record ends (machine isn't always open in the time range) |
| efficiency | real | efficiency coefficient on the machine, ranged 0\~1           |
