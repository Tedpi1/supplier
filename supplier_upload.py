import pandas as pd
import mysql.connector
from mysql.connector import Error
import tkinter as tk
from tkinter import filedialog


def connect_to_database():
    """Establish a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            database="ja_db",
            user="root",
            password="2044",
        )

        if connection.is_connected():
            print("Connected to the database.")
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None


def load_excel_data(file_path):
    """Load the data from the Excel file into a pandas DataFrame."""
    try:
        data = pd.read_excel(file_path)
        print(f"Excel file '{file_path}' loaded successfully.")
        print("Columns in the file:", data.columns)
        print("First few rows of data:")
        print(data.head())  # Show the first 5 rows for inspection
        return data
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return None


def clean_data(data):
    """Clean data by removing rows with NaN or empty values in critical columns."""
    # Remove rows with NaN or empty strings in 'SUPPLIER ID', 'CREDITORS', 'TERMS'
    data = data.dropna(subset=["SUPPLIER ID", "CREDITORS", "TERMS"])
    data = data[
        (data["SUPPLIER ID"] != "") & (data["CREDITORS"] != "") & (data["TERMS"] != "")
    ]

    # Ensure 'SUPPLIER ID' is numeric, convert non-numeric to NaN
    data["SUPPLIER ID"] = pd.to_numeric(data["SUPPLIER ID"], errors="coerce")

    # Drop rows with NaN in 'SUPPLIER ID' after conversion
    data = data.dropna(subset=["SUPPLIER ID"])

    return data


def insert_data_into_database(connection, data):
    """Insert the data into the MySQL table."""
    try:
        cursor = connection.cursor()

        # Assuming your table has columns: supplyid, creditor, and terms
        insert_query = """
        INSERT INTO creditor_credit (supplyid, creditor, terms)
        VALUES (%s, %s, %s)
        """

        # Clean the data to ensure there are no NaN or empty values
        cleaned_data = clean_data(data)

        # Insert valid rows into the database
        for index, row in cleaned_data.iterrows():
            supplyid = int(row["SUPPLIER ID"])  # Ensure it's an integer
            creditor = row["CREDITORS"]
            terms = row["TERMS"]

            # Insert each row of data into the database
            cursor.execute(insert_query, (supplyid, creditor, terms))

        connection.commit()
        print(f"{cursor.rowcount} rows inserted successfully.")
    except Error as e:
        print(f"Error inserting data: {e}")
    finally:
        cursor.close()


def select_file():
    """Open a file dialog to select the Excel file."""
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(
        title="Select the Excel file",
        filetypes=(("Excel Files", "*.xlsx;*.xls"), ("All Files", "*.*")),
    )
    return file_path


def main():
    # Prompt the user to select the Excel file
    file_path = select_file()

    if not file_path:
        print("No file selected. Exiting.")
        return

    # Connect to the database
    connection = connect_to_database()
    if connection:
        # Load data from Excel
        data = load_excel_data(file_path)

        if data is not None:
            # Ensure the required columns exist
            if (
                "SUPPLIER ID" in data.columns
                and "CREDITORS" in data.columns
                and "TERMS" in data.columns
            ):
                # Insert the data into the database
                insert_data_into_database(connection, data)
            else:
                print(
                    "The Excel file must contain the required columns: 'SUPPLIER ID', 'CREDITORS', and 'TERMS'."
                )

        # Close the database connection
        connection.close()


if __name__ == "__main__":
    main()
