import sqlite3

username = input("Introduce username: ")

# Create SQLite database
conn = sqlite3.connect(f'p2p_messaging_app_{username}.db')

# Create a cursor object using the cursor() method
cursor = conn.cursor()

# Create 'Contacts' table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Contacts (
    Username TEXT NOT NULL UNIQUE,
    Blocked INTEGER DEFAULT 0
);
''')

# Create 'Messages' table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Messages (
    MessageID INTEGER PRIMARY KEY AUTOINCREMENT,
    SenderUsername INTEGER,
    ReceiverUsername INTEGER,
    MessageText TEXT NOT NULL,
    Delivered INTEGER NOT NULL,
    Timestamp DATETIME NOT NULL
);
''')

# Commit the transaction
conn.commit()

# Close the connection
conn.close()

print("Database and tables created successfully.")
