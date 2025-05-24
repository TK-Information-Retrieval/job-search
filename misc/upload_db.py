import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import ast
from sqlalchemy import text
import json
from urllib.parse import quote_plus
import time
import sys
from dotenv import load_dotenv
import os
import sqlalchemy

load_dotenv()

def format_json_string(json_str):
    if not json_str or pd.isna(json_str):
        return None
    try:
        json.loads(json_str)
        return json_str
    except:
        try:
            dict_data = ast.literal_eval(json_str)
            return json.dumps(dict_data)
        except:
            return None

def format_benefits(benefits_str):
    if not benefits_str or pd.isna(benefits_str):
        return None
    
    if benefits_str.startswith('{') and benefits_str.endswith('}'):
        items = benefits_str[1:-1].split(', ')
        return json.dumps(items)
    return benefits_str

db_params = {
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),  
    'password': os.getenv('DB_PASSWORD'), 
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}
csv_file_path = 'job_descriptions.csv'
try:
    print("Testing database connection...")
    conn = psycopg2.connect(
        user=db_params['user'],
        password=db_params['password'],
        host=db_params['host'],
        port=db_params['port'],
        database=db_params['database'],
        connect_timeout=10 
    )
    conn.close()
    print("Database connection successful!")
except Exception as e:
    print(f"Error connecting to database: {e}")
    print("\nTroubleshooting tips:")
    print("1. Check if the Supabase host is correct")
    print("2. Verify your credentials")
    print("3. Make sure your network can reach Supabase")
    sys.exit(1)

print(pd.__version__)
print(sqlalchemy.__version__)

password_encoded = quote_plus(db_params['password'])
connection_string = f"postgresql://{db_params['user']}:{password_encoded}@{db_params['host']}:{db_params['port']}/{db_params['database']}"

try:
    engine = create_engine(
        connection_string,
        connect_args={
            'connect_timeout': 30, 
            'application_name': 'job_listings_import' 
        }
    )
    print("SQLAlchemy engine created successfully")
except Exception as e:
    print(f"Error creating SQLAlchemy engine: {e}")
    sys.exit(1)

try:
    with engine.begin() as connection:
        result = connection.execute(text("SELECT to_regclass('public.job_listings')"))
        table_exists = result.scalar()
        
        if not table_exists:
            print("Creating job_listings table...")
            connection.execute(text("""
                CREATE TABLE job_listings (
                    job_id BIGINT PRIMARY KEY,
                    experience VARCHAR(100),
                    qualifications VARCHAR(100),
                    salary_range VARCHAR(50),
                    location VARCHAR(100),
                    country VARCHAR(100),
                    latitude DECIMAL(10, 6),
                    longitude DECIMAL(10, 6),
                    work_type VARCHAR(50),
                    company_size INTEGER,
                    job_posting_date DATE,
                    preference VARCHAR(50),
                    contact_person VARCHAR(100),
                    contact VARCHAR(100),
                    job_title VARCHAR(100),
                    role VARCHAR(100),
                    job_portal VARCHAR(100),
                    job_description TEXT,
                    benefits TEXT,
                    skills TEXT,
                    responsibilities TEXT,
                    company VARCHAR(100),
                    company_profile JSONB
                )
            """))
            print("Table created successfully")
        else:
            print("Table already exists, proceeding with import")
except Exception as e:
    print(f"Error checking/creating table: {e}")
    sys.exit(1)

try:
    print(f"Reading CSV file: {csv_file_path}")
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            sample = f.read(1024)
        print("CSV file is readable")
    except Exception as file_error:
        print(f"Error reading CSV file: {file_error}")
        sys.exit(1)
        
    chunksize = 5000  
    total_rows = 0
    total_file_rows = sum(1 for _ in open(csv_file_path)) - 1 
    print(f"Total rows in CSV: {total_file_rows}")
    
    start_time = time.time()
    
    for chunk_index, chunk in enumerate(pd.read_csv(csv_file_path, chunksize=chunksize)):
        chunk_start = time.time()
        if chunk_index < 170:
            continue
        if chunk_index > 250:
            break
        print(f"\nProcessing chunk {chunk_index+1}...")
        
        # Clean up data
        print("Formatting JSON and Benefits columns...")
        chunk['Company Profile'] = chunk['Company Profile'].apply(format_json_string)
        chunk['Benefits'] = chunk['Benefits'].apply(format_benefits)
        
        print("Converting data types...")
        chunk['Job Posting Date'] = pd.to_datetime(chunk['Job Posting Date'], errors='coerce')
        chunk['latitude'] = pd.to_numeric(chunk['latitude'], errors='coerce')
        chunk['longitude'] = pd.to_numeric(chunk['longitude'], errors='coerce')
        chunk['Company Size'] = pd.to_numeric(chunk['Company Size'], errors='coerce')
        chunk = chunk.drop_duplicates(subset=['Job Id'])
        
        chunk.columns = [col.lower().replace(" ", "_") for col in chunk.columns]
        
        # Write to PostgreSQL
        print(f"Writing {len(chunk)} rows to database...")
        try:
            chunk.to_sql('job_listings', engine, if_exists='append', index=False, 
                        method='multi', chunksize=500)
            
            total_rows += len(chunk)
            elapsed = time.time() - start_time
            chunk_time = time.time() - chunk_start
            
            # Progress reporting
            percent_complete = (total_rows / total_file_rows) * 100
            print(f"Processed {total_rows}/{total_file_rows} rows ({percent_complete:.1f}%)")
            print(f"Chunk processing time: {chunk_time:.2f}s")
            print(f"Total elapsed time: {elapsed:.2f}s")
            print(f"Estimated time remaining: {(elapsed/total_rows)*(total_file_rows-total_rows):.2f}s")
            
        except Exception as import_error:
            print(f"Error importing chunk {chunk_index+1}: {import_error}")
            print("Continuing with next chunk...")
            continue
    
    print(f"\nTotal of {total_rows} rows imported successfully!")
    total_time = time.time() - start_time
    print(f"Total import time: {total_time:.2f}s ({total_rows/total_time:.2f} rows/second)")

except Exception as e:
    print(f"Error during CSV processing: {e}")

# Verify data
print("\nVerifying imported data...")
try:
    with psycopg2.connect(**db_params) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM public.job_listings")
            count = cursor.fetchone()[0]
            print(f"Total rows in database: {count}")
            
            cursor.execute("SELECT * FROM public.job_listings LIMIT 3")
            sample_data = cursor.fetchall()
            print("\nSample data from database:")
            for row in sample_data:
                print(row)
except Exception as e:
    print(f"Error verifying data: {e}")

print("\nImport process completed!")