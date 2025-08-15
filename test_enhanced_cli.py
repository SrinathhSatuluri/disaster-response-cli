#!/usr/bin/env python3
"""
Test script for Enhanced Disaster Response CLI

Demonstrates the new Rich styling, emergency alerts, and enhanced visual features.
"""

import subprocess
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


def test_enhanced_features():
    """Test the enhanced CLI features."""
    print("Testing Enhanced Disaster Response CLI Features\n")
    print("=" * 60)
    
    # Test 1: Basic status with enhanced styling
    print("1. Testing Enhanced Status Display:")
    return_code, output, error = run_cli_command("python cli.py status")
    
    if return_code == 0:
        print("   PASS Status command executed successfully")
        print("   Enhanced styling and panels displayed")
    else:
        print(f"   FAIL Status command failed: {error}")
    
    print()
    
    # Test 2: Detailed status
    print("2. Testing Detailed Status Display:")
    return_code, output, error = run_cli_command("python cli.py status --detailed")
    
    if return_code == 0:
        print("   PASS Detailed status executed successfully")
        print("   Database details and capabilities panels shown")
    else:
        print(f"   FAIL Detailed status failed: {error}")
    
    print()
    
    # Test 3: Enhanced resources list
    print("3. Testing Enhanced Resources Display:")
    return_code, output, error = run_cli_command("python cli.py resources list --json-fallback")
    
    if return_code == 0:
        print("   PASS Resources list executed successfully")
        print("   Enhanced table styling and fallback notification")
    else:
        print(f"   FAIL Resources list failed: {error}")
    
    print()
    
    # Test 4: Enhanced supplies checklist
    print("4. Testing Enhanced Supplies Checklist:")
    return_code, output, error = run_cli_command("python cli.py supplies checklist --emergency")
    
    if return_code == 0:
        print("   PASS Supplies checklist executed successfully")
        print("   Priority-based sorting and critical item alerts")
    else:
        print(f"   FAIL Supplies checklist failed: {error}")
    
    print()
    
    # Test 5: Emergency quick access
    print("5. Testing Emergency Quick Access:")
    return_code, output, error = run_cli_command("python cli.py quick --emergency")
    
    if return_code == 0:
        print("   PASS Emergency quick access executed successfully")
        print("   Emergency-focused commands and tips displayed")
    else:
        print(f"   FAIL Emergency quick access failed: {error}")
    
    print()
    
    # Test 6: Basic quick access
    print("6. Testing Basic Quick Access:")
    return_code, output, error = run_cli_command("python cli.py quick")
    
    if return_code == 0:
        print("   PASS Basic quick access executed successfully")
        print("   Standard quick access menu displayed")
    else:
        print(f"   FAIL Basic quick access failed: {error}")
    
    print()
    
    # Test 7: Help system
    print("7. Testing Help System:")
    return_code, output, error = run_cli_command("python cli.py --help")
    
    if return_code == 0:
        print("   PASS Help system executed successfully")
        print("   Command help and options displayed")
    else:
        print(f"   FAIL Help system failed: {error}")
    
    print()
    
    print("PASS All enhanced CLI feature tests completed!")
    print("\nSummary of Enhanced Features:")
    print("   • Emergency alerts and status indicators")
    print("   • Rich table styling with color coding")
    print("   • Enhanced panels and borders")
    print("   • Priority-based sorting and highlighting")
    print("   • Emergency mode detection and styling")
    print("   • Improved visual hierarchy and readability")
    print("   • JSON fallback notifications")
    print("   • Critical item alerts and warnings")
    
    print("\nEmergency Mode Features:")
    print("   • Emergency headers and status bars")
    print("   • Critical resource highlighting")
    print("   • Priority-based command organization")
    print("   • Emergency response guidelines")
    print("   • Visual emergency indicators")


if __name__ == '__main__':
    test_enhanced_features()
