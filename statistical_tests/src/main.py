import pandas as pd
from scipy import stats
import argparse

def convert_likert_to_numeric(df, columns):
    """
    Converts specified columns with Likert scale strings to numeric values.
    Uses a default 5-point Likert scale mapping.
    """
    likert_mapping = {
        'strongly disagree': 1,
        'somewhat disagree': 2,
        'neither agree nor disagree': 3,
        'somewhat agree': 4,
        'strongly agree': 5
    }
    for col in columns:
        if col in df.columns:
            # Convert column to lowercase strings before mapping
            df[col] = df[col].astype(str).str.lower().map(likert_mapping)
    return df

def main():
    parser = argparse.ArgumentParser(description="Perform statistical analysis on a CSV file.")
    parser.add_argument("file_path", help="Path to the CSV file.")
    parser.add_argument("--likert", action="store_true", help="Convert Likert scale responses to numeric values.")
    args = parser.parse_args()

    # Load the CSV file
    try:
        data = pd.read_csv(args.file_path)
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return

    # Ask for the type of test
    print("Select the statistical test you want to perform:")
    print("1. One-way ANOVA")
    test_choice = input("Enter the number of your choice: ")

    if test_choice == '1':
        # Ask for the columns to analyze
        columns_input = input("Enter the column names separated by commas: ")
        columns = [col.strip() for col in columns_input.split(',')]

        # Optionally convert Likert scale data
        if args.likert:
            data = convert_likert_to_numeric(data, columns)

        # Perform one-way ANOVA
        try:
            # Ensure all specified columns exist
            valid_columns = [col for col in columns if col in data.columns]
            if len(valid_columns) != len(columns):
                missing = set(columns) - set(valid_columns)
                print(f"Warning: The following columns were not found and will be ignored: {', '.join(missing)}")
            
            if len(valid_columns) < 2:
                print("Error: ANOVA requires at least two columns of data.")
                return

            groups = [data[col].dropna() for col in valid_columns]
            f_statistic, p_value = stats.f_oneway(*groups)
            print(f"F-statistic: {f_statistic}, p-value: {p_value}")
        except Exception as e:
            print(f"Error performing ANOVA: {e}")
    else:
        print("Invalid choice. Please select a valid test.")

if __name__ == "__main__":
    main()