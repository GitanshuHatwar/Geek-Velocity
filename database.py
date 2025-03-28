import psycopg2

# Database connection
conn = psycopg2.connect(
    dbname="Flask_database",
    user="postgres",
    password="root",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

# Create table
cur.execute("""
    CREATE TABLE IF NOT EXISTS vehicle_data (
        id SERIAL PRIMARY KEY,
        vehicle_count INT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        location VARCHAR(255) NOT NULL
    );
""")

conn.commit()
cur.close()
conn.close()

print("Table created successfully!")
