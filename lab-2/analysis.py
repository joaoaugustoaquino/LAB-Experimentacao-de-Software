import pandas as pd

df = pd.read_csv("data/final_class.csv")

print("Medianas:")

print("CBO:", df["cbo"].median())
print("WMC:", df["wmc"].median())
print("LOC:", df["loc"].median())
print("LCOM:", df["lcom"].median())