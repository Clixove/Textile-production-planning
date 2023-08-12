import sqlite3
import matplotlib.pyplot as plt
from km_matcher import KMMatcher
import pandas as pd
import numpy as np
from tqdm import tqdm

# %% read data
con = sqlite3.connect('../data/H_company.db')
with open('../sql/spinning_efficiency_FDY.sql', 'r') as f:
    efficiency = pd.read_sql(f.read(), con)
con.close()

f, ax = plt.subplots()
ax.hist(efficiency['mean_efficiency'], bins=11, alpha=0.7, edgecolor='k', range=(0.95, 1))
ax.set_xlabel('Efficiency')
ax.set_ylabel('Count')
f.savefig('results/efficiency_DTY.svg')
plt.close(f)

# %% data pre-processing
utility = pd.read_pickle('raw/dea_orders_utility.pkl')
# Orders with large utility first
utility.sort_values(by='utility', axis=0, inplace=True, ascending=False)

eff_quantile = efficiency['mean_efficiency'].apply(lambda x: np.mean(efficiency['mean_efficiency'] <= x))
util_quantile = utility['utility'].apply(lambda x: np.mean(utility['utility'] <= x))
cost = eff_quantile.values[np.newaxis, :] * util_quantile.values[:, np.newaxis]

factory_names = efficiency.apply(lambda x: f"{x['factory_id']}-{x['line_id']}", axis=1).values
batch_names = utility['batch_id'].values

f, ax = plt.subplots(figsize=(24, 12))
im = ax.imshow(cost.T)
ax.set_yticks(np.arange(len(factory_names)), labels=factory_names)
ax.set_xticks(np.arange(len(batch_names)), labels=batch_names, rotation=90)
ax.set_ylabel('Lines')
ax.set_xlabel('Batches')
ax.figure.colorbar(im)
f.savefig('results/cost_matrix_heatmap_DTY.svg')
plt.close(f)

# %% max weight assignment
# Batch size should be smaller than number of factories
batch_size = 37
plan = np.zeros(shape=utility.shape[0])
for i in np.arange(utility.shape[0] / batch_size).astype(int):
    cost_i = cost[i * batch_size:(i + 1) * batch_size, :]
    matcher = KMMatcher(cost_i)
    matcher.solve()
    plan[i * batch_size:(i + 1) * batch_size] = matcher.xy
utility[['factory_id', 'line_id', 'efficiency']] = efficiency.loc[plan, :].values
total_efficiency = np.sum(utility['total_price'] * utility['efficiency']) / np.sum(utility['total_price'])

plan_array = np.zeros(shape=(batch_size, cost.shape[1]))
for i in np.arange(batch_size):
    plan_array[i, plan[i].astype('int')] = 1

f, ax = plt.subplots(figsize=(8, 8))
im = ax.imshow(plan_array.T, cmap='binary')
ax.set_yticks(np.arange(len(factory_names)), labels=factory_names)
ax.set_xticks(np.arange(batch_size), labels=batch_names[:batch_size], rotation=90)
ax.set_ylabel('Lines')
ax.set_xlabel('Batches')
f.subplots_adjust(left=0.2, right=0.95, top=0.95, bottom=0.2)
f.savefig('results/allocation_plan_heatmap_DTY.svg')
plt.close(f)

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

# %% save results
pd.to_pickle({'bootstrap': total_eff_boot,
              'observed': total_efficiency}, 'raw/allocating_bootstrap.pkl')
utility.to_excel('results/allocating_plan.xlsx', index=False)
