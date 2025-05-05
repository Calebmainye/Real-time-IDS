"""
Database operations for the intrusion detection system.
This module handles the storage and retrieval of alerts, users,
and system metrics.
"""

import sqlite3
import json
import os
import logging
from datetime import datetime
import uuid

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Class for managing database operations.
    """
    
    def __init__(self, db_file='ids_database.db'):
        """
        Initialize the database manager.
        
        Args:
            db_file (str): Path to the SQLite database file
        """
        self.db_file = db_file
        self.conn = None
        self.initialized = False
        
        self.initialize_db()
    
    def get_connection(self):
        """
        Get a database connection.
        
        Returns:
            sqlite3.Connection: Database connection
        """
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_file)
            # Enable foreign keys
            self.conn.execute("PRAGMA foreign_keys = ON")
            # Configure row factory to return dictionaries
            self.conn.row_factory = sqlite3.Row
        
        return self.conn
    
    def close_connection(self):
        """
        Close the database connection.
        """
        if self.conn is not None:
            self.conn.close()
            self.conn = None
    
    def initialize_db(self):
        """
        Initialize the database by creating required tables.
        """
        if self.initialized:
            return
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_login TEXT
            )
            ''')
            
            # Create alerts table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                source TEXT NOT NULL,
                confidence REAL NOT NULL,
                is_resolved INTEGER DEFAULT 0,
                resolved_at TEXT,
                resolved_by TEXT,
                details TEXT NOT NULL,
                user_id TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            ''')
            
            # Create metrics table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                value REAL NOT NULL,
                details TEXT
            )
            ''')
            
            # Create settings table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                description TEXT,
                updated_at TEXT NOT NULL
            )
            ''')
            
            conn.commit()
            self.initialized = True
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    # User operations
    def add_user(self, email, name, password_hash):
        """
        Add a new user to the database.
        
        Args:
            email (str): User email
            name (str): User name
            password_hash (str): Hashed password
            
        Returns:
            str: User ID
        """
        try:
            user_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                'INSERT INTO users (id, email, name, password_hash, created_at) VALUES (?, ?, ?, ?, ?)',
                (user_id, email, name, password_hash, now)
            )
            
            conn.commit()
            logger.info(f"User added successfully: {email}")
            return user_id
        except Exception as e:
            logger.error(f"Error adding user: {str(e)}")
            raise
    
    def get_user_by_email(self, email):
        """
        Get a user by email.
        
        Args:
            email (str): User email
            
        Returns:
            dict: User data or None if not found
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            raise
    
    def update_last_login(self, user_id):
        """
        Update a user's last login timestamp.
        
        Args:
            user_id (str): User ID
        """
        try:
            now = datetime.now().isoformat()
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                'UPDATE users SET last_login = ? WHERE id = ?',
                (now, user_id)
            )
            
            conn.commit()
            logger.info(f"Last login updated for user: {user_id}")
        except Exception as e:
            logger.error(f"Error updating last login: {str(e)}")
            raise
    
    # Alert operations
    def add_alert(self, alert_data, user_id=None):
        """
        Add a new alert to the database.
        
        Args:
            alert_data (dict): Alert data
            user_id (str, optional): User ID associated with the alert
            
        Returns:
            str: Alert ID
        """
        try:
            # Generate ID if not provided
            if 'id' not in alert_data:
                alert_data['id'] = str(uuid.uuid4())
            
            # Ensure timestamp exists
            if 'timestamp' not in alert_data:
                alert_data['timestamp'] = datetime.now().isoformat()
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Convert details to JSON string
            details_json = json.dumps(alert_data.get('details', {}))
            
            cursor.execute(
                '''
                INSERT INTO alerts 
                (id, timestamp, source, confidence, details, user_id) 
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                (
                    alert_data['id'],
                    alert_data['timestamp'],
                    alert_data['source'],
                    alert_data['confidence'],
                    details_json,
                    user_id
                )
            )
            
            conn.commit()
            logger.info(f"Alert added successfully: {alert_data['id']}")
            return alert_data['id']
        except Exception as e:
            logger.error(f"Error adding alert: {str(e)}")
            raise
    
    def get_alerts(self, limit=100, offset=0, resolved=None, user_id=None):
        """
        Get alerts from the database.
        
        Args:
            limit (int, optional): Maximum number of alerts to retrieve
            offset (int, optional): Number of alerts to skip
            resolved (bool, optional): Filter by resolved status
            user_id (str, optional): Filter by user ID
            
        Returns:
            list: List of alert dictionaries
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = 'SELECT * FROM alerts'
            params = []
            
            # Build WHERE clause
            where_clauses = []
            
            if resolved is not None:
                where_clauses.append('is_resolved = ?')
                params.append(1 if resolved else 0)
            
            if user_id is not None:
                where_clauses.append('user_id = ?')
                params.append(user_id)
            
            if where_clauses:
                query += ' WHERE ' + ' AND '.join(where_clauses)
            
            # Add ORDER BY, LIMIT, and OFFSET
            query += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries and parse details JSON
            alerts = []
            for row in rows:
                alert = dict(row)
                alert['details'] = json.loads(alert['details'])
                alerts.append(alert)
            
            logger.info(f"Retrieved {len(alerts)} alerts")
            return alerts
        except Exception as e:
            logger.error(f"Error getting alerts: {str(e)}")
            raise
    
    def get_alert_by_id(self, alert_id):
        """
        Get an alert by ID.
        
        Args:
            alert_id (str): Alert ID
            
        Returns:
            dict: Alert data or None if not found
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM alerts WHERE id = ?', (alert_id,))
            row = cursor.fetchone()
            
            if row:
                alert = dict(row)
                alert['details'] = json.loads(alert['details'])
                return alert
            return None
        except Exception as e:
            logger.error(f"Error getting alert by ID: {str(e)}")
            raise
    
    def resolve_alert(self, alert_id, resolved_by=None):
        """
        Mark an alert as resolved.
        
        Args:
            alert_id (str): Alert ID
            resolved_by (str, optional): User ID of resolver
        """
        try:
            now = datetime.now().isoformat()
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                'UPDATE alerts SET is_resolved = 1, resolved_at = ?, resolved_by = ? WHERE id = ?',
                (now, resolved_by, alert_id)
            )
            
            conn.commit()
            logger.info(f"Alert resolved: {alert_id}")
        except Exception as e:
            logger.error(f"Error resolving alert: {str(e)}")
            raise
    
    # Metrics operations
    def add_metric(self, metric_type, value, details=None):
        """
        Add a new metric to the database.
        
        Args:
            metric_type (str): Type of metric
            value (float): Metric value
            details (dict, optional): Additional details
            
        Returns:
            str: Metric ID
        """
        try:
            metric_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            details_json = None
            if details:
                details_json = json.dumps(details)
            
            cursor.execute(
                'INSERT INTO metrics (id, timestamp, metric_type, value, details) VALUES (?, ?, ?, ?, ?)',
                (metric_id, now, metric_type, value, details_json)
            )
            
            conn.commit()
            logger.info(f"Metric added: {metric_type} = {value}")
            return metric_id
        except Exception as e:
            logger.error(f"Error adding metric: {str(e)}")
            raise
    
    def get_metrics(self, metric_type=None, start_time=None, end_time=None, limit=100):
        """
        Get metrics from the database.
        
        Args:
            metric_type (str, optional): Filter by metric type
            start_time (str, optional): Start timestamp
            end_time (str, optional): End timestamp
            limit (int, optional): Maximum number of metrics to retrieve
            
        Returns:
            list: List of metric dictionaries
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = 'SELECT * FROM metrics'
            params = []
            
            # Build WHERE clause
            where_clauses = []
            
            if metric_type:
                where_clauses.append('metric_type = ?')
                params.append(metric_type)
            
            if start_time:
                where_clauses.append('timestamp >= ?')
                params.append(start_time)
            
            if end_time:
                where_clauses.append('timestamp <= ?')
                params.append(end_time)
            
            if where_clauses:
                query += ' WHERE ' + ' AND '.join(where_clauses)
            
            # Add ORDER BY and LIMIT
            query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries and parse details JSON
            metrics = []
            for row in rows:
                metric = dict(row)
                if metric['details']:
                    metric['details'] = json.loads(metric['details'])
                metrics.append(metric)
            
            logger.info(f"Retrieved {len(metrics)} metrics")
            return metrics
        except Exception as e:
            logger.error(f"Error getting metrics: {str(e)}")
            raise
    
    def get_metric_summary(self, metric_type, interval='day', start_time=None, end_time=None):
        """
        Get summary statistics for a metric type.
        
        Args:
            metric_type (str): Type of metric
            interval (str, optional): Time interval for grouping ('hour', 'day', 'week', 'month')
            start_time (str, optional): Start timestamp
            end_time (str, optional): End timestamp
            
        Returns:
            dict: Summary statistics
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Build time grouping function based on interval
            if interval == 'hour':
                time_func = "strftime('%Y-%m-%d %H', timestamp)"
            elif interval == 'day':
                time_func = "strftime('%Y-%m-%d', timestamp)"
            elif interval == 'week':
                time_func = "strftime('%Y-%W', timestamp)"
            elif interval == 'month':
                time_func = "strftime('%Y-%m', timestamp)"
            else:
                raise ValueError(f"Invalid interval: {interval}")
            
            query = f'''
            SELECT 
                {time_func} as period,
                COUNT(*) as count,
                AVG(value) as avg,
                MIN(value) as min,
                MAX(value) as max,
                SUM(value) as sum
            FROM metrics
            WHERE metric_type = ?
            '''
            
            params = [metric_type]
            
            # Add time filters if provided
            if start_time:
                query += ' AND timestamp >= ?'
                params.append(start_time)
            
            if end_time:
                query += ' AND timestamp <= ?'
                params.append(end_time)
            
            # Group by period and order by period
            query += f' GROUP BY {time_func} ORDER BY {time_func}'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            summary = {
                'metric_type': metric_type,
                'interval': interval,
                'periods': [dict(row) for row in rows]
            }
            
            logger.info(f"Generated metric summary for {metric_type} by {interval}")
            return summary
        except Exception as e:
            logger.error(f"Error getting metric summary: {str(e)}")
            raise
    
    # Settings operations
    def set_setting(self, key, value, description=None):
        """
        Set a system setting.
        
        Args:
            key (str): Setting key
            value (str): Setting value
            description (str, optional): Setting description
        """
        try:
            now = datetime.now().isoformat()
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Convert value to string if it's not already
            if not isinstance(value, str):
                value = str(value)
            
            # Check if setting exists
            cursor.execute('SELECT * FROM settings WHERE key = ?', (key,))
            row = cursor.fetchone()
            
            if row:
                # Update existing setting
                cursor.execute(
                    'UPDATE settings SET value = ?, description = ?, updated_at = ? WHERE key = ?',
                    (value, description, now, key)
                )
            else:
                # Insert new setting
                cursor.execute(
                    'INSERT INTO settings (key, value, description, updated_at) VALUES (?, ?, ?, ?)',
                    (key, value, description, now)
                )
            
            conn.commit()
            logger.info(f"Setting updated: {key} = {value}")
        except Exception as e:
            logger.error(f"Error setting setting: {str(e)}")
            raise
    
    def get_setting(self, key, default=None):
        """
        Get a system setting.
        
        Args:
            key (str): Setting key
            default (str, optional): Default value if setting not found
            
        Returns:
            str: Setting value
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            row = cursor.fetchone()
            
            if row:
                return row['value']
            return default
        except Exception as e:
            logger.error(f"Error getting setting: {str(e)}")
            return default
    
    def get_all_settings(self):
        """
        Get all system settings.
        
        Returns:
            dict: Dictionary mapping keys to values
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT key, value, description, updated_at FROM settings')
            rows = cursor.fetchall()
            
            settings = {row['key']: {
                'value': row['value'],
                'description': row['description'],
                'updated_at': row['updated_at']
            } for row in rows}
            
            logger.info(f"Retrieved {len(settings)} settings")
            return settings
        except Exception as e:
            logger.error(f"Error getting all settings: {str(e)}")
            raise
    
    # Statistics methods
    def get_alert_stats(self, start_time=None, end_time=None):
        """
        Get statistics about alerts.
        
        Args:
            start_time (str, optional): Start timestamp
            end_time (str, optional): End timestamp
            
        Returns:
            dict: Alert statistics
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = '''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_resolved = 1 THEN 1 ELSE 0 END) as resolved,
                SUM(CASE WHEN is_resolved = 0 THEN 1 ELSE 0 END) as unresolved,
                AVG(confidence) as avg_confidence,
                COUNT(DISTINCT source) as source_count
            FROM alerts
            '''
            
            params = []
            
            # Add time filters if provided
            where_clauses = []
            
            if start_time:
                where_clauses.append('timestamp >= ?')
                params.append(start_time)
            
            if end_time:
                where_clauses.append('timestamp <= ?')
                params.append(end_time)
            
            if where_clauses:
                query += ' WHERE ' + ' AND '.join(where_clauses)
            
            cursor.execute(query, params)
            row = cursor.fetchone()
            
            stats = dict(row)
            
            # Get source breakdown
            source_query = '''
            SELECT source, COUNT(*) as count
            FROM alerts
            '''
            
            if where_clauses:
                source_query += ' WHERE ' + ' AND '.join(where_clauses)
            
            source_query += ' GROUP BY source ORDER BY count DESC'
            
            cursor.execute(source_query, params)
            source_rows = cursor.fetchall()
            
            stats['sources'] = [dict(row) for row in source_rows]
            
            # Calculate resolution time for resolved alerts
            if start_time or end_time:
                resolution_query = '''
                SELECT AVG(JULIANDAY(resolved_at) - JULIANDAY(timestamp)) * 24 * 60 as avg_resolution_minutes
                FROM alerts
                WHERE is_resolved = 1
                '''
                
                if where_clauses:
                    resolution_query += ' AND ' + ' AND '.join(where_clauses)
                
                cursor.execute(resolution_query, params)
                resolution_row = cursor.fetchone()
                
                if resolution_row and resolution_row['avg_resolution_minutes'] is not None:
                    stats['avg_resolution_minutes'] = resolution_row['avg_resolution_minutes']
            
            logger.info("Generated alert statistics")
            return stats
        except Exception as e:
            logger.error(f"Error getting alert stats: {str(e)}")
            raise
    
    def get_user_stats(self):
        """
        Get statistics about users.
        
        Returns:
            dict: User statistics
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get total user count
            cursor.execute('SELECT COUNT(*) as total FROM users')
            total_row = cursor.fetchone()
            
            # Get users with recent logins
            cursor.execute('''
            SELECT COUNT(*) as active
            FROM users
            WHERE last_login IS NOT NULL
            AND JULIANDAY('now') - JULIANDAY(last_login) <= 30
            ''')
            active_row = cursor.fetchone()
            
            # Get new users in the last 30 days
            cursor.execute('''
            SELECT COUNT(*) as new
            FROM users
            WHERE JULIANDAY('now') - JULIANDAY(created_at) <= 30
            ''')
            new_row = cursor.fetchone()
            
            stats = {
                'total': total_row['total'],
                'active_last_30_days': active_row['active'],
                'new_last_30_days': new_row['new']
            }
            
            logger.info("Generated user statistics")
            return stats
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            raise