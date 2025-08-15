#!/usr/bin/env python3
"""
Test script for Disaster Database Module

Demonstrates the database functionality with sample data.
"""

from database import db
from datetime import datetime
import json


def test_database_functionality():
    """Test the database functionality with sample data."""
    print("Testing Disaster Response Database\n")
    
    # Test 1: Create sample resources
    print("1. Creating sample resources...")
    sample_resources = [
        {
            'id': 'RES-001',
            'type': 'vehicle',
            'name': 'Ambulance Alpha',
            'location': 'Station A',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'capacity': '2 patients + 2 crew',
            'equipment': ['defibrillator', 'oxygen', 'first_aid_kit']
        },
        {
            'id': 'RES-002',
            'type': 'vehicle',
            'name': 'Fire Truck Bravo',
            'location': 'Station B',
            'latitude': 40.7589,
            'longitude': -73.9851,
            'capacity': '6 firefighters',
            'equipment': ['water_tank', 'ladders', 'jaws_of_life']
        },
        {
            'id': 'RES-003',
            'type': 'equipment',
            'name': 'Portable Generator',
            'location': 'Warehouse C',
            'capacity': '5000W',
            'fuel_type': 'gasoline'
        }
    ]
    
    for resource in sample_resources:
        if db.create_resource(resource):
            print(f"   ✓ Created {resource['name']}")
        else:
            print(f"   ✗ Failed to create {resource['name']}")
    
    # Test 2: Create sample emergency contacts
    print("\n2. Creating sample emergency contacts...")
    sample_contacts = [
        {
            'id': 'CONT-001',
            'name': 'John Smith',
            'organization': 'Fire Department',
            'role': 'Fire Chief',
            'phone': '555-0101',
            'email': 'chief@firedept.gov',
            'contact_type': 'emergency',
            'priority': 'high'
        },
        {
            'id': 'CONT-002',
            'name': 'Dr. Sarah Johnson',
            'organization': 'City Hospital',
            'role': 'Emergency Director',
            'phone': '555-0202',
            'phone_alt': '555-0203',
            'email': 'emergency@cityhospital.gov',
            'contact_type': 'medical',
            'priority': 'high'
        },
        {
            'id': 'CONT-003',
            'name': 'Mike Wilson',
            'organization': 'Police Department',
            'role': 'Dispatch Supervisor',
            'phone': '555-0303',
            'email': 'dispatch@police.gov',
            'contact_type': 'emergency',
            'priority': 'normal'
        }
    ]
    
    for contact in sample_contacts:
        if db.create_emergency_contact(contact):
            print(f"   ✓ Created {contact['name']} ({contact['organization']})")
        else:
            print(f"   ✗ Failed to create {contact['name']}")
    
    # Test 3: Create sample personnel
    print("\n3. Creating sample personnel...")
    sample_personnel = [
        {
            'id': 'PER-001',
            'name': 'Alex Rodriguez',
            'role': 'Firefighter',
            'phone': '555-0401',
            'email': 'arodriguez@firedept.gov',
            'location': 'Station A',
            'skills': ['fire_suppression', 'rescue', 'hazmat'],
            'certifications': ['firefighter_1', 'emt_basic'],
            'availability_hours': '24/7'
        },
        {
            'id': 'PER-002',
            'name': 'Lisa Chen',
            'role': 'EMT',
            'phone': '555-0402',
            'email': 'lchen@ambulance.gov',
            'location': 'Station A',
            'skills': ['emergency_medicine', 'patient_transport'],
            'certifications': ['emt_paramedic', 'cpr_instructor'],
            'availability_hours': '12-hour shifts'
        }
    ]
    
    for person in sample_personnel:
        if db.create_personnel(person):
            print(f"   ✓ Created {person['name']} ({person['role']})")
        else:
            print(f"   ✗ Failed to create {person['name']}")
    
    # Test 4: Create sample incidents
    print("\n4. Creating sample incidents...")
    sample_incidents = [
        {
            'id': 'INC-001',
            'type': 'fire',
            'description': 'Building fire at downtown office complex',
            'location': '123 Main Street',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'priority': 'high',
            'severity': 'severe',
            'reported_by': 'CONT-003'
        },
        {
            'id': 'INC-002',
            'type': 'medical',
            'description': 'Multiple vehicle accident on highway',
            'location': 'I-95 Exit 15',
            'latitude': 40.7589,
            'longitude': -73.9851,
            'priority': 'critical',
            'severity': 'critical',
            'reported_by': 'CONT-002'
        }
    ]
    
    for incident in sample_incidents:
        if db.create_incident(incident):
            print(f"   ✓ Created incident {incident['id']} ({incident['type']})")
        else:
            print(f"   ✗ Failed to create incident {incident['id']}")
    
    # Test 5: Create sample locations
    print("\n5. Creating sample locations...")
    sample_locations = [
        {
            'id': 'LOC-001',
            'name': 'Emergency Operations Center',
            'address': '456 Emergency Way',
            'latitude': 40.7505,
            'longitude': -73.9934,
            'type': 'command_center',
            'description': 'Primary emergency coordination facility',
            'capacity': 50,
            'facilities': ['communications', 'meeting_rooms', 'equipment_storage']
        },
        {
            'id': 'LOC-002',
            'name': 'Evacuation Shelter A',
            'address': '789 Shelter Street',
            'latitude': 40.7450,
            'longitude': -73.9900,
            'type': 'shelter',
            'description': 'Primary evacuation shelter',
            'capacity': 200,
            'facilities': ['beds', 'food_service', 'medical_station']
        }
    ]
    
    for location in sample_locations:
        if db.create_location(location):
            print(f"   ✓ Created {location['name']}")
        else:
            print(f"   ✗ Failed to create {location['name']}")
    
    # Test 6: Test resource assignment
    print("\n6. Testing resource assignment...")
    if db.assign_resource('RES-001', 'INC-001', 'PER-001', 'Assigned to fire incident'):
        print("   ✓ Assigned RES-001 to INC-001")
    else:
        print("   ✗ Failed to assign resource")
    
    # Test 7: Display database information
    print("\n7. Database Information:")
    db_info = db.get_database_info()
    print(f"   Database Size: {db_info.get('database_size_mb', 0)} MB")
    print(f"   Table Counts: {db_info.get('table_counts', {})}")
    print(f"   Resource Status: {db_info.get('resource_status_summary', {})}")
    print(f"   Incident Status: {db_info.get('incident_status_summary', {})}")
    
    # Test 8: Query examples
    print("\n8. Query Examples:")
    
    # Get all available resources
    available_resources = db.get_resources(status='available')
    print(f"   Available Resources: {len(available_resources)}")
    
    # Get high-priority emergency contacts
    high_priority_contacts = db.get_emergency_contacts(priority='high')
    print(f"   High Priority Contacts: {len(high_priority_contacts)}")
    
    # Get firefighters
    firefighters = db.get_personnel(role='Firefighter')
    print(f"   Firefighters: {len(firefighters)}")
    
    # Get active incidents
    active_incidents = db.get_incidents(status='active')
    print(f"   Active Incidents: {len(active_incidents)}")
    
    # Test 9: Export functionality
    print("\n9. Testing export functionality...")
    if db.export_table_to_json('resources', 'data/exported_resources.json'):
        print("   ✓ Exported resources table to JSON")
    else:
        print("   ✗ Failed to export resources table")
    
    print("\nPASS Database testing completed successfully!")
    print("\nYou can now use the CLI tool to interact with the database:")
    print("  python cli.py resources")
    print("  python cli.py status")


if __name__ == '__main__':
    test_database_functionality()
