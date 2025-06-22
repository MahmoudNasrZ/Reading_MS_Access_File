import pyodbc
import os

# db_path = r"D:\Python\2021-007-R.mdb"

db_path = r"D:\Python\2021-007-R.mdb"
#Write a log file
def write_log(file_path, content):
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(content + "\n")
#read a log file .mdb, *.accdb Microsoft Access database
def read_logs(table_name):
    try:
        conn_str = (
            r"Driver={Microsoft Access Driver (*.mdb, *.accdb , *.ars, *.ARS)};"
            f"DBQ={db_path};"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        query = f"SELECT * FROM [{table_name}]"
        cursor.execute(query)

        rows = cursor.fetchall()
        for row in rows:
            write_log('logs.txt', str(row))
            print(row)

        return f"{len(rows)} rows read."

    except Exception as e:
        print("Error:", e)
        return "Error occurred"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
#Read File .mdb, *.accdb Microsoft Access database by value
def read_logs_by_value(table_name, target, target_value):
    try:
        conn_str = (
            r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
            f"DBQ={db_path};"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        query = f"SELECT * FROM [{table_name}] WHERE [{target}] = ?"
        cursor.execute(query, (target_value,))

        rows = cursor.fetchall()
        if not rows:
            print("No matching rows found.")
            return "No results"

        for row in rows:
            print(row)
            write_log("logs.txt", str(row))

        return f"{len(rows)} rows matched and logged."

    except Exception as e:
        print("Error:", e)
        return "Error occurred"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

#List all tables in the database
def list_tables():
    try:
        conn_str = (
            r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
            f"DBQ={db_path};"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        tables = []
        for row in cursor.tables(tableType='TABLE'):
            tables.append(row.table_name)

        if not tables:
            print("No tables found in the database.")
        else:
            print("Available tables:")
            for i, table in enumerate(tables, 1):
                print(f"{i}. {table}")
        return tables
    except Exception as e:
        print("Error listing tables:", e)
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

#Switch function to handle user input and call appropriate functions
def switch_example(value):
    match value:
        case 1 | 2:
            tables = list_tables()
            if not tables:
                return "No tables to select from."

            try:
                selected = int(input("Enter the number of the table: ")) - 1
                table_name = tables[selected]
            except (ValueError, IndexError):
                return "Invalid table selection."

            if value == 1:
                return read_logs(table_name)
            else:
                column = input("Enter the column name to filter by (e.g., 'Component'): ")
                target_value = input("Enter the value to match: ")
                try:
                    target_value = int(target_value)
                except ValueError:
                    pass
                return read_logs_by_value(table_name, target=column, target_value=target_value)

        case 3:
            return "exit"
        case _:
            return "Invalid option. Please try again."

# Call the switch function
flag = True
while flag:
    try:
        print("\nChoose an option:")
        print("1. Read all rows from a table")
        print("2. Filter rows by column value")
        print("3. Exit")
        print("4. Show available tables")  

        choice = int(input("Enter your choice: "))
        
        if choice == 4:
            list_tables()
            continue

        result = switch_example(choice)
        if result == "exit":
            flag = False
        else:
            print(result)
    except ValueError:
        print("Invalid input. Please enter a number.")
