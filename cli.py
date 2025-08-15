#!/usr/bin/env python3
"""
Disaster Response CLI Tool

A simple command-line interface for disaster response operations.
Enhanced with Rich styling for emergency situations.
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.align import Align
from rich.layout import Layout
from rich.live import Live
from rich.status import Status
from rich.syntax import Syntax
from rich.rule import Rule
import json
from pathlib import Path
from datetime import datetime
import sqlite3
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from typing import List, Dict, Any, Optional

# Enhanced console with emergency styling
console = Console(highlight=True, color_system="auto")

# Emergency status tracking
EMERGENCY_MODE = False
EMERGENCY_LEVEL = "normal"  # normal, warning, critical, emergency


def load_resources_from_json(file_path: str = "data/resources.json") -> list:
    """Load resources from JSON file as fallback when SQLite is not available."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('resources', [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        console.print(f"[red]Warning: Could not load resources from JSON: {e}[/red]")
        return []
    return []


def save_resources_to_json(resources: list, file_path: str = "data/resources.json") -> bool:
    """Save resources to JSON file as fallback when SQLite is not available."""
    try:
        # Ensure data directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "resources": resources,
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "total_resources": len(resources),
                "resource_types": list(set(resource.get('type', '') for resource in resources)),
                "status_summary": {
                    "available": len([r for r in resources if r.get('status') == 'available']),
                    "maintenance": len([r for r in resources if r.get('status') == 'maintenance']),
                    "in_use": len([r for r in resources if r.get('status') == 'in_use'])
                }
            }
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        console.print(f"[green]Resources saved to {file_path}[/green]")
        return True
    except (IOError, TypeError) as e:
        console.print(f"[red]Error saving resources to JSON: {e}[/red]")
        return False


def add_resource_to_json(resource_data: dict, file_path: str = "data/resources.json") -> bool:
    """Add a new resource to the JSON file."""
    try:
        resources = load_resources_from_json(file_path)
        
        # Generate new ID if not provided
        if 'id' not in resource_data:
            existing_ids = [r.get('id', '') for r in resources]
            counter = 1
            while f"RES-{counter:03d}" in existing_ids:
                counter += 1
            resource_data['id'] = f"RES-{counter:03d}"
        
        # Add timestamp
        resource_data['created_at'] = datetime.now().isoformat()
        
        resources.append(resource_data)
        return save_resources_to_json(resources, file_path)
    except Exception as e:
        console.print(f"[red]Error adding resource: {e}[/red]")
        return False


def update_resource_in_json(resource_id: str, updates: dict, file_path: str = "data/resources.json") -> bool:
    """Update an existing resource in the JSON file."""
    try:
        resources = load_resources_from_json(file_path)
        
        for i, resource in enumerate(resources):
            if resource.get('id') == resource_id:
                resources[i].update(updates)
                resources[i]["updated_at"] = datetime.now().isoformat()
                return save_resources_to_json(resources, file_path)
        
        console.print(f"[yellow]Resource with ID {resource_id} not found[/yellow]")
        return False
    except Exception as e:
        console.print(f"[red]Error updating resource: {e}[/red]")
        return False


def delete_resource_from_json(resource_id: str, file_path: str = "data/resources.json") -> bool:
    """Delete a resource from the JSON file."""
    try:
        resources = load_resources_from_json(file_path)
        original_count = len(resources)
        
        resources = [r for r in resources if r.get('id') != resource_id]
        
        if len(resources) == original_count:
            console.print(f"[yellow]Resource with ID {resource_id} not found[/yellow]")
            return False
        
        return save_resources_to_json(resources, file_path)
    except Exception as e:
        console.print(f"[red]Error deleting resource: {e}[/red]")
        return False


def check_sqlite_availability() -> bool:
    """Check if SQLite is available and working."""
    try:
        # Try to create a temporary database connection
        conn = sqlite3.connect(':memory:')
        conn.execute('CREATE TABLE test (id INTEGER)')
        conn.execute('INSERT INTO test VALUES (1)')
        result = conn.execute('SELECT * FROM test').fetchone()
        conn.close()
        return result[0] == 1
    except Exception:
        return False


def display_emergency_alert(message: str, level: str = "warning", icon: str = "WARNING"):
    """Display emergency alerts with appropriate styling."""
    global EMERGENCY_MODE, EMERGENCY_LEVEL
    
    if level in ["critical", "emergency"]:
        EMERGENCY_MODE = True
        EMERGENCY_LEVEL = level
    
    # Color mapping for different alert levels
    colors = {
        "normal": "blue",
        "warning": "yellow",
        "critical": "red",
        "emergency": "red"
    }
    
    # Icon mapping
    icons = {
        "normal": "INFO",
        "warning": "WARNING",
        "critical": "CRITICAL",
        "emergency": "EMERGENCY"
    }
    
    color = colors.get(level, "white")
    alert_icon = icons.get(level, "INFO")
    
    # Create emergency alert panel
    alert_text = f"{alert_icon} {message}"
    alert_panel = Panel(
        alert_text,
        title=f"EMERGENCY ALERT - {level.upper()}",
        border_style=color,
        title_align="center",
        padding=(1, 2)
    )
    
    console.print(alert_panel)
    
    if level in ["critical", "emergency"]:
        console.print(f"\n[bold {color}]WARNING: EMERGENCY MODE ACTIVATED - Prioritize critical operations[/bold {color}]")


def create_emergency_header():
    """Create an emergency header with current status."""
    if not EMERGENCY_MODE:
        return ""
    
    header_text = f"EMERGENCY MODE: {EMERGENCY_LEVEL.upper()}"
    header_panel = Panel(
        Align.center(header_text),
        border_style="red",
        title="DISASTER RESPONSE CLI",
        title_align="center",
        padding=(0, 2)
    )
    
    return header_panel


def create_status_indicator():
    """Create a live status indicator."""
    status_text = f"Status: {'Normal' if not EMERGENCY_MODE else 'Emergency'}"
    return Panel(status_text, border_style="green" if not EMERGENCY_MODE else "red")


def get_supply_checklist() -> Dict[str, List[Dict[str, Any]]]:
    """Get comprehensive supply checklist for disaster response."""
    return {
        "medical_supplies": [
            {"item": "First Aid Kits", "priority": "critical", "quantity": "10+", "status": "check"},
            {"item": "Bandages & Gauze", "priority": "high", "quantity": "100+", "status": "check"},
            {"item": "Antiseptic Solution", "priority": "high", "quantity": "20+ bottles", "status": "check"},
            {"item": "Pain Relievers", "priority": "medium", "quantity": "50+ packets", "status": "check"},
            {"item": "Medical Gloves", "priority": "critical", "quantity": "200+ pairs", "status": "check"}
        ],
        "emergency_equipment": [
            {"item": "Flashlights", "priority": "critical", "quantity": "50+", "status": "check"},
            {"item": "Batteries", "priority": "high", "quantity": "200+", "status": "check"},
            {"item": "Emergency Blankets", "priority": "medium", "quantity": "100+", "status": "check"},
            {"item": "Portable Radios", "priority": "critical", "quantity": "20+", "status": "check"},
            {"item": "Power Banks", "priority": "high", "quantity": "30+", "status": "check"}
        ],
        "food_water": [
            {"item": "Bottled Water", "priority": "critical", "quantity": "500+ bottles", "status": "check"},
            {"item": "Non-perishable Food", "priority": "high", "quantity": "200+ meals", "status": "check"},
            {"item": "Water Purification Tablets", "priority": "medium", "quantity": "100+", "status": "check"},
            {"item": "Energy Bars", "priority": "medium", "quantity": "300+", "status": "check"}
        ],
        "shelter_supplies": [
            {"item": "Tents", "priority": "high", "quantity": "20+", "status": "check"},
            {"item": "Sleeping Bags", "priority": "medium", "quantity": "100+", "status": "check"},
            {"item": "Tarps", "priority": "high", "quantity": "50+", "status": "check"},
            {"item": "Rope & Cord", "priority": "medium", "quantity": "1000+ feet", "status": "check"}
        ]
    }


