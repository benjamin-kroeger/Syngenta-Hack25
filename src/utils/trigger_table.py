from datetime import timedelta
import pandas as pd




if __name__ == "__main__":
    # Load DataFrame
    df = pd.read_csv("../utils/issues_df.csv")
    df['date'] = pd.to_datetime(df['date'])  # Ensure date column is in datetime format

    # Compute triggers
    #trigger_df_v3 = check_trigger_v3(df)

    # Save to CSV
    #trigger_df_v3.to_csv("trigger_table.csv", index=False)
