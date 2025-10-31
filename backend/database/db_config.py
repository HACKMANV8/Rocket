# backend/database/db_config.py
import mysql.connector
from sqlalchemy import create_engine
from config import Config  # ← Changed this line
import logging
import time

logger = logging.getLogger(__name__)

def get_mysql_connection():
    """Create MySQL connection"""
    try:
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            port=Config.MYSQL_PORT
        )
        return conn
    except Exception as e:
        logger.error(f"MySQL connection failed: {e}")
        raise

def get_sqlalchemy_engine():
    """Create SQLAlchemy engine"""
    connection_string = (
        f"mysql+mysqlconnector://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}"
        f"@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.MYSQL_DB}"
    )
    return create_engine(connection_string)

def init_database(retries=10, delay=5):
    """Retry connecting to MySQL until it is ready"""
    for i in range(retries):
        try:
            conn = get_mysql_connection()
            conn.close()
            logger.info("✅ MySQL connection successful")
            return True
        except Exception as e:
            logger.warning(f"Attempt {i+1}/{retries}: MySQL not ready yet. Retrying in {delay}s...")
            time.sleep(delay)
    logger.error("❌ Could not connect to MySQL after multiple retries")
    return False