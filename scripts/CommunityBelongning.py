import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('../data/SCMH_Data_En.csv')

df = df[df['Indicator Measure'].isin(['Percentage (%) of population aged 18 years and older who reported high community belonging'])]
df = df[df['Gender'].isin(['females','males'])]

pivot_df = df.groupby(['Geography', 'Gender'])['Prevalence'].mean().unstack()

pivot_df = pivot_df.sort_index()

ax = pivot_df.plot(kind='barh', figsize=(12, 8), color={'males': '#1f77b4', 'females': '#ff7f0e'})

plt.title('High Community Belonging by Gender across 13 Regions')
plt.xlabel('Prevalence (%)')
plt.ylabel('Region')
plt.legend(title='Gender')
plt.grid(axis='x', linestyle='--', alpha=0.6)
plt.tight_layout()

plt.savefig('../plots/ComunityBelonging.png')
