import psycopg2
from configparser import ConfigParser
import csv
import sys

# --- Configuration Loading ---
def load_config(filename='database.ini', section='postgresql'):
    """ Load database configuration from file """
    parser = ConfigParser()
    parser.read(filename)

    # Get section, default to postgresql
    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {filename} file')

    return config

# --- Database Connection ---
def connect(config):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # Connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**config)
        print('Connection successful.')
        return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(f"Error connecting to database: {error}")
        sys.exit(1) # Exit if connection fails

# --- Table Creation ---
def create_tables(conn):
    """ Create phonebook table """
    commands = (
        """
        CREATE TABLE phonebook (
            contact_id SERIAL PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50),
            phone VARCHAR(20) UNIQUE NOT NULL
        )
        """
    )
    try:
        with conn.cursor() as cur:
            # Execute each command
            for command in commands:
                cur.execute(command)
        # Commit the changes
        conn.commit()
        print("Table 'phonebook' created successfully (or already existed and was reset).")
    except (psycopg2.DatabaseError, Exception) as error:
        print(f"Error creating table: {error}")
        conn.rollback() # Rollback changes on error

# --- Data Insertion ---

# Method 1: Insert from Console Input
def insert_contact_from_console(conn):
    """ Insert a new contact into the phonebook table from console input """
    sql = """INSERT INTO phonebook(first_name, last_name, phone)
             VALUES(%s, %s, %s) RETURNING contact_id;"""
    contact_id = None
    try:
        first_name = input("Enter first name: ")
        last_name = input("Enter last name (optional, press Enter to skip): ")
        phone = input("Enter phone number: ")

        if not first_name or not phone:
            print("First name and phone number cannot be empty.")
            return

        last_name = last_name if last_name else None # Handle empty last name

        with conn.cursor() as cur:
            # Execute the INSERT statement
            cur.execute(sql, (first_name, last_name, phone))

            # Get the generated id back
            rows = cur.fetchone()
            if rows:
                contact_id = rows[0]

            # Commit the changes to the database
            conn.commit()
            print(f"Contact '{first_name} {last_name or ''}' added successfully with ID: {contact_id}")

    except (psycopg2.DatabaseError, Exception) as error:
        print(f"Error inserting contact: {error}")
        conn.rollback()

# Method 2: Insert from CSV File
def insert_contacts_from_csv(conn, csv_filepath):
    """ Insert multiple contacts into the phonebook table from a CSV file """
    sql = "INSERT INTO phonebook(first_name, last_name, phone) VALUES(%s, %s, %s)"
    contacts_to_insert = []
    inserted_count = 0
    skipped_count = 0

    try:
        with open(csv_filepath, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader) # Skip header row
            print(f"CSV Headers: {header}") # Assuming format: first_name,last_name,phone

            for row in reader:
                if len(row) == 3:
                    first_name, last_name, phone = row
                    # Basic validation
                    if first_name and phone:
                         contacts_to_insert.append(
                            (first_name.strip(), last_name.strip() if last_name else None, phone.strip())
                         )
                    else:
                         print(f"Skipping row due to missing data: {row}")
                         skipped_count += 1
                else:
                    print(f"Skipping row due to incorrect column count: {row}")
                    skipped_count += 1

        if not contacts_to_insert:
            print("No valid contacts found in CSV to insert.")
            return

        with conn.cursor() as cur:
            # Use executemany for efficient bulk insertion
            cur.executemany(sql, contacts_to_insert)
            inserted_count = cur.rowcount # executemany doesn't update rowcount reliably across drivers, but good for psycopg2
            conn.commit()
            print(f"Successfully inserted {len(contacts_to_insert)} contacts from CSV.") # More reliable count
            if skipped_count > 0:
                print(f"Skipped {skipped_count} rows due to formatting issues or missing data.")

    except FileNotFoundError:
        print(f"Error: CSV file not found at '{csv_filepath}'")
    except (psycopg2.DatabaseError, Exception) as error:
        print(f"Database error during CSV insert: {error}")
        conn.rollback()
    except Exception as e:
        print(f"An unexpected error occurred during CSV processing: {e}")


# --- Data Update ---
def update_contact(conn):
    """ Update a contact's first name or phone number based on their current phone number """
    current_phone = input("Enter the CURRENT phone number of the contact to update: ")
    if not current_phone:
        print("Current phone number cannot be empty.")
        return

    new_first_name = input("Enter the new first name (press Enter to keep current): ")
    new_phone = input("Enter the new phone number (press Enter to keep current): ")

    if not new_first_name and not new_phone:
        print("No updates specified.")
        return

    update_parts = []
    params = []

    if new_first_name:
        update_parts.append("first_name = %s")
        params.append(new_first_name)
    if new_phone:
        update_parts.append("phone = %s")
        params.append(new_phone)

    params.append(current_phone) # For the WHERE clause

    sql = f"UPDATE phonebook SET {', '.join(update_parts)} WHERE phone = %s"

    try:
        updated_rows = 0
        with conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            updated_rows = cur.rowcount
            conn.commit()

        if updated_rows > 0:
            print(f"Successfully updated contact with current phone '{current_phone}'.")
        else:
            print(f"No contact found with phone number '{current_phone}'. No updates made.")

    except (psycopg2.DatabaseError, Exception) as error:
        print(f"Error updating contact: {error}")
        conn.rollback()

# --- Data Querying ---
def query_contacts(conn, first_name_filter=None, phone_filter=None):
    """ Query contacts from the phonebook table with optional filters """
    base_sql = "SELECT contact_id, first_name, last_name, phone FROM phonebook"
    filters = []
    params = []

    if first_name_filter:
        # Use ILIKE for case-insensitive partial matching
        filters.append("first_name ILIKE %s")
        params.append(f"%{first_name_filter}%")
    if phone_filter:
        # Exact match or partial match? Let's do partial for flexibility.
        filters.append("phone LIKE %s")
        params.append(f"%{phone_filter}%")

    if filters:
        sql = f"{base_sql} WHERE {' AND '.join(filters)}"
    else:
        sql = base_sql

    sql += " ORDER BY first_name, last_name" # Add ordering

    try:
        with conn.cursor() as cur:
            if params:
                cur.execute(sql, tuple(params))
            else:
                cur.execute(sql)

            print(f"\n--- Query Results ({cur.rowcount} found) ---")
            if cur.rowcount == 0:
                print("No contacts found matching the criteria.")
                return []

            results = cur.fetchall()
            # Print results nicely
            print(f"{'ID':<5} {'First Name':<15} {'Last Name':<15} {'Phone':<15}")
            print("-" * 55)
            for row in results:
                contact_id, first_name, last_name, phone = row
                print(f"{contact_id:<5} {first_name:<15} {last_name or '':<15} {phone:<15}")
            print("-" * 55)
            return results

    except (psycopg2.DatabaseError, Exception) as error:
        print(f"Error querying contacts: {error}")
        return []

# --- Data Deletion ---
def delete_contact(conn):
    """ Delete contacts by first name or phone number """
    delete_by = input("Delete by 'name' (first name) or 'phone'? ").lower()
    identifier = input(f"Enter the {delete_by} to delete: ")

    if not identifier:
        print("Identifier cannot be empty.")
        return

    deleted_rows = 0
    sql = ""

    if delete_by == 'name':
        print("Warning: Deleting by first name may remove multiple contacts.")
        confirm = input(f"Are you sure you want to delete all contacts with first name '{identifier}'? (yes/no): ").lower()
        if confirm != 'yes':
            print("Deletion cancelled.")
            return
        sql = "DELETE FROM phonebook WHERE first_name = %s"
    elif delete_by == 'phone':
        sql = "DELETE FROM phonebook WHERE phone = %s"
    else:
        print("Invalid choice. Please enter 'name' or 'phone'.")
        return

    try:
        with conn.cursor() as cur:
            cur.execute(sql, (identifier,))
            deleted_rows = cur.rowcount
            conn.commit()

        if deleted_rows > 0:
            print(f"Successfully deleted {deleted_rows} contact(s) matching '{identifier}'.")
        else:
            print(f"No contacts found matching '{identifier}'. No deletions made.")

    except (psycopg2.DatabaseError, Exception) as error:
        print(f"Error deleting contact: {error}")
        conn.rollback()

# --- Main Application Logic ---
def main():
    config = load_config()
    conn = connect(config)

    if not conn:
        return # Exit if connection failed

    # Ensure table exists
    create_tables(conn)

    # --- Example Usage ---
    while True:
        print("\n--- PhoneBook Menu ---")
        print("1. Add Contact (Console)")
        print("2. Add Contacts (CSV)")
        print("3. Update Contact (by current phone)")
        print("4. Get all contacts")
        print("5. Query Contacts (Filter)")
        print("6. Delete Contact (by name or phone)")
        print("7. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            insert_contact_from_console(conn)
        elif choice == '2':
            csv_path = input("Enter the path to the CSV file: ")
            # Create a dummy CSV if it doesn't exist for testing
            try:
                with open(csv_path, 'x') as f: # 'x' creates only if it doesn't exist
                   writer = csv.writer(f)
                   writer.writerow(['first_name','last_name','phone'])
                   writer.writerow(['Alice','Smith','111-222-3333'])
                   writer.writerow(['Bob','','444-555-6666'])
                   print(f"Created a sample CSV at '{csv_path}' as it didn't exist.")
            except FileExistsError:
                pass # File already exists, proceed normally
            except Exception as e:
                print(f"Could not create sample CSV: {e}")

            insert_contacts_from_csv(conn, csv_path)
        elif choice == '3':
            update_contact(conn)
        elif choice == '4':
            query_contacts(conn)
        elif choice == '5':
            fname_filter = input("Enter first name filter (leave blank for no filter): ")
            phone_filter = input("Enter phone filter (leave blank for no filter): ")
            query_contacts(conn, fname_filter or None, phone_filter or None)
        elif choice == '6':
            delete_contact(conn)
        elif choice == '7':
            print("Exiting PhoneBook application.")
            break
        else:
            print("Invalid choice. Please try again.")

    # Close the connection
    if conn:
        conn.close()
        print('Database connection closed.')


if __name__ == '__main__':
    main()