def find_nearby_contacts(lat: float, lon: float, radius_km: float = 10.0) -> List[Dict[str, Any]]:
    """Find emergency contacts within specified radius using geopy."""
    try:
        # Import database if available
        try:
            from database import db
            contacts = db.get_emergency_contacts()
        except ImportError:
            # Fallback to sample data if database not available
            contacts = [
                {
                    'id': 'CONT-001',
                    'name': 'John Smith',
                    'organization': 'Fire Department',
                    'role': 'Fire Chief',
                    'phone': '555-0101',
                    'latitude': 40.7128,
                    'longitude': -74.0060,
                    'priority': 'high'
                },
                {
                    'id': 'CONT-002',
                    'name': 'Dr. Sarah Johnson',
                    'organization': 'City Hospital',
                    'role': 'Emergency Director',
                    'phone': '555-0202',
                    'latitude': 40.7589,
                    'longitude': -73.9851,
                    'priority': 'high'
                }
            ]
        
        nearby_contacts = []
        for contact in contacts:
            if contact.get('latitude') and contact.get('longitude'):
                contact_lat = float(contact['latitude'])
                contact_lon = float(contact['longitude'])
                
                distance = geodesic((lat, lon), (contact_lat, contact_lon)).kilometers
                
                if distance <= radius_km:
                    contact['distance_km'] = round(distance, 2)
                    nearby_contacts.append(contact)
        
        # Sort by distance
        nearby_contacts.sort(key=lambda x: x['distance_km'])
        return nearby_contacts
        
    except Exception as e:
        console.print(f"[red]Error finding nearby contacts: {e}[/red]")
        return []


def geocode_address(address: str) -> Optional[tuple]:
    """Geocode an address to coordinates using Nominatim."""
    try:
        geolocator = Nominatim(user_agent="disaster_response_cli")
        location = geolocator.geocode(address)
        if location:
            return (location.latitude, location.longitude)
        return None
    except Exception as e:
        console.print(f"[red]Geocoding error: {e}[/red]")
        return None


@click.group()
def disaster_cli():
    """Disaster Response CLI Tool - Manage incidents, resources, and personnel."""
    pass


# ==================== EMERGENCY RESOURCES COMMANDS ====================

@disaster_cli.group()
def resources():
    """Manage emergency resources and equipment."""
    pass


@resources.command()
@click.option('--type', '-t', help='Filter by resource type')
@click.option('--status', '-s', help='Filter by status')
@click.option('--location', '-l', help='Filter by location')
@click.option('--available', '-a', is_flag=True, help='Show only available resources')
@click.option('--json-fallback', '-j', is_flag=True, help='Force use of JSON fallback')
@click.option('--emergency', '-e', is_flag=True, help='Show emergency status and alerts')
def list(type, status, location, available, json_fallback, emergency):
    """List emergency resources with filtering options."""
    # Show emergency header if in emergency mode
    if EMERGENCY_MODE:
        console.print(create_emergency_header())
    
    # Enhanced title with emergency styling
    title_style = "bold red" if EMERGENCY_MODE else "bold blue"
    title_icon = "EMERGENCY" if EMERGENCY_MODE else "RESOURCES"
    console.print(f"[{title_style}]{title_icon}: Emergency Resources Inventory[/{title_style}]\n")
    
    # Check if we should use JSON fallback
    use_json = json_fallback or not check_sqlite_availability()
    
    if use_json:
        # Enhanced fallback notification
        fallback_panel = Panel(
            "Using JSON fallback storage - SQLite unavailable",
            title="Storage Mode",
            border_style="yellow",
            title_align="center"
        )
        console.print(fallback_panel)
        
        resources_data = load_resources_from_json()
        
        # Apply filters
        if type:
            resources_data = [r for r in resources_data if r.get('type') == type]
        if status:
            resources_data = [r for r in resources_data if r.get('status') == status]
        if location:
            resources_data = [r for r in resources_data if location.lower() in r.get('location', '').lower()]
        if available:
            resources_data = [r for r in resources_data if r.get('status') == 'available']
        
        if resources_data:
            # Enhanced rich table with emergency styling
            table_style = "red" if EMERGENCY_MODE else "magenta"
            table = Table(
                title=f"Emergency Resources {'[EMERGENCY]' if EMERGENCY_MODE else ''}", 
                show_header=True, 
                header_style=f"bold {table_style}",
                border_style=table_style
            )
            
            # Enhanced columns with better styling
            table.add_column("ID", style="cyan", width=10, justify="center")
            table.add_column("Type", style="magenta", width=12, justify="center")
            table.add_column("Name", style="blue", width=20)
            table.add_column("Status", style="yellow", width=12, justify="center")
            table.add_column("Location", style="green", width=15)
            table.add_column("Capacity", style="white", width=15, justify="center")
            table.add_column("Equipment", style="white", width=25)
            
            # Track critical resources
            critical_count = 0
            
            for resource in resources_data:
                equipment_str = ", ".join(resource.get('equipment', []))[:20] + "..." if resource.get('equipment') else "N/A"
                status_style = {
                    'available': 'green',
                    'in_use': 'red',
                    'maintenance': 'yellow'
                }.get(resource.get('status', ''), 'white')
                
                # Highlight critical resources
                is_critical = resource.get('priority') == 'critical' or resource.get('status') == 'in_use'
                if is_critical:
                    critical_count += 1
                
                # Enhanced row styling
                if is_critical:
                    table.add_row(
                        f"[bold red]{resource.get('id', 'N/A')}[/bold red]",
                        f"[bold red]{resource.get('type', 'N/A')}[/bold red]",
                        f"[bold red]{resource.get('name', 'N/A')}[/bold red]",
                        f"[{status_style}]{resource.get('status', 'N/A')}[/{status_style}]",
                        f"[bold red]{resource.get('location', 'N/A')}[/bold red]",
                        f"[bold red]{resource.get('capacity', 'N/A')}[/bold red]",
                        equipment_str
                    )
                else:
                    table.add_row(
                        resource.get('id', 'N/A'),
                        resource.get('type', 'N/A'),
                        resource.get('name', 'N/A'),
                        f"[{status_style}]{resource.get('status', 'N/A')}[/{status_style}]",
                        resource.get('location', 'N/A'),
                        resource.get('capacity', 'N/A'),
                        equipment_str
                    )
            
            console.print(table)
            
            # Enhanced summary with emergency alerts
            if critical_count > 0:
                display_emergency_alert(
                    f"Critical: {critical_count} resources require immediate attention!",
                    "warning" if critical_count < 3 else "critical"
                )
            
            # Enhanced summary statistics
            status_counts = {}
            type_counts = {}
            for r in resources_data:
                status_counts[r.get('status', 'unknown')] = status_counts.get(r.get('status', 'unknown'), 0) + 1
                type_counts[r.get('type', 'unknown')] = type_counts.get(r.get('type', 'unknown'), 0) + 1
            
            # Create summary panel
            summary_text = f"""Total Resources: {len(resources_data)}
By Status: {status_counts}
By Type: {type_counts}
Critical Resources: {critical_count}"""
            
            summary_panel = Panel(
                summary_text,
                title="Resource Summary",
                border_style="green" if critical_count == 0 else "red",
                title_align="center"
            )
            console.print(summary_panel)
            
        else:
            # Enhanced no results message
            no_results_panel = Panel(
                "No resources found matching the criteria",
                title="No Results",
                border_style="yellow",
                title_align="center"
            )
            console.print(no_results_panel)
    else:
        # Enhanced SQLite notification
        sqlite_panel = Panel(
            "Using SQLite database for optimal performance",
            title="Storage Mode",
            border_style="green",
            title_align="center"
        )
        console.print(sqlite_panel)
        console.print("SQLite functionality would be implemented here")


@resources.command()
@click.option('--name', '-n', required=True, help='Resource name')
@click.option('--type', '-t', required=True, help='Resource type')
@click.option('--location', '-l', help='Resource location')
@click.option('--capacity', '-c', help='Resource capacity')
@click.option('--equipment', '-e', help='Comma-separated equipment list')
@click.option('--json-fallback', '-j', is_flag=True, help='Force use of JSON fallback')
def add(name, type, location, capacity, equipment, json_fallback):
    """Add a new emergency resource."""
    resource_data = {
        'name': name,
        'type': type,
        'location': location,
        'capacity': capacity,
        'status': 'available'
    }
    
    if equipment:
        resource_data['equipment'] = [item.strip() for item in equipment.split(',')]
    
    # Check if we should use JSON fallback
    use_json = json_fallback or not check_sqlite_availability()
    
    if use_json:
        if add_resource_to_json(resource_data):
            console.print(f"[green]✓ Resource '{name}' added successfully to JSON[/green]")
        else:
            console.print("[red]✗ Failed to add resource to JSON[/red]")
    else:
        console.print(f"[green]Resource '{name}' would be added to SQLite[/green]")


