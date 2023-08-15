# Textile production planning

Decision making of textile production in H company: customer management and production tasks distribution

## Database

File `data/H_company.db` is a SQLite database, which includes records of textile (chemical fiber) production in H company.

**customers**

The quality of the customers measured by H company.

| Name        | Type    | Description                                                  |
| ----------- | ------- | ------------------------------------------------------------ |
| customer_id | text    | customer's identifier                                        |
| parts       | text    | the production that the customer buys; one company can have multiple records if buying multiple parts from H company |
| score       | integer | the score of the customer, ranges 1\~5                       |

**factories**

The factories managed by H company.

Each factory manages multiple batches. Each batch has the same production settings. Production tasks assigned to the same batch number must produce the same type of textile. I don't know the relationship between batch, factory, parts and specification in advance, but look up them from orders. (See the view "batches".)

| Name       | Type | Description          |
| ---------- | ---- | -------------------- |
| factory_id | text | Factory's identifier |

**orders**

The orders placed by customers. 

When an order is placed, H company will allocate a batch according to the specification. Then, H company checks whether there is stocked production. If there is, it will ship; if not, it will start producing. The batches distributed to 5 of the factories recorded efficiency. Among which, there are 40 batches in 2 factories records efficiency of spinning, and 218 batches in 3 factories records efficiency of texturing. The records of efficiency in spinning and texturing don't have common batches or factories. Other batches don't record efficiency.

| Name          | Type    | Description                                     |
| ------------- | ------- | ----------------------------------------------- |
| order_id      | integer | the order's identifier                          |
| created_time  | text    | datetime when the order is received             |
| customer_id   | text    | the customer's identifier who placed the order  |
| batch_id      | text    | the batch's identifier                          |
| factory_id    | text    | the factory's identifier who works on the order |
| weight        | real    | the weight of ordered textile (KG)              |
| parts         | text    | the production type of ordered textile          |
| specification | text    | the specification of ordered textile            |
| price         | real    | the price of 1KG ordered production (CNY 2020)  |
| voucher       | real    | the discount amount of this order (CNY 2020)    |
| quality       | real    | the quality of ordered textile, ranged 1\~5     |

**spinning**

Spinning produces FDY and POY from melted polyester, and wind the fibers on the bobbin. 

This table tracks to 40 batches in orders. **If one shift has multiple records, I have summarized the production and scrap rate. In this dataset, it's guaranteed `(batch_id, date, night)` is unique.**

| Name       | Type    | Description                                                  |
| ---------- | ------- | ------------------------------------------------------------ |
| batch_id   | text    | the batch's identifier                                       |
| date       | text    | the date of shift                                            |
| night      | integer | whether the night shift                                      |
| production | real    | the mass of total production (KG)                            |
| scrap_rate | real    | the mass of abandoned bobbin over total mass of bobbins, in percentage ranged 0\~100, efficiency is 100 / (100 + scrap_rate) |

**texturing**

Texturing produces DTY from the output of spinning.

This table tracks to 218 batches in orders. The efficiency of the same batch may change in different weather. **I have manually adjusted with concerns to correct the mistakes of workers recording the time range (from `start_time` to `end_time`). In this dataset, it's guaranteed the time ranges for each `batch_id` don't overlap.**

