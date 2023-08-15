import matplotlib.pyplot as plt
import pandas as pd
import sqlite3

c = sqlite3.connect("data/H_company.db")
efficiency = pd.read_sql(sql="select efficiency from DEA", con=c)
c.close()

fig, ax = plt.subplots()
ax.hist(efficiency, bins=21, edgecolor='black')
ax.set_xlabel('Efficiency')
ax.set_ylabel('Count')
fig.savefig('results/3_efficiency_histogram.eps')
plt.close(fig)
