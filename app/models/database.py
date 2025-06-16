import os
from typing import Dict, Any, Optional
import pymongo
from pymongo import MongoClient
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize MongoDB client
mongo_client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
db = mongo_client['medauth']

# Initialize PostgreSQL connection
pg_conn = None
try:
    # Use direct connection string from environment variable
    pg_conn = psycopg2.connect(os.getenv('DATABASE_URL'))
except psycopg2.OperationalError as e:
    print(f"Warning: Could not connect to PostgreSQL: {e}")
    print("The application will continue with MongoDB only.")
    pg_conn = None
except Exception as e:
    print(f"Warning: Unexpected error connecting to PostgreSQL: {e}")
    print("The application will continue with MongoDB only.")
    pg_conn = None

def init_db():
    """Initialize database collections and tables"""
    # MongoDB collections
    doctors = db['doctors']
    prescriptions = db['prescriptions']
    
    # Create indexes
    doctors.create_index([('license_number', pymongo.ASCENDING)], unique=True)
    prescriptions.create_index([('doctor_license', pymongo.ASCENDING)])
    
    # PostgreSQL tables (only if connection is available)
    if pg_conn:
        try:
            with pg_conn.cursor() as cur:
                # Create drug interactions table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS drug_interactions (
                        id SERIAL PRIMARY KEY,
                        drug1 VARCHAR(100) NOT NULL,
                        drug2 VARCHAR(100) NOT NULL,
                        severity VARCHAR(20) NOT NULL,
                        description TEXT NOT NULL,
                        UNIQUE(drug1, drug2)
                    )
                """)
                
                # Create drug contraindications table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS drug_contraindications (
                        id SERIAL PRIMARY KEY,
                        drug_name VARCHAR(100) NOT NULL,
                        conditions TEXT[] NOT NULL,
                        severity VARCHAR(20) NOT NULL,
                        UNIQUE(drug_name)
                    )
                """)
            
            pg_conn.commit()
        except Exception as e:
            print(f"Warning: Could not initialize PostgreSQL tables: {e}")
    else:
        print("PostgreSQL initialization skipped - using MongoDB only mode")

def get_doctor_by_license(license_number: str) -> Optional[Dict[str, Any]]:
    """Get doctor information by license number"""
    return db.doctors.find_one({'license_number': license_number})

def get_drug_interactions(drug1: str, drug2: str) -> Optional[Dict[str, Any]]:
    """Get drug interaction information"""
    with pg_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT * FROM drug_interactions 
            WHERE (drug1 = %s AND drug2 = %s) 
            OR (drug1 = %s AND drug2 = %s)
        """, (drug1, drug2, drug2, drug1))
        return cur.fetchone()

def get_drug_contraindications(drug_name: str) -> Optional[Dict[str, Any]]:
    """Get drug contraindications"""
    with pg_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT * FROM drug_contraindications 
            WHERE drug_name = %s
        """, (drug_name,))
        return cur.fetchone()

def save_prescription_verification(verification_data: Dict[str, Any]) -> str:
    """Save prescription verification results"""
    result = db.prescriptions.insert_one(verification_data)
    return str(result.inserted_id)

def get_prescription_history(doctor_license: str, limit: int = 10) -> list:
    """Get prescription verification history for a doctor"""
    return list(db.prescriptions.find(
        {'doctor_license': doctor_license},
        sort=[('timestamp', -1)],
        limit=limit
    ))

def add_doctor(doctor_data: Dict[str, Any]) -> str:
    """Add a new doctor to the database"""
    result = db.doctors.insert_one(doctor_data)
    return str(result.inserted_id)

def update_doctor_status(license_number: str, status: str) -> bool:
    """Update doctor's license status"""
    result = db.doctors.update_one(
        {'license_number': license_number},
        {'$set': {'status': status}}
    )
    return result.modified_count > 0

def add_drug_interaction(interaction_data: Dict[str, Any]) -> int:
    """Add a new drug interaction"""
    with pg_conn.cursor() as cur:
        cur.execute("""
            INSERT INTO drug_interactions (drug1, drug2, severity, description)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (drug1, drug2) DO UPDATE
            SET severity = EXCLUDED.severity,
                description = EXCLUDED.description
            RETURNING id
        """, (
            interaction_data['drug1'],
            interaction_data['drug2'],
            interaction_data['severity'],
            interaction_data['description']
        ))
        pg_conn.commit()
        return cur.fetchone()[0]

def add_drug_contraindication(contraindication_data: Dict[str, Any]) -> int:
    """Add a new drug contraindication"""
    with pg_conn.cursor() as cur:
        cur.execute("""
            INSERT INTO drug_contraindications (drug_name, conditions, severity)
            VALUES (%s, %s, %s)
            ON CONFLICT (drug_name) DO UPDATE
            SET conditions = EXCLUDED.conditions,
                severity = EXCLUDED.severity
            RETURNING id
        """, (
            contraindication_data['drug_name'],
            contraindication_data['conditions'],
            contraindication_data['severity']
        ))
        pg_conn.commit()
        return cur.fetchone()[0] 