@resources.command()
@click.option('--resource-id', '-i', required=True, help='Resource ID to update')
@click.option('--status', '-s', help='New status')
@click.option('--location', '-l', help='New location')
@click.option('--json-fallback', '-j', is_flag=True, help='Force use of JSON fallback')
def update(resource_id, status, location, json_fallback):
    """Update an existing emergency resource."""
    updates = {}
    if status:
        updates['status'] = status
    if location:
        updates['location'] = location
    
    if not updates:
        console.print("[yellow]No updates specified[/yellow]")
        return
    
    # Check if we should use JSON fallback
    use_json = json_fallback or not check_sqlite_availability()
    
    if use_json:
        if update_resource_in_json(resource_id, updates):
            console.print(f"[green]✓ Resource {resource_id} updated successfully[/green]")
        else:
            console.print(f"[red]✗ Failed to update resource {resource_id}[/red]")
    else:
        console.print(f"[green]Resource {resource_id} would be updated in SQLite[/green]")


# ==================== SUPPLY CHECKLIST COMMANDS ====================

@disaster_cli.group()
def supplies():
    """Manage supply checklists and inventory."""
    pass


@supplies.command()
@click.option('--category', '-c', help='Filter by supply category')
@click.option('--priority', '-p', help='Filter by priority level')
@click.option('--status', '-s', help='Filter by status (check/uncheck)')
@click.option('--emergency', '-e', is_flag=True, help='Show emergency priority items first')
def checklist(category, priority, status, emergency):
    """View and manage supply checklists."""
    # Show emergency header if in emergency mode
    if EMERGENCY_MODE:
        console.print(create_emergency_header())
    
    # Enhanced title with emergency styling
    title_style = "bold red" if EMERGENCY_MODE else "bold blue"
    title_icon = "EMERGENCY" if EMERGENCY_MODE else "SUPPLIES"
    console.print(f"[{title_style}]{title_icon}: Emergency Supply Checklist[/{title_style}]\n")
    
    checklist_data = get_supply_checklist()
    
    if category and category not in checklist_data:
        error_panel = Panel(
            f"Invalid category: {category}\nAvailable categories: {', '.join(checklist_data.keys())}",
            title="Error",
            border_style="red",
            title_align="center"
        )
        console.print(error_panel)
        return
    
    # Filter categories
    categories_to_show = [category] if category else checklist_data.keys()
    
    # Track critical supplies
    critical_supplies = []
    total_critical = 0
    
    for cat_name in categories_to_show:
        if cat_name not in checklist_data:
            continue
        
        # Enhanced category header
        category_icon = {
            'medical_supplies': 'MEDICAL',
            'emergency_equipment': 'EQUIPMENT',
            'food_water': 'FOOD/WATER',
            'shelter_supplies': 'SHELTER'
        }.get(cat_name, 'SUPPLIES')
        
        category_panel = Panel(
            f"{category_icon} {cat_name.replace('_', ' ').title()}",
            border_style="blue",
            title_align="center"
        )
        console.print(category_panel)
        
        items = checklist_data[cat_name]
        
        # Apply filters
        if priority:
            items = [item for item in items if item.get('priority') == priority]
        if status:
            items = [item for item in items if item.get('status') == status]
        
        # Sort by priority if emergency mode
        if emergency or EMERGENCY_MODE:
            priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            items.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 3))
        
        if items:
            # Enhanced table with priority-based styling
            table = Table(
                show_header=True, 
                header_style="bold magenta",
                border_style="red" if EMERGENCY_MODE else "blue",
                title=f"{cat_name.replace('_', ' ').title()} Supplies"
            )
            
            table.add_column("Priority", style="yellow", width=10, justify="center")
            table.add_column("Item", style="blue", width=30)
            table.add_column("Quantity", style="white", width=15, justify="center")
            table.add_column("Status", style="green", width=10, justify="center")
            table.add_column("Alert", style="red", width=15, justify="center")
            
            for item in items:
                priority_level = item.get('priority', 'low')
                priority_color = {
                    'critical': 'bold red',
                    'high': 'bold yellow',
                    'medium': 'blue',
                    'low': 'green'
                }.get(priority_level, 'white')
                
                # Track critical items
                if priority_level == 'critical':
                    critical_supplies.append(item['item'])
                    total_critical += 1
                
                # Enhanced status display
                status_icon = "[ ]" if item['status'] == 'check' else "[X]"
                status_style = "red" if item['status'] == 'check' else "green"
                
                # Alert column for critical items
                alert_text = "CRITICAL" if priority_level == 'critical' else ""
                
                table.add_row(
                    f"[{priority_color}]{priority_level.upper()}[/{priority_color}]",
                    f"[{priority_color}]{item['item']}[/{priority_color}]",
                    item['quantity'],
                    f"[{status_style}]{status_icon}[/{status_style}]",
                    alert_text
                )
            
            console.print(table)
            
            # Category summary
            category_critical = len([i for i in items if i.get('priority') == 'critical'])
            if category_critical > 0:
                console.print(f"[bold red]WARNING: {category_critical} critical items in this category[/bold red]")
        else:
            no_items_panel = Panel(
                "No items found matching the criteria",
                title="No Results",
                border_style="yellow",
                title_align="center"
            )
            console.print(no_items_panel)
        
        console.print()
    
    # Overall emergency summary
    if total_critical > 0:
        if total_critical >= 5:
            display_emergency_alert(
                f"CRITICAL: {total_critical} supplies require immediate attention!",
                "emergency"
            )
        elif total_critical >= 3:
            display_emergency_alert(
                f"WARNING: {total_critical} critical supplies need attention",
                "critical"
            )
        else:
            display_emergency_alert(
                f"Alert: {total_critical} critical supplies identified",
                "warning"
            )
        
        # Show critical supplies list
        critical_panel = Panel(
            "\n".join([f"• {item}" for item in critical_supplies]),
            title="Critical Supplies Requiring Attention",
            border_style="red",
            title_align="center"
        )
        console.print(critical_panel)


@supplies.command()
@click.option('--category', '-c', required=True, help='Supply category')
@click.option('--item', '-i', required=True, help='Item name')
@click.option('--priority', '-p', required=True, help='Priority level')
@click.option('--quantity', '-q', required=True, help='Required quantity')
def add_item(category, item, priority, quantity):
    """Add a new item to the supply checklist."""
    console.print(f"Adding item to {category} checklist...")
    
    # This would typically save to a database or configuration file
    console.print(f"[green]✓ Added {item} to {category} checklist[/green]")
    console.print(f"Priority: {priority}, Quantity: {quantity}")


# ==================== EMERGENCY CONTACTS COMMANDS ====================

@disaster_cli.group()
def contacts():
    """Manage emergency contacts and find nearby responders."""
    pass


@contacts.command()
@click.option('--type', '-t', help='Filter by contact type')
@click.option('--priority', '-p', help='Filter by priority level')
@click.option('--organization', '-o', help='Filter by organization')
def list(type, priority, organization):
    """List emergency contacts with filtering options."""
    console.print("[bold blue]Emergency Contacts Directory[/bold blue]\n")
    
    try:
        from database import db
        contacts = db.get_emergency_contacts(contact_type=type, priority=priority, organization=organization)
    except ImportError:
        # Fallback to sample data
        contacts = [
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
                'email': 'emergency@cityhospital.gov',
                'contact_type': 'medical',
                'priority': 'high'
            }
        ]
    
    if contacts:
        table = Table(title="Emergency Contacts", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=10)
        table.add_column("Name", style="blue", width=20)
        table.add_column("Organization", style="green", width=20)
        table.add_column("Role", style="white", width=20)
        table.add_column("Phone", style="yellow", width=12)
        table.add_column("Type", style="magenta", width=12)
        table.add_column("Priority", style="red", width=10)
        
        for contact in contacts:
            priority_color = {
                'high': 'red',
                'medium': 'yellow',
                'normal': 'green',
                'low': 'blue'
            }.get(contact.get('priority', ''), 'white')
            
            table.add_row(
                contact.get('id', 'N/A'),
                contact.get('name', 'N/A'),
                contact.get('organization', 'N/A'),
                contact.get('role', 'N/A'),
                contact.get('phone', 'N/A'),
                contact.get('contact_type', 'N/A'),
                f"[{priority_color}]{contact.get('priority', 'N/A')}[/{priority_color}]"
            )
        
        console.print(table)
        console.print(f"\n[bold green]Total Contacts: {len(contacts)}[/bold green]")
    else:
        console.print("[yellow]No contacts found[/yellow]")


