# Function to extract data and turn it into a dataframe making it easier to work with
# input:
# - filename (including specific location of file) (note: remove the "-" that BERT adds)
# - device_id (if you want all devices, input 0)

# output: cleaned up dataframe file with three collumns: Time, Power [W], TimeDiff [s], Energy [Wh]

def data_cleaner(data_raw, 
                device_id=0, 
                modify_columns=True,
                drop_columns=True, 
                selected_columns = ['_time', 'device_id','analogInput_3'],
                calc_energy= True
                  ):
    import pandas as pd
    import numpy as np

    if device_id > 0:
        data = data_raw[data_raw['device_id'] == device_id]
    data = data_raw

    # data['_time'] = pd.to_datetime(data['_time'])
    data['_time'] = pd.to_datetime(data['_time'], errors='coerce')

    data = data.sort_values(by='_time')

    if modify_columns is True:
        data = data[selected_columns]
        data = data.rename(columns={'_time': 'Time', 'analogInput_3': 'Power'})

        data['Power'] = data['Power'] / 1000
    if calc_energy is True:
        data['TimeDiff'] = data['Time'].diff().dt.total_seconds()
    
        data['Energy'] = data['TimeDiff'] * data['Power']
        data['Energy'] = data['Energy'] / 3600
        
        data = data.drop(columns=['TimeDiff'])

    data = data.fillna(0)
    dropped_rows = data[data['Time'] == 0]
    if not dropped_rows.empty:
        print("Dropped rows:\n", dropped_rows)
    data = data[data['Time'] != 0]


    # data = data.sort_values(by='Time').reset_index(drop=True)
    
    return data