import psycopg2
from configparser import ConfigParser
import csv
import sys

# --- Configuration Loading (load_config - unchanged) ---
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

# --- Database Connection (connect - unchanged) ---
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


# --- Table Creation (create_tables - unchanged, but optional now) ---
# You might run the SQL above separately or ensure it runs once during setup.
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

# Method 1: Use the upsert_contact Procedure
def insert_or_update_contact_from_console(conn):
    """ Insert or update a contact using the upsert_contact procedure """
    try:
        first_name = input("Enter first name: ")
        last_name = input("Enter last name (optional, press Enter to skip): ")
        phone = input("Enter phone number: ")

        if not first_name or not phone:
            print("First name and phone number cannot be empty.")
            return

        last_name = last_name if last_name else None # Handle empty last name

        with conn.cursor() as cur:
            # Call the stored procedure
            cur.execute("CALL upsert_contact(%s, %s, %s);", (first_name, last_name, phone))
            conn.commit()
            # Note: RAISE NOTICE messages from the procedure might appear in server logs
            # or potentially be captured depending on psycopg2 settings/level.
            # For simplicity, we just print a generic success message here.
            print(f"Procedure upsert_contact executed for {first_name} {last_name or ''}.")

    except (psycopg2.DatabaseError, Exception) as error:
        print(f"Error calling upsert_contact procedure: {error}")
        conn.rollback()

# Method 2: Use the insert_many_contacts Function
def insert_contacts_from_csv_db_func(conn, csv_filepath):
    """ Insert multiple contacts from CSV using the insert_many_contacts function """
    first_names = []
    last_names = []
    phones = []
    read_count = 0
    invalid_entries_from_db = []

    try:
        with open(csv_filepath, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader) # Skip header row
            print(f"CSV Headers: {header}") # Assuming format: first_name,last_name,phone

            for row in reader:
                read_count += 1
                if len(row) == 3:
                    fname, lname, ph = row
                    first_names.append(fname.strip())
                    # Handle potentially empty last names read from CSV
                    last_names.append(lname.strip() if lname and lname.strip() else None)
                    phones.append(ph.strip())
                else:
                    print(f"Skipping row {read_count+1} due to incorrect column count: {row}")


        if not first_names:
            print("No valid contacts prepared from CSV to insert.")
            return

        with conn.cursor() as cur:
            # Call the database function
            # Pass lists/tuples directly, psycopg2 converts them to PostgreSQL arrays
            cur.execute("SELECT * FROM insert_many_contacts(%s, %s, %s);", (first_names, last_names, phones))
            # Fetch the result (the array of invalid entries)
            result = cur.fetchone()
            if result:
                invalid_entries_from_db = result[0] # The function returns a single row with one column (the array)

            conn.commit()

            processed_count = len(first_names)
            invalid_count = len(invalid_entries_from_db)
            inserted_count = processed_count - invalid_count

            print(f"\n--- Bulk Insert Summary ---")
            print(f"Processed {processed_count} contacts from CSV.")
            print(f"Successfully inserted/handled by DB function: approximately {inserted_count}") # Approximation due to potential skips
            if invalid_entries_from_db:
                print(f"Entries reported as invalid or skipped by DB function ({invalid_count}):")
                for entry in invalid_entries_from_db:
                    print(f"  - {entry}")
            else:
                 print("No invalid entries reported by the database function.")
            print("-" * 25)


    except FileNotFoundError:
        print(f"Error: CSV file not found at '{csv_filepath}'")
    except (psycopg2.DatabaseError, Exception) as error:
        print(f"Database error during bulk insert call: {error}")
        conn.rollback()
    except Exception as e:
        print(f"An unexpected error occurred during CSV processing or DB call: {e}")


# --- Data Update (Simplified - Covered by upsert_contact) ---
# The `upsert_contact` procedure handles updates if the name exists.
# If you need a specific update function *only* (not insert), you'd create another procedure.
# The previous Python `update_contact` logic is replaced by calling `upsert_contact`.