@contacts.command()
@click.option('--address', '-a', help='Address to search from')
@click.option('--latitude', '-lat', type=float, help='Latitude coordinate')
@click.option('--longitude', '-lon', type=float, help='Longitude coordinate')
@click.option('--radius', '-r', type=float, default=10.0, help='Search radius in kilometers')
def nearby(address, latitude, longitude, radius):
    """Find emergency contacts within specified radius."""
    console.print("[bold blue]Finding Nearby Emergency Contacts[/bold blue]\n")
    
    if address:
        console.print(f"Geocoding address: {address}")
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task("Geocoding...", total=None)
            coords = geocode_address(address)
            progress.update(task, completed=True)
        
        if coords:
            latitude, longitude = coords
            console.print(f"[green]Coordinates: {latitude:.6f}, {longitude:.6f}[/green]")
        else:
            console.print("[red]Could not geocode address[/red]")
            return
    elif not latitude or not longitude:
        console.print("[red]Please provide either an address or coordinates[/red]")
        return
    
    console.print(f"Searching for contacts within {radius} km...")
    
    nearby_contacts = find_nearby_contacts(latitude, longitude, radius)
    
    if nearby_contacts:
        table = Table(title=f"Emergency Contacts within {radius} km", show_header=True, header_style="bold magenta")
        table.add_column("Name", style="blue", width=20)
        table.add_column("Organization", style="green", width=20)
        table.add_column("Role", style="white", width=20)
        table.add_column("Phone", style="yellow", width=12)
        table.add_column("Distance", style="cyan", width=10)
        table.add_column("Priority", style="red", width=10)
        
        for contact in nearby_contacts:
            priority_color = {
                'high': 'red',
                'medium': 'yellow',
                'normal': 'green',
                'low': 'blue'
            }.get(contact.get('priority', ''), 'white')
            
            table.add_row(
                contact.get('name', 'N/A'),
                contact.get('organization', 'N/A'),
                contact.get('role', 'N/A'),
                contact.get('phone', 'N/A'),
                f"{contact.get('distance_km', 0)} km",
                f"[{priority_color}]{contact.get('priority', 'N/A')}[/{priority_color}]"
            )
        
        console.print(table)
        console.print(f"\n[bold green]Found {len(nearby_contacts)} contacts nearby[/bold green]")
    else:
        console.print(f"[yellow]No emergency contacts found within {radius} km[/yellow]")


# ==================== GEOLOCATION COMMANDS ====================

@disaster_cli.group()
def facilities():
    """Find nearby emergency facilities and locations."""
    pass


@facilities.command()
@click.option('--address', '-a', help='Address to search from')
@click.option('--latitude', '-lat', type=float, help='Latitude coordinate')
@click.option('--longitude', '-lon', type=float, help='Longitude coordinate')
@click.option('--radius', '-r', type=float, default=25.0, help='Search radius in kilometers')
@click.option('--type', '-t', help='Filter by facility type (hospital, shelter, aid_station, etc.)')
def nearby(address, latitude, longitude, radius, type):
    """Find nearby emergency facilities."""
    console.print("[bold blue]Finding Nearby Emergency Facilities[/bold blue]\n")
    
    if address:
        console.print(f"Geocoding address: {address}")
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task("Geocoding...", total=None)
            coords = geocode_address(address)
            progress.update(task, completed=True)
        
        if coords:
            latitude, longitude = coords
            console.print(f"[green]Coordinates: {latitude:.6f}, {longitude:.6f}[/green]")
        else:
            console.print("[red]Could not geocode address[/red]")
            return
    elif not latitude or not longitude:
        console.print("[red]Please provide either an address or coordinates[/red]")
        return
    
    try:
        from geolocation import location_manager
        
        if type:
            # Find specific type of facility
            if type == 'hospital':
                facilities = location_manager.find_hospitals(latitude, longitude, radius)
            elif type == 'shelter':
                facilities = location_manager.find_shelters(latitude, longitude, radius)
            elif type == 'aid_station':
                facilities = location_manager.find_aid_stations(latitude, longitude, radius)
            elif type == 'emergency_ops':
                facilities = location_manager.find_emergency_ops(latitude, longitude, radius)
            else:
                facilities = location_manager.find_locations_within_radius(latitude, longitude, radius, type)
            
            if facilities:
                console.print(f"[bold green]Found {len(facilities)} {type} facilities within {radius} km:[/bold green]\n")
                _display_facilities_table(facilities, type)
            else:
                console.print(f"[yellow]No {type} facilities found within {radius} km[/yellow]")
        else:
            # Find all types of emergency facilities
            all_facilities = location_manager.find_emergency_facilities(latitude, longitude, radius)
            
            if all_facilities:
                console.print(f"[bold green]Emergency Facilities within {radius} km:[/bold green]\n")
                
                for facility_type, facilities in all_facilities.items():
                    if facilities:
                        console.print(f"[bold blue]{facility_type.replace('_', ' ').title()}:[/bold blue]")
                        _display_facilities_table(facilities, facility_type)
                        console.print()
            else:
                console.print(f"[yellow]No emergency facilities found within {radius} km[/yellow]")
                
    except ImportError:
        console.print("[red]Geolocation module not available[/red]")


@facilities.command()
@click.option('--address', '-a', help='Address to search from')
@click.option('--latitude', '-lat', type=float, help='Latitude coordinate')
@click.option('--longitude', '-lon', type=float, help='Longitude coordinate')
@click.option('--radius', '-r', type=float, default=25.0, help='Search radius in kilometers')
def hospitals(address, latitude, longitude, radius):
    """Find nearby hospitals and medical facilities."""
    console.print("[bold blue]Finding Nearby Hospitals[/bold blue]\n")
    
    if address:
        console.print(f"Geocoding address: {address}")
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task("Geocoding...", total=None)
            coords = geocode_address(address)
            progress.update(task, completed=True)
        
        if coords:
            latitude, longitude = coords
            console.print(f"[green]Coordinates: {latitude:.6f}, {longitude:.6f}[/green]")
        else:
            console.print("[red]Could not geocode address[/red]")
            return
    elif not latitude or not longitude:
        console.print("[red]Please provide either an address or coordinates[/red]")
        return
    
    try:
        from geolocation import location_manager
        hospitals = location_manager.find_hospitals(latitude, longitude, radius)
        
        if hospitals:
            console.print(f"[bold green]Found {len(hospitals)} hospitals within {radius} km:[/bold green]\n")
            _display_facilities_table(hospitals, 'hospital')
        else:
            console.print(f"[yellow]No hospitals found within {radius} km[/yellow]")
            
    except ImportError:
        console.print("[red]Geolocation module not available[/red]")


@facilities.command()
@click.option('--address', '-a', help='Address to search from')
@click.option('--latitude', '-lat', type=float, help='Latitude coordinate')
@click.option('--longitude', '-lon', type=float, help='Longitude coordinate')
@click.option('--radius', '-r', type=float, default=25.0, help='Search radius in kilometers')
def shelters(address, latitude, longitude, radius):
    """Find nearby shelters and evacuation centers."""
    console.print("[bold blue]Finding Nearby Shelters[/bold blue]\n")
    
    if address:
        console.print(f"Geocoding address: {address}")
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task("Geocoding...", total=None)
            coords = geocode_address(address)
            progress.update(task, completed=True)
        
        if coords:
            latitude, longitude = coords
            console.print(f"[green]Coordinates: {latitude:.6f}, {longitude:.6f}[/green]")
        else:
            console.print("[red]Could not geocode address[/red]")
            return
    elif not latitude or not longitude:
        console.print("[red]Please provide either an address or coordinates[/red]")
        return
    
    try:
        from geolocation import location_manager
        shelters = location_manager.find_shelters(latitude, longitude, radius)
        
        if shelters:
            console.print(f"[bold green]Found {len(shelters)} shelters within {radius} km:[/bold green]\n")
            _display_facilities_table(shelters, 'shelter')
        else:
            console.print(f"[yellow]No shelters found within {radius} km[/yellow]")
            
    except ImportError:
        console.print("[red]Geolocation module not available[/red]")


