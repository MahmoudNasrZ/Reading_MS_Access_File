import subprocess

# db_path = "2015-004.ars"
db_path = "2006-001.ars"
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
            print("Available tables:")
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
            write_log("logs.txt", line)

        return f"{len(lines)} rows read."
    except subprocess.CalledProcessError as e:
        print(f"Error reading table {table_name}:", e.stderr)
        return "Error occurred"

def read_logs_by_value(table_name, column_name, target_value):
    try:
        # Export entire table
        result = subprocess.run(
            ['mdb-export', '-D', '%Y-%m-%d', db_path, table_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        lines = result.stdout.strip().splitlines()

        # Get header
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
        print("Error reading or filtering table:", e.stderr)
        return "Error occurred"

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
                column = input("Enter the column name to filter by (e.g., 'Component'): ").strip()
                target_value = input("Enter the value to match: ").strip()
                return read_logs_by_value(table_name, column_name=column, target_value=target_value)

        case 3:
            return "exit"
        case _:
            return "Invalid option. Please try again."

# Main loop
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
