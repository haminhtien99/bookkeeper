import sqlite3
def create_table_db(db_file):
    """
    Создать таблицу, если не существует
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    query_budget = '''
    CREATE TABLE IF NOT EXISTS budget (
                pk INTEGER PRIMARY KEY,
                day FLOAT,
                week FLOAT,
                month FLOAT)
    '''
    query_category = '''
    CREATE TABLE IF NOT EXISTS category (
                pk INTEGER PRIMARY KEY,
                name TEXT,
                parent INTEGER
                )'''
    query_expense = '''
    CREATE TABLE IF NOT EXISTS expense (
                pk INTEGER PRIMARY KEY,
                comment TEXT,
                amount FLOAT,
                category INTEGER,
                added_date TEXT,
                expense_date TEXT,
                FOREIGN KEY (pk) REFERENCES category(pk) ON DELETE CASCADE
                )'''
    
    cursor.execute(query_expense)
    print('create')
    conn.close()

    # Close the connection
    conn.close()
import sqlite3

# Connect to the database
conn = sqlite3.connect('bookkeeper/view/new_database.db')
cursor = conn.cursor()

# Execute the DROP TABLE statement to delete the table
cursor.execute("DROP TABLE IF EXISTS category")

# Commit the transaction
conn.commit()

# Close the connection
conn.close()