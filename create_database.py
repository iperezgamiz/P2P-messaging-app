import sqlite3

# Create SQLite database
conn = sqlite3.connect('p2p_messaging_app.db')

# Create a cursor object using the cursor() method
cursor = conn.cursor()

# Create 'Contacts' table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Contacts (
    Username TEXT NOT NULL UNIQUE,
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
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (SenderUsername) REFERENCES Users(UserID),
    FOREIGN KEY (ReceiverUsername) REFERENCES Users(UserID)
);
''')

# Commit the transaction
conn.commit()

# Close the connection
conn.close()

print("Database and tables created successfully.")