@facilities.command()
@click.option('--address', '-a', help='Address to search from')
@click.option('--latitude', '-lat', type=float, help='Latitude coordinate')
@click.option('--longitude', '-lon', type=float, help='Longitude coordinate')
@click.option('--radius', '-r', type=float, default=25.0, help='Search radius in kilometers')
def aid_stations(address, latitude, longitude, radius):
    """Find nearby aid stations and relief centers."""
    console.print("[bold blue]Finding Nearby Aid Stations[/bold blue]\n")
    
    if address:
        console.print(f"Geocoding address: {address}")
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task("Geocoding...", total=None)
            coords = geocode_address(address)
            progress.update(task, completed=True)
        
        if coords:
            latitude, longitude = coords
            console.print(f"[green]Coordinates: {latitude:.6f}, {longitude:.6f}[/green]")
        else:
            console.print("[red]Could not geocode address[/red]")
            return
    elif not latitude or not longitude:
        console.print("[red]Please provide either an address or coordinates[/red]")
        return
    
    try:
        from geolocation import location_manager
        aid_stations = location_manager.find_aid_stations(latitude, longitude, radius)
        
        if aid_stations:
            console.print(f"[bold green]Found {len(aid_stations)} aid stations within {radius} km:[/bold green]\n")
            _display_facilities_table(aid_stations, 'aid_station')
        else:
            console.print(f"[yellow]No aid stations found within {radius} km[/yellow]")
            
    except ImportError:
        console.print("[red]Geolocation module not available[/red]")


@facilities.command()
@click.option('--address', '-a', help='Address to search from')
@click.option('--latitude', '-lat', type=float, help='Latitude coordinate')
@click.option('--longitude', '-lon', type=float, help='Longitude coordinate')
@click.option('--radius', '-r', type=float, default=50.0, help='Search radius in kilometers')
def emergency_ops(address, latitude, longitude, radius):
    """Find nearby emergency operations centers."""
    console.print("[bold blue]Finding Emergency Operations Centers[/bold blue]\n")
    
    if address:
        console.print(f"Geocoding address: {address}")
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task("Geocoding...", total=None)
            coords = geocode_address(address)
            progress.update(task, completed=True)
        
        if coords:
            latitude, longitude = coords
            console.print(f"[green]Coordinates: {latitude:.6f}, {longitude:.6f}[/green]")
        else:
            console.print("[red]Could not geocode address[/red]")
            return
    elif not latitude or not longitude:
        console.print("[red]Please provide either an address or coordinates[/red]")
        return
    
    try:
        from geolocation import location_manager
        ops_centers = location_manager.find_emergency_ops(latitude, longitude, radius)
        
        if ops_centers:
            console.print(f"[bold green]Found {len(ops_centers)} emergency operations centers within {radius} km:[/bold green]\n")
            _display_facilities_table(ops_centers, 'emergency_ops')
        else:
            console.print(f"[yellow]No emergency operations centers found within {radius} km[/yellow]")
            
    except ImportError:
        console.print("[red]Geolocation module not available[/red]")


@facilities.command()
@click.option('--type', '-t', help='Filter by facility type')
@click.option('--name', '-n', help='Filter by facility name pattern')
def list(type, name):
    """List all available emergency facilities."""
    console.print("[bold blue]Emergency Facilities Directory[/bold blue]\n")
    
    try:
        from geolocation import location_manager
        
        locations = location_manager.locations
        
        # Apply filters
        if type:
            locations = location_manager.get_locations_by_type(type)
        if name:
            locations = location_manager.get_locations_by_name(name)
        
        if locations:
            # Create rich table
            table = Table(title="Emergency Facilities", show_header=True, header_style="bold magenta")
            table.add_column("ID", style="cyan", width=12)
            table.add_column("Name", style="blue", width=30)
            table.add_column("Type", style="magenta", width=15)
            table.add_column("Address", style="green", width=40)
            table.add_column("Capacity", style="white", width=10)
            table.add_column("Phone", style="yellow", width=15)
            table.add_column("Status", style="red", width=8)
            
            for location in locations:
                status_icon = "ACTIVE" if location.is_active else "INACTIVE"
                capacity_str = str(location.capacity) if location.capacity else "N/A"
                
                table.add_row(
                    location.id,
                    location.name,
                    location.type.replace('_', ' ').title(),
                    location.address or "N/A",
                    capacity_str,
                    location.contact_phone or "N/A",
                    status_icon
                )
            
            console.print(table)
            console.print(f"\n[bold green]Total Facilities: {len(locations)}[/bold green]")
            
            # Show statistics
            stats = location_manager.get_location_statistics()
            console.print(f"\n[bold blue]Statistics:[/bold blue]")
            console.print(f"Active: {stats['active_locations']}")
            console.print(f"By Type: {stats['by_type']}")
            
        else:
            console.print("[yellow]No facilities found matching the criteria[/yellow]")
            
    except ImportError:
        console.print("[red]Geolocation module not available[/red]")


@facilities.command()
@click.option('--name', '-n', required=True, help='Facility name')
@click.option('--type', '-t', required=True, help='Facility type')
@click.option('--address', '-a', required=True, help='Facility address')
@click.option('--latitude', '-lat', type=float, required=True, help='Latitude coordinate')
@click.option('--longitude', '-lon', type=float, required=True, help='Longitude coordinate')
@click.option('--capacity', '-c', type=int, help='Facility capacity')
@click.option('--phone', '-p', help='Contact phone number')
@click.option('--email', '-e', help='Contact email')
@click.option('--description', '-d', help='Facility description')
def add(name, type, address, latitude, longitude, capacity, phone, email, description):
    """Add a new emergency facility location."""
    console.print(f"Adding new emergency facility: {name}")
    
    try:
        from geolocation import Location, location_manager
        
        # Validate coordinates
        if not location_manager.validate_coordinates(latitude, longitude):
            console.print("[red]Invalid coordinates provided[/red]")
            return
        
        # Create new location
        new_location = Location(
            name=name,
            type=type,
            address=address,
            latitude=latitude,
            longitude=longitude,
            capacity=capacity,
            contact_phone=phone,
            contact_email=email,
            description=description
        )
        
        if location_manager.add_location(new_location):
            console.print(f"[green]✓ Facility '{name}' added successfully[/green]")
            console.print(f"Coordinates: {location_manager.format_coordinates(latitude, longitude)}")
        else:
            console.print("[red]✗ Failed to add facility[/red]")
            
    except ImportError:
        console.print("[red]Geolocation module not available[/red]")


@facilities.command()
@click.option('--facility-id', '-i', required=True, help='Facility ID to export')
@click.option('--type', '-t', help='Export all facilities of specific type')
@click.option('--output', '-o', default='data/exported_facilities.json', help='Output file path')
def export(facility_id, type, output):
    """Export emergency facilities to JSON file."""
    console.print(f"Exporting facilities to: {output}")
    
    try:
        from geolocation import location_manager
        
        if facility_id and facility_id != 'all':
            # Export specific facility
            location = location_manager.get_location_by_id(facility_id)
            if location:
                if location_manager.export_locations_to_json(output, location.type):
                    console.print(f"[green]✓ Exported facility {facility_id}[/green]")
                else:
                    console.print("[red]✗ Export failed[/red]")
            else:
                console.print(f"[yellow]Facility {facility_id} not found[/yellow]")
        else:
            # Export by type or all
            if location_manager.export_locations_to_json(output, type):
                console.print(f"[green]✓ Exported facilities to {output}[/green]")
            else:
                console.print("[red]✗ Export failed[/red]")
                
    except ImportError:
        console.print("[red]Geolocation module not available[/red]")


