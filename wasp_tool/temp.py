import pandas as pd
import itertools

import wasp_tool.utilities as utilities


celestrak = pd.read_csv("wasp_tool/data/celestrak.csv", header=0)
lyngsat = pd.read_csv("wasp_tool/data/lyngsat.csv", header=0)
altervista = pd.read_csv("wasp_tool/data/altervista.csv", header=0)
satbeams = pd.read_csv("wasp_tool/data/satbeams.csv", header=0)

path_data = utilities.get_project_path().joinpath('data')

# going to go with a simple title style of sat name 

sat_lst = list(itertools.chain(altervista["Satellite"], celestrak["Satellite"], satbeams["Satellite"], lyngsat["Satellite"]))

# loop through list of lists 
for i, ele in enumerate(sat_lst):
    sat = ele.title()
    sat = sat.replace("-", " ")
    sat_lst[i] = sat

print(len(sat_lst))

master_list = list(set(sat_lst))

print(len(master_list))

    # do we need to add it to master list and or master dict 



# to keep track of unique satellite names
# master_list = []

# don't worry about lyngsat special chars for now
#1) keep /
#2) separate ()


# altervista Series and West New

#master_list.extend(celestrak["Satellite"])
# #master_list.extend(celestrak["Extra Names"])
# master_list.extend(lyngsat["Satellite"])
# #master_list.extend(altervista["Satellite"])
# #master_list.extend(satbeams["Satellite"])
# #master_list.extend(satbeams["Extra Names"])

# print(master_list)

# for ele in master_list:
#      ele = ele.encode("utf-8")#.replace(u"\u0252", "*")

# #u'00CO'
# #str.decode("utf-8").replace(u"\u2022", "*")

# print(master_list)

# # to keep track of vehicles with multiple names
# master_dict = {}

# get sat other names
# for ele in master_list:
#     if ele in master_list:
#         temp = ele.split("(")
#         key = temp[0].strip()
#         vals = []
#         if "," in temp[1]:
        
#         else:
#             vals.append(temp[1].strip()[-1])
#         master_dict[key] = vals

# / are half owned satellites and should nto be separated 


# split into separate elements by comma
# master_list = [ele for item in master_list for ele in str(item).split(',')]

# # remove nans
# master_list = [x for x in master_list if str(x) != 'nan']

# # remove items containing non-ascii chars
# master_list = [x for x in master_list if str(x).isascii()]

# master_list = [x.replace("-", " ") for x in master_list]
# print(len(master_list))

# master_list = list(set([x.strip().lower() for x in master_list]))
# print(len(master_list))

dict_ = {"Satellite": master_list}

# split by / and also parenthesis 

# there is a + sign

# where are all 3 cases coming from

# also series case for altervista

# case of 513-515 altervista

# telstar 5. moving to 66 east orbital location
# weird satbeams case of extra information

utilities.save_dict_to_csv(path_data, dict_, "master.csv")