#!/usr/bin/env python3
"""
Test script for Disaster Response CLI Features

Demonstrates the new CLI functionality including:
- Emergency resources management
- Supply checklists
- Nearby emergency contacts with geopy
"""

import subprocess
import sys
from pathlib import Path


def run_cli_command(command):
    """Run a CLI command and return the result."""
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)


def test_cli_features():
    """Test all the new CLI features."""
    print("🚨 Testing Disaster Response CLI Features\n")
    
    # Test 1: Quick access menu
    print("1. Testing Quick Access Menu...")
    return_code, output, error = run_cli_command("python cli.py quick")
    if return_code == 0:
        print("   ✓ Quick access menu working")
    else:
        print(f"   ✗ Quick access failed: {error}")
    
    # Test 2: Emergency Resources
    print("\n2. Testing Emergency Resources...")
    
    # List resources
    return_code, output, error = run_cli_command("python cli.py resources list")
    if return_code == 0:
        print("   ✓ Resources list command working")
    else:
        print(f"   ✗ Resources list failed: {error}")
    
    # Add a resource
    return_code, output, error = run_cli_command(
        'python cli.py resources add --name "Test Generator" --type equipment --location "Warehouse" --capacity "2000W"'
    )
    if return_code == 0:
        print("   ✓ Resource add command working")
    else:
        print(f"   ✗ Resource add failed: {error}")
    
    # Test 3: Supply Checklists
    print("\n3. Testing Supply Checklists...")
    
    # Show all supplies
    return_code, output, error = run_cli_command("python cli.py supplies checklist")
    if return_code == 0:
        print("   ✓ Supplies checklist command working")
    else:
        print(f"   ✗ Supplies checklist failed: {error}")
    
    # Filter by category
    return_code, output, error = run_cli_command("python cli.py supplies checklist --category medical_supplies")
    if return_code == 0:
        print("   ✓ Supplies category filter working")
    else:
        print(f"   ✗ Supplies category filter failed: {error}")
    
    # Filter by priority
    return_code, output, error = run_cli_command("python cli.py supplies checklist --priority critical")
    if return_code == 0:
        print("   ✓ Supplies priority filter working")
    else:
        print(f"   ✗ Supplies priority filter failed: {error}")
    
    # Test 4: Emergency Contacts
    print("\n4. Testing Emergency Contacts...")
    
    # List contacts
    return_code, output, error = run_cli_command("python cli.py contacts list")
    if return_code == 0:
        print("   ✓ Contacts list command working")
    else:
        print(f"   ✗ Contacts list failed: {error}")
    
    # Filter contacts by type
    return_code, output, error = run_cli_command("python cli.py contacts list --type emergency")
    if return_code == 0:
        print("   ✓ Contacts type filter working")
    else:
        print(f"   ✗ Contacts type filter failed: {error}")
    
    # Test 5: Nearby Contacts (with coordinates)
    print("\n5. Testing Nearby Contacts...")
    
    # Test with coordinates (New York City area)
    return_code, output, error = run_cli_command(
        "python cli.py contacts nearby --latitude 40.7128 --longitude -74.0060 --radius 5"
    )
    if return_code == 0:
        print("   ✓ Nearby contacts with coordinates working")
    else:
        print(f"   ✗ Nearby contacts with coordinates failed: {error}")
    
    # Test 6: System Status
    print("\n6. Testing System Status...")
    
    return_code, output, error = run_cli_command("python cli.py status")
    if return_code == 0:
        print("   ✓ Status command working")
    else:
        print(f"   ✗ Status command failed: {error}")
    
    # Test 7: Help Commands
    print("\n7. Testing Help Commands...")
    
    # Main help
    return_code, output, error = run_cli_command("python cli.py --help")
    if return_code == 0:
        print("   ✓ Main help command working")
    else:
        print(f"   ✗ Main help command failed: {error}")
    
    # Resources help
    return_code, output, error = run_cli_command("python cli.py resources --help")
    if return_code == 0:
        print("   ✓ Resources help command working")
    else:
        print(f"   ✗ Resources help command failed: {error}")
    
    # Supplies help
    return_code, output, error = run_cli_command("python cli.py supplies --help")
    if return_code == 0:
        print("   ✓ Supplies help command working")
    else:
        print(f"   ✗ Supplies help command failed: {error}")
    
    # Contacts help
    return_code, output, error = run_cli_command("python cli.py contacts --help")
    if return_code == 0:
        print("   ✓ Contacts help command working")
    else:
        print(f"   ✗ Contacts help command failed: {error}")
    
    print("\n✅ CLI feature testing completed!")
    print("\n[bold]Available Commands:[/bold]")
    print("  python cli.py quick                    - Quick access menu")
    print("  python cli.py resources list           - List emergency resources")
    print("  python cli.py supplies checklist       - View supply checklists")
    print("  python cli.py contacts list            - List emergency contacts")
    print("  python cli.py contacts nearby          - Find nearby contacts")
    print("  python cli.py status                   - System status")
    print("\n[bold]Example Usage:[/bold]")
    print("  python cli.py resources list --available")
    print("  python cli.py supplies checklist --category medical_supplies")
    print("  python cli.py contacts nearby --address 'New York, NY' --radius 10")


if __name__ == '__main__':
    test_cli_features()