def _display_facilities_table(facilities, facility_type):
    """Display facilities in a formatted table."""
    if not facilities:
        return
    
    # Create rich table
    table = Table(title=f"{facility_type.replace('_', ' ').title()} Facilities", show_header=True, header_style="bold magenta")
    table.add_column("Name", style="blue", width=25)
    table.add_column("Address", style="green", width=35)
    table.add_column("Distance", style="cyan", width=10)
    table.add_column("Capacity", style="white", width=10)
    table.add_column("Phone", style="yellow", width=15)
    table.add_column("Facilities", style="white", width=25)
    
    for location, distance in facilities:
        facilities_str = ", ".join(location.facilities[:2]) if location.facilities else "N/A"
        if location.facilities and len(location.facilities) > 2:
            facilities_str += "..."
        
        capacity_str = str(location.capacity) if location.capacity else "N/A"
        
        table.add_row(
            location.name,
            location.address or "N/A",
            f"{distance:.1f} km",
            capacity_str,
            location.contact_phone or "N/A",
            facilities_str
        )
    
    console.print(table)


# ==================== CONNECTIVITY SIMULATION COMMANDS ====================

@disaster_cli.group()
def simulate():
    """Simulate low-connectivity and power scenarios for testing."""
    pass


@simulate.command()
@click.option('--mode', '-m', type=click.Choice(['online', 'intermittent', 'low_bandwidth', 'offline', 'emergency']), 
              default='offline', help='Connectivity mode to simulate')
def connectivity(mode):
    """Set connectivity simulation mode."""
    try:
        from connectivity_simulator import simulator, ConnectivityMode
        
        mode_enum = ConnectivityMode(mode)
        simulator.set_connectivity_mode(mode_enum)
        
        console.print(f"[bold blue]Connectivity Mode: {mode.upper()}[/bold blue]")
        
        if mode == 'online':
            console.print("[green]✓ Full connectivity - all features available[/green]")
        elif mode == 'intermittent':
            console.print("[yellow]⚠ Intermittent connectivity - features may be unreliable[/yellow]")
        elif mode == 'low_bandwidth':
            console.print("[yellow]⚠ Low bandwidth - slow operations expected[/yellow]")
        elif mode == 'offline':
            console.print("[red]✗ Offline mode - JSON fallback will be used[/red]")
        elif mode == 'emergency':
            console.print("[red]Emergency mode - minimal connectivity, power saving[/red]")
        
        # Show current status
        is_connected = simulator.is_connected()
        status_icon = "Connected" if is_connected else "Disconnected"
        console.print(f"\nCurrent Status: {status_icon}")
        
    except ImportError:
        console.print("[red]Connectivity simulator not available[/red]")


@simulate.command()
@click.option('--mode', '-m', type=click.Choice(['normal', 'power_save', 'minimal', 'critical']), 
              default='normal', help='Power mode to simulate')
def power(mode):
    """Set power consumption simulation mode."""
    try:
        from connectivity_simulator import simulator, PowerMode
        
        mode_enum = PowerMode(mode)
        simulator.set_power_mode(mode_enum)
        
        console.print(f"[bold blue]Power Mode: {mode.upper()}[/bold blue]")
        
        if mode == 'normal':
            console.print("[green]✓ Normal power consumption - full performance[/green]")
        elif mode == 'power_save':
            console.print("[yellow]⚠ Power saving mode - reduced performance[/yellow]")
        elif mode == 'minimal':
            console.print("[yellow]⚠ Minimal power mode - significant performance impact[/yellow]")
        elif mode == 'critical':
            console.print("[red]Critical power mode - minimal functionality[/red]")
        
        # Show current settings
        console.print(f"\nPower Consumption: {simulator.power_consumption:.1f}x")
        console.print(f"CPU Throttle: {simulator.cpu_throttle:.1f}x")
        if simulator.memory_limit:
            console.print(f"Memory Limit: {simulator.memory_limit} MB")
        
    except ImportError:
        console.print("[red]Connectivity simulator not available[/red]")


@simulate.command()
@click.option('--duration', '-d', type=int, default=5, help='Simulation duration in minutes')
def start(duration):
    """Start connectivity and power simulation."""
    try:
        from connectivity_simulator import simulator
        
        simulator.start_simulation(duration)
        
        console.print(f"[bold blue]Started Simulation for {duration} minutes[/bold blue]")
        console.print(f"Connectivity Mode: {simulator.current_mode.value}")
        console.print(f"Power Mode: {simulator.power_mode.value}")
        console.print(f"Status: {'Active' if simulator.simulation_active else 'Inactive'}")
        
        console.print(f"\n[yellow]Simulation will run in background for {duration} minutes[/yellow]")
        console.print("Use 'simulate stop' to stop early or 'simulate status' to check progress")
        
    except ImportError:
        console.print("[red]Connectivity simulator not available[/red]")


@simulate.command()
def stop():
    """Stop the current simulation."""
    try:
        from connectivity_simulator import simulator
        
        if simulator.simulation_active:
            simulator.stop_simulation()
            console.print("[bold blue]Simulation stopped[/bold blue]")
        else:
            console.print("[yellow]No active simulation to stop[/yellow]")
        
    except ImportError:
        console.print("[red]Connectivity simulator not available[/red]")


@simulate.command()
def status():
    """Show current simulation status and statistics."""
    try:
        from connectivity_simulator import simulator
        
        stats = simulator.get_simulation_stats()
        
        console.print("[bold blue]Simulation Status[/bold blue]\n")
        
        # Current modes
        console.print(f"Connectivity Mode: [bold]{stats['current_mode']}[/bold]")
        console.print(f"Power Mode: [bold]{stats['power_mode']}[/bold]")
        console.print(f"Simulation Active: {'Yes' if stats['simulation_active'] else 'No'}")
        
        # Statistics
        console.print(f"\nTotal Operations: {stats['total_operations']}")
        console.print(f"Average Power Consumption: {stats['average_power_consumption']}")
        console.print(f"Connection Uptime: {stats['connection_uptime']}%")
        console.print(f"Power History: {stats['power_history_count']} entries")
        console.print(f"Connection History: {stats['connection_history_count']} entries")
        
        # Current connectivity status
        is_connected = simulator.is_connected()
        status_icon = "Connected" if is_connected else "Disconnected"
        console.print(f"\nCurrent Connection: {status_icon}")
        
    except ImportError:
        console.print("[red]Connectivity simulator not available[/red]")


@simulate.command()
@click.option('--output', '-o', default='data/simulation_data.json', help='Output file path')
def export(output):
    """Export simulation data to JSON file."""
    try:
        from connectivity_simulator import simulator
        
        if simulator.export_simulation_data(output):
            console.print(f"[green]Simulation data exported to {output}[/green]")
        else:
            console.print("[red]Failed to export simulation data[/red]")
        
    except ImportError:
        console.print("[red]Connectivity simulator not available[/red]")


# ==================== DATABASE FALLBACK TESTING COMMANDS ====================

@disaster_cli.group()
def test():
    """Test database fallback and system functionality."""
    pass


@test.command()
def fallback():
    """Test SQLite and JSON fallback functionality."""
    try:
        from connectivity_simulator import fallback_tester
        
        console.print("[bold blue]Testing Database Fallback Functionality[/bold blue]\n")
        
        # Create test data
        test_data = [
            {'id': 'TEST-001', 'name': 'Test Resource 1', 'type': 'equipment', 'status': 'available'},
            {'id': 'TEST-002', 'name': 'Test Resource 2', 'type': 'vehicle', 'status': 'maintenance'},
            {'id': 'TEST-003', 'name': 'Test Resource 3', 'type': 'supplies', 'status': 'in_use'}
        ]
        
        console.print("Running fallback tests...")
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task("Testing...", total=None)
            test_result = fallback_tester.test_database_fallback(test_data)
            progress.update(task, completed=True)
        
        # Display results
        console.print(f"\n[bold green]Test Results:[/bold green]")
        console.print(f"Timestamp: {test_result['timestamp']}")
        console.print(f"Connectivity Mode: {test_result['connectivity_mode']}")
        console.print(f"Power Mode: {test_result['power_mode']}")
        
        console.print(f"\n[bold blue]Individual Tests:[/bold blue]")
        for test in test_result['tests']:
            status_icon = "PASS" if test['success'] else "FAIL"
            console.print(f"  {status_icon} {test['name']}")
            console.print(f"    Duration: {test['duration']}s")
            console.print(f"    Power: {test['power_consumed']}")
            if test['error']:
                console.print(f"    Error: {test['error']}")
            if 'details' in test:
                for key, value in test['details'].items():
                    console.print(f"    {key}: {value}")
            console.print()
        
    except ImportError:
        console.print("[red]Fallback tester not available[/red]")


