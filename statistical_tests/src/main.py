import pandas as pd
from scipy import stats
import argparse

def find_data_start_row(file_path):
    try:
        df_peek = pd.read_csv(file_path, header=0, usecols=['Finished'])
        first_data_index = df_peek['Finished'].eq('TRUE').idxmax()
        rows_to_skip = range(1, first_data_index + 1)
        return list(rows_to_skip)
    except (ValueError, KeyError, FileNotFoundError):
        return [1, 2]

def convert_likert_to_numeric(df, columns, likert_mapping):

    for col in columns:
        if col in df.columns:
            # lowercase
            df[col] = df[col].astype(str).str.lower().map(likert_mapping)
    return df

def main():
    parser = argparse.ArgumentParser(description="Perform statistical analysis on a CSV file.")
    parser.add_argument("file_path", help="Path to the CSV file.")
    parser.add_argument("--likert", action="store_true", help="Convert 5-point agreement Likert scale to numeric.")
    parser.add_argument("--likert2", action="store_true", help="Convert 5-point satisfaction Likert scale to numeric.")
    args = parser.parse_args()

    # load it
    try:
        rows_to_skip = find_data_start_row(args.file_path)
        data = pd.read_csv(args.file_path, header=0, skiprows=rows_to_skip)
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return

    # what test?
    print("Select the statistical test you want to perform:")
    print("1. One-way ANOVA")
    print("2. Friedman Test")
    test_choice = input("Enter the number of your choice: ")

    if test_choice == '1':
        # Ask for the columns to analyze
        columns_input = input("Enter the column names separated by commas: ")
        columns = [col.strip() for col in columns_input.split(',')]

        # convert if using likert
        if args.likert:
            likert_mapping_1 = {
                'strongly disagree': 1,
                'somewhat disagree': 2,
                'neither agree nor disagree': 3,
                'somewhat agree': 4,
                'strongly agree': 5
            }
            data = convert_likert_to_numeric(data, columns, likert_mapping_1)
        elif args.likert2:
            likert_mapping_2 = {
                "extremely difficult": 1,
                "somewhat difficult": 2,
                "neither easy nor difficult": 3,
                "somewhat easy": 4,
                "extremely easy": 5,
            }
            data = convert_likert_to_numeric(data, columns, likert_mapping_2)

        # one-way ANOVA
        try:
            valid_columns = [col for col in columns if col in data.columns]
            if len(valid_columns) != len(columns):
                missing = set(columns) - set(valid_columns)
                print(f"Warning: The following columns were not found and will be ignored: {', '.join(missing)}")
            
            if len(valid_columns) < 2:
                print("Error: ANOVA requires at least two columns of data.")
                return

       
            print("\n--- Descriptive Statistics ---")
            for col in valid_columns:
                numeric_col = pd.to_numeric(data[col], errors='coerce').dropna()
                if not numeric_col.empty:
                    mean = numeric_col.mean()
                    std_dev = numeric_col.std()
                    count = numeric_col.count()
                    print(f"Column: {col} | Mean: {mean:.2f} | Std Dev: {std_dev:.2f} | Count: {count}")
            print("---------------------------\n")

            groups = [data[col].dropna() for col in valid_columns]
            f_statistic, p_value = stats.f_oneway(*groups)
            print(f"F-statistic: {f_statistic}, p-value: {p_value}")
        except Exception as e:
            print(f"Error performing ANOVA: {e}")
    elif test_choice == '2':
        columns_input = input("Enter the column names for the ranked data, separated by commas: ")
        columns = [col.strip() for col in columns_input.split(',')]

        try:
            # make sure all the cols exist
            valid_columns = [col for col in columns if col in data.columns]
            if len(valid_columns) != len(columns):
                missing = set(columns) - set(valid_columns)
                print(f"Warning: The following columns were not found and will be ignored: {', '.join(missing)}")
            
            if len(valid_columns) < 2:
                print("Error: The Friedman test requires at least two columns of data.")
                return

            # friedman
            ranked_data = data[valid_columns].dropna()

            if len(ranked_data) == 0:
                print("Error: No complete sets of ranked data found after removing rows with missing values.")
                return

            groups = [ranked_data[col] for col in valid_columns]
            statistic, p_value = stats.friedmanchisquare(*groups)
            print(f"Friedman test statistic: {statistic}, p-value: {p_value}")
        except Exception as e:
            print(f"Error performing Friedman test: {e}")
    else:
        print("Invalid choice. Please select a valid test.")

if __name__ == "__main__":
    main()