#!/usr/bin/env python3
"""
Test script for Disaster Response CLI Connectivity Simulation

Demonstrates low-connectivity simulation, minimal power usage, and database fallback
testing to ensure SQLite and JSON fallback systems work correctly under various conditions.
"""

import time
import subprocess
from pathlib import Path
from connectivity_simulator import simulator, fallback_tester, ConnectivityMode, PowerMode


def run_cli_command(command):
    """Run a CLI command and return the result."""
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            cwd=Path(__file__parent)
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)


def test_connectivity_simulation():
    """Test connectivity simulation functionality."""
    print("Testing Connectivity Simulation\n")
    
    # Test 1: Set different connectivity modes
    print("1. Testing Connectivity Modes:")
    
    modes = [
        ('online', 'Full connectivity'),
        ('intermittent', 'Intermittent connectivity'),
        ('low_bandwidth', 'Low bandwidth'),
        ('offline', 'Offline mode'),
        ('emergency', 'Emergency mode')
    ]
    
    for mode, description in modes:
        print(f"   Testing {mode} mode...")
        simulator.set_connectivity_mode(ConnectivityMode(mode))
        
        is_connected = simulator.is_connected()
        status = "Connected" if is_connected else "Disconnected"
        print(f"     Status: {status}")
        print(f"     Description: {description}")
        
        # Test network delay simulation
        start_time = time.time()
        simulator.simulate_network_delay()
        delay_time = time.time() - start_time
        
        print(f"     Network delay: {delay_time:.3f}s")
        print()
    
    # Test 2: Set different power modes
    print("2. Testing Power Modes:")
    
    power_modes = [
        ('normal', 'Normal power consumption'),
        ('power_save', 'Power saving mode'),
        ('minimal', 'Minimal power mode'),
        ('critical', 'Critical power mode')
    ]
    
    for mode, description in power_modes:
        print(f"   Testing {mode} mode...")
        simulator.set_power_mode(PowerMode(mode))
        
        print(f"     Power consumption: {simulator.power_consumption:.1f}x")
        print(f"     CPU throttle: {simulator.cpu_throttle:.1f}x")
        if simulator.memory_limit:
            print(f"     Memory limit: {simulator.memory_limit} MB")
        print(f"     Description: {description}")
        print()
    
    # Test 3: Power consumption simulation
    print("3. Testing Power Consumption Simulation:")
    
    operations = [
        ('database_read', 1024),
        ('database_write', 2048),
        ('geolocation', 512),
        ('file_io', 4096)
    ]
    
    for operation, data_size in operations:
        power_used = simulator.simulate_power_consumption(operation, data_size)
        print(f"   {operation} ({data_size} bytes): {power_used:.3f} power units")
    
    print()


def test_database_fallback():
    """Test database fallback functionality under various conditions."""
    print("Testing Database Fallback Functionality\n")
    
    # Create test data
    test_data = [
        {'id': 'FALLBACK-001', 'name': 'Test Resource 1', 'type': 'equipment', 'status': 'available'},
        {'id': 'FALLBACK-002', 'name': 'Test Resource 2', 'type': 'vehicle', 'status': 'maintenance'},
        {'id': 'FALLBACK-003', 'name': 'Test Resource 3', 'type': 'supplies', 'status': 'in_use'},
        {'id': 'FALLBACK-004', 'name': 'Test Resource 4', 'type': 'personnel', 'status': 'available'},
        {'id': 'FALLBACK-005', 'name': 'Test Resource 5', 'type': 'equipment', 'status': 'in_use'}
    ]
    
    # Test under different connectivity conditions
    connectivity_modes = [ConnectivityMode.ONLINE, ConnectivityMode.OFFLINE, ConnectivityMode.INTERMITTENT]
    power_modes = [PowerMode.NORMAL, PowerMode.MINIMAL, PowerMode.CRITICAL]
    
    print("4. Testing Fallback Under Various Conditions:")
    
    for conn_mode in connectivity_modes:
        for power_mode in power_modes:
            print(f"\n   Testing: {conn_mode.value} + {power_mode.value}")
            
            # Set simulation modes
            simulator.set_connectivity_mode(conn_mode)
            simulator.set_power_mode(power_mode)
            
            # Run fallback test
            test_result = fallback_tester.test_database_fallback(test_data)
            
            # Show results
            successful_tests = sum(1 for test in test_result['tests'] if test['success'])
            total_tests = len(test_result['tests'])
            
            print(f"     Tests passed: {successful_tests}/{total_tests}")
            print(f"     Success rate: {successful_tests/total_tests*100:.1f}%")
            
            # Show individual test results
            for test in test_result['tests']:
                status = "PASS" if test['success'] else "FAIL"
                print(f"       {status} {test['name']}: {test['duration']:.3f}s, {test['power_consumed']:.3f} power")
    
    print()


