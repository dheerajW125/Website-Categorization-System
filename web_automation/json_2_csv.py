import json
import pandas as pd

with open("./Final_Results_From_URLS_0_to_4500.json", "r") as f:
    data = json.load(f)

pd.DataFrame(data).to_csv("Final_Results_From_URLS_0_to_4500.csv", index=False)