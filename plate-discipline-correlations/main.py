from pybaseball import batting_stats
from plate_discipline_stats import Descriptors, PlateDisciplineStats, Outcomes
from sklearn.metrics import r2_score
import itertools
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def main():
    df = batting_stats(2023, 2024, ind=1, qual=100)

    # split by season
    df_2023 = df[df['Season'] == 2023]
    df_2024 = df[df['Season'] == 2024]
    
    # grab just the cols we need, from the enums 
    cols = ([x.value for x in Descriptors]+[x.value for x in PlateDisciplineStats]+[x.value for x in Outcomes])

    # produce_correlations(df_2023[cols])
    produce_correlations(df_2024[cols])

def produce_correlations(df):
    ratio_df = calculate_ratios(df)
    merged_df = df.merge(ratio_df, on='Name')

    # drop the original descriptor and independent variable columns
    merged_df = merged_df.drop((x.value for x in PlateDisciplineStats), axis=1)
    merged_df = merged_df.drop((x.value for x in Descriptors), axis=1)

    for outcome in Outcomes:
        print(f"\nCorrelation for outcome: {outcome.value} \n")

        # ---------------------------------------------------  R
        # correlations = merged_df.corr()[outcome.value]
        # print(correlations)

        # ---------------------------------------------------  R^2
        for pred in merged_df.columns[len(Outcomes):]:
            # purge infs and NaNs
            merged_df = merged_df.reset_index(drop=True)
            merged_df.replace([np.inf, -np.inf], np.nan, inplace=True)
            merged_df.dropna(inplace=True)

            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)

            y_true = merged_df[outcome.value]
            y_pred = merged_df[pred]

            r2 = r2_score(y_true, y_pred)
            print(f"R^2 for {outcome.value}/{pred}: {r2}")


def calculate_ratios(df):
    columns = [x.value for x in PlateDisciplineStats]
    combinations = itertools.permutations(columns, 2)
    ratios = []

    for pair in combinations:
        col1, col2 = pair
        ratio = df[col1] / df[col2]
        ratio_name = f"{col1}/{col2}"
        ratios.append(ratio.rename(ratio_name))

    # concatenate the ratios into a new df
    ratio_df = pd.concat(ratios, axis=1)
    ratio_df['Name'] = df['Name']

    return ratio_df

if __name__ == "__main__":
    main()