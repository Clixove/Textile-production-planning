## Functions

The production log is not well-organized, so we only use FDY orders and production log  of spinning for analysis. The time period of 2020-10-12 to 2020-11-21 is "current" and the time period before 2020-10-12 is historical.

We aim to provide production plan for current period based on statistics of historical period.

### 1. Data pre-processing

**Orders**

H company tracks the production process by batch identifier, so we group the orders into batches. In this step, we input the current orders and historical orders, and expect the script to output batches and historical batches.

The script to retrieve current orders is `sql/batches_FDY.sql` and that to retrieve historical order is `sql/batches_hist_FDY.sql`.

We group orders into batches with the following rules:

- Sum of textile's weight

- Sum of total price, where for each order, total price is "weight * price - voucher"

- Scarcity of specification, represented by the sum of the specification's weight in historical orders

- Average of textile's quality, weighted by textile's weight. we convert each quality to an ordinal variable by the following table.

| Start with | AAA  | AA   | A    | B    |
| ---------- | ---- | ---- | ---- | ---- |
| Value      | 4    | 3    | 2    | 1    |

The customer's level should be the same for orders in the same batch.

**Efficiency**

FDY textile involves in only spinning. We use historical production log of spinning to evaluate the efficiency of each assembly line. In this step, we input historical log of spinning and expect the script to output efficiency of each assembly line.

The efficiency of each shift is represented by "one minus the ratio of textile on abandoned bobbins over textile on all bobbins". The efficiency of each batch is that of the mean of all shifts producing textile in this batch.

The script to retrieve efficiency is `sql/spinning_efficiency_FDY.sql`.

### 2. Data enveloping analysis

With batches and efficiency, we aim to evaluate the batches. H company prefer to plan batches with higher utilities. We use data enveloping analysis to implement this step, which is a multi-input and multi-output operation method.

The script of this step is `1_utility_FDY.py`.

Following section 1, we retrieve 5 variables as the following table.

| Name                | Type | Description                                                  |
| ------------------- | ---- | ------------------------------------------------------------ |
| batch_id            | text | The identifier of this batch.                                |
| total_weight        | real | The total weight of textile in this batch.                   |
| total_price         | real | The total price of textile in this batch.                    |
| total_weight_inhist | real | The weight of textile in historical batches which have the same specification. |
| quality             | real | The mean of the quality of textile in this batch, weighted by the textile's weight. |
| customer_level      | real | The level of the customer who ordered textile in this batch. |

We construct a pipeline to perform data pre-processing.

1. For "total_weight" and "total_price", perform $x \to \ln x$.

2. For "total_weight_inhist", perform $x \to - \ln x$.

3. Denote $\bar x$ as the mean of each variable and $\sigma(x)$ as the standard deviation of each variable. For all variables, assign outliers which is smaller than $\bar x - 3 \sigma(x)$ to $\bar x - 3 \sigma(x)$. Assign outliers which is larger than $\bar x + 3 \sigma(x)$ to $\bar x + 3 \sigma(x)$.

4. For all variables, perform $x \to \frac{x - \min x}{\max x - \min x}$.

After pre-processing we obtain 5 variables, where "quality", "total_weight", and "total_weight_inhist" are input variables, and "customer_level" and "total_price" are output variables.

Assuming a total of $N$ historical batches, the value of the output indicators of a batch $i$ are $y_{i,1},y_{i,2},...,y_{i,k}$, and the input indicators are $x_{i,1},x_{i,2},...,x_{i,m}$.

The utility of batch $i$ is $θ_i$, which is the value of target function of

$$
\begin{aligned}
\max & \quad \theta_i = \frac{\sum_{j=1}^k y_{i,j} u_{i,j}}{\sum_{j=1}^m x_{i,j} v_{i,j}} \\
s.t. & \quad \forall n=1,2,...,N, \quad \theta_n = \frac{\sum_{j=1}^k y_{n,j} u_{n,j}}{\sum_{j=1}^m x_{n,j} v_{n,j}} \leq 1 \\
& \quad u_{i,1}, u_{i, 2}, ..., u_{i,k}, v_{i,1}, v_{i,2}, ..., v_{i, m} \geq 0
\end{aligned}
$$

We do linearization using the properties of 

$$
\frac{a}{b} \leq 1 \quad and \quad a,b \geq 0 \quad \Leftrightarrow \quad a-b \leq 0.
$$

Equivalently, we have

$$
\begin{aligned}
\max & \quad \theta_i = \sum_{j=1}^k y_{i,j}u_{i,j} \\
s.t. & \quad \forall n=1,2,...,N, \sum_{j=1}^k y_{n,j}u_{n,j} - \sum_{j=1}^m x_{n,j} v_{n,j} \leq 0 \\
& \quad \sum_{j=1}^m x_{i,j}v_{i,j} = 1 \\
& \quad u_{i,1}, u_{i, 2}, ..., u_{i,k}, v_{i,1}, v_{i,2}, ..., v_{i, m} \geq 0
\end{aligned}
$$

where $u, v$ are the internal parameters of the model, representing the weights of input and output indicators. According to the linear programming results of this model, the performance of each batch can be obtained, although the dimension of the input and output indicators are larger than 1.

### 3. Assignment

The efficiency of each spinning assembly line is 

$$
1 - \mathrm{\frac{abandoned\ bobbins}{all\ bobbins}}
$$

The quantile of efficiency for any current batch in the population of all historical batches is $q_e$. Similarly, we find the quantile of utility of batches is $q_u$ from section 2. 

We define a cost matrix $C = q_e q_u$, which represents the utility of each batch-line assignment. Also, we have some pre-processing steps

1. Sort the batches with descending order of utility.

2. Truncate the array of batches into blocks, where the number of batches in each of the blocks should be strictly smaller than the number of lines.

We use maximum assignment optimization to implement the allocation of  batches. If the batch $i$ is assigned to the line $j$, we have $x_{ij} = 1$; otherwise, we have $x_{ij} = 0$.

$$
\begin{aligned}
\max & \quad z = \sum_{i, j} C_{ij} x_{ij} \\
s.t. & \quad \sum_i x_{ij} = 1 \\
     & \quad \sum_j x_{ij} \leq 1 \\
     & \quad x_{ij} \in \{0, 1\}
\end{aligned}
$$

The first and second constraint means: each batch must be assigned to exactly 1 line, and each line can work on at most 1 batch.

The result of assignment $x_{ij}$ is the production plan. The efficiency of each batch is the average of each line's efficiency weighted by the total price of the batch. We use bootstrap to compare the assignment with random assignment.

## Citation

[1] Github - Mayorx/Hungarian-Algorithm: (Kuhn-Munkres) Numpy Implementation, Rectangular Matrix Is Supported (|X| <= |Y|). 100X100000 In 0.153 S. [Link](https://github.com/mayorx/hungarian-algorithm)

[2] Charnes, Abraham, William W. Cooper, and Edwardo Rhodes. "Measuring the efficiency of decision making units." *European journal of operational research* 2.6 (1978): 429-444. [Link](https://personal.utdallas.edu/~ryoung/phdseminar/CCR1978.pdf)