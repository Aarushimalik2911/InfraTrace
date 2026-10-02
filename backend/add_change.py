from database import get_connection

connection = get_connection()
cursor = connection.cursor()

cursor.execute("""
INSERT INTO resource_changes
(resource_id, commit_id, author, change_description)
VALUES
(%s, %s, %s, %s);
""", (
    1,
    "a8f31c2",
    "Aarushi",
    "Increased VM size from Standard_B1s to Standard_B2s"
))

connection.commit()

cursor.close()
connection.close()

print("Resource change added successfully!")