# --- NEW FUNCTION: Create DB Functions and Procedures ---
def create_db_functions_and_procedures(conn):
    """ Create or replace the necessary functions and procedures in the DB """
    commands = (
        """
        CREATE OR REPLACE FUNCTION search_contacts_by_pattern(p_pattern TEXT)
        RETURNS SETOF phonebook
        LANGUAGE sql
        AS $$
            SELECT contact_id, first_name, last_name, phone
            FROM phonebook
            WHERE first_name ILIKE ('%' || p_pattern || '%')
               OR last_name ILIKE ('%' || p_pattern || '%')
               OR phone LIKE ('%' || p_pattern || '%')
            ORDER BY first_name, last_name;
        $$;
        """,
        """
        CREATE OR REPLACE PROCEDURE upsert_contact(
            p_first_name VARCHAR(50),
            p_last_name VARCHAR(50),
            p_phone VARCHAR(20)
        )
        LANGUAGE plpgsql
        AS $$
        DECLARE
            v_contact_id INT;
        BEGIN
            SELECT contact_id INTO v_contact_id
            FROM phonebook
            WHERE first_name = p_first_name
              AND (last_name = p_last_name OR (last_name IS NULL AND p_last_name IS NULL))
            LIMIT 1;

            IF FOUND THEN
                UPDATE phonebook
                SET phone = p_phone
                WHERE contact_id = v_contact_id;
                RAISE NOTICE 'Updated phone for existing contact % %.', p_first_name, COALESCE(p_last_name, '');
            ELSE
                INSERT INTO phonebook (first_name, last_name, phone)
                VALUES (p_first_name, p_last_name, p_phone);
                RAISE NOTICE 'Inserted new contact % %.', p_first_name, COALESCE(p_last_name, '');
            END IF;
        END;
        $$;
        """,        """
        CREATE OR REPLACE FUNCTION insert_many_contacts(
            p_first_names TEXT[],
            p_last_names TEXT[],
            p_phones TEXT[]
        )
        RETURNS TEXT[]
        LANGUAGE plpgsql
        AS $$
        DECLARE
            i INT;
            invalid_entries TEXT[] := '{}';
            v_fname TEXT;
            v_lname TEXT;
            v_phone TEXT;
            phone_pattern CONSTANT TEXT := '^\+?[0-9\s\-()]+$';
        BEGIN
            IF array_length(p_first_names, 1) != array_length(p_last_names, 1) OR
               array_length(p_first_names, 1) != array_length(p_phones, 1) THEN
                RAISE EXCEPTION 'Input arrays must have the same length';
            END IF;

            FOR i IN 1 .. array_length(p_first_names, 1) LOOP
                v_fname := trim(p_first_names[i]);
                v_lname := trim(p_last_names[i]);
                v_phone := trim(p_phones[i]);
                IF v_lname = '' THEN v_lname := NULL; END IF;

                IF v_fname IS NULL OR v_fname = '' OR v_phone IS NULL OR v_phone = '' OR v_phone !~ phone_pattern THEN
                    invalid_entries := array_append(invalid_entries,
                        'Invalid Data: First=' || COALESCE(v_fname, 'NULL') ||
                        ', Last=' || COALESCE(v_lname, 'NULL') ||
                        ', Phone=' || COALESCE(v_phone, 'NULL'));
                    CONTINUE;
                END IF;

                BEGIN
                    INSERT INTO phonebook (first_name, last_name, phone)
                    VALUES (v_fname, v_lname, v_phone);
                EXCEPTION
                    WHEN unique_violation THEN
                         invalid_entries := array_append(invalid_entries,
                            'Skipped (Phone Exists): First=' || v_fname ||
                            ', Last=' || COALESCE(v_lname, 'NULL') ||
                            ', Phone=' || v_phone);
                    WHEN others THEN
                        invalid_entries := array_append(invalid_entries,
                            'Error Inserting: First=' || v_fname ||
                            ', Last=' || COALESCE(v_lname, 'NULL') ||
                            ', Phone=' || v_phone || ' Reason: ' || SQLERRM);
                END;
            END LOOP;
            RETURN invalid_entries;
        END;
        $$;
        """,
        """
        CREATE OR REPLACE FUNCTION get_contacts_paginated(
            p_limit INT,
            p_offset INT
        )
        RETURNS SETOF phonebook
        LANGUAGE sql
        AS $$
            SELECT contact_id, first_name, last_name, phone
            FROM phonebook
            ORDER BY first_name, last_name
            LIMIT p_limit
            OFFSET p_offset;
        $$;
        """,
        """
        CREATE OR REPLACE PROCEDURE delete_contact_by_identifier(
            p_identifier TEXT,
            p_delete_by TEXT
        )
        LANGUAGE plpgsql
        AS $$
        DECLARE
            deleted_count INT := 0;
        BEGIN
            IF p_delete_by = 'name' THEN
                DELETE FROM phonebook WHERE first_name = p_identifier;
                GET DIAGNOSTICS deleted_count = ROW_COUNT;
                RAISE NOTICE 'Deleted % contacts with first name %.', deleted_count, p_identifier;
            ELSIF p_delete_by = 'phone' THEN
                DELETE FROM phonebook WHERE phone = p_identifier;
                GET DIAGNOSTICS deleted_count = ROW_COUNT;
                RAISE NOTICE 'Deleted % contacts with phone %.', deleted_count, p_identifier;
            ELSE
                RAISE EXCEPTION 'Invalid delete_by parameter: Must be ''name'' or ''phone''. Received: %', p_delete_by;
            END IF;
            IF deleted_count = 0 THEN
                RAISE NOTICE 'No contacts found matching the criteria.';
            END IF;
        END;
        $$;
        """
    )
    try:
        with conn.cursor() as cur:
            for command in commands:
                cur.execute(command)
        conn.commit()
        print("Database functions/procedures ensured.")
    except (psycopg2.DatabaseError, Exception) as error:
        print(f"Error creating database functions/procedures: {error}")
        conn.rollback()
        raise # Re-raise the error
# --- Data Querying ---

# Query using the search function
def query_contacts_by_pattern(conn, pattern):
    """ Query contacts using the search_contacts_by_pattern function """
    if not pattern:
         print("Search pattern cannot be empty.")
         return []

    print(f"\n--- Searching for pattern: '{pattern}' ---")
    results = []
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts_by_pattern(%s);", (pattern,))
            results = cur.fetchall() # Fetch all results from the function call

            print(f"Found {cur.rowcount} contacts matching the pattern.")
            if cur.rowcount > 0:
                # Print results nicely (same format as before)
                print(f"{'ID':<5} {'First Name':<15} {'Last Name':<15} {'Phone':<15}")
                print("-" * 55)
                for row in results:
                    contact_id, first_name, last_name, phone = row
                    print(f"{contact_id:<5} {first_name:<15} {last_name or '':<15} {phone:<15}")
                print("-" * 55)
            return results

    except (psycopg2.DatabaseError, Exception) as error:
        print(f"Error querying contacts by pattern: {error}")
        return []

# Query using pagination function
def query_contacts_paginated(conn, limit, offset):
    """ Query contacts using the get_contacts_paginated function """
    print(f"\n--- Fetching contacts: Page limit={limit}, Offset={offset} ---")
    results = []
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM get_contacts_paginated(%s, %s);", (limit, offset))
            results = cur.fetchall()

            print(f"Retrieved {cur.rowcount} contacts for this page.")
            if cur.rowcount > 0:
                # Print results nicely
                print(f"{'ID':<5} {'First Name':<15} {'Last Name':<15} {'Phone':<15}")
                print("-" * 55)
                for row in results:
                    contact_id, first_name, last_name, phone = row
                    print(f"{contact_id:<5} {first_name:<15} {last_name or '':<15} {phone:<15}")
                print("-" * 55)
            return results

    except (psycopg2.DatabaseError, Exception) as error:
        print(f"Error querying paginated contacts: {error}")
        return []


# --- Data Deletion ---
def delete_contact_db_proc(conn):
     """ Delete contacts using the delete_contact_by_identifier procedure """
     try:
        delete_by = input("Delete by 'name' (first name) or 'phone'? ").lower()
        identifier = input(f"Enter the exact {delete_by} to delete: ")

        if not identifier:
            print("Identifier cannot be empty.")
            return

        if delete_by not in ['name', 'phone']:
            print("Invalid choice. Please enter 'name' or 'phone'.")
            return

        if delete_by == 'name':
            print("Warning: This will delete ALL contacts with this exact first name.")
            confirm = input(f"Are you sure? (yes/no): ").lower()
            if confirm != 'yes':
                print("Deletion cancelled.")
                return

        with conn.cursor() as cur:
            # Call the stored procedure
            cur.execute("CALL delete_contact_by_identifier(%s, %s);", (identifier, delete_by))
            conn.commit()
            # The procedure itself prints notices about deletion count
            print(f"Procedure delete_contact_by_identifier executed for {delete_by}: '{identifier}'. Check server logs/output for details.")

     except (psycopg2.DatabaseError, Exception) as error:
        print(f"Error calling delete_contact_by_identifier procedure: {error}")
        conn.rollback()


# --- Main Application Logic (Modified) ---
def main():
    config = load_config()
    conn = connect(config)

    if not conn:
        return # Exit if connection failed

    # Optional: Ensure table exists (if not done separately)
    # create_tables(conn)
    # Optional: Ensure functions/procedures exist (run SQL scripts once)

    while True:
        print("\n--- PhoneBook Menu (DB Functions/Procedures) ---")
        print("1. Add/Update Contact (Console - Upsert)")
        print("2. Add Contacts (CSV - Bulk Function)")
        # Update option is implicitly handled by option 1 now
        print("3. Get Contacts (Paginated)")
        print("4. Search Contacts (Pattern)")
        print("5. Delete Contact (Procedure)")
        print("6. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            insert_or_update_contact_from_console(conn)
        elif choice == '2':
            csv_path = input("Enter the path to the CSV file: ")
            # You might still want the dummy CSV creation logic here for testing
            insert_contacts_from_csv_db_func(conn, csv_path)
        elif choice == '3':
            try:
                limit = int(input("Enter page size (limit): "))
                page = int(input("Enter page number: "))
                offset = (page - 1) * limit
                if limit <= 0 or page <= 0:
                     print("Limit and page number must be positive.")
                     continue
                query_contacts_paginated(conn, limit, offset)
            except ValueError:
                print("Invalid number entered.")
        elif choice == '4':
            pattern = input("Enter search pattern (part of name or phone): ")
            query_contacts_by_pattern(conn, pattern)
        elif choice == '5':
            delete_contact_db_proc(conn)
        elif choice == '6':
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