| Name       | Type | Description                                                  |
| ---------- | ---- | ------------------------------------------------------------ |
| batch_id   | text | the batch's identifier                                       |
| start_time | text | datetime when the record starts                              |
| end_time   | text | datetime when the record ends (machine isn't always open in the time range) |
| efficiency | real | efficiency coefficient on the machine, ranged 0\~1           |

## Tutorial

The script  [1_date_distribution.py](1_date_distribution.py)  shows the distribution of dates of the orders. I split orders in first 80% dates to training set, where `created_time <= '2020-09-06'`; and orders in last 20% dates to testing set, where `created_time > '2020-09-06'`. 

I use 3 metrics to represent the benefits of each order, and 3 other metrics to represent the cost of each order.

Benefits:

- Amount of money earned from the order.
- Customer score. (If the customer has a higher order, giving priority to this order is good to maintain valuable customer relationship.)
- Logarithmic of weight. (Larger orders are preferred to dilute fixed costs, such as selling fee and warehouse rental fee, of each order.)

Costs:

- Weight of raw materials. (Assume equal to weight of the production.)
- Quality of raw materials. (Higher-quality products need more costs of quality control.)
- Rarity of raw materials. (Rare specification adds more difficulty. Rarity is calculated based on weight of the production historically ordered.)

*Assumption: the values of benefits and costs of all orders should be positive. (Required by DEA)*

To find the formula that how I calculate the values, read these queries which retrieve the values of benefits and costs of each order:

- The training set  [orders_benefit_cost_train.sql](sql\orders_benefit_cost_train.sql)  
- The testing set  [orders_benefit_cost_test.sql](sql\orders_benefit_cost_test.sql)  

| Name       | Type    | Description                    |
| ---------- | ------- | ------------------------------ |
| order_id   | integer | the order's identifier         |
| b_payment  | real    | benefit: amount of money       |
| b_customer | integer | benefit: customer score        |
| b_scale    | real    | benefit: logarithmic of weight |
| c_material | real    | cost: weight of raw materials  |
| c_quality  | integer | cost: quality of raw materials |
| c_rarity   | real    | cost: rarity of raw materials  |

We use data enveloping analysis to measure the efficiency of each order.

### Data enveloping analysis

Assume the values of benefits of the current order are $y_{0,1}, ...,y_{0,p}$ where $k$ is the number of benefits. The values of costs of the current order are $x_{k, 1}, ... x_{k, q}$ where $m$ is the number of costs.

The efficiency of the current order is $\theta_0$, the solution of LP(1). Denote the orders in the training set are $i=1,...,N$.

$$
\begin{aligned}
\max & \quad \theta_0 = \frac{\sum_{j=1}^k y_{0,j} u_{0,j}}{\sum_{j=1}^m x_{0,j} v_{0,j}} \\
s.t. & \quad \theta_i = \frac{\sum_{j=1}^k y_{i,j} u_{i,j}}{\sum_{j=1}^m x_{i,j} v_{i,j}} \leq 1,
\forall i=1,...,N \\
& \quad u_{i,1}, ..., u_{i,k}, v_{i,1}, ..., v_{i, m} \geq 0
\end{aligned} \tag{1}
$$

Because $\theta_i \leq 1$ and  $\sum_{j=1}^k y_{i,j} u_{i,j} \geq 0, \sum_{j=1}^m x_{i,j} v_{i,j} \geq 0$, there is $\sum_{j=1}^k y_{i,j} u_{i,j} - \sum_{j=1}^m x_{i,j} v_{i,j} \leq 0$.

We do linearization using this properties, thus LP(1) is transformed to LP(2).

$$
\begin{aligned}
\max & \quad \theta_0 = \sum_{j=1}^k y_{0,j} u_{0,j} \\
s.t. & \quad \sum_{j=1}^k y_{i,j} u_{i,j} - \sum_{j=1}^m x_{i,j} v_{i,j} \leq 0,
\forall i=1,...,N \\
& \quad \sum_{j=1}^m x_{0,j} v_{0,j} = 1 \\
& \quad u_{i,1}, ..., u_{i,k}, v_{i,1}, ..., v_{i, m} \geq 0
\end{aligned} \tag{2}
$$

In LP(2), $\mathbf{u, v}$ are variables, representing the weights of benefits and costs. The solution of $\theta_0$ is efficiency of each order. In the training set, there is always $\theta_0 \in [0, 1]$; in the testing set, we use a clip function $\theta_0 \to \max(0, \min(\theta_0, 1))$ to force $\theta_0 \in [0, 1]$.



The results of orders' efficiency (in both training and testing set) are saved in DEA table in the database.

| Name       | Type    | Description                                           |
| ---------- | ------- | ----------------------------------------------------- |
| order_id   | integer | the order's identifier                                |
| efficiency | real    | DEA efficiency coefficient of this order, ranged 0\~1 |

In [ground truth](https://en.wikipedia.org/wiki/Ground_truth#Statistics_and_machine_learning), some orders are allocated to batches that I lose track of; other orders are allocated to batches, whose production is tracked in spinning and texturing table. The following analysis are focused only on those whose batches are tracked. To filter these orders, I provide the following queries:

- Tracked in spinning table, training set  [spinning_orders_train.sql](sql\spinning_orders_train.sql) 
- Tracked in spinning table, testing set  [spinning_orders_test.sql](sql\spinning_orders_test.sql) 
- Tracked in texturing table, training set  [texturing_orders_train.sql](sql\texturing_orders_train.sql) 
- Tracked in texturing table, testing set  [texturing_orders_test.sql](sql\texturing_orders_test.sql) 

On one hand, we have known the efficiency of orders by DEA, which represents the benefits of this order. The results have the following structure.

| Name       | Type    | Description                                             |
| ---------- | ------- | ------------------------------------------------------- |
| order_id   | integer | the order's identifier                                  |
| efficiency | real    | DEA efficiency coefficient of this order, ranged 0\~1   |
| weight     | integer | the weight of ordered product, rounded to integer (KG)  |
| batch_id   | text    | the ground truth: which batch the order is allocated to |

On the other hand, we can read the efficiency of each batch via its historical production records in spinning and texturing tables. The queries are written in  [texturing_batch_efficiency.sql](sql\texturing_batch_efficiency.sql) and  [spinning_batch_efficiency.sql](sql\spinning_batch_efficiency.sql)

| Name                     | Type | Description                                                  |
| ------------------------ | ---- | ------------------------------------------------------------ |
| batch_id                 | text | the batch's identifier                                       |
| scrap_rate \| efficiency | real | see the meaning in "Database" section: "spinning/scrap_rate" and "texturing/efficiency" |
| capacity                 | real | (not used) the total weight of production that the batch can handle in a specific period; simulated by the total weight the batch has produced in history |
| first_appear             | text | (not used) the date when the efficiency of the batch is first recorded |

*In the following context, I use min-cost flow algorithm to solve this assignment problem. Formally, I should consider the capacity of batches. However, I don't know the real capacity of these factories, and simulating the value by the total weight the batch has produced in history will make the assignment problem infeasible. So **I assume the capacity of each batch is infinity**, which means each batch can handle the production tasks of all allocated orders.*

The ground truth provides an production plan, which is adopted by the real H company and allocates the filtered orders to the trackable batches. I aim to find an optimal production plan to allocate these orders to batches, which achieves the maximum overall benefits under the criteria I already find: DEA efficiency of orders and efficiency of batches.

### Assignment problem

Denote the efficiency of each order $i=1,...,N$ is $p_i$ and the efficiency of each batch $j=1,...,M$ is $q_j$. Denote unit cost matrix $C_{ij} = - p_i q_j$. Denote the matrix $\mathbf{x}$ is the production plan, where $x_{ij} = 1$ if and only if order $i$ is assigned to batch $j$. Denote the weight of production in order $i$ is $w_{i}$, and its amount allocated to batch $j$ is the variable $a_{ij}$. The optimal production plan is the solution of mixed integer programming MIP(3).

$$
\begin{aligned}
\min & \quad z = \sum_{i=1}^N \sum_{j=1}^M C_{ij} x_{ij} a_{ij} \\
s.t. & \quad \sum_{j=1}^M x_{ij} \geq 1, \forall i=1,...,N                 & \text{assignment} \\
     & \quad \sum_{i=1}^N a_{ij} x_{ij} \leq +\infty, \forall j=1,...,N & \text{capacity (x)} \\
     & \quad \sum_{j=1}^M a_{ij} x_{ij} = w_i, \forall i=1,...,N        & \text{supply} \\
     & \quad x_{ij} \in \{0, 1\}
\end{aligned} \tag{3}
$$

*The capacity constraint is disabled in this case.*

According to [this article](https://developers.google.com/optimization/flow/assignment_min_cost_flow), such weighted assignment problem can be solved by min-cost flow algorithm.

The result $\mathbf{x}$ is the production plan, and $\mathbf{a}$ shows the weight of production of each allocation. With the optimal objective function, the overall efficiency is  $e = - {z^* \over \sum_{i=1}^N w_i}$. I compare the performance of our models with the production plan in real based on this metric.

