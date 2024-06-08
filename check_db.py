import sqlite3

# Connect to your database
conn = sqlite3.connect('db/finance.db')
cursor = conn.cursor()

# Fetch all categories
cursor.execute("SELECT * FROM category")
categories = cursor.fetchall()

# Print categories to verify
print("Categories:")
for category in categories:
    print(category)

# Close the connection
conn.close()
