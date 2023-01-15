import os
import pandas as pd
import time
from tqdm import tqdm
from natsort import natsorted
from shutil import make_archive
#### This module changes the unique household IDs under the 'LCLid' column to numerical data ranging from 0 - 5566. ####
#### Then it seperates the 'Std' and 'ToU' customer types into dataframes and deletes the 'stdorToU' column.        ####
#### Finally, the dataframes are saved to seperate folders.

## Path for LCL data files and new files
#path_in_Big = "C:\\Users\\corso\OneDrive - University College London\\Documents\\ERBE CDT\\Energy Data Analysis\\LCL-FullData\\CC_LCL-FullData.csv"
path_in_Sml = "C:\\Users\\corso\OneDrive - University College London\\Documents\\ERBE CDT\\Energy Data Analysis\\Data\\Partitioned LCL Data\\Small LCL Data\\"
path_out = "C:\\Users\\corso\OneDrive - University College London\\Documents\\ERBE CDT\\Energy Data Analysis\\Data\\Condensed\\"
## Get LCL data files from path
directory = natsorted(os.listdir(path_in_Sml))
## Dataframe to add th unique Id's  to from each file
UID_Total = pd.DataFrame({'UID':[]})
start_time = time.time()

## Loop through each file, tqdm displays a progress bar
for file in tqdm(directory, desc = 'File progress'):
    ## Read in the data from each file into a pandas dataframe
    csvFile = pd.read_csv(path_in_Sml+file)

    ## Finding unique entries for customer group incase there is something other than 'Std' or 'ToU'
    group_types = pd.unique(csvFile["stdorToU"])
    ## Finding unique Household IDs
    UID = pd.DataFrame([pd.unique(csvFile["LCLid"])]).T
    UID.columns = ['UID']
    ## Adding new Household IDs to UID_Total
    UID_Total = pd.concat([UID_Total,UID], ignore_index=True).drop_duplicates()

    ## Looping over each unique Household ID
    for HH in range(len(UID)):
        ## Changing Household ID to corresponding index of UID_Total to give it a numerical value
        csvFile.loc[csvFile["LCLid"] == UID["UID"][HH], "LCLid"] = UID_Total[UID_Total['UID'] == UID['UID'][HH]].index.tolist()[0]

    ## Set to True to save files to new location. Used to test above code without saving
    block = False
    if not block:
        if "Std" in group_types:
            ## Add Household entries from 'Std' group to new Dataframe
            Control = csvFile[csvFile["stdorToU"] == "Std"]
            ## Delete 'stdorToU' column
            del Control["stdorToU"]
            ## Save new file to new location seperated by 'Std' group type
            Control.to_csv(path_out + 'Control\\' + file, index=False)

        if "ToU" in group_types:
            ## Add Household entries from 'ToU' group to new Dataframe
            ToUTariff = csvFile[csvFile["stdorToU"] == "ToU"]
            ## Delete 'stdorToU' column
            del ToUTariff["stdorToU"]
            ## Save new file to new location seperated by 'ToU' group type
            ToUTariff.to_csv(path_out + 'ToU\\' + file, index=False)

        ## Loop through customer group types incase there is something other than 'Std' or 'ToU'
        for group_type in group_types.tolist():
            if group_type not in ['Std','ToU']:
                ## If there is a customer group entry that is neither 'Std' nor 'ToU', then
                ## add Household entries from customer group belonging to neither 'Std' nor 'ToU' to new Dataframe
                Other = csvFile.loc[((csvFile['stdorToU'] != 'Std') & (csvFile['stdorToU'] != 'ToU'))]
                ## Save new Dataframe to file in new location seperated by group other than 'Std' or 'ToU'
                Other.to_csv(path_out + ' Other\\' + file, index=False)

print("It took ", round(time.time() - start_time,1), 'seconds to run this program')

start_time = time.time()
make_archive(path_out + "Control", 'zip', path_out + "Control")
make_archive(path_out + "ToU", 'zip', path_out + "ToU")

print("It took ", round(time.time() - start_time, 1), 'seconds to save the zip files')