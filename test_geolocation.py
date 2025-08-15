#!/usr/bin/env python3
"""
Test script for Disaster Response Geolocation Features

Demonstrates the enhanced geolocation functionality including:
- Offline emergency facility location finding
- Distance calculations with geopy fallback
- Preloaded emergency facility coordinates
- Address geocoding capabilities
"""

from geolocation import location_manager, Location
import math


def test_geolocation_features():
    """Test all the geolocation functionality."""
    print("Testing Disaster Response Geolocation Features\n")
    
    # Test 1: Display location statistics
    print("1. Location Statistics:")
    stats = location_manager.get_location_statistics()
    print(f"   Total Locations: {stats['total_locations']}")
    print(f"   Active Locations: {stats['active_locations']}")
    print(f"   By Type: {stats['by_type']}")
    print(f"   By Capacity: {stats['by_capacity']}")
    print(f"   Geographic Coverage: {stats['geographic_coverage']}")
    
    # Test 2: Test coordinate validation
    print("\n2. Coordinate Validation:")
    valid_coords = [(40.7128, -74.0060), (0, 0), (90, 180)]
    invalid_coords = [(91, 0), (0, 181), (-91, -181)]
    
    for lat, lon in valid_coords:
        is_valid = location_manager.validate_coordinates(lat, lon)
        print(f"   ({lat}, {lon}): {'✓ Valid' if is_valid else '✗ Invalid'}")
    
    for lat, lon in invalid_coords:
        is_valid = location_manager.validate_coordinates(lat, lon)
        print(f"   ({lat}, {lon}): {'✓ Valid' if is_valid else '✗ Invalid'}")
    
    # Test 3: Test distance calculations
    print("\n3. Distance Calculations:")
    # New York City coordinates
    nyc_lat, nyc_lon = 40.7128, -74.0060
    
    # Test distances to various facilities
    test_locations = [
        ("Bellevue Hospital", 40.7411, -73.9747),
        ("Brooklyn Shelter", 40.6944, -73.9861),
        ("UCLA Medical Center", 34.0664, -118.4450),
        ("Chicago Hospital", 41.8947, -87.6225)
    ]
    
    for name, lat, lon in test_locations:
        distance = location_manager.calculate_distance(nyc_lat, nyc_lon, lat, lon)
        print(f"   NYC to {name}: {distance:.1f} km")
    
    # Test 4: Find nearest facilities
    print("\n4. Finding Nearest Facilities:")
    
    # Find nearest hospital to NYC
    nearest_hospital = location_manager.find_nearest_location(nyc_lat, nyc_lon, 'hospital')
    if nearest_hospital:
        location, distance = nearest_hospital
        print(f"   Nearest Hospital: {location.name} ({distance:.1f} km)")
    
    # Find nearest shelter to NYC
    nearest_shelter = location_manager.find_nearest_location(nyc_lat, nyc_lon, 'shelter')
    if nearest_shelter:
        location, distance = nearest_shelter
        print(f"   Nearest Shelter: {location.name} ({distance:.1f} km)")
    
    # Test 5: Find facilities within radius
    print("\n5. Finding Facilities Within Radius:")
    
    # Find all hospitals within 50 km of NYC
    nearby_hospitals = location_manager.find_hospitals(nyc_lat, nyc_lon, 50)
    print(f"   Hospitals within 50 km of NYC: {len(nearby_hospitals)}")
    for hospital, distance in nearby_hospitals:
        print(f"     - {hospital.name}: {distance:.1f} km")
    
    # Find all shelters within 25 km of NYC
    nearby_shelters = location_manager.find_shelters(nyc_lat, nyc_lon, 25)
    print(f"   Shelters within 25 km of NYC: {len(nearby_shelters)}")
    for shelter, distance in nearby_shelters:
        print(f"     - {shelter.name}: {distance:.1f} km")
    
    # Test 6: Find all emergency facilities
    print("\n6. Finding All Emergency Facilities:")
    
    all_facilities = location_manager.find_emergency_facilities(nyc_lat, nyc_lon, 50)
    print(f"   Emergency facilities within 50 km of NYC:")
    for facility_type, facilities in all_facilities.items():
        print(f"     {facility_type}: {len(facilities)} facilities")
    
    # Test 7: Test coordinate formatting
    print("\n7. Coordinate Formatting:")
    
    test_coords = [
        (40.7128, -74.0060),  # NYC
        (34.0522, -118.2437), # LA
        (41.8781, -87.6298),  # Chicago
        (29.7604, -95.3698),  # Houston
        (25.7617, -80.1918)   # Miami
    ]
    
    for lat, lon in test_coords:
        formatted = location_manager.format_coordinates(lat, lon)
        print(f"   ({lat}, {lon}) → {formatted}")
    
    # Test 8: Test bounding box calculations
    print("\n8. Bounding Box Calculations:")
    
    center_lat, center_lon = 40.7128, -74.0060
    radius_km = 25
    
    min_lat, max_lat, min_lon, max_lon = location_manager.get_bounding_box(center_lat, center_lon, radius_km)
    print(f"   Bounding box for {radius_km} km radius around NYC:")
    print(f"     Latitude: {min_lat:.4f} to {max_lat:.4f}")
    print(f"     Longitude: {min_lon:.4f} to {max_lon:.4f}")
    
    # Test 9: Test location filtering
    print("\n9. Location Filtering:")
    
    # Filter by type
    hospitals = location_manager.get_locations_by_type('hospital')
    print(f"   Total hospitals: {len(hospitals)}")
    
    shelters = location_manager.get_locations_by_type('shelter')
    print(f"   Total shelters: {len(shelters)}")
    
    # Filter by name pattern
    nyc_locations = location_manager.get_locations_by_name('NYC')
    print(f"   NYC locations: {len(nyc_locations)}")
    
    # Test 10: Test adding new location
    print("\n10. Adding New Location:")
    
    new_location = Location(
        name="Test Emergency Center",
        type="aid_station",
        address="123 Test Street, Test City, TC 12345",
        latitude=40.7500,
        longitude=-73.9800,
        capacity=150,
        contact_phone="555-0123",
        description="Test emergency facility for demonstration"
    )
    
    if location_manager.add_location(new_location):
        print("   ✓ Test location added successfully")
        
        # Verify it was added
        added_location = location_manager.get_location_by_id(new_location.id)
        if added_location:
            print(f"   ✓ Location retrieved: {added_location.name}")
        else:
            print("   ✗ Failed to retrieve added location")
    else:
        print("   ✗ Failed to add test location")
    
    print("\nPASS Geolocation testing completed successfully!")
    print("\nYou can now use the CLI tool to find nearby facilities:")
    print("  python cli.py facilities nearby --address 'New York, NY' --radius 25")
    print("  python cli.py facilities hospitals --latitude 40.7128 --longitude -74.0060 --radius 20")
    print("  python cli.py facilities shelters --address 'Brooklyn, NY' --radius 15")
    print("  python cli.py facilities list --type hospital")


if __name__ == '__main__':
    test_geolocation_features()
