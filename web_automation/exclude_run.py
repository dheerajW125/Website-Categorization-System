import pandas as pd

samp_run = pd.read_csv("./Final_Results_From_URLS_0_to_4500.csv")
samp_all = pd.read_csv("./sample_all.csv")

# print(len(samp_2000))
# print(len(samp_all))

smp_all = {}

for s in samp_all["site"]:
    if s.strip() in smp_all:
        smp_all[s]+=1
    else:
        smp_all[s]=1

smp_all = {k:v for k,v in sorted(smp_all.items(), key=lambda item: item[1], reverse=True)}

dupli_list = []

for k,v in smp_all.items():
    if v==1: break
    dupli_list.append((k,v))

with open("duplicate_list.txt", "w") as f:
    for dl in dupli_list:
        f.write(str(dl)+"\n")

smp_sites = set([i.strip() for i in samp_run["url"]])

print("Total Unique Link:",len(smp_all))

for i in smp_sites:
    if i.strip() in smp_all.keys():
        del smp_all[i.strip()]

print("Links need to run:",len(smp_all))
        

df_new_sites = pd.DataFrame({"site": list(smp_all.keys())})
df_new_sites.to_csv("new_sites.csv", index=False)
print(f"Exported {len(smp_all.keys())} new sites to new_sites.csv")