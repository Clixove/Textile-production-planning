import pandas as pd
import matplotlib.pyplot as plt
from pandas_profiling import ProfileReport
import sqlite3

# %% Distribution of utilities of the orders.
y_test_df = pd.read_pickle('raw/dea_orders_utility.pkl')
utility = y_test_df['utility']

f1, ax1 = plt.subplots()
ax1.hist(utility, bins=21, alpha=0.7, edgecolor='k')
ax1.set_xlabel('Utility')
ax1.set_ylabel('Count')
f1.savefig('results/distribution_utility_DTY.svg')
plt.close(f1)

# %% Bootstrap results of allocation plan.
allocating = pd.read_pickle('raw/allocating_bootstrap.pkl')
bootstrap = allocating['bootstrap']
observed = allocating['observed']

f2, ax2 = plt.subplots()
ax2.hist(bootstrap, bins=21, alpha=0.7, edgecolor='k',
         range=[0.95, 1], label='Bootstrap')
ax2.axvline(observed, color='red', linestyle="--", label='DEA + Hungarian')
ax2.set_xlabel('Efficiency')
ax2.set_ylabel('Count')
ax2.legend()
f2.savefig('results/bootstrap_DTY.svg')
plt.close(f2)

# %% Data profiling.
con = sqlite3.connect('../data/H_company.db')
with open('../sql/batches_FDY.sql', 'r') as f:
    orders = pd.read_sql(f.read(), con)
con.close()
profile = ProfileReport(orders, title='DEA data', plot={'dpi': 200, 'image_format': 'png'}, interactions=None)
profile = profile.to_html()
with open('results/dea_data_distribution.html', 'w') as f:
    f.write(profile)

orders_transformer = pd.read_pickle('raw/dea_ppr.pkl')
orders_processed = orders_transformer.transform(orders)
profile = ProfileReport(orders_processed, title='DEA data pre-processed', plot={'dpi': 200, 'image_format': 'png'},
                        interactions=None)
profile = profile.to_html()
with open('results/dea_data_processed_distribution.html', 'w') as f:
    f.write(profile)
