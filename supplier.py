import mysql.connector
from mysql.connector import Error
from datetime import datetime


def write_supplier_balances_to_mysql():
    # Collect supplier data
    print("Enter supplier data. Type 'done' when finished.")
    supplier_data = {}
    while True:
        supplier_name = input("Enter supplier name: ")
        if supplier_name.lower() == "done":
            break
        try:
            balance = float(input(f"Enter balance for {supplier_name}: "))

            # In a real application, you should fetch supplier_id and currency_id from the database
            supplier_id = int(input(f"Enter supplier ID for {supplier_name}: "))
            currency_id = int(input(f"Enter currency ID for {supplier_name}: "))

            balance_date = (
                datetime.now().date()
            )  # Set the balance date to the current date

            # Store the data in the dictionary
            supplier_data[supplier_name] = {
                "balance": balance,
                "supplier_id": supplier_id,
                "currency_id": currency_id,
                "balance_date": balance_date,
            }
        except ValueError:
            print(
                "Invalid input. Please enter valid numbers for balance and amount paid."
            )

    # Connect to MySQL Database
    try:
        connection = mysql.connector.connect(
            host="localhost",  # Your MySQL server address
            database="ja_db",  # Database name
            user="root",  # Your MySQL username
            password="2044",  # Your MySQL password
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Insert supplier data into the supplier_openningbalance table
            for supplier, data in supplier_data.items():
                query = """
                    INSERT INTO supplier_openningbalance (
                        balance_date, ob_amount, supplier_id, currency_id, last_modified
                    ) 
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                """
                values = (
                    data["balance_date"],  # balance_date from the input
                    data["balance"],  # ob_amount from the input
                    data["supplier_id"],  # supplier_id from the input
                    data["currency_id"],  # currency_id from the input
                )
                cursor.execute(query, values)

            # Commit the transaction
            connection.commit()
            print(f"Supplier balances have been saved to the MySQL database.")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# Run the function
write_supplier_balances_to_mysql()