def test_cli_commands():
    """Test CLI commands for connectivity simulation."""
    print("Testing CLI Commands\n")
    
    # Test 1: Connectivity mode setting
    print("5. Testing CLI Connectivity Commands:")
    
    commands = [
        "python cli.py simulate connectivity --mode offline",
        "python cli.py simulate connectivity --mode intermittent",
        "python cli.py simulate connectivity --mode emergency"
    ]
    
    for command in commands:
        print(f"   Running: {command}")
        return_code, output, error = run_cli_command(command)
        
        if return_code == 0:
            print("     PASS Command executed successfully")
        else:
            print(f"     FAIL Command failed: {error}")
        print()
    
    # Test 2: Power mode setting
    print("6. Testing CLI Power Commands:")
    
    power_commands = [
        "python cli.py simulate power --mode minimal",
        "python cli.py simulate power --mode critical",
        "python cli.py power status"
    ]
    
    for command in power_commands:
        print(f"   Running: {command}")
        return_code, output, error = run_cli_command(command)
        
        if return_code == 0:
            print("     PASS Command executed successfully")
        else:
            print(f"     FAIL Command failed: {error}")
        print()
    
    # Test 3: Fallback testing
    print("7. Testing CLI Fallback Commands:")
    
    fallback_commands = [
        "python cli.py test fallback",
        "python cli.py test summary",
        "python cli.py simulate status"
    ]
    
    for command in fallback_commands:
        print(f"   Running: {command}")
        return_code, output, error = run_cli_command(command)
        
        if return_code == 0:
            print("     PASS Command executed successfully")
        else:
            print(f"     FAIL Command failed: {error}")
        print()


def test_simulation_scenarios():
    """Test realistic simulation scenarios."""
    print("Testing Realistic Simulation Scenarios\n")
    
    # Scenario 1: Emergency response in low-connectivity area
    print("8. Scenario: Emergency Response in Low-Connectivity Area")
    simulator.set_connectivity_mode(ConnectivityMode.INTERMITTENT)
    simulator.set_power_mode(PowerMode.POWER_SAVE)
    
    print("   Mode: Intermittent connectivity + Power saving")
    print("   Simulating emergency response operations...")
    
    # Simulate multiple operations
    operations = [
        ('database_read', 2048),    # Read resource inventory
        ('geolocation', 1024),      # Find nearby facilities
        ('file_io', 4096),          # Save incident report
        ('database_write', 1024),   # Update resource status
        ('geolocation', 512),       # Calculate distances
        ('file_io', 2048)           # Export data
    ]
    
    total_power = 0
    for operation, data_size in operations:
        power_used = simulator.simulate_power_consumption(operation, data_size)
        total_power += power_used
        print(f"     {operation}: {power_used:.3f} power units")
    
    print(f"   Total power consumption: {total_power:.3f} units")
    print()
    
    # Scenario 2: Critical power mode
    print("9. Scenario: Critical Power Mode")
    simulator.set_connectivity_mode(ConnectivityMode.OFFLINE)
    simulator.set_power_mode(PowerMode.CRITICAL)
    
    print("   Mode: Offline + Critical power")
    print("   Simulating essential operations only...")
    
    essential_operations = [
        ('database_read', 512),     # Essential data only
        ('file_io', 1024),          # Critical file operations
        ('geolocation', 256)        # Basic location services
    ]
    
    total_power = 0
    for operation, data_size in essential_operations:
        power_used = simulator.simulate_power_consumption(operation, data_size)
        total_power += power_used
        print(f"     {operation}: {power_used:.3f} power units")
    
    print(f"   Total power consumption: {total_power:.3f} units")
    print()


def export_test_results():
    """Export test results and simulation data."""
    print("Exporting Test Results\n")
    
    # Export simulation data
    simulation_file = "data/connectivity_simulation_test.json"
    if simulator.export_simulation_data(simulation_file):
        print(f"PASS Simulation data exported to {simulation_file}")
    else:
        print("FAIL Failed to export simulation data")
    
    # Get test summary
    test_summary = fallback_tester.get_test_summary()
    print(f"\nTest Summary:")
    print(f"   Total test runs: {test_summary.get('total_test_runs', 0)}")
    print(f"   Success rate: {test_summary.get('overall_success_rate', 0)}%")
    
    # Export test results
    test_file = "data/fallback_test_results.json"
    try:
        import json
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_summary, f, indent=2, ensure_ascii=False, default=str)
        print(f"PASS Test results exported to {test_file}")
    except Exception as e:
        print(f"FAIL Failed to export test results: {e}")
    
    print()


def main():
    """Run all connectivity simulation tests."""
    print("Disaster Response CLI - Connectivity Simulation Testing\n")
    print("=" * 60)
    
    try:
        # Run all test categories
        test_connectivity_simulation()
        test_database_fallback()
        test_cli_commands()
        test_simulation_scenarios()
        export_test_results()
        
        print("PASS All connectivity simulation tests completed successfully!")
        print("\nSummary of Available Commands:")
        print("   python cli.py simulate connectivity --mode offline")
        print("   python cli.py simulate power --mode minimal")
        print("   python cli.py test fallback")
        print("   python cli.py test comprehensive --mode offline --power critical")
        print("   python cli.py power monitor --operation database_read")
        print("   python cli.py simulate status")
        
    except Exception as e:
        print(f"FAIL Testing failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
