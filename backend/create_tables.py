from database import get_connection

connection = get_connection()
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS resources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100),
    provider VARCHAR(50),
    environment VARCHAR(50),
    owner VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS resource_changes (
    id SERIAL PRIMARY KEY,
    resource_id INTEGER REFERENCES resources(id),
    commit_id VARCHAR(255),
    author VARCHAR(255),
    change_description TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

connection.commit()

cursor.close()
connection.close()

print("Tables created successfully!")