import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# %% Constants.
n_boot = 1000

# %% Load data.
c = sqlite3.connect("data/H_company.db")
with open('sql/allocation_spinning_maxflow.sql') as f:
    sql_max_flow = f.read()
max_flow = pd.read_sql(con=c, sql=sql_max_flow)
max_flow_train = max_flow.loc[max_flow['is_training_set'] == 1, :]
max_flow_test = max_flow.loc[max_flow['is_training_set'] == 0, :]
with open('sql/allocation_spinning_baseline.sql') as f:
    sql_baseline = f.read()
baseline = pd.read_sql(con=c, sql=sql_baseline)
baseline_train = baseline.loc[baseline['is_training_set'] == 1, :]
baseline_test = baseline.loc[baseline['is_training_set'] == 0, :]
c.close()

# %% Training set.
def evaluate(plan: pd.DataFrame) -> float:
    return (plan['weight'] * plan['efficiency']).sum() / plan['weight'].sum()

rs = np.random.RandomState(seed=781120)
n = baseline_train.shape[0]
max_flow_e_train = evaluate(max_flow_train)
baseline_e_train_boot = np.full(n_boot, np.nan)
for i in range(n_boot):
    baseline_idx_train_boot = rs.choice(np.unique(baseline_train['order_id']), size=n)
    baseline_train_boot = baseline_train.loc[baseline_train['order_id'].isin(baseline_idx_train_boot), :]
    baseline_e_train_boot[i] = evaluate(baseline_train_boot)

# %% Testing set.
n = baseline_test.shape[0]
max_flow_e_test = evaluate(max_flow_test)
baseline_e_test_boot = np.full(n_boot, np.nan)
max_flow_e_test_boot = np.full(n_boot, np.nan)
for i in range(n_boot):
    baseline_idx_test_boot = rs.choice(np.unique(baseline_test['order_id']), size=n)
    baseline_test_boot = baseline_test.loc[baseline_test['order_id'].isin(baseline_idx_test_boot), :]
    baseline_e_test_boot[i] = evaluate(baseline_test_boot)

# %%
fig, axes = plt.subplots(ncols=2)
axes[0].boxplot([baseline_e_train_boot, max_flow_e_train], vert=True,
           labels=['Baseline\n(Training)', 'Max-flow\n(Training)'],
           medianprops={'color': '#808080'})
axes[0].set_ylabel('Weighted average efficiency')
axes[1].boxplot([baseline_e_test_boot, max_flow_e_test], vert=True,
           labels=['Baseline\n(Testing)', 'Max-flow\n(Testing)'],
           medianprops={'color': '#808080'})
fig.subplots_adjust(wspace=0.25)
fig.savefig("results/7_spinning_comparison_boxplot.eps")
plt.close(fig)
