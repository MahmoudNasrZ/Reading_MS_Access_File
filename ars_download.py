import subprocess
import os
import requests
import atexit
from datetime import datetime

# === CONFIGURATION ===
source = input("Enter the source file path or URL (Example: https://arsdev.s3.us-west-1.amazonaws.com/2015-004.ars): ") 
# source = "./temp_downloaded.ars"

db_path = f"temp_downloaded_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.ars"  if source.startswith("http") else source


# === DOWNLOAD FILE IF NEEDED ===
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


# === CLEANUP TEMP FILE ===
# if source.startswith("http"):
#     @atexit.register
#     def cleanup():
#         if os.path.exists(db_path):
#             os.remove(db_path)
#             print(f"Removed temporary file: {db_path}")


# === LOGGING ===
def write_log(file_path, content):
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(content + "\n")


# === MDBTOOLS FUNCTIONS ===
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
        for line in lines:
            print(line)
            write_log(f"logs_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt", line)
        return f"{len(lines)} rows read."
    except subprocess.CalledProcessError as e:
        print(f"Error reading table '{table_name}':", e.stderr)
        return "Error occurred"


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


# === MENU HANDLER ===
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
                column = input("Enter the column name to filter by: ").strip()
                target_value = input("Enter the value to match: ").strip()
                return read_logs_by_value(table_name, column, target_value)

        case 3:
            return "exit"
        case _:
            return "Invalid option. Please try again."


# === MAIN LOOP ===
if __name__ == "__main__":
    try:
        download_if_needed()
    except Exception as e:
        print("Startup error:", e)
        exit(1)

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
