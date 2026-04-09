import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/final_class.csv")


df = df[(df["loc"] > 0) & (df["wmc"] > 0)]


loc_limit = df["loc"].quantile(0.95)
wmc_limit = df["wmc"].quantile(0.95)

df_loc = df[df["loc"] <= loc_limit]
df_wmc = df[df["wmc"] <= wmc_limit]
df_scatter = df[(df["loc"] <= loc_limit) & (df["wmc"] <= wmc_limit)]

plt.figure()
plt.hist(df_loc["loc"], bins=50)
plt.title("Distribuição de LOC")
plt.xlabel("Linhas de Código")
plt.ylabel("Frequência")
plt.show()

plt.figure()
plt.hist(df_wmc["wmc"], bins=50)
plt.title("Distribuição de WMC")
plt.xlabel("Complexidade")
plt.ylabel("Frequência")
plt.show()


plt.figure()
plt.scatter(df_scatter["loc"], df_scatter["wmc"], alpha=0.3)
plt.title("LOC vs WMC")
plt.xlabel("LOC")
plt.ylabel("WMC")
plt.show()