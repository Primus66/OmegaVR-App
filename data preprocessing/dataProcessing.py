"""
Given multiple CSV files, this script will merge them into one CSV file.
Each CSV file has rows with unique class names corresponding to different integers:
{'Left Click': 1, 'Right Click': 2, 'Scroll Up': 3, 'Scroll Down': 4}
After each unique class name, there are 100 rows of numerical data belongs to that class.
This srcipt will:
1. Read from multiple CSV files and merge them into one CSV files
2. The rows with unique class name will be removed and the integer value will be added to a new column called 'Class'.
"""

# Import necessary libraries
import os
import pandas as pd
import ast
import numpy as np

# Define the CSVDataProcessor class
class CSVDataProcessor:
    # Initialize the class with folder path and output file name
    def __init__(self, folder_path, output_file):
        self.folder_path = folder_path  # Path to the folder containing CSV files
        self.output_file = output_file  # Name of the output file
        # Mapping of class names to integers
        self.class_dict = {'Left Click': 1, 'Right Click': 2, 'Scroll Up': 3, 'Scroll Down': 4}

    # Method to process and merge CSV files
    def process_csv_files(self):
        # List all CSV files in the folder
        csv_files = [f for f in os.listdir(self.folder_path) if f.endswith('.csv')]
        dfs = []  # List to store dataframes

        # Read each CSV file and append to the list
        for file in csv_files:
            df = pd.read_csv(os.path.join(self.folder_path, file), header=None)
            dfs.append(df)

        # Merge all dataframes into one
        merged_df = pd.concat(dfs, ignore_index=True)
        # Set column name for the merged dataframe
        merged_df.columns = ['Electrodes Reading']
        rows_to_remove = []  # List to store rows to be removed

        # Iterate over each row to find and process class names
        for index, row in merged_df.iterrows():
            if row.iloc[0] in self.class_dict:
                rows_to_remove.append(index)  # Mark row for removal
                class_name = row.iloc[0]  # Get class name
                class_value = self.class_dict[class_name]  # Get class value
                # Assign class value to the next 100 rows
                merged_df.loc[index:index+100, 'Class'] = class_value
                print(f'Found class {class_name} at row {index}')

        # Remove rows with class names
        merged_df = merged_df.drop(rows_to_remove)

        # Convert string representation of list in 'Electrodes Reading' into actual list
        merged_df['Electrodes Reading'] = merged_df['Electrodes Reading'].apply(ast.literal_eval)

        # Expand the list in 'Electrodes Reading' into separate columns
        expanded_df = pd.DataFrame(merged_df['Electrodes Reading'].to_list(), index=merged_df.index)

        # Add a column for class values to the expanded dataframe
        expanded_df['Class'] = merged_df['Class'].values

        # Save the expanded dataframe to a CSV file
        expanded_df.to_csv(self.output_file, index=False)
        print(f'Merged data saved to {self.output_file}')


# Example usage
processor = CSVDataProcessor('data', 'merged_data.csv')  # Create an instance of the class
processor.process_csv_files()  # Call the method to process and merge CSV files
