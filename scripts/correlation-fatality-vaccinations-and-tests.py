import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import itertools
import sys
import os

# Set file paths
scripts_dir = os.getcwd()
project_path = os.path.join(scripts_dir, "../")
data_path = f"{project_path}/data/original_data/"
files = {
    "cfr": "case-fatality-rate-of-covid-19.csv",
    "tests": "cumulative-covid-19-tests-per-1000-people.csv",
    "vaccine_doses": "covid-19-vaccine-doses-people-with-at-least-one-dose-people-with-a-full-initial-protocol-and-boosters-per-100-people.csv"
}
if not os.path.exists(os.path.join(project_path, "plots/fatality_vs_vaccines")): os.mkdir(os.path.join(project_path, "plots/fatality_vs_vaccines"))

try:
    save = sys.argv[1]
except:
    save = 0
    print("Add argument '0' if you want to show interactively, '1' to save to file. Default is 0.")

# Load and filter for Canada
def load_canada_data(filename, columns=None):
    df = pd.read_csv(data_path + filename)
    df = df[df["Entity"] == "Canada"]
    df = df[["Day"] + ([col for col in df.columns if col != "Entity" and col != "Code" and col != "Day"] if columns is None else columns)]
    df["Day"] = pd.to_datetime(df["Day"])
    return df

# Load datasets
df_cfr = load_canada_data(files["cfr"])
df_tests = load_canada_data(files["tests"])
vaccine_cols = [
    "COVID-19 doses (cumulative, per hundred)",
    "People vaccinated (cumulative, per hundred)",
    "People fully vaccinated (cumulative, per hundred)",
    "Booster doses (cumulative, per hundred)"
]
df_vaccines = load_canada_data(files["vaccine_doses"], columns=vaccine_cols)

# Merge all datasets on Day
df_merged = df_cfr.merge(df_tests, on="Day", how="inner", suffixes=('', '_tests'))
df_merged = df_merged.merge(df_vaccines, on="Day", how="inner")

# Clean vaccine column names
clean_vaccine_cols = [col.replace(" (cumulative, per hundred)", "") for col in vaccine_cols]

# Assign cleaned column names
df_merged.columns = ['Day', 'Case Fatality Rate', 'COVID Tests per 1000'] + clean_vaccine_cols

# Drop rows with missing values
df_clean = df_merged.dropna()


# Assume df_clean has already been created and contains 'Day' + all numeric columns
variables = df_clean.columns.drop(['Day'])  # Exclude 'Day'

# Create all unique variable pairs (A, B) where A ≠ B
pairs = list(itertools.combinations(variables, 2))


scaler = MinMaxScaler()
df_scaled = df_clean.copy()
df_scaled[variables] = scaler.fit_transform(df_clean[variables])

# Plot each pair
for var1, var2 in pairs:
    plt.figure(figsize=(10, 5))

    # Plot both lines on the same axes
    plt.plot(df_scaled['Day'], df_scaled[var1], label=var1, color='blue')
    plt.plot(df_scaled['Day'], df_scaled[var2], label=var2, color='red', alpha=0.7)

    plt.title(f'{var1} vs {var2} Over Time')
    plt.xlabel('Date')
    plt.ylabel('Value (normalized scale recommended if needed)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    if save!='0':
        plt.savefig(f"../plots/fatality_vs_vaccines/{var1}_vs_{var2}.png", dpi=300)
    else:
        plt.show()


# Compute correlation matrix
corr_matrix = df_scaled.drop(columns="Day").corr()

# Plot
'''
A clear downward line: this suggests higher full vaccination rates are associated with lower CFR.
Scattered points with no clear trend: little to no linear relationship.
Wide spread around the line: indicates weak or noisy correlation — other factors may be influencing CFR.
'''
for column in ['COVID Tests per 1000'] + clean_vaccine_cols:
    sns.lmplot(data=df_clean, x=column, y='Case Fatality Rate', aspect=1.5)
    plt.title(f'Case Fatality Rate vs {column}')

    # Display correlation
    corr_coef = corr_matrix.loc['Case Fatality Rate', column]
    corr_text = f'correlation = {corr_coef:.2f}'
    plt.gca().text(0.75, 0.95, corr_text, transform=plt.gca().transAxes,
                   fontsize=12, verticalalignment='top',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))

    plt.tight_layout()
    if save!='0':
        plt.savefig(f"../plots/fatality_vs_vaccines/fatality_rate_vs_{column}_regression.png", dpi=300)
    else:
        plt.show()
plt.close()

# Heatmap all vs all
plt.figure(figsize=(10, 8))  # Set figure size explicitly
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", square=True)
plt.xticks(rotation=45, ha='right')
plt.title("Correlation of Case Fatality Rate with Vaccination and Testing Metrics in Canada", pad=20)
plt.tight_layout()


if save != '0':
    plt.savefig(f"../plots/fatality_vs_vaccines/fatality_rate_vs_testing_and_vaccination_metrics_heatmap.png", dpi=300, bbox_inches='tight')
else:
    plt.show()

