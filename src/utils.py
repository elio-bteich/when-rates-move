import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def load_fred_csv(filepath, old_value_colname, new_value_colname, old_date_colname="observation_date", new_date_colname="date"):
    df = pd.read_csv(filepath)
    df[old_date_colname] = pd.to_datetime(df[old_date_colname])
    df.rename(columns={old_date_colname: new_date_colname, old_value_colname: new_value_colname}, inplace=True)
    return df[[new_date_colname, new_value_colname]]

def display_correlation_matrix(df, title="Correlation Matrix", figsize=(16, 12), annot=True, cmap="coolwarm", fmt=".2f"):
    # On suppose que le df possède une colonne "date"
    corr_matrix = df.drop(columns=["date"]).corr()

    # Heatmap
    plt.figure(figsize=figsize)
    sns.heatmap(corr_matrix, cmap=cmap, center=0, annot=annot, fmt=fmt)
    plt.title(title)
    plt.tight_layout()
    plt.show()

def trend_accuracy(y_true, y_pred):
    true_delta = np.sign(np.diff(y_true))
    pred_delta = np.sign(np.diff(y_pred))
    return np.mean(true_delta == pred_delta)