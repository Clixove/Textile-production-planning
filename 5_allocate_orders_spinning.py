from min_cost_flow import allocate
import pandas as pd
import sqlite3

# %% Load data.
c = sqlite3.connect("data/H_company.db")
with open('sql/spinning_orders_train.sql') as f:
    sql_orders_train = f.read()
with open('sql/spinning_orders_test.sql') as f:
    sql_orders_test = f.read()
orders_train = pd.read_sql(con=c, sql=sql_orders_train)
orders_test = pd.read_sql(con=c, sql=sql_orders_test)
with open('sql/spinning_batch_efficiency.sql') as f:
    sql_batches = f.read()
batches = pd.read_sql(con=c, sql=sql_batches)

# %% Train the model.
efficiency_train, plan_train = allocate(
    order_id=orders_train['order_id'].values,
    order_weight=orders_train['weight'].values,
    order_efficiency=orders_train['efficiency'].values,
    batch_id=batches['batch_id'].values,
    batch_efficiency=100 / (100 + batches['scrap_rate'].values),
    round_n_decimal=4
)

# %% Predict on the testing set.
efficiency_test, plan_test = allocate(
    order_id=orders_test['order_id'].values,
    order_weight=orders_test['weight'].values,
    order_efficiency=orders_test['efficiency'].values,
    batch_id=batches['batch_id'].values,
    batch_efficiency=100 / (100 + batches['scrap_rate'].values),
    round_n_decimal=4
)

# %% Export.
with open('results/5_average_efficiency.txt', 'w') as f:
    f.write('Average efficiency\n'
            f'Min-cost flow (training): {efficiency_train}\n'
            f'Min-cost flow (testing): {efficiency_test}\n')
plan = pd.concat([plan_train, plan_test], axis='rows', ignore_index=True)
plan.to_sql(name='min_cost_flow_spinning', con=c, if_exists='replace', index=False)

# %% Post-process.
c.close()
