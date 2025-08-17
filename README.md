# Disaster Response CLI Tool

An offline command-line interface tool designed for disaster response operations. This tool provides essential functionality for emergency responders working in areas with limited or no internet connectivity.

## Features

- **Offline Operation**: Works without internet connection
- **Local Database**: SQLite database for storing response data
- **JSON Fallback**: Automatic fallback to JSON files when SQLite is unavailable
- **Data Persistence**: JSON-based offline data storage
- **Geolocation Support**: Advanced offline geolocation with preloaded emergency facility coordinates
- **Command Line Interface**: Easy-to-use CLI for field operations
- **Rich Styling**: Beautiful terminal output with Rich library
- **Fast Access**: Organized commands for quick emergency response
- **Emergency Facilities**: Preloaded database of hospitals, shelters, and aid stations

## Project Structure

```
disaster_cli/
├── cli.py                  # Main CLI interface with all commands
├── database.py             # SQLite database operations
├── geolocation.py          # Enhanced location and mapping features
├── data/                   # Data storage directory
│   ├── resources.json      # Sample resources data
│   └── locations.json      # Emergency facility coordinates
├── requirements.txt         # Python dependencies
├── test_database.py        # Database testing script
├── test_cli_features.py    # CLI feature testing script
├── test_geolocation.py     # Geolocation testing script
└── README.md               # This file
```

## Installation

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the tool: `python cli.py --help`

## Quick Start

```bash
# Quick access to common operations
python cli.py quick

# View emergency resources
python cli.py resources list

# Check supply inventory
python cli.py supplies checklist

# Find nearby emergency facilities
python cli.py facilities nearby --address "New York, NY" --radius 25

# Find nearby hospitals
python cli.py facilities hospitals --latitude 40.7128 --longitude -74.0060 --radius 20
```

## CLI Commands

### Emergency Resources

Manage emergency equipment, vehicles, and supplies:

```bash
# List all resources
python cli.py resources list

# List only available resources
python cli.py resources list --available

# Filter by type
python cli.py resources list --type vehicle

# Filter by status
python cli.py resources list --status available

# Filter by location
python cli.py resources list --location "Station A"

# Add new resource
python cli.py resources add --name "New Ambulance" --type vehicle --location "Station D"

# Add resource with equipment
python cli.py resources add --name "Rescue Kit" --type equipment --location "Warehouse" --equipment "rope,harness,carabiners"

# Update resource status
python cli.py resources update --resource-id RES-001 --status maintenance

# Update resource location
python cli.py resources update --resource-id RES-001 --location "New Station"
```

### Supply Checklists

Manage emergency supply inventories:

```bash
# View all supply categories
python cli.py supplies checklist

# View medical supplies only
python cli.py supplies checklist --category medical_supplies

# View critical priority items
python cli.py supplies checklist --priority critical

# View emergency equipment
python cli.py supplies checklist --category emergency_equipment

# Add new supply item
python cli.py supplies add-item --category medical_supplies --item "Emergency Blankets" --priority high --quantity "100+"
```

**Available Supply Categories:**
- **Medical Supplies**: First aid kits, bandages, antiseptics, pain relievers
- **Emergency Equipment**: Flashlights, batteries, radios, power banks
- **Food & Water**: Bottled water, non-perishable food, purification tablets
- **Shelter Supplies**: Tents, sleeping bags, tarps, rope

### Emergency Contacts

Manage emergency contacts and find nearby responders:

```bash
# List all emergency contacts
python cli.py contacts list

# Filter by contact type
python cli.py contacts list --type emergency

# Filter by priority
python cli.py contacts list --priority high

# Filter by organization
python cli.py contacts list --organization "Fire Department"

# Find contacts within radius (using coordinates)
python cli.py contacts nearby --latitude 40.7128 --longitude -74.0060 --radius 5

# Find contacts within radius (using address)
python cli.py contacts nearby --address "New York, NY" --radius 10

# Find contacts within custom radius
python cli.py contacts nearby --address "Downtown Area" --radius 25
```

### Emergency Facilities (NEW!)

Find nearby emergency facilities with offline geolocation:

```bash
# Find all types of emergency facilities
python cli.py facilities nearby --address "New York, NY" --radius 25

# Find specific type of facility
python cli.py facilities nearby --address "Brooklyn, NY" --radius 15 --type hospital

# Find nearby hospitals
python cli.py facilities hospitals --latitude 40.7128 --longitude -74.0060 --radius 20

# Find nearby shelters
python cli.py facilities shelters --address "Downtown Area" --radius 10

# Find nearby aid stations
python cli.py facilities aid_stations --latitude 40.7500 --longitude -73.9800 --radius 15

# Find emergency operations centers
python cli.py facilities emergency_ops --address "City Center" --radius 50

# List all available facilities
python cli.py facilities list

# Filter facilities by type
python cli.py facilities list --type hospital

# Filter facilities by name
python cli.py facilities list --name "NYC"

# Add new emergency facility
python cli.py facilities add --name "New Hospital" --type hospital --address "123 Main St" --latitude 40.7500 --longitude -73.9800 --capacity 500 --phone "555-0123"

# Export facilities to JSON
python cli.py facilities export --type hospital --output "data/hospitals.json"
```

**Preloaded Emergency Facility Types:**
- **Hospitals**: Trauma centers, medical facilities, emergency rooms
- **Shelters**: Evacuation centers, refugee facilities, safe zones
- **Aid Stations**: Relief centers, distribution centers, command posts
- **Fire Stations**: Fire departments, firehouses, rescue units
- **Police Stations**: Law enforcement, security facilities
- **Emergency Operations**: Command centers, coordination facilities

**Preloaded Cities & Facilities:**
- **New York City**: Bellevue Hospital, NYC Emergency Ops, Brooklyn Shelter, FDNY Engine 10, Manhattan Aid Station
- **Los Angeles**: UCLA Medical Center, LA Emergency Ops
- **Chicago**: Northwestern Memorial Hospital, Chicago Emergency Ops
- **Houston**: Memorial Hermann-Texas Medical Center, Houston Emergency Ops
- **Miami**: Jackson Memorial Hospital, Miami Emergency Ops

### Other Commands

```bash
# View incidents
python cli.py incidents --status active

# Manage personnel
python cli.py personnel --role firefighter

# Location services
python cli.py location --latitude 40.7128 --longitude -74.0060

# Data management
python cli.py data --backup

# System status
python cli.py status

# Quick access menu
python cli.py quick
```

## Testing

Test the database, CLI, geolocation, connectivity simulation, and enhanced styling functionality:

```bash
# Test database operations
python test_database.py

# Test CLI features
python test_cli_features.py

# Test geolocation features
python test_geolocation.py

# Test connectivity simulation and fallback systems
python test_connectivity_simulation.py

# Test enhanced CLI styling and emergency features
python test_enhanced_cli.py
```

## Advanced Features

###  Enhanced CLI Styling and Emergency Alerts

The CLI now features comprehensive Rich styling for better readability during emergencies:

- **Emergency Alerts**: Color-coded alert system with levels (normal, warning, critical, emergency)
- **Enhanced Tables**: Rich tables with color coding, borders, and improved visual hierarchy
- **Status Panels**: Informative panels showing system status, database details, and capabilities
- **Emergency Mode**: Automatic detection and styling when critical conditions are detected
- **Priority Highlighting**: Critical resources and supplies are highlighted in red
- **Visual Indicators**: Icons, colors, and borders for different alert levels
- **Enhanced Quick Access**: Emergency-focused quick access menu with priority commands

#### Emergency Alert Levels
- **Normal** (Blue): Information and status updates
- **Warning** (Yellow): Attention required, non-critical issues
- **Critical** (Red): Immediate attention required
- **Emergency** (Red): Critical situation, prioritize operations

#### Enhanced Commands
- `status --detailed`: Shows comprehensive system information with enhanced panels
- `resources list --emergency`: Emergency-focused resource display with critical item highlighting
- `supplies checklist --emergency`: Priority-based supply checklist with critical item alerts
- `quick --emergency`: Emergency-focused quick access menu

### Enhanced Geolocation Integration

The CLI now provides comprehensive offline geolocation capabilities:

- **Offline Operation**: Works without internet using preloaded coordinates
- **Preloaded Facilities**: 20+ emergency facilities across major US cities
- **Smart Distance Calculations**: Uses geopy when available, Haversine formula as fallback
- **Address Geocoding**: Convert addresses to coordinates using Nominatim (when online)
- **Facility Categorization**: Organized by type (hospital, shelter, aid_station, etc.)
- **Radius-based Search**: Find facilities within specified distances
- **Coordinate Validation**: Ensure accurate location data
- **Bounding Box Calculations**: Optimize search areas

