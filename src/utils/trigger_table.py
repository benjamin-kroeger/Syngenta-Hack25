from datetime import timedelta
import pandas as pd

def check_trigger_v3(df):
    results = []

    # Ensure sorting within the function
    df = df.sort_values(by=['crop', 'measure', 'date'])

    # Group by crop and measure
    for (crop, measure), group in df.groupby(['crop', 'measure']):
        # Directly check the condition for the entire group
        trigger = (group['value'] >= 9).any() or (group['value'] >= 6).sum() >= 4

        results.append({'crop': crop, 'measure': measure, 'trigger': trigger})

    return pd.DataFrame(results)

if __name__ == "__main__":
    # Load DataFrame
    df = pd.read_csv("../utils/issues_df.csv")
    df['date'] = pd.to_datetime(df['date'])  # Ensure date column is in datetime format

    # Compute triggers
    trigger_df_v3 = check_trigger_v3(df)

    # Save to CSV
    trigger_df_v3.to_csv("trigger_table.csv", index=False)
