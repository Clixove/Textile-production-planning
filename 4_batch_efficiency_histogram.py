import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
import matplotlib

c = sqlite3.connect("data/H_company.db")
with open('sql/spinning_batch_efficiency.sql') as f:
    sql_batch_efficiency = f.read()
spinning = pd.read_sql(sql=sql_batch_efficiency, con=c)
c.close()

fig, ax = plt.subplots()
ax.hist(spinning['scrap_rate'], bins=11, edgecolor='black')
ax.set_xlabel('Efficiency')
ax.set_ylabel('Count')
ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter())
ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
fig.savefig('results/4_efficiency_histogram.eps')
plt.close(fig)