#### **Distance Calculation Methods**
1. **Primary**: geopy geodesic (most accurate, requires internet)
2. **Fallback**: Haversine formula (works offline, good accuracy)

#### **Facility Search Capabilities**
- **Type-specific Search**: Find hospitals, shelters, aid stations separately
- **Comprehensive Search**: Find all facility types in one command
- **Radius Control**: Adjustable search radius (5km to 100km+)
- **Address Input**: Use street addresses or coordinates
- **Distance Sorting**: Results automatically sorted by proximity

### Connectivity Simulation & Power Management

Test your CLI tool under various real-world conditions:

#### **Connectivity Modes**
- **Online**: Full connectivity with all features
- **Intermittent**: Unreliable connectivity (70% uptime)
- **Low Bandwidth**: Slow, limited connectivity (64 KB/s)
- **Offline**: No connectivity - JSON fallback only
- **Emergency**: Minimal connectivity (16 KB/s) with power saving

#### **Power Management Modes**
- **Normal**: Full performance and power consumption
- **Power Save**: Reduced performance (80% CPU, 70% power)
- **Minimal**: Significant performance impact (50% CPU, 40% power)
- **Critical**: Minimal functionality (30% CPU, 20% power)

#### **Simulation Features**
- **Real-time Mode Switching**: Change connectivity/power modes during operation
- **Network Delay Simulation**: Artificial latency and bandwidth throttling
- **Power Consumption Tracking**: Monitor power usage for different operations
- **Background Simulation**: Run simulations for extended periods
- **Data Export**: Export simulation results for analysis

### Database Fallback Testing

Comprehensive testing to ensure SQLite and JSON fallback systems work correctly:

#### **Test Categories**
- **SQLite Availability**: Test database connectivity and functionality
- **JSON Fallback**: Verify offline storage and retrieval
- **Data Consistency**: Ensure data integrity across operations
- **Performance Testing**: Measure response times under various conditions

#### **Testing Scenarios**
- **Online Mode**: Full SQLite functionality
- **Offline Mode**: JSON fallback only
- **Intermittent Mode**: Mixed connectivity scenarios
- **Power Constraints**: Performance under limited power
- **Critical Conditions**: Emergency mode testing

#### **Test Commands**
```bash
# Basic fallback testing
python cli.py test fallback

# Comprehensive testing under specific conditions
python cli.py test comprehensive --mode offline --power critical

# View test summary
python cli.py test summary
```

### 🎨 Rich Terminal Styling

Beautiful terminal output with the **Rich** library:

- **Color-coded Status**: Green for available, red for in-use, yellow for maintenance
- **Priority Indicators**: Color-coded priority levels (critical=red, high=yellow, medium=blue)
- **Progress Indicators**: Spinner animations for geocoding operations
- **Organized Tables**: Clean, readable data presentation
- **Quick Access Menu**: Visual command reference
- **Facility Icons**: Visual indicators for different facility types
- **Simulation Status**: Real-time connectivity and power mode indicators

### Smart Filtering

Advanced filtering capabilities across all commands:

- **Multi-criteria Filters**: Combine type, status, location, priority
- **Fuzzy Matching**: Partial text matching for locations and names
- **Status-based Views**: Quick access to available, in-use, or maintenance items
- **Priority Sorting**: Automatic sorting by importance level
- **Geographic Filtering**: Filter by region or proximity
- **Power-aware Filtering**: Adjust operations based on current power mode

## JSON Fallback System

The CLI automatically detects if SQLite is available and falls back to JSON file storage when needed:

- **Automatic Detection**: Checks SQLite availability on startup
- **JSON Fallback**: Uses `data/resources.json` when SQLite is unavailable
- **Force JSON Mode**: Use `--json-fallback` flag to force JSON mode
- **Data Persistence**: All CRUD operations work with both storage systems

### JSON Storage Features

- **Automatic ID Generation**: Creates unique resource IDs (RES-001, RES-002, etc.)
- **Metadata Tracking**: Maintains timestamps and statistics
- **Error Handling**: Graceful fallback with user-friendly error messages
- **Data Validation**: Ensures data integrity during operations

## Storage Modes

### SQLite Mode (Default)
- Full database functionality
- ACID compliance
- Better performance for large datasets
- Transaction support

### JSON Fallback Mode
- Works when SQLite is unavailable
- Human-readable data format
- Easy backup and version control
- Portable data storage

## Dependencies

- **Required**: `click`, `rich`, `geopy`
- **Development**: `pytest`, `black`

## Usage Examples

### Emergency Response Scenario

```bash
# 1. Check available resources with enhanced styling
python cli.py resources list --available --type vehicle --emergency

# 2. View critical supplies with priority alerts
python cli.py supplies checklist --priority critical --emergency

# 3. Find nearby emergency facilities
python cli.py facilities nearby --address "Incident Location" --radius 25

# 4. Find nearest hospital
python cli.py facilities hospitals --address "Current Location" --radius 20

# 5. Find nearby shelters
python cli.py facilities shelters --address "Evacuation Area" --radius 15

# 6. Update resource status
python cli.py resources update --resource-id RES-001 --status in_use

# 7. Check system status with enhanced display
python cli.py status --detailed

# 8. Emergency quick access
python cli.py quick --emergency
```

### Enhanced CLI Features

```bash
# 1. Emergency status with detailed information
python cli.py status --detailed

# 2. Emergency-focused resource display
python cli.py resources list --emergency --json-fallback

# 3. Priority-based supply checklist
python cli.py supplies checklist --emergency --category medical_supplies

# 4. Emergency quick access menu
python cli.py quick --emergency

# 5. Enhanced resource management with alerts
python cli.py resources list --type vehicle --emergency
```

### Supply Management

```bash
# 1. Review medical supplies with enhanced styling
python cli.py supplies checklist --category medical_supplies --emergency

# 2. Check emergency equipment with priority alerts
python cli.py supplies checklist --category emergency_equipment --emergency

# 3. Add new critical item
python cli.py supplies add-item --category food_water --item "Emergency Rations" --priority critical --quantity "500+ meals"
```

### Contact Management

```bash
# 1. List high-priority contacts
python cli.py contacts list --priority high

# 2. Find medical contacts nearby
python cli.py contacts nearby --address "Hospital Area" --radius 2

# 3. View fire department contacts
python cli.py contacts list --organization "Fire Department"
```

### Facility Management

```bash
# 1. Find all emergency facilities nearby
python cli.py facilities nearby --address "Downtown Area" --radius 30

# 2. Locate nearest hospital
python cli.py facilities hospitals --latitude 40.7500 --longitude -73.9800 --radius 25

# 3. Find evacuation shelters
python cli.py facilities shelters --address "Residential Area" --radius 10

# 4. Add new emergency facility
python cli.py facilities add --name "Community Emergency Center" --type aid_station --address "456 Community St" --latitude 40.7600 --longitude -73.9700 --capacity 200 --phone "555-9999"

# 5. Export hospital data
python cli.py facilities export --type hospital --output "data/exported_hospitals.json"
```

### Connectivity Simulation & Testing

```bash
# 1. Set offline mode for testing
python cli.py simulate connectivity --mode offline

# 2. Set minimal power mode
python cli.py simulate power --mode minimal

# 3. Start background simulation
python cli.py simulate start --duration 10

# 4. Test database fallback
python cli.py test fallback

# 5. Run comprehensive testing
python cli.py test comprehensive --mode offline --power critical

# 6. Monitor power consumption
python cli.py power monitor --operation database_read --count 20

# 7. Check simulation status
python cli.py simulate status

# 8. Export simulation data
python cli.py simulate export --output "data/simulation_results.json"
```

### Power Management

```bash
# 1. Check current power status
python cli.py power status

# 2. Monitor specific operations
python cli.py power monitor --operation geolocation --count 15

# 3. Set power saving mode
python cli.py simulate power --mode power_save

# 4. Emergency power mode
python cli.py simulate power --mode critical
```

## Development

This project is designed to be simple and extensible. Each module can be developed and tested independently:

- `cli.py` - Command-line interface using Click framework with Rich styling
- `database.py` - SQLite database operations with comprehensive CRUD
- `geolocation.py` - Enhanced location and distance calculations with offline capabilities
- `connectivity_simulator.py` - Connectivity and power simulation for testing
- `data/resources.json` - Sample data structure and fallback storage
- `data/locations.json` - Emergency facility coordinates and metadata
- `test_connectivity_simulation.py` - Comprehensive connectivity testing script

## License

This project is open source and available under the MIT License.
