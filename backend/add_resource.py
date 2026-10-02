from database import get_connection

connection = get_connection()
cursor = connection.cursor()

cursor.execute("""
INSERT INTO resources
(name, type, provider, environment, owner)
VALUES
(%s, %s, %s, %s, %s)
RETURNING id;
""", (
    "infra-vm-01",
    "Virtual Machine",
    "Azure",
    "Development",
    "Aarushi"
))

resource_id = cursor.fetchone()[0]

connection.commit()

cursor.close()
connection.close()

print(f"Resource added successfully! ID: {resource_id}")