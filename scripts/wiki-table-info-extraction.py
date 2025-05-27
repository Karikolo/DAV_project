import os.path
import pandas as pd


def data_extraction(file, cleaning=0):

    if cleaning:
        data = pd.read_csv(file)
        data = data.replace(r'\[\w+\]', '', regex=True)
        data.to_csv(file)
    else:
        data = pd.read_csv(file, skiprows=1)
    data['Designated VOC '] = pd.to_datetime(data['Designated VOC '])
    data['Earliest sample '] = pd.to_datetime(data['Earliest sample '])
    # pd.to_datetime(data['Day'])
    return data



file_path = "../data/original_data/covid-variants-wikipedia-table.csv"
dataset = data_extraction(file_path)
print(dataset.columns)
print(dataset)