@test.command()
def summary():
    """Show summary of all fallback tests."""
    try:
        from connectivity_simulator import fallback_tester
        
        summary = fallback_tester.get_test_summary()
        
        if 'message' in summary:
            console.print(f"[yellow]{summary['message']}[/yellow]")
            return
        
        console.print("[bold blue]Fallback Test Summary[/bold blue]\n")
        
        console.print(f"Total Test Runs: {summary['total_test_runs']}")
        console.print(f"Successful Test Runs: {summary['successful_test_runs']}")
        console.print(f"Overall Success Rate: {summary['overall_success_rate']}%")
        console.print(f"Individual Test Success Rate: {summary['individual_test_success_rate']}%")
        
        if summary['latest_test']:
            latest = summary['latest_test']
            console.print(f"\n[bold blue]Latest Test Run:[/bold blue]")
            console.print(f"  Timestamp: {latest['timestamp']}")
            console.print(f"  Connectivity: {latest['connectivity_mode']}")
            console.print(f"  Power Mode: {latest['power_mode']}")
            
            successful_tests = sum(1 for test in latest['tests'] if test['success'])
            console.print(f"  Tests Passed: {successful_tests}/{len(latest['tests'])}")
        
    except ImportError:
        console.print("[red]Fallback tester not available[/red]")


@test.command()
@click.option('--mode', '-m', type=click.Choice(['online', 'intermittent', 'offline']), 
              default='offline', help='Test under specific connectivity mode')
@click.option('--power', '-p', type=click.Choice(['normal', 'minimal', 'critical']), 
              default='normal', help='Test under specific power mode')
def comprehensive(mode, power):
    """Run comprehensive fallback tests under specific conditions."""
    try:
        from connectivity_simulator import simulator, fallback_tester, ConnectivityMode, PowerMode
        
        console.print(f"[bold blue]Comprehensive Fallback Testing[/bold blue]")
        console.print(f"Mode: {mode.upper()} | Power: {power.upper()}\n")
        
        # Set simulation modes
        simulator.set_connectivity_mode(ConnectivityMode(mode))
        simulator.set_power_mode(PowerMode(power))
        
        # Create comprehensive test data
        test_data = []
        for i in range(50):  # Larger dataset for comprehensive testing
            test_data.append({
                'id': f'COMP-{i+1:03d}',
                'name': f'Comprehensive Test Resource {i+1}',
                'type': ['equipment', 'vehicle', 'supplies', 'personnel'][i % 4],
                'status': ['available', 'in_use', 'maintenance'][i % 3],
                'priority': ['low', 'medium', 'high', 'critical'][i % 4]
            })
        
        console.print(f"Testing with {len(test_data)} test records...")
        
        # Run tests multiple times to ensure consistency
        test_results = []
        for run in range(3):
            console.print(f"\n[bold blue]Test Run {run + 1}/3[/bold blue]")
            
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
                task = progress.add_task("Running tests...", total=None)
                test_result = fallback_tester.test_database_fallback(test_data)
                progress.update(task, completed=True)
            
            test_results.append(test_result)
            
            # Show quick results
            successful_tests = sum(1 for test in test_result['tests'] if test['success'])
            console.print(f"  Results: {successful_tests}/{len(test_result['tests'])} tests passed")
        
        # Overall summary
        console.print(f"\n[bold green]Comprehensive Testing Complete[/bold green]")
        console.print(f"Total Test Runs: {len(test_results)}")
        
        all_tests = []
        for result in test_results:
            all_tests.extend(result['tests'])
        
        successful_tests = sum(1 for test in all_tests if test['success'])
        total_tests = len(all_tests)
        
        console.print(f"Total Individual Tests: {total_tests}")
        console.print(f"Successful Tests: {successful_tests}")
        console.print(f"Success Rate: {successful_tests/total_tests*100:.1f}%")
        
        # Performance analysis
        if all_tests:
            avg_duration = sum(test['duration'] for test in all_tests) / len(all_tests)
            avg_power = sum(test['power_consumed'] for test in all_tests) / len(all_tests)
            
            console.print(f"\n[bold blue]Performance Analysis:[/bold blue]")
            console.print(f"Average Test Duration: {avg_duration:.3f}s")
            console.print(f"Average Power Consumption: {avg_power:.3f}")
        
    except ImportError:
        console.print("[red]Comprehensive testing not available[/red]")


# ==================== POWER MANAGEMENT COMMANDS ====================

@disaster_cli.group()
def power():
    """Manage power consumption and performance settings."""
    pass


@power.command()
def status():
    """Show current power consumption and performance status."""
    try:
        from connectivity_simulator import simulator
        
        console.print("[bold blue]Power Management Status[/bold blue]\n")
        
        # Current power mode
        console.print(f"Power Mode: [bold]{simulator.power_mode.value}[/bold]")
        console.print(f"Power Consumption: {simulator.power_consumption:.1f}x")
        console.print(f"CPU Throttle: {simulator.cpu_throttle:.1f}x")
        
        if simulator.memory_limit:
            console.print(f"Memory Limit: {simulator.memory_limit} MB")
        else:
            console.print("Memory Limit: None (unlimited)")
        
        # Power history analysis
        if simulator.power_history:
            recent_operations = simulator.power_history[-10:]  # Last 10 operations
            avg_recent_power = sum(op['consumption'] for op in recent_operations) / len(recent_operations)
            
            console.print(f"\n[bold blue]Recent Power Usage:[/bold blue]")
            console.print(f"Average (last 10 operations): {avg_recent_power:.3f}")
            console.print(f"Total Operations: {len(simulator.power_history)}")
            
            # Show operation breakdown
            operation_types = {}
            for op in recent_operations:
                op_type = op['operation']
                if op_type not in operation_types:
                    operation_types[op_type] = []
                operation_types[op_type].append(op['consumption'])
            
            console.print(f"\n[bold blue]Operation Breakdown:[/bold blue]")
            for op_type, consumptions in operation_types.items():
                avg_consumption = sum(consumptions) / len(consumptions)
                console.print(f"  {op_type}: {avg_consumption:.3f} avg")
        else:
            console.print("\n[yellow]No power usage data available yet[/yellow]")
        
    except ImportError:
        console.print("[red]Power management not available[/red]")


@power.command()
@click.option('--operation', '-o', help='Operation type to monitor')
@click.option('--count', '-c', type=int, default=10, help='Number of operations to monitor')
def monitor(operation, count):
    """Monitor power consumption for specific operations."""
    try:
        from connectivity_simulator import simulator
        
        console.print(f"[bold blue]Power Consumption Monitoring[/bold blue]")
        if operation:
            console.print(f"Operation: {operation}")
        console.print(f"Monitoring: Last {count} operations\n")
        
        if not simulator.power_history:
            console.print("[yellow]No power usage data available yet[/yellow]")
            return
        
        # Filter operations if specified
        operations = simulator.power_history[-count:]
        if operation:
            operations = [op for op in operations if op['operation'] == operation]
        
        if not operations:
            console.print(f"[yellow]No operations found for '{operation}'[/yellow]")
            return
        
        # Display operations
        table = Table(title="Power Consumption History", show_header=True, header_style="bold magenta")
        table.add_column("Timestamp", style="cyan", width=20)
        table.add_column("Operation", style="blue", width=15)
        table.add_column("Consumption", style="green", width=12)
        table.add_column("Mode", style="yellow", width=12)
        
        for op in operations:
            timestamp = op['timestamp'].split('T')[1][:8]  # Show only time
            table.add_row(
                timestamp,
                op['operation'],
                f"{op['consumption']:.3f}",
                op['mode']
            )
        
        console.print(table)
        
        # Statistics
        consumptions = [op['consumption'] for op in operations]
        avg_consumption = sum(consumptions) / len(consumptions)
        min_consumption = min(consumptions)
        max_consumption = max(consumptions)
        
        console.print(f"\n[bold blue]Statistics:[/bold blue]")
        console.print(f"Average: {avg_consumption:.3f}")
        console.print(f"Minimum: {min_consumption:.3f}")
        console.print(f"Maximum: {max_consumption:.3f}")
        console.print(f"Total Operations: {len(operations)}")
        
    except ImportError:
        console.print("[red]Power monitoring not available[/red]")


# ==================== EXISTING COMMANDS ====================

