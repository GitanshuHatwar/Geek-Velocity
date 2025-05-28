import psycopg2
from datetime import datetime

def init_db():
    """Initialize database connection and create tables if they don't exist"""
    try:
        conn = psycopg2.connect(
            dbname="traffic_management",
            user="postgres",
            password="root",
            host="localhost",
            port="5432"
        )
        
        cur = conn.cursor()
        
        # Create main traffic data table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS traffic_data (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                location VARCHAR(255) NOT NULL,
                lane_number INT NOT NULL,
                total_vehicles INT NOT NULL,
                green_light_duration INT NOT NULL
            );
        """)
        
        # Create vehicle details table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vehicle_details (
                id SERIAL PRIMARY KEY,
                traffic_data_id INT REFERENCES traffic_data(id),
                vehicle_type VARCHAR(50) NOT NULL,
                bbox_coordinates JSONB NOT NULL
            );
        """)
        
        conn.commit()
        print("Database tables created successfully!")
        
    except Exception as e:
        print(f"Database initialization error: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()

def save_traffic_data(location, vehicle_data, green_light_times):
    """Save traffic analysis results to database"""
    try:
        conn = psycopg2.connect(
            dbname="traffic_management",
            user="postgres",
            password="root",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        
        # Insert data for each lane
        for idx, (data, duration) in enumerate(zip(vehicle_data, green_light_times)):
            # Insert main traffic data
            cur.execute("""
                INSERT INTO traffic_data (location, lane_number, total_vehicles, green_light_duration)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (location, idx+1, data['count'], duration))
            
            traffic_id = cur.fetchone()[0]
            
            # Insert vehicle details
            for vehicle in data['vehicles']:
                cur.execute("""
                    INSERT INTO vehicle_details (traffic_data_id, vehicle_type, bbox_coordinates)
                    VALUES (%s, %s, %s)
                """, (traffic_id, vehicle['label'], 
                     {'x1': vehicle['bbox'][0], 'y1': vehicle['bbox'][1],
                      'x2': vehicle['bbox'][2], 'y2': vehicle['bbox'][3]}))
        
        conn.commit()
        print("Traffic data saved successfully!")
        
    except Exception as e:
        print(f"Error saving traffic data: {e}")
        conn.rollback()
    finally:
        if cur: cur.close()
        if conn: conn.close()

# Initialize database when this module is imported
init_db()
