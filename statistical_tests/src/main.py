import pandas as pd
from scipy import stats
import argparse
import matplotlib.pyplot as plt
import os
from datetime import datetime

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
            df[col] = df[col].astype(str).str.lower().map(likert_mapping)
    return df

def select_columns_by_name():
    """
    Prompts the user to enter column names directly.
    """
    columns_input = input("\nEnter the column names to analyze, separated by commas: ")
    columns = [col.strip() for col in columns_input.split(',')]
    return columns

def select_columns_by_number(df):
    """
    Lists all columns, prompts the user to select by number, and returns column names.
    """
    column_list = df.columns.tolist()
    print("\nAvailable columns:")
    for i, col_name in enumerate(column_list):
        print(f"  {i + 1}: {col_name}")

    selected_columns = []
    while True:
        try:
            selection_input = input("\nEnter the numbers of the columns to analyze, separated by commas: ")
            selected_indices = [int(num.strip()) - 1 for num in selection_input.split(',')]
            
            # validate indices
            if any(i < 0 or i >= len(column_list) for i in selected_indices):
                print(f"Error: Invalid selection. Please choose numbers between 1 and {len(column_list)}.")
                continue

            selected_columns = [column_list[i] for i in selected_indices]
            break
        except ValueError:
            print("Error: Invalid input. Please enter a comma-separated list of numbers.")
    
    return selected_columns

def main():
    parser = argparse.ArgumentParser(description="Perform statistical analysis on a CSV file.")
    parser.add_argument("file_path", help="Path to the CSV file.")
    parser.add_argument("--likert", action="store_true", help="Convert 5-point agreement Likert scale to numeric.")
    parser.add_argument("--likert2", action="store_true", help="Convert 5-point satisfaction Likert scale to numeric.")
    parser.add_argument("--likert3", action="store_true", help="Convert 5-point frequency Likert scale to numeric. Another Likert mapping.")
    parser.add_argument("--select-by-number", action="store_true", help="Select columns by number from a list instead of by name.")
    parser.add_argument("--save-charts", action="store_true", help="Save charts to files instead of displaying them.")
    args = parser.parse_args()

    # load it
    try:
        skip_input = input("Enter the number of rows to ignore after the header (e.g., 2), or press Enter to auto-detect: ")
        if skip_input.strip().isdigit():
            num_to_skip = int(skip_input)
            rows_to_skip = list(range(1, num_to_skip + 1))
        else:
            print("Auto-detecting data start row...")
            rows_to_skip = find_data_start_row(args.file_path)
        
        data = pd.read_csv(args.file_path, header=0, skiprows=rows_to_skip)
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return

    # what test?
    print("Select the statistical test you want to perform:")
    print("1. One-way ANOVA")
    print("2. Friedman Test")
    print("3. Distribution charts")
    test_choice = input("Enter the number of your choice: ")

    if test_choice == '1':
        # ask for cols
        if args.select_by_number:
            columns = select_columns_by_number(data)
        else:
            columns = select_columns_by_name()

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
        elif args.likert3:
            likert_mapping_3 = {
                "strongly agree": 1,
                "agree": 2,
                "neutral": 3,
                "disagree": 4,
                "strongly disagree": 5,
            }
            data = convert_likert_to_numeric(data, columns, likert_mapping_3)

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
        if args.select_by_number:
            columns = select_columns_by_number(data)
        else:
            columns = select_columns_by_name()

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
    elif test_choice == '3':
        if args.select_by_number:
            columns = select_columns_by_number(data)
        else:
            columns = select_columns_by_name()

        valid_columns = [col for col in columns if col in data.columns]
        if len(valid_columns) != len(columns):
            missing = set(columns) - set(valid_columns)
            print(f"Warning: The following columns were not found and will be ignored: {', '.join(missing)}")

        if not valid_columns:
            print("No valid columns to analyze.")
            return

        output_dir = "output"
        if args.save_charts:
            os.makedirs(output_dir, exist_ok=True)

        for col in valid_columns:
            try:
                processed_series = data[col].dropna().astype(str).str.split(',').explode().str.strip()
                counts = processed_series.value_counts()

                if counts.empty:
                    print(f"\nColumn '{col}' has no data to plot.")
                    continue

                total_responses = counts.sum()

                plt.figure(figsize=(10, 6))
                ax = counts.plot(kind='bar')
                
                labels = [f'{count}\n({count/total_responses:.1%})' for count in counts]

                ax.bar_label(ax.containers[0], labels=labels, padding=3)

                plt.title(f'Distribution for "{col}"')
                plt.ylabel('Count')
                plt.xlabel('Response')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()

                if args.save_charts:
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    safe_col_name = "".join(c for c in col if c.isalnum() or c in ('_', '-')).rstrip()
                    filename = f"{safe_col_name}_{timestamp}.png"
                    filepath = os.path.join(output_dir, filename)
                    
                    plt.savefig(filepath)
                    plt.close()
                    print(f"Chart saved to {filepath}")
                else:
                    plt.show()

            except Exception as e:
                print(f"Could not generate chart for column '{col}': {e}")
    else:
        print("Invalid choice. Please select a valid test.")

if __name__ == "__main__":
    main()