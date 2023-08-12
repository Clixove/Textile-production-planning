import sqlite3
import pandas as pd
from math import log
import pickle
from DEA import DEA

# %% Load training set.
c = sqlite3.connect("data/H_company.db")
c.create_function("log", 2, lambda base, x: log(x, base))
with open("sql/orders_benefit_cost_train.sql") as f:
    sql_orders_train = f.read()
with open("sql/orders_benefit_cost_test.sql") as f:
    sql_orders_test = f.read()
orders_train = pd.read_sql(sql=sql_orders_train, con=c)
orders_test = pd.read_sql(sql=sql_orders_test, con=c)

# %% Fit DEA model.
dea = DEA(output_cols=['b_payment', 'b_customer', 'b_scale'],
          input_cols=['c_material', 'c_quality', 'c_rarity'])
orders_train['efficiency'] = dea.fit_transform(orders_train)
orders_test['efficiency'] = dea.transform(orders_test)
efficiency = pd.concat([orders_train[['order_id', 'efficiency']], orders_test[['order_id', 'efficiency']]],
                       axis='rows', ignore_index=True)

# %% Export.
efficiency.to_sql(name='DEA', con=c, if_exists='replace', index=False)
c.close()
