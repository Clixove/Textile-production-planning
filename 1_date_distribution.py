import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# %% Orders.
c = sqlite3.connect("data/H_company.db")
orders = pd.read_sql(con=c, sql="select date(created_time) as date, count(*) as count "
                                "from main.orders group by date")
c.close()

# %% Fill date range.
orders['date'] = pd.to_datetime(orders['date'])
orders_date_range = pd.date_range(start=orders['date'].min(), end=orders['date'].max())
orders_date_range = pd.DataFrame({'date': orders_date_range})
orders = pd.merge(orders, orders_date_range, 'outer', left_on='date', right_on='date',  sort=True)
orders['count'].fillna(value=0, inplace=True)
orders.sort_values(by='date', inplace=True, ignore_index=True, axis='rows')

# %% Map dates to weeks.
heatmap_data = np.full((7, orders.shape[0] // 7 + 1), fill_value=np.nan)
mondays = ([], [])
i = 0
for (j, row) in orders.iterrows():
    dow = row['date'].dayofweek
    if dow == 0:  # Monday
        i += (j > 0)  # if not the first week, week number + 1
        mondays[0].append(i)
        mondays[1].append(row['date'].date())
    heatmap_data[dow, i] = row['count']

# %% Draw dates distribution.
fig, ax = plt.subplots(figsize=(20, 5))
sns.heatmap(heatmap_data, vmin=0, vmax=50, cmap='Blues', ax=ax, annot=True, square=True, fmt='.0f', cbar=False)
ax.set_title('Orders\' Date Distribution Heatmap')
ax.set_xlabel('Weeks')
ax.set_ylabel('Days')
ax.set_xticks(ticks=np.array(mondays[0]) + 0.5, labels=mondays[1], rotation=90)
ax.xaxis.set_ticks_position('top')
ax.set_yticks(ticks=np.arange(7) + 0.5, labels=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], rotation=0)
fig.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.8)
fig.savefig("results/1_orders_date_heatmap.eps", dpi=600)
