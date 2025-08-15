#!/usr/bin/env python3
"""
Database Module for Disaster Response Tool

Handles SQLite database operations for incidents, resources, personnel, 
emergency contacts, and locations with comprehensive CRUD functionality.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json


class DisasterDatabase:
    """Comprehensive database manager for disaster response data."""
    
    def __init__(self, db_path: str = "data/disaster.db"):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self):
        """Initialize database with all required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create incidents table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS incidents (
                        id TEXT PRIMARY KEY,
                        type TEXT NOT NULL,
                        description TEXT,
                        location TEXT,
                        latitude REAL,
                        longitude REAL,
                        status TEXT DEFAULT 'active',
                        priority TEXT DEFAULT 'medium',
                        severity TEXT DEFAULT 'moderate',
                        reported_by TEXT,
                        assigned_to TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        resolved_at TIMESTAMP
                    )
                ''')
                
                # Create resources table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS resources (
                        id TEXT PRIMARY KEY,
                        type TEXT NOT NULL,
                        name TEXT NOT NULL,
                        status TEXT DEFAULT 'available',
                        location TEXT,
                        latitude REAL,
                        longitude REAL,
                        assigned_to TEXT,
                        capacity TEXT,
                        fuel_type TEXT,
                        equipment TEXT,
                        maintenance_due DATE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create personnel table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS personnel (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        role TEXT NOT NULL,
                        contact TEXT,
                        phone TEXT,
                        email TEXT,
                        status TEXT DEFAULT 'available',
                        location TEXT,
                        latitude REAL,
                        longitude REAL,
                        skills TEXT,
                        certifications TEXT,
                        availability_hours TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create emergency_contacts table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS emergency_contacts (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        organization TEXT,
                        role TEXT,
                        phone TEXT NOT NULL,
                        phone_alt TEXT,
                        email TEXT,
                        address TEXT,
                        latitude REAL,
                        longitude REAL,
                        contact_type TEXT DEFAULT 'emergency',
                        priority TEXT DEFAULT 'normal',
                        notes TEXT,
                        is_active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create locations table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS locations (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        address TEXT,
                        latitude REAL NOT NULL,
                        longitude REAL NOT NULL,
                        type TEXT,
                        description TEXT,
                        capacity INTEGER,
                        facilities TEXT,
                        access_notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create resource_assignments table for tracking resource usage
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS resource_assignments (
                        id TEXT PRIMARY KEY,
                        resource_id TEXT NOT NULL,
                        incident_id TEXT,
                        assigned_to TEXT,
                        assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        returned_at TIMESTAMP,
                        notes TEXT,
                        FOREIGN KEY (resource_id) REFERENCES resources (id),
                        FOREIGN KEY (incident_id) REFERENCES incidents (id)
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_resources_type ON resources(type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_resources_status ON resources(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_personnel_role ON personnel(role)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_emergency_contacts_type ON emergency_contacts(contact_type)')
                
                conn.commit()
                self.logger.info("Database initialized successfully with all tables")
                
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise
    
    def get_connection(self):
        """Get a database connection."""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results as a list of dictionaries.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of dictionaries representing the results
        """
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, params)
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except sqlite3.Error as e:
            self.logger.error(f"Query execution failed: {e}")
            return []
    
    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """
        Execute an INSERT, UPDATE, or DELETE query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Update execution failed: {e}")
            return False
    
    def execute_single_value(self, query: str, params: tuple = ()) -> Optional[Any]:
        """
        Execute a query that returns a single value.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Single value result or None
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result[0] if result else None
        except sqlite3.Error as e:
            self.logger.error(f"Single value query failed: {e}")
            return None
    
    # ==================== RESOURCE OPERATIONS ====================
    
    def create_resource(self, resource_data: Dict[str, Any]) -> bool:
        """Create a new resource."""
        query = '''
            INSERT INTO resources (id, type, name, status, location, latitude, longitude, 
                                 capacity, fuel_type, equipment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            resource_data.get('id'),
            resource_data.get('type'),
            resource_data.get('name'),
            resource_data.get('status', 'available'),
            resource_data.get('location'),
            resource_data.get('latitude'),
            resource_data.get('longitude'),
            resource_data.get('capacity'),
            resource_data.get('fuel_type'),
            json.dumps(resource_data.get('equipment', [])) if resource_data.get('equipment') else None
        )
        return self.execute_update(query, params)
    
    def get_resources(self, resource_type: Optional[str] = None, 
                     status: Optional[str] = None, 
                     location: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get resources with optional filtering."""
        query = "SELECT * FROM resources WHERE 1=1"
        params = []
        
        if resource_type:
            query += " AND type = ?"
            params.append(resource_type)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if location:
            query += " AND location LIKE ?"
            params.append(f"%{location}%")
        
        query += " ORDER BY type, name"
        return self.execute_query(query, tuple(params))
    
    def get_resource_by_id(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific resource by ID."""
        results = self.execute_query("SELECT * FROM resources WHERE id = ?", (resource_id,))
        return results[0] if results else None
    
    def update_resource(self, resource_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing resource."""
        if not updates:
            return False
        
        set_clauses = []
        params = []
        
        for key, value in updates.items():
            if key in ['equipment'] and isinstance(value, list):
                set_clauses.append(f"{key} = ?")
                params.append(json.dumps(value))
            else:
                set_clauses.append(f"{key} = ?")
                params.append(value)
        
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        params.append(resource_id)
        
        query = f"UPDATE resources SET {', '.join(set_clauses)} WHERE id = ?"
        return self.execute_update(query, tuple(params))
    
    def delete_resource(self, resource_id: str) -> bool:
        """Delete a resource."""
        return self.execute_update("DELETE FROM resources WHERE id = ?", (resource_id,))
    
    def assign_resource(self, resource_id: str, incident_id: str, assigned_to: str, notes: str = "") -> bool:
        """Assign a resource to an incident."""
        # First update resource status
        if not self.update_resource(resource_id, {'status': 'in_use', 'assigned_to': assigned_to}):
            return False
        
        # Create assignment record
        assignment_id = f"ASS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        query = '''
            INSERT INTO resource_assignments (id, resource_id, incident_id, assigned_to, notes)
            VALUES (?, ?, ?, ?, ?)
        '''
        return self.execute_update(query, (assignment_id, resource_id, incident_id, assigned_to, notes))
    
    def return_resource(self, resource_id: str) -> bool:
        """Return a resource (mark as available)."""
        # Update resource status
        if not self.update_resource(resource_id, {'status': 'available', 'assigned_to': None}):
            return False
        
        # Mark assignment as returned
        query = '''
            UPDATE resource_assignments 
            SET returned_at = CURRENT_TIMESTAMP 
            WHERE resource_id = ? AND returned_at IS NULL
        '''
        return self.execute_update(query, (resource_id,))
    
    # ==================== EMERGENCY CONTACTS OPERATIONS ====================
    
    def create_emergency_contact(self, contact_data: Dict[str, Any]) -> bool:
        """Create a new emergency contact."""
        query = '''
            INSERT INTO emergency_contacts (id, name, organization, role, phone, phone_alt, 
                                          email, address, latitude, longitude, contact_type, 
                                          priority, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            contact_data.get('id'),
            contact_data.get('name'),
            contact_data.get('organization'),
            contact_data.get('role'),
            contact_data.get('phone'),
            contact_data.get('phone_alt'),
            contact_data.get('email'),
            contact_data.get('address'),
            contact_data.get('latitude'),
            contact_data.get('longitude'),
            contact_data.get('contact_type', 'emergency'),
            contact_data.get('priority', 'normal'),
            contact_data.get('notes')
        )
        return self.execute_update(query, params)
    
    def get_emergency_contacts(self, contact_type: Optional[str] = None, 
                              priority: Optional[str] = None,
                              organization: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get emergency contacts with optional filtering."""
        query = "SELECT * FROM emergency_contacts WHERE is_active = 1"
        params = []
        
        if contact_type:
            query += " AND contact_type = ?"
            params.append(contact_type)
        
        if priority:
            query += " AND priority = ?"
            params.append(priority)
        
        if organization:
            query += " AND organization LIKE ?"
            params.append(f"%{organization}%")
        
        query += " ORDER BY priority DESC, name"
        return self.execute_query(query, tuple(params))
    
    def get_emergency_contact_by_id(self, contact_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific emergency contact by ID."""
        results = self.execute_query("SELECT * FROM emergency_contacts WHERE id = ?", (contact_id,))
        return results[0] if results else None
    
    def update_emergency_contact(self, contact_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing emergency contact."""
        if not updates:
            return False
        
        set_clauses = []
        params = []
        
        for key, value in updates.items():
            set_clauses.append(f"{key} = ?")
            params.append(value)
        
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        params.append(contact_id)
        
        query = f"UPDATE emergency_contacts SET {', '.join(set_clauses)} WHERE id = ?"
        return self.execute_update(query, tuple(params))
    
    def delete_emergency_contact(self, contact_id: str) -> bool:
        """Soft delete an emergency contact (mark as inactive)."""
        return self.update_emergency_contact(contact_id, {'is_active': 0})
    
    # ==================== INCIDENT OPERATIONS ====================
    
    def create_incident(self, incident_data: Dict[str, Any]) -> bool:
        """Create a new incident."""
        query = '''
            INSERT INTO incidents (id, type, description, location, latitude, longitude, 
                                 priority, severity, reported_by, assigned_to)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            incident_data.get('id'),
            incident_data.get('type'),
            incident_data.get('description'),
            incident_data.get('location'),
            incident_data.get('latitude'),
            incident_data.get('longitude'),
            incident_data.get('priority', 'medium'),
            incident_data.get('severity', 'moderate'),
            incident_data.get('reported_by'),
            incident_data.get('assigned_to')
        )
        return self.execute_update(query, params)
    
    def get_incidents(self, status: str = 'active', 
                     priority: Optional[str] = None,
                     type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get incidents with optional filtering."""
        query = "SELECT * FROM incidents WHERE 1=1"
        params = []
        
        if status != 'all':
            query += " AND status = ?"
            params.append(status)
        
        if priority:
            query += " AND priority = ?"
            params.append(priority)
        
        if type:
            query += " AND type = ?"
            params.append(type)
        
        query += " ORDER BY created_at DESC"
        return self.execute_query(query, tuple(params))
    
    def update_incident_status(self, incident_id: str, status: str, 
                             resolved_by: Optional[str] = None) -> bool:
        """Update incident status."""
        updates = {'status': status, 'updated_at': 'CURRENT_TIMESTAMP'}
        
        if status == 'resolved':
            updates['resolved_at'] = 'CURRENT_TIMESTAMP'
            if resolved_by:
                updates['assigned_to'] = resolved_by
        
        return self.update_incident(incident_id, updates)
    
    def update_incident(self, incident_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing incident."""
        if not updates:
            return False
        
        set_clauses = []
        params = []
        
        for key, value in updates.items():
            if value == 'CURRENT_TIMESTAMP':
                set_clauses.append(f"{key} = CURRENT_TIMESTAMP")
            else:
                set_clauses.append(f"{key} = ?")
                params.append(value)
        
        params.append(incident_id)
        
        query = f"UPDATE incidents SET {', '.join(set_clauses)} WHERE id = ?"
        return self.execute_update(query, tuple(params))
    
    # ==================== PERSONNEL OPERATIONS ====================
    
    def create_personnel(self, personnel_data: Dict[str, Any]) -> bool:
        """Create new personnel record."""
        query = '''
            INSERT INTO personnel (id, name, role, contact, phone, email, location, 
                                 latitude, longitude, skills, certifications, availability_hours)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            personnel_data.get('id'),
            personnel_data.get('name'),
            personnel_data.get('role'),
            personnel_data.get('contact'),
            personnel_data.get('phone'),
            personnel_data.get('email'),
            personnel_data.get('location'),
            personnel_data.get('latitude'),
            personnel_data.get('longitude'),
            json.dumps(personnel_data.get('skills', [])) if personnel_data.get('skills') else None,
            json.dumps(personnel_data.get('certifications', [])) if personnel_data.get('certifications') else None,
            personnel_data.get('availability_hours')
        )
        return self.execute_update(query, params)
    
    def get_personnel(self, role: Optional[str] = None, 
                     status: Optional[str] = None,
                     skills: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get personnel with optional filtering."""
        query = "SELECT * FROM personnel WHERE 1=1"
        params = []
        
        if role:
            query += " AND role = ?"
            params.append(role)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if skills:
            # Simple skill matching (could be enhanced with full-text search)
            skill_conditions = []
            for skill in skills:
                skill_conditions.append("skills LIKE ?")
                params.append(f"%{skill}%")
            query += f" AND ({' OR '.join(skill_conditions)})"
        
        query += " ORDER BY role, name"
        return self.execute_query(query, tuple(params))
    
    # ==================== LOCATION OPERATIONS ====================
    
    def create_location(self, location_data: Dict[str, Any]) -> bool:
        """Create a new location record."""
        query = '''
            INSERT INTO locations (id, name, address, latitude, longitude, type, 
                                 description, capacity, facilities, access_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            location_data.get('id'),
            location_data.get('name'),
            location_data.get('address'),
            location_data.get('latitude'),
            location_data.get('longitude'),
            location_data.get('type'),
            location_data.get('description'),
            location_data.get('capacity'),
            json.dumps(location_data.get('facilities', [])) if location_data.get('facilities') else None,
            location_data.get('access_notes')
        )
        return self.execute_update(query, params)
    
    def get_locations(self, location_type: Optional[str] = None,
                     near_coordinates: Optional[Tuple[float, float, float]] = None) -> List[Dict[str, Any]]:
        """
        Get locations with optional filtering.
        
        Args:
            location_type: Filter by location type
            near_coordinates: Tuple of (lat, lon, radius_km) for proximity search
        """
        query = "SELECT * FROM locations WHERE 1=1"
        params = []
        
        if location_type:
            query += " AND type = ?"
            params.append(location_type)
        
        if near_coordinates:
            lat, lon, radius_km = near_coordinates
            # Simple bounding box approximation (could be enhanced with proper distance calculation)
            lat_range = radius_km / 111.0  # Rough conversion: 1 degree ≈ 111 km
            lon_range = radius_km / (111.0 * abs(lat) / 90.0)  # Adjust for latitude
            
            query += " AND latitude BETWEEN ? AND ? AND longitude BETWEEN ? AND ?"
            params.extend([lat - lat_range, lat + lat_range, lon - lon_range, lon + lon_range])
        
        query += " ORDER BY name"
        return self.execute_query(query, tuple(params))
    
    # ==================== UTILITY OPERATIONS ====================
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get comprehensive database statistics and information."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get table counts
                tables = ['incidents', 'resources', 'personnel', 'emergency_contacts', 'locations']
                counts = {}
                
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    counts[table] = cursor.fetchone()[0]
                
                # Get database size
                cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
                size_bytes = cursor.fetchone()[0]
                
                # Get resource status summary
                cursor.execute("SELECT status, COUNT(*) FROM resources GROUP BY status")
                resource_status = dict(cursor.fetchall())
                
                # Get incident status summary
                cursor.execute("SELECT status, COUNT(*) FROM incidents GROUP BY status")
                incident_status = dict(cursor.fetchall())
                
                # Get personnel role summary
                cursor.execute("SELECT role, COUNT(*) FROM personnel GROUP BY role")
                personnel_roles = dict(cursor.fetchall())
                
                return {
                    'table_counts': counts,
                    'database_size_bytes': size_bytes,
                    'database_size_mb': round(size_bytes / (1024 * 1024), 2),
                    'resource_status_summary': resource_status,
                    'incident_status_summary': incident_status,
                    'personnel_role_summary': personnel_roles,
                    'last_updated': datetime.now().isoformat()
                }
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get database info: {e}")
            return {}
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database."""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            self.logger.info(f"Database backed up to: {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Database backup failed: {e}")
            return False
    
    def export_table_to_json(self, table_name: str, export_path: str) -> bool:
        """Export a table to JSON format."""
        try:
            data = self.execute_query(f"SELECT * FROM {table_name}")
            
            export_data = {
                "table": table_name,
                "exported_at": datetime.now().isoformat(),
                "record_count": len(data),
                "data": data
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Table {table_name} exported to: {export_path}")
            return True
        except Exception as e:
            self.logger.error(f"Export failed: {e}")
            return False


# Global database instance
db = DisasterDatabase()
