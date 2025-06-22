import subprocess
import os
import requests
import atexit
from datetime import datetime

source = None
db_path = None
#==List of functions to handle file operations and database interactions==#
def list_log_files():
    log_files = [f for f in os.listdir('.') if f.startswith('logs')]
    if not log_files:
        print("No log files found starting with 'logs'")
        return []
    print("Available log files:")
    for i, file in enumerate(log_files, 1):
        print(f"{i}. {file}")
    return log_files

#==Switch Case to get User Input==#

def File_display(value):
    global source, db_path
    match value:
        case 1:
            source = input("Enter the source file path or URL: ").strip()
            if source.startswith("http"):
                db_path = f"temp_downloaded_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.ars"
            else:
                db_path = source
            return "Source set."

        case 2:
            ars_files = [f for f in os.listdir('.') if f.lower().endswith(('.ars', '.mdb', '.accdb'))]
            if not ars_files:
                return "No .ars/.mdb/.accdb files found in current directory."

            print("Available files:")
            for i, file in enumerate(ars_files, 1):
                print(f"{i}. {file}")
            try:
                selected = int(input("Enter the number of the file to use: ")) - 1
                source = ars_files[selected]
                db_path = source
                return f"Using: {source}"
            except (ValueError, IndexError):
                return "Invalid selection."

        case 3:
            list_log_files()
            return "Listed log files."

        case 4:
            return "exit"

        case _:
            return "Invalid option. Please try again."

#=== Function to download the file if it's a URL or check if it exists locally ===#
def download_if_needed():
    if source.startswith("http"):
        print(f"Downloading file from: {source}")
        response = requests.get(source)
        if response.status_code == 200:
            with open(db_path, "wb") as f:
                f.write(response.content)
            print(f"Download complete → saved as '{db_path}'")
        else:
            raise Exception(f"Download failed with status code: {response.status_code}")
    else:
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"File '{db_path}' not found.")


# @atexit.register
# def cleanup():
#     if source and source.startswith("http") and os.path.exists(db_path):
#         os.remove(db_path)
#         print(f"Removed temporary file: {db_path}")

#== Function to write logs to a file ===#
def write_log(file_path, content):
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(content + "\n")


def list_tables():
    try:
        result = subprocess.run(
            ['mdb-tables', '-1', db_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        tables = result.stdout.strip().splitlines()
        if not tables:
            print("No tables found in the database.")
        else:
            print("\nAvailable tables:")
            for i, table in enumerate(tables, 1):
                print(f"{i}. {table}")
        return tables
    except subprocess.CalledProcessError as e:
        print("Error listing tables:", e.stderr)
        return []

#== Function to read logs from a table and write to a log file ===#
def read_logs(table_name):
    try:
        result = subprocess.run(
            ['mdb-export', db_path, table_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        lines = result.stdout.strip().splitlines()
        log_file = f"logs_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt"
        for line in lines:
            print(line)
            write_log(log_file, line)
        return f"{len(lines)} rows read and saved to {log_file}."
    except subprocess.CalledProcessError as e:
        print(f"Error reading table '{table_name}':", e.stderr)
        return "Error occurred"

#== Function to read logs by a specific column value and write to a log file ===#
def read_logs_by_value(table_name, column_name, target_value):
    try:
        result = subprocess.run(
            ['mdb-export', '-D', '%Y-%m-%d', db_path, table_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        lines = result.stdout.strip().splitlines()

        header_result = subprocess.run(
            ['mdb-export', '-H', db_path, table_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        headers = header_result.stdout.strip().split(',')

        if column_name not in headers:
            print(f"Column '{column_name}' not found in table.")
            return "No results"

        col_index = headers.index(column_name)
        match_count = 0
        for line in lines:
            fields = line.split(',')
            if len(fields) > col_index and fields[col_index].strip('"') == str(target_value):
                print(line)
                write_log("logs.txt", line)
                match_count += 1

        return f"{match_count} rows matched and logged." if match_count else "No matching rows found."

    except subprocess.CalledProcessError as e:
        print("Error filtering table:", e.stderr)
        return "Error occurred"

#== Function to handle table menu operations ===#
def Table_Menu(value):
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
                column = input("Enter the column name to filter by: ").strip()
                target_value = input("Enter the value to match: ").strip()
                return read_logs_by_value(table_name, column, target_value)

        case 3:
            return "exit"

        case _:
            return "Invalid option. Please try again."

#==Main Program Execution==#
if __name__ == "__main__":
    flag = True
    while flag:
        try:
            print("\nStartup Menu:")
            print("1. Enter URL or local file path")
            print("2. Choose from existing .ars/.mdb/.accdb files")
            print("3. Show log files")
            print("4. Exit")

            choice = int(input("Your choice: "))
            result = File_display(choice)
            if result == "exit":
                flag = False
            else:
                print(result)
                if db_path:
                    break  # proceed to next stage
        except ValueError:
            print("Invalid input. Please enter a number.")

    if not db_path:
        print("No file selected. Exiting.")
        exit()

    try:
        download_if_needed()
    except Exception as e:
        print("Startup error:", e)
        exit(1)

#==Main Menu for Table Operations==#
    # Inner loop
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

            result = Table_Menu(choice)
            if result == "exit":
                flag = False
            else:
                print(result)
        except ValueError:
            print("Invalid input. Please enter a number.")