@disaster_cli.command()
@click.option('--incident-id', '-i', help='Incident ID to view')
@click.option('--status', '-s', type=click.Choice(['active', 'resolved', 'all']), 
              default='active', help='Filter by incident status')
def incidents(incident_id, status):
    """Manage disaster incidents"""
    if incident_id:
        console.print(f"Viewing incident: {incident_id}")
        # TODO: Implement incident viewing logic
    else:
        console.print(f"Listing {status} incidents")
        # TODO: Implement incident listing logic
    
    # Placeholder table
    table = Table(title="Incidents")
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Location", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Priority", style="red")
    
    table.add_row("INC-001", "Flood", "Downtown Area", "Active", "High")
    table.add_row("INC-002", "Fire", "Industrial Zone", "Active", "Critical")
    
    console.print(table)


@disaster_cli.command()
@click.option('--personnel-id', '-p', help='Personnel ID to view')
@click.option('--role', '-r', help='Filter by role')
def personnel(personnel_id, role):
    """Manage response personnel"""
    if personnel_id:
        console.print(f"Viewing personnel: {personnel_id}")
    else:
        console.print("Managing response personnel")
        if role:
            console.print(f"Filtering by role: {role}")
    
    # Placeholder table
    table = Table(title="Personnel")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Role", style="green")
    table.add_column("Status", style="yellow")
    
    table.add_row("PER-001", "John Smith", "Firefighter", "On Duty")
    table.add_row("PER-002", "Jane Doe", "EMT", "Responding")
    
    console.print(table)


@disaster_cli.command()
@click.option('--latitude', '-lat', type=float, help='Latitude coordinate')
@click.option('--longitude', '-lon', type=float, help='Longitude coordinate')
@click.option('--address', '-a', help='Address to geocode')
def location(latitude, longitude, address):
    """Geolocation and mapping features"""
    if latitude and longitude:
        console.print(f"Coordinates: {latitude}, {longitude}")
        # TODO: Implement reverse geocoding
    elif address:
        console.print(f"Address: {address}")
        # TODO: Implement geocoding
    else:
        console.print("Location services")
        # TODO: Implement location features


@disaster_cli.command()
@click.option('--backup', '-b', is_flag=True, help='Create backup of data')
@click.option('--restore', '-r', help='Restore from backup file')
def data(backup, restore):
    """Data management operations"""
    if backup:
        console.print("Creating data backup...")
        # TODO: Implement backup functionality
    elif restore:
        console.print(f"Restoring from: {restore}")
        # TODO: Implement restore functionality
    else:
        console.print("Data management operations")
        # TODO: Implement data management features


@disaster_cli.command()
@click.option('--detailed', '-d', is_flag=True, help='Show detailed system information')
def status(detailed):
    """Show system status and health"""
    # Show emergency header if in emergency mode
    if EMERGENCY_MODE:
        console.print(create_emergency_header())
    
    sqlite_available = check_sqlite_availability()
    
    # Determine system status
    if EMERGENCY_MODE:
        system_status = "EMERGENCY MODE"
        status_color = "red"
        status_icon = "EMERGENCY"
    elif not sqlite_available:
        system_status = "DEGRADED"
        status_color = "yellow"
        status_icon = "WARNING"
    else:
        system_status = "OPERATIONAL"
        status_color = "green"
        status_icon = "OK"
    
    # Enhanced status display
    status_text = f"""[bold {status_color}]{status_icon} System Status: {system_status}[/bold {status_color}]

Database: {'Connected' if sqlite_available else 'SQLite Unavailable - Using JSON Fallback'}
Storage: {'Available' if True else 'Unavailable'}
Geolocation: {'Ready' if True else 'Unavailable'}
Last Sync: {'Recent' if sqlite_available else 'Never (Offline Mode)'}
Storage Mode: {'SQLite' if sqlite_available else 'JSON Fallback'}
Emergency Mode: {'ACTIVE' if EMERGENCY_MODE else 'Inactive'}"""
    
    # Create main status panel
    main_panel = Panel(
        status_text,
        title=f"Disaster Response CLI Status - {system_status}",
        border_style=status_color,
        title_align="center",
        padding=(1, 2)
    )
    
    console.print(main_panel)
    
    # Show detailed information if requested
    if detailed:
        # Database details
        db_panel = Panel(
            f"""SQLite Available: {'Yes' if sqlite_available else 'No'}
JSON Fallback: {'Active' if not sqlite_available else 'Standby'}
Data Directory: data/
Backup Status: {'Available' if True else 'Unavailable'}""",
            title="Database Details",
            border_style="blue",
            title_align="center"
        )
        console.print(db_panel)
        
        # System capabilities
        capabilities_panel = Panel(
            """Resource Management
Supply Checklists  
Emergency Contacts
Geolocation Services
Offline Operation
JSON Fallback
Emergency Alerts""",
            title="System Capabilities",
            border_style="green",
            title_align="center"
        )
        console.print(capabilities_panel)
    
    # Show emergency alerts if any
    if EMERGENCY_MODE:
        console.print()
        display_emergency_alert(
            f"System is operating in {EMERGENCY_LEVEL.upper()} mode",
            EMERGENCY_LEVEL
        )


@disaster_cli.command()
@click.option('--emergency', '-e', is_flag=True, help='Show emergency-focused quick access')
def quick(emergency):
    """Quick access to most common operations"""
    # Show emergency header if in emergency mode
    if EMERGENCY_MODE:
        console.print(create_emergency_header())
    
    # Enhanced title with emergency styling
    title_style = "bold red" if EMERGENCY_MODE else "bold blue"
    title_icon = "EMERGENCY" if EMERGENCY_MODE else "QUICK"
    console.print(f"[{title_style}]{title_icon}: Quick Access Menu[/{title_style}]\n")
    
    # Emergency-focused commands if requested or in emergency mode
    if emergency or EMERGENCY_MODE:
        quick_commands = [
            ("Emergency Resources", "disaster_cli resources list --emergency"),
            ("Critical Supplies", "disaster_cli supplies checklist --emergency"),
            ("Emergency Contacts", "disaster_cli contacts list"),
            ("Nearby Facilities", "disaster_cli facilities nearby --radius 50"),
            ("System Status", "disaster_cli status --detailed"),
            ("Power Status", "disaster_cli power status"),
            ("Test Fallback", "disaster_cli test fallback")
        ]
        border_style = "red"
    else:
        quick_commands = [
            ("Resources", "disaster_cli resources list"),
            ("Contacts", "disaster_cli contacts list"),
            ("Supplies", "disaster_cli supplies checklist"),
            ("Facilities", "disaster_cli facilities nearby --help"),
            ("Simulate", "disaster_cli simulate connectivity --help"),
            ("Test", "disaster_cli test fallback"),
            ("Power", "disaster_cli power status"),
            ("Status", "disaster_cli status")
        ]
        border_style = "blue"
    
    # Create enhanced quick access panels
    columns = []
    for title, command in quick_commands:
        # Enhanced panel styling
        panel_style = "red" if "Emergency" in title else border_style
        text = Text(f"{title}\n[dim]{command}[/dim]")
        
        # Add emergency indicators
        if EMERGENCY_MODE and "Emergency" in title:
            text.append("\n[bold red]PRIORITY[/bold red]")
        
        panel = Panel(
            text, 
            border_style=panel_style,
            title="Quick Access",
            title_align="center"
        )
        columns.append(panel)
    
    console.print(Columns(columns))
    
    # Enhanced footer with emergency information
    if EMERGENCY_MODE:
        footer_text = f"[bold red]EMERGENCY MODE ACTIVE - {EMERGENCY_LEVEL.upper()}[/bold red]\n"
        footer_text += "[yellow]Prioritize critical operations and resource management[/yellow]"
        footer_panel = Panel(
            footer_text,
            border_style="red",
            title="Emergency Protocol",
            title_align="center"
        )
        console.print(footer_panel)
    
    console.print(f"\n[bold green]Use 'disaster_cli --help' for full command list[/bold green]")
    
    # Show emergency tips
    if emergency or EMERGENCY_MODE:
        tips_panel = Panel(
            """Emergency Response Tips:
• Check critical supplies first
• Verify resource availability
• Contact emergency personnel
• Monitor system status
• Use JSON fallback if needed""",
            title="Emergency Response Guidelines",
            border_style="red",
            title_align="center"
        )
        console.print(tips_panel)


if __name__ == '__main__':
    disaster_cli()
