import sqlite3
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from dea import DEA
from pre_processing import *

# %% read historical orders
con = sqlite3.connect('data/H_company.db')
with open('sql/batches_hist_FDY.sql', 'r') as f:
    orders_h = pd.read_sql(f.read(), con)
with open('sql/batches_FDY.sql', 'r') as f:
    orders = pd.read_sql(f.read(), con)
con.close()

# %% pre-processing
transformer = Pipeline([
    ('drop_batch_id', DropColumn(cols=['batch_id'])),
    ('force_float_64', ForceFloat64()),
    ('ln_x', ApplyColumn(cols=['total_weight', 'total_price', 'total_weight_inhist'],
                         func=np.log, new_cols_prefix='log', inplace=True)),
    ('reverse_scarcity', ApplyColumn(cols=['total_weight_inhist_log'],
                                     new_cols=['scarcity'], func=float.__neg__, inplace=True)),
    ('remove_abnormal', GaussianAbnormal(cols=['quality', 'customer_level', 'total_weight_log', 'total_price_log',
                                               'scarcity'])),
    ('zipping', MinMaxScaler(clip=True)),
    ('sort_in_out', ArrayExchangeColumn(col_order=[0, 2, 4, 1, 3],
                                        col_names=['in_quality', 'in_weight', 'in_scarcity', 'out_customer_level',
                                                   'out_price']))
])
x_train = transformer.fit_transform(orders_h)
pd.to_pickle(transformer, 'raw/dea_ppr.pkl')

# %% data enveloping analysis - fit
dea = DEA(input_cols=['in_quality', 'in_weight', 'in_scarcity'],
          output_cols=['out_customer_level', 'out_price'])
dea.fit(x_train)
pd.to_pickle(dea, 'raw/dea_mdl.pkl')

# %% data enveloping analysis - predict
x_test = transformer.transform(orders)
y_test = dea.predict(x_test)
y_test_df = pd.DataFrame({'batch_id': orders['batch_id'], 'total_price': orders['total_price'], 'utility': y_test})
pd.to_pickle(y_test_df, 'raw/dea_orders_utility.pkl')
