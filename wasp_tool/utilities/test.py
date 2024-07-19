
import pandas as pd

df = pd.read_csv("../WASP/wasp_tool/utilities/sats.csv", header=0)

norad_numbers = int(df[df["Name"].str.contains("TDRS 3", na=False)]["NORAD ID"][0])


print(norad_numbers)
