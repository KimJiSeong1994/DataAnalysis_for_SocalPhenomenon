# =============================================== [ setting ] ==========================================================
import pandas as pd
import re
import glob
import os

file_list =  glob.glob("./data/*.csv")
everytime_data = pd.DataFrame(None, columns = ["Univ", "Categories", "obs_id", "Date", "Title", "Content"])
for path in file_list :
    data = pd.read_csv(path).iloc[:, 1:]
    everytime_data = pd.concat([everytime_data, data])

# everytime_data.to_csv("./total_everytime_data.csv", encoding = "utf-8")
# ============================================= [ preprocessing ] ======================================================

# def preprocess(df) :
#     # + todo [ Date info. parsing ] =======
#     everytime_data[everytime_data["Date"].str.contains("[0-9]{2}/[0-9]{2}")]["Date"] = everytime_data[everytime_data["Date"].str.contains("[0-9]{2}/[0-9]{2}")]["Date"].
