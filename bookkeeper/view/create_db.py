import sqlite3
connection = sqlite3.connect('bookkeeper/view/new_database.db')

# Tạo bảng expense
query = '''DELETE FROM expense'''

connection.execute(query)

# Commit các thay đổi và đóng kết nối
connection.commit()
connection.close()

print("Database created successfully!")