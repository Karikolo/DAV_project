import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


def data_extraction(file, cleaning=0):

    if cleaning:
        data = pd.read_csv(file)
        data = data.replace(r'\[\w+\]', '', regex=True)
        data.iloc[0] = data.iloc[0].replace('\n', ' ', regex=True)
        for _, row in data.iterrows():
            row = row.str.strip()
        print(data.iloc[0])
        data.to_csv(file)
    else:
        data = pd.read_csv(file, skiprows=1)
        data['Designated VOC'] = pd.to_datetime(data['Designated VOC'])
        data['Earliest sample'] = pd.to_datetime(data['Earliest sample'])
        # pd.to_datetime(data['Day'])
    return data


'''
Plot with:
print(variants_df.columns)
print(variants_df)

file_path = "../data/original_data/covid-variants-wikipedia-table.csv"
variants_df = data_extraction(file_path)
# Generate unique, consistent colors for each variant
cmap = plt.cm.get_cmap('tab10')
color_map = {variant: cmap(i % 10) for i, variant in enumerate(variants_df['WHO label'].unique())}
variants_df = variants_df[variants_df['WHO label'] != "Alpha"]
fig = plt.figure(figsize=(12,6))
for i, row in variants_df.iterrows():
    variant = row['WHO label']
    early_date = row['Earliest sample']
    voc_date = row['Designated VOC']
    place = row['First outbreak']
    color = color_map[variant]
    light_color = mcolors.to_rgba(color, alpha=0.3)  # same color, lighter

    # Vertical line for earliest sample
    plt.axvline(early_date, color=color, linestyle='--', linewidth=2)
    plt.text(
        early_date,
        plt.ylim()[1] * (0.8 + 0.15*(i%2)),  # place text near top
        f"{variant}\n{place}\n{early_date.date()}",
        rotation=90, verticalalignment='top',
        color=color, fontsize=9
    )

    # Vertical line for VOC designation
    plt.axvline(voc_date, color=light_color, linestyle='--', linewidth=2)
    plt.text(
        voc_date,
        plt.ylim()[1] * (0.95 - 0.15*(i%2)),  # place text near top, +/- 5% for visibility
        f"{variant}\n{voc_date.date()}",
        rotation=90, verticalalignment='top',
        color=color, fontsize=9
    )

plt.show()
'''