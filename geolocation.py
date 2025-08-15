#!/usr/bin/env python3
"""
Geolocation Module for Disaster Response Tool

Provides offline and online geolocation capabilities for finding nearby
emergency facilities, calculating distances, and managing location data.
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

try:
    from geopy.distance import geodesic
    from geopy.geocoders import Nominatim
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False
    geodesic = None
    Nominatim = None


@dataclass
class Location:
    """Represents a geographic location with metadata."""
    id: str
    name: str
    type: str
    address: Optional[str] = None
    latitude: float = 0.0
    longitude: float = 0.0
    description: Optional[str] = None
    capacity: Optional[int] = None
    facilities: Optional[List[str]] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    operating_hours: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class LocationManager:
    """Manages geographic locations and provides offline geolocation services."""
    
    def __init__(self, data_path: str = "data/locations.json"):
        """
        Initialize the location manager.
        
        Args:
            data_path: Path to the locations data file
        """
        self.data_path = Path(data_path)
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.locations: List[Location] = []
        self._load_locations()
        
        # Predefined emergency facility types
        self.emergency_types = {
            'hospital': ['hospital', 'medical_center', 'clinic', 'emergency_room'],
            'shelter': ['shelter', 'evacuation_center', 'refuge', 'safe_zone'],
            'aid_station': ['aid_station', 'relief_center', 'distribution_center', 'command_post'],
            'fire_station': ['fire_station', 'firehouse', 'fire_department'],
            'police_station': ['police_station', 'police_department', 'law_enforcement'],
            'emergency_ops': ['emergency_ops', 'command_center', 'operations_center']
        }
    
    def _load_locations(self):
        """Load locations from JSON file or create default emergency facilities."""
        try:
            if self.data_path.exists():
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.locations = [Location(**loc) for loc in data.get('locations', [])]
                self.logger.info(f"Loaded {len(self.locations)} locations from {self.data_path}")
            else:
                self._create_default_locations()
                self._save_locations()
        except Exception as e:
            self.logger.error(f"Error loading locations: {e}")
            self._create_default_locations()
    
    def _create_default_locations(self):
        """Create default emergency facility locations for major cities."""
        default_locations = [
            # New York City Area
            Location(
                id="LOC-NYC-001",
                name="Bellevue Hospital Center",
                type="hospital",
                address="462 First Avenue, New York, NY 10016",
                latitude=40.7411,
                longitude=-73.9747,
                description="Major trauma center and emergency hospital",
                capacity=1000,
                facilities=["emergency_room", "trauma_center", "icu", "helicopter_pad"],
                contact_phone="212-562-4141",
                operating_hours="24/7"
            ),
            Location(
                id="LOC-NYC-002",
                name="NYC Emergency Operations Center",
                type="emergency_ops",
                address="165 Cadman Plaza East, Brooklyn, NY 11201",
                latitude=40.6989,
                longitude=-73.9939,
                description="Primary emergency coordination facility",
                capacity=200,
                facilities=["command_center", "communications", "situation_room"],
                contact_phone="718-422-8700",
                operating_hours="24/7"
            ),
            Location(
                id="LOC-NYC-003",
                name="Brooklyn Evacuation Shelter",
                type="shelter",
                address="150 Ashland Place, Brooklyn, NY 11201",
                latitude=40.6944,
                longitude=-73.9861,
                description="Primary evacuation shelter for Brooklyn",
                capacity=500,
                facilities=["beds", "food_service", "medical_station", "showers"],
                contact_phone="718-422-8700",
                operating_hours="24/7 during emergencies"
            ),
            Location(
                id="LOC-NYC-004",
                name="FDNY Engine 10",
                type="fire_station",
                address="124 Liberty Street, New York, NY 10006",
                latitude=40.7097,
                longitude=-74.0127,
                description="Downtown fire station",
                capacity=20,
                facilities=["fire_trucks", "rescue_equipment", "hazmat_gear"],
                contact_phone="212-267-7000",
                operating_hours="24/7"
            ),
            Location(
                id="LOC-NYC-005",
                name="Manhattan Aid Station",
                type="aid_station",
                address="350 Canal Street, New York, NY 10013",
                latitude=40.7196,
                longitude=-73.9969,
                description="Downtown aid and distribution center",
                capacity=100,
                facilities=["first_aid", "food_distribution", "information_desk"],
                contact_phone="212-226-3000",
                operating_hours="8AM-8PM"
            ),
            
            # Los Angeles Area
            Location(
                id="LOC-LA-001",
                name="UCLA Medical Center",
                type="hospital",
                address="757 Westwood Plaza, Los Angeles, CA 90095",
                latitude=34.0664,
                longitude=-118.4450,
                description="Major medical center and trauma hospital",
                capacity=800,
                facilities=["emergency_room", "trauma_center", "burn_unit", "helicopter_pad"],
                contact_phone="310-825-9111",
                operating_hours="24/7"
            ),
            Location(
                id="LOC-LA-002",
                name="LA Emergency Operations Center",
                type="emergency_ops",
                address="500 E Temple Street, Los Angeles, CA 90012",
                latitude=34.0522,
                longitude=-118.2437,
                description="Los Angeles emergency coordination center",
                capacity=150,
                facilities=["command_center", "communications", "situation_room"],
                contact_phone="213-978-3800",
                operating_hours="24/7"
            ),
            
            # Chicago Area
            Location(
                id="LOC-CHI-001",
                name="Northwestern Memorial Hospital",
                type="hospital",
                address="251 E Huron St, Chicago, IL 60611",
                latitude=41.8947,
                longitude=-87.6225,
                description="Major downtown hospital and trauma center",
                capacity=900,
                facilities=["emergency_room", "trauma_center", "icu", "helicopter_pad"],
                contact_phone="312-926-2000",
                operating_hours="24/7"
            ),
            Location(
                id="LOC-CHI-002",
                name="Chicago Emergency Operations Center",
                type="emergency_ops",
                address="1411 W Madison St, Chicago, IL 60607",
                latitude=41.8819,
                longitude=-87.6681,
                description="Chicago emergency coordination center",
                capacity=120,
                facilities=["command_center", "communications", "situation_room"],
                contact_phone="312-746-6000",
                operating_hours="24/7"
            ),
            
            # Houston Area
            Location(
                id="LOC-HOU-001",
                name="Memorial Hermann-Texas Medical Center",
                type="hospital",
                address="6411 Fannin St, Houston, TX 77030",
                latitude=29.7069,
                longitude=-95.3975,
                description="Major trauma center and emergency hospital",
                capacity=1100,
                facilities=["emergency_room", "trauma_center", "icu", "helicopter_pad"],
                contact_phone="713-704-4000",
                operating_hours="24/7"
            ),
            Location(
                id="LOC-HOU-002",
                name="Houston Emergency Operations Center",
                type="emergency_ops",
                address="5320 N Shepherd Dr, Houston, TX 77091",
                latitude=29.8347,
                longitude=-95.4344,
                description="Houston emergency coordination center",
                capacity=100,
                facilities=["command_center", "communications", "situation_room"],
                contact_phone="713-884-4500",
                operating_hours="24/7"
            ),
            
            # Miami Area
            Location(
                id="LOC-MIA-001",
                name="Jackson Memorial Hospital",
                type="hospital",
                address="1611 NW 12th Ave, Miami, FL 33136",
                latitude=25.7907,
                longitude=-80.2100,
                description="Major trauma center and emergency hospital",
                capacity=1200,
                facilities=["emergency_room", "trauma_center", "icu", "helicopter_pad"],
                contact_phone="305-585-1111",
                operating_hours="24/7"
            ),
            Location(
                id="LOC-MIA-002",
                name="Miami Emergency Operations Center",
                type="emergency_ops",
                address="444 SW 2nd Ave, Miami, FL 33130",
                latitude=25.7617,
                longitude=-80.1918,
                description="Miami emergency coordination center",
                capacity=80,
                facilities=["command_center", "communications", "situation_room"],
                contact_phone="305-579-6000",
                operating_hours="24/7"
            )
        ]
        
        self.locations = default_locations
        self.logger.info(f"Created {len(self.locations)} default emergency facility locations")
    
    def _save_locations(self):
        """Save locations to JSON file."""
        try:
            data = {
                "locations": [asdict(loc) for loc in self.locations],
                "metadata": {
                    "last_updated": datetime.now().isoformat(),
                    "total_locations": len(self.locations),
                    "facility_types": list(self.emergency_types.keys())
                }
            }
            
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Saved {len(self.locations)} locations to {self.data_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving locations: {e}")
            return False
    
    def add_location(self, location: Location) -> bool:
        """Add a new location."""
        try:
            # Generate ID if not provided
            if not location.id:
                location.id = f"LOC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Add timestamps
            if not location.created_at:
                location.created_at = datetime.now().isoformat()
            location.updated_at = datetime.now().isoformat()
            
            self.locations.append(location)
            self._save_locations()
            return True
        except Exception as e:
            self.logger.error(f"Error adding location: {e}")
            return False
    
    def get_location_by_id(self, location_id: str) -> Optional[Location]:
        """Get a location by its ID."""
        for location in self.locations:
            if location.id == location_id:
                return location
        return None
    
    def get_locations_by_type(self, facility_type: str) -> List[Location]:
        """Get all locations of a specific type."""
        if facility_type in self.emergency_types:
            type_variants = self.emergency_types[facility_type]
            return [loc for loc in self.locations if loc.type in type_variants]
        else:
            return [loc for loc in self.locations if loc.type == facility_type]
    
    def get_locations_by_name(self, name_pattern: str) -> List[Location]:
        """Get locations matching a name pattern."""
        pattern_lower = name_pattern.lower()
        return [loc for loc in self.locations if pattern_lower in loc.name.lower()]
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula.
        
        Args:
            lat1, lon1: First coordinate pair
            lat2, lon2: Second coordinate pair
            
        Returns:
            Distance in kilometers
        """
        if GEOPY_AVAILABLE and geodesic:
            # Use geopy for more accurate calculations
            return geodesic((lat1, lon1), (lat2, lon2)).kilometers
        else:
            # Fallback to Haversine formula
            return self._haversine_distance(lat1, lon1, lat2, lon2)
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance using Haversine formula (offline fallback)."""
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        radius = 6371
        
        return radius * c
    
    def find_nearest_location(self, lat: float, lon: float, facility_type: Optional[str] = None) -> Optional[Tuple[Location, float]]:
        """
        Find the nearest location of a specific type.
        
        Args:
            lat, lon: Current coordinates
            facility_type: Type of facility to search for
            
        Returns:
            Tuple of (Location, distance_km) or None if no locations found
        """
        locations_to_search = self.locations
        if facility_type:
            locations_to_search = self.get_locations_by_type(facility_type)
        
        if not locations_to_search:
            return None
        
        nearest = None
        min_distance = float('inf')
        
        for location in locations_to_search:
            if location.is_active:
                distance = self.calculate_distance(lat, lon, location.latitude, location.longitude)
                if distance < min_distance:
                    min_distance = distance
                    nearest = location
        
        if nearest:
            return (nearest, min_distance)
        return None
    
    def find_locations_within_radius(self, lat: float, lon: float, radius_km: float, 
                                   facility_type: Optional[str] = None) -> List[Tuple[Location, float]]:
        """
        Find all locations within a specified radius.
        
        Args:
            lat, lon: Center coordinates
            radius_km: Search radius in kilometers
            facility_type: Optional filter by facility type
            
        Returns:
            List of tuples (Location, distance_km) sorted by distance
        """
        locations_to_search = self.locations
        if facility_type:
            locations_to_search = self.get_locations_by_type(facility_type)
        
        nearby_locations = []
        
        for location in locations_to_search:
            if location.is_active:
                distance = self.calculate_distance(lat, lon, location.latitude, location.longitude)
                if distance <= radius_km:
                    nearby_locations.append((location, distance))
        
        # Sort by distance
        nearby_locations.sort(key=lambda x: x[1])
        return nearby_locations
    
    def find_emergency_facilities(self, lat: float, lon: float, radius_km: float = 25.0) -> Dict[str, List[Tuple[Location, float]]]:
        """
        Find all types of emergency facilities within radius.
        
        Args:
            lat, lon: Center coordinates
            radius_km: Search radius in kilometers
            
        Returns:
            Dictionary organized by facility type with nearby locations
        """
        results = {}
        
        for facility_type in self.emergency_types.keys():
            nearby = self.find_locations_within_radius(lat, lon, radius_km, facility_type)
            if nearby:
                results[facility_type] = nearby
        
        return results
    
    def find_hospitals(self, lat: float, lon: float, radius_km: float = 25.0) -> List[Tuple[Location, float]]:
        """Find nearby hospitals."""
        return self.find_locations_within_radius(lat, lon, radius_km, 'hospital')
    
    def find_shelters(self, lat: float, lon: float, radius_km: float = 25.0) -> List[Tuple[Location, float]]:
        """Find nearby shelters."""
        return self.find_locations_within_radius(lat, lon, radius_km, 'shelter')
    
    def find_aid_stations(self, lat: float, lon: float, radius_km: float = 25.0) -> List[Tuple[Location, float]]:
        """Find nearby aid stations."""
        return self.find_locations_within_radius(lat, lon, radius_km, 'aid_station')
    
    def find_emergency_ops(self, lat: float, lon: float, radius_km: float = 50.0) -> List[Tuple[Location, float]]:
        """Find nearby emergency operations centers."""
        return self.find_locations_within_radius(lat, lon, radius_km, 'emergency_ops')
    
    def validate_coordinates(self, lat: float, lon: float) -> bool:
        """Validate that coordinates are within reasonable bounds."""
        return -90 <= lat <= 90 and -180 <= lon <= 180
    
    def format_coordinates(self, lat: float, lon: float) -> str:
        """Format coordinates in readable format."""
        lat_dir = "N" if lat >= 0 else "S"
        lon_dir = "E" if lon >= 0 else "W"
        
        lat_abs = abs(lat)
        lon_abs = abs(lon)
        
        lat_deg = int(lat_abs)
        lat_min = int((lat_abs - lat_deg) * 60)
        lat_sec = round((lat_abs - lat_deg - lat_min/60) * 3600, 2)
        
        lon_deg = int(lon_abs)
        lon_min = int((lon_abs - lon_deg) * 60)
        lon_sec = round((lon_abs - lon_deg - lon_min/60) * 3600, 2)
        
        return f"{lat_deg}°{lat_min}'{lat_sec}\"{lat_dir}, {lon_deg}°{lon_min}'{lon_sec}\"{lon_dir}"
    
    def _decimal_to_dms(self, decimal_degrees: float) -> Tuple[int, int, float]:
        """Convert decimal degrees to degrees, minutes, seconds."""
        degrees = int(decimal_degrees)
        minutes = int((decimal_degrees - degrees) * 60)
        seconds = (decimal_degrees - degrees - minutes/60) * 3600
        return degrees, minutes, seconds
    
    def get_bounding_box(self, center_lat: float, center_lon: float, radius_km: float) -> Tuple[float, float, float, float]:
        """
        Get bounding box coordinates for a given center and radius.
        
        Args:
            center_lat, center_lon: Center coordinates
            radius_km: Radius in kilometers
            
        Returns:
            Tuple of (min_lat, max_lat, min_lon, max_lon)
        """
        # Approximate conversion: 1 degree ≈ 111 km
        lat_range = radius_km / 111.0
        lon_range = radius_km / (111.0 * abs(center_lat) / 90.0)  # Adjust for latitude
        
        min_lat = center_lat - lat_range
        max_lat = center_lat + lat_range
        min_lon = center_lon - lon_range
        max_lon = center_lon + lon_range
        
        return min_lat, max_lat, min_lon, max_lon
    
    def export_locations_to_json(self, export_path: str, facility_type: Optional[str] = None) -> bool:
        """Export locations to JSON file."""
        try:
            locations_to_export = self.locations
            if facility_type:
                locations_to_export = self.get_locations_by_type(facility_type)
            
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "facility_type": facility_type or "all",
                "total_locations": len(locations_to_export),
                "locations": [asdict(loc) for loc in locations_to_export]
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Exported {len(locations_to_export)} locations to {export_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting locations: {e}")
            return False
    
    def import_locations_from_json(self, import_path: str) -> bool:
        """Import locations from JSON file."""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported_locations = []
            for loc_data in data.get('locations', []):
                location = Location(**loc_data)
                imported_locations.append(location)
            
            self.locations.extend(imported_locations)
            self._save_locations()
            
            self.logger.info(f"Imported {len(imported_locations)} locations from {import_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error importing locations: {e}")
            return False
    
    def get_location_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about stored locations."""
        stats = {
            "total_locations": len(self.locations),
            "active_locations": len([loc for loc in self.locations if loc.is_active]),
            "by_type": {},
            "by_capacity": {
                "small": 0,      # < 100
                "medium": 0,     # 100-500
                "large": 0,      # 500-1000
                "xlarge": 0      # > 1000
            },
            "geographic_coverage": {
                "north_america": 0,
                "europe": 0,
                "asia": 0,
                "other": 0
            }
        }
        
        # Count by type
        for location in self.locations:
            if location.type not in stats["by_type"]:
                stats["by_type"][location.type] = 0
            stats["by_type"][location.type] += 1
        
        # Count by capacity
        for location in self.locations:
            if location.capacity:
                if location.capacity < 100:
                    stats["by_capacity"]["small"] += 1
                elif location.capacity < 500:
                    stats["by_capacity"]["medium"] += 1
                elif location.capacity < 1000:
                    stats["by_capacity"]["large"] += 1
                else:
                    stats["by_capacity"]["xlarge"] += 1
        
        # Geographic coverage (simplified)
        for location in self.locations:
            if 25 <= location.latitude <= 50 and -125 <= location.longitude <= -65:
                stats["geographic_coverage"]["north_america"] += 1
            elif 35 <= location.latitude <= 70 and -10 <= location.longitude <= 40:
                stats["geographic_coverage"]["europe"] += 1
            elif 10 <= location.latitude <= 60 and 60 <= location.longitude <= 150:
                stats["geographic_coverage"]["asia"] += 1
            else:
                stats["geographic_coverage"]["other"] += 1
        
        return stats


# Global location manager instance
location_manager = LocationManager()
