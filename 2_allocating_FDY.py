import sqlite3
from km_matcher import KMMatcher
import pandas as pd
import numpy as np
from tqdm import tqdm

# %% read data
con = sqlite3.connect('data/H_company.db')
with open('sql/spinning_efficiency_FDY.sql', 'r') as f:
    efficiency = pd.read_sql(f.read(), con)
con.close()

# %% data pre-processing
utility = pd.read_pickle('raw/dea_orders_utility.pkl')
# Orders with large utility first
utility.sort_values(by='utility', axis=0, inplace=True, ascending=False)

eff_quantile = efficiency['mean_efficiency'].apply(lambda x: np.mean(efficiency['mean_efficiency'] <= x))
util_quantile = utility['utility'].apply(lambda x: np.mean(utility['utility'] <= x))
cost = eff_quantile.values[np.newaxis, :] * util_quantile.values[:, np.newaxis]

# %% max weight assignment
# Batch size should be smaller than number of factories
batch_size = 20
plan = np.zeros(shape=utility.shape[0])
for i in np.arange(utility.shape[0] / batch_size).astype(int):
    cost_i = cost[i * batch_size:(i + 1) * batch_size, :]
    matcher = KMMatcher(cost_i)
    matcher.solve()
    plan[i * batch_size:(i + 1) * batch_size] = matcher.xy
utility[['factory_id', 'line_id', 'efficiency']] = efficiency.loc[plan, :].values
total_efficiency = np.sum(utility['total_price'] * utility['efficiency']) / np.sum(utility['total_price'])

# %% bootstrap
rng = np.random.default_rng(seed=403)
n_simulation = 1000
total_eff_boot = np.zeros(shape=n_simulation)
total_eff_free_boot = np.zeros(shape=n_simulation)
for j in tqdm(np.arange(n_simulation)):
    plan_boot = np.zeros(shape=utility.shape[0])
    eff_quantile_boot = eff_quantile.values.flatten()
    rng.shuffle(eff_quantile_boot)
    util_quantile_boot = util_quantile.values.flatten()
    rng.shuffle(util_quantile_boot)
    cost_boot = eff_quantile_boot[np.newaxis, :] * util_quantile_boot[:, np.newaxis]
    for i in np.arange(utility.shape[0] / batch_size).astype(int):
        cost_boot_i = cost_boot[i * batch_size:(i + 1) * batch_size, :]
        matcher = KMMatcher(cost_boot_i)
        matcher.solve()
        plan_boot[i * batch_size:(i + 1) * batch_size] = matcher.xy
    utility_boot = utility.copy()
    utility_boot[['factory_id', 'line_id', 'efficiency']] = efficiency.loc[plan_boot, :].values
    total_eff_boot[j] = np.sum(utility_boot['total_price'] * utility_boot['efficiency']) / \
                        np.sum(utility_boot['total_price'])

    plan_free_boot = np.floor(rng.uniform(low=0, high=efficiency.shape[0], size=utility.shape[0]))
    utility_free_boot = utility.copy()
    utility_free_boot[['factory_id', 'line_id', 'efficiency']] = efficiency.loc[plan_boot, :].values
    total_eff_free_boot[j] = np.sum(utility_boot['total_price'] * utility_boot['efficiency']) / \
                             np.sum(utility_boot['total_price'])

# %% save results
pd.to_pickle({'bootstrap-allocating': total_eff_boot,
              'bootstrap-utility': total_eff_free_boot,
              'observed': total_efficiency}, 'raw/allocating_bootstrap.pkl')
utility.to_excel('results/allocating_plan.xlsx', index=False)
