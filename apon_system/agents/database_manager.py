import sqlite3
import logging
from typing import List, Dict
from config import settings

logger = logging.getLogger('DatabaseManager')
DB_PATH = getattr(settings, 'DB_PATH', 'apon_intelligence.db')

def init_database():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                competitor TEXT NOT NULL,
                price REAL NOT NULL,
                source TEXT,
                timestamp TEXT NOT NULL,
                availability TEXT,
                confidence REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                analysis_data TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_content TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

def save_price_data(price_data: List[Dict]) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        for item in price_data:
            cursor.execute('''
                INSERT INTO price_data 
                (product_name, competitor, price, source, timestamp, availability, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                item['product_name'],
                item['competitor'],
                item['price'],
                item['source'],
                item['timestamp'],
                item['availability'],
                item['confidence']
            ))
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(price_data)} price records to database")
        return True
    except Exception as e:
        logger.error(f"Error saving price data: {e}")
        return False

def save_analysis(analysis: Dict) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO analyses (product_name, analysis_data, timestamp)
            VALUES (?, ?, ?)
        ''', (
            analysis['product_name'],
            str(analysis),
            analysis['analysis_timestamp']
        ))
        conn.commit()
        conn.close()
        logger.info(f"Saved analysis for {analysis['product_name']}")
        return True
    except Exception as e:
        logger.error(f"Error saving analysis: {e}")
        return False
