#!/usr/bin/env python3
"""
Connectivity Simulator for Disaster Response CLI Tool

Simulates various connectivity and power scenarios to test offline functionality
and ensure SQLite/JSON fallback systems work correctly.
"""

import time
import random
import threading
from typing import Dict, List, Optional, Callable
from enum import Enum
import logging
from pathlib import Path
import json
import sqlite3
from datetime import datetime, timedelta


class ConnectivityMode(Enum):
    """Different connectivity simulation modes."""
    ONLINE = "online"           # Full connectivity
    INTERMITTENT = "intermittent"  # Intermittent connectivity
    LOW_BANDWIDTH = "low_bandwidth"  # Slow, limited connectivity
    OFFLINE = "offline"         # No connectivity
    EMERGENCY = "emergency"     # Emergency mode (minimal power)


class PowerMode(Enum):
    """Different power usage modes."""
    NORMAL = "normal"           # Normal power consumption
    POWER_SAVE = "power_save"   # Reduced power usage
    MINIMAL = "minimal"         # Minimal power usage
    CRITICAL = "critical"       # Critical power mode


class ConnectivitySimulator:
    """Simulates various connectivity and power scenarios."""
    
    def __init__(self):
        self.current_mode = ConnectivityMode.ONLINE
        self.power_mode = PowerMode.NORMAL
        self.simulation_active = False
        self.logger = logging.getLogger(__name__)
        
        # Connectivity simulation parameters
        self.connection_stability = 1.0  # 0.0 = always offline, 1.0 = always online
        self.bandwidth_limit = float('inf')  # bytes per second
        self.latency_ms = 0  # artificial latency in milliseconds
        
        # Power simulation parameters
        self.power_consumption = 1.0  # multiplier for power usage
        self.cpu_throttle = 1.0  # CPU performance multiplier
        self.memory_limit = None  # memory usage limit in MB
        
        # Simulation state
        self.simulation_thread = None
        self.connection_history = []
        self.power_history = []
        
        # Callbacks for mode changes
        self.mode_change_callbacks: List[Callable] = []
        
    def add_mode_change_callback(self, callback: Callable):
        """Add a callback function to be called when modes change."""
        self.mode_change_callbacks.append(callback)
    
    def _notify_mode_change(self):
        """Notify all registered callbacks of mode changes."""
        for callback in self.mode_change_callbacks:
            try:
                callback(self.current_mode, self.power_mode)
            except Exception as e:
                self.logger.error(f"Error in mode change callback: {e}")
    
    def set_connectivity_mode(self, mode: ConnectivityMode):
        """Set the current connectivity mode."""
        old_mode = self.current_mode
        self.current_mode = mode
        
        # Apply mode-specific settings
        if mode == ConnectivityMode.ONLINE:
            self.connection_stability = 1.0
            self.bandwidth_limit = float('inf')
            self.latency_ms = 0
        elif mode == ConnectivityMode.INTERMITTENT:
            self.connection_stability = 0.7
            self.bandwidth_limit = 1024 * 1024  # 1 MB/s
            self.latency_ms = 100
        elif mode == ConnectivityMode.LOW_BANDWIDTH:
            self.connection_stability = 0.9
            self.bandwidth_limit = 64 * 1024  # 64 KB/s
            self.latency_ms = 500
        elif mode == ConnectivityMode.OFFLINE:
            self.connection_stability = 0.0
            self.bandwidth_limit = 0
            self.latency_ms = 0
        elif mode == ConnectivityMode.EMERGENCY:
            self.connection_stability = 0.1
            self.bandwidth_limit = 16 * 1024  # 16 KB/s
            self.latency_ms = 1000
        
        if old_mode != mode:
            self.logger.info(f"Connectivity mode changed from {old_mode.value} to {mode.value}")
            self._notify_mode_change()
    
    def set_power_mode(self, mode: PowerMode):
        """Set the current power mode."""
        old_mode = self.power_mode
        self.power_mode = mode
        
        # Apply mode-specific settings
        if mode == PowerMode.NORMAL:
            self.power_consumption = 1.0
            self.cpu_throttle = 1.0
            self.memory_limit = None
        elif mode == PowerMode.POWER_SAVE:
            self.power_consumption = 0.7
            self.cpu_throttle = 0.8
            self.memory_limit = 512  # 512 MB
        elif mode == PowerMode.MINIMAL:
            self.power_consumption = 0.4
            self.cpu_throttle = 0.5
            self.memory_limit = 256  # 256 MB
        elif mode == PowerMode.CRITICAL:
            self.power_consumption = 0.2
            self.cpu_throttle = 0.3
            self.memory_limit = 128  # 128 MB
        
        if old_mode != mode:
            self.logger.info(f"Power mode changed from {old_mode.value} to {mode.value}")
            self._notify_mode_change()
    
    def is_connected(self) -> bool:
        """Check if currently connected based on simulation settings."""
        if self.current_mode == ConnectivityMode.OFFLINE:
            return False
        
        # Simulate intermittent connectivity
        if self.current_mode == ConnectivityMode.INTERMITTENT:
            return random.random() < self.connection_stability
        
        return True
    
    def simulate_network_delay(self):
        """Simulate network latency and bandwidth limitations."""
        if self.latency_ms > 0:
            time.sleep(self.latency_ms / 1000.0)
        
        if self.bandwidth_limit < float('inf'):
            # Simulate bandwidth throttling
            time.sleep(0.1)  # Small delay to simulate slow connection
    
    def simulate_power_consumption(self, operation: str, data_size: int = 0):
        """Simulate power consumption for operations."""
        base_consumption = 1.0
        
        # Adjust based on operation type
        if operation == "database_read":
            base_consumption = 0.5
        elif operation == "database_write":
            base_consumption = 1.2
        elif operation == "geolocation":
            base_consumption = 0.8
        elif operation == "file_io":
            base_consumption = 0.6
        
        # Adjust based on data size
        if data_size > 0:
            size_factor = min(data_size / (1024 * 1024), 2.0)  # Cap at 2x for large files
            base_consumption *= (1.0 + size_factor * 0.1)
        
        # Apply power mode multiplier
        adjusted_consumption = base_consumption * self.power_consumption
        
        # Record power usage
        self.power_history.append({
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'consumption': adjusted_consumption,
            'mode': self.power_mode.value
        })
        
        # Simulate CPU throttling
        if self.cpu_throttle < 1.0:
            time.sleep(0.01 * (1.0 - self.cpu_throttle))
        
        return adjusted_consumption
    
    def start_simulation(self, duration_minutes: int = 10):
        """Start a connectivity simulation for a specified duration."""
        if self.simulation_active:
            self.logger.warning("Simulation already active")
            return
        
        self.simulation_active = True
        self.simulation_thread = threading.Thread(
            target=self._run_simulation,
            args=(duration_minutes,),
            daemon=True
        )
        self.simulation_thread.start()
        self.logger.info(f"Started connectivity simulation for {duration_minutes} minutes")
    
    def stop_simulation(self):
        """Stop the current simulation."""
        self.simulation_active = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=1.0)
        self.logger.info("Stopped connectivity simulation")
    
    def _run_simulation(self, duration_minutes: int):
        """Run the connectivity simulation."""
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        
        while self.simulation_active and datetime.now() < end_time:
            # Simulate connectivity changes
            if self.current_mode == ConnectivityMode.INTERMITTENT:
                # Randomly change connection status
                if random.random() < 0.1:  # 10% chance of status change
                    self.connection_stability = max(0.1, min(0.9, 
                        self.connection_stability + random.uniform(-0.2, 0.2)))
            
            # Record connection status
            self.connection_history.append({
                'timestamp': datetime.now().isoformat(),
                'mode': self.current_mode.value,
                'connected': self.is_connected(),
                'stability': self.connection_stability,
                'bandwidth': self.bandwidth_limit,
                'latency': self.latency_ms
            })
            
            time.sleep(30)  # Update every 30 seconds
    
    def get_simulation_stats(self) -> Dict:
        """Get statistics about the current simulation."""
        total_operations = len(self.power_history)
        avg_power_consumption = sum(h['consumption'] for h in self.power_history) / total_operations if total_operations > 0 else 0
        
        connection_uptime = sum(1 for h in self.connection_history if h['connected']) / len(self.connection_history) if self.connection_history else 0
        
        return {
            'current_mode': self.current_mode.value,
            'power_mode': self.power_mode.value,
            'total_operations': total_operations,
            'average_power_consumption': round(avg_power_consumption, 3),
            'connection_uptime': round(connection_uptime * 100, 1),
            'simulation_active': self.simulation_active,
            'power_history_count': len(self.power_history),
            'connection_history_count': len(self.connection_history)
        }
    
    def export_simulation_data(self, output_path: str):
        """Export simulation data to JSON file."""
        data = {
            'exported_at': datetime.now().isoformat(),
            'simulation_stats': self.get_simulation_stats(),
            'power_history': self.power_history,
            'connection_history': self.connection_history
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            self.logger.info(f"Simulation data exported to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export simulation data: {e}")
            return False


class DatabaseFallbackTester:
    """Tests SQLite and JSON fallback functionality under various conditions."""
    
    def __init__(self, connectivity_simulator: ConnectivitySimulator):
        self.simulator = connectivity_simulator
        self.logger = logging.getLogger(__name__)
        self.test_results = []
        
    def test_database_fallback(self, test_data: List[Dict]) -> Dict:
        """Test database fallback functionality."""
        test_result = {
            'timestamp': datetime.now().isoformat(),
            'connectivity_mode': self.simulator.current_mode.value,
            'power_mode': self.simulator.power_mode.value,
            'tests': []
        }
        
        # Test 1: SQLite availability
        sqlite_test = self._test_sqlite_availability()
        test_result['tests'].append(sqlite_test)
        
        # Test 2: JSON fallback functionality
        json_test = self._test_json_fallback(test_data)
        test_result['tests'].append(json_test)
        
        # Test 3: Data consistency
        consistency_test = self._test_data_consistency(test_data)
        test_result['tests'].append(consistency_test)
        
        # Test 4: Performance under current conditions
        performance_test = self._test_performance(test_data)
        test_result['tests'].append(performance_test)
        
        self.test_results.append(test_result)
        return test_result
    
    def _test_sqlite_availability(self) -> Dict:
        """Test if SQLite is available and working."""
        test_name = "SQLite Availability"
        start_time = time.time()
        
        try:
            # Test basic SQLite functionality
            conn = sqlite3.connect(':memory:')
            conn.execute('CREATE TABLE test (id INTEGER, name TEXT)')
            conn.execute('INSERT INTO test VALUES (1, "test")')
            result = conn.execute('SELECT * FROM test').fetchone()
            conn.close()
            
            success = result == (1, "test")
            duration = time.time() - start_time
            
            # Simulate power consumption
            power_used = self.simulator.simulate_power_consumption("database_test", 1024)
            
            return {
                'name': test_name,
                'success': success,
                'duration': round(duration, 3),
                'power_consumed': round(power_used, 3),
                'error': None
            }
            
        except Exception as e:
            duration = time.time() - start_time
            return {
                'name': test_name,
                'success': False,
                'duration': round(duration, 3),
                'power_consumed': 0,
                'error': str(e)
            }
    
    def _test_json_fallback(self, test_data: List[Dict]) -> Dict:
        """Test JSON fallback functionality."""
        test_name = "JSON Fallback"
        start_time = time.time()
        
        try:
            # Test JSON read/write
            test_file = "data/test_fallback.json"
            Path(test_file).parent.mkdir(parents=True, exist_ok=True)
            
            # Write test data
            with open(test_file, 'w', encoding='utf-8') as f:
                json.dump({'test_data': test_data, 'timestamp': datetime.now().isoformat()}, f, indent=2)
            
            # Read test data
            with open(test_file, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            
            # Clean up
            Path(test_file).unlink(missing_ok=True)
            
            success = loaded_data['test_data'] == test_data
            duration = time.time() - start_time
            
            # Simulate power consumption
            data_size = len(json.dumps(test_data).encode('utf-8'))
            power_used = self.simulator.simulate_power_consumption("file_io", data_size)
            
            return {
                'name': test_name,
                'success': success,
                'duration': round(duration, 3),
                'power_consumed': round(power_used, 3),
                'error': None
            }
            
        except Exception as e:
            duration = time.time() - start_time
            return {
                'name': test_name,
                'success': False,
                'duration': round(duration, 3),
                'power_consumed': 0,
                'error': str(e)
            }
    
    def _test_data_consistency(self, test_data: List[Dict]) -> Dict:
        """Test data consistency between operations."""
        test_name = "Data Consistency"
        start_time = time.time()
        
        try:
            # Test data integrity
            original_count = len(test_data)
            original_hash = hash(str(sorted(test_data, key=lambda x: x.get('id', ''))))
            
            # Simulate some operations
            modified_data = test_data.copy()
            if modified_data:
                modified_data[0]['test_flag'] = True
            
            # Verify data integrity
            count_consistent = len(modified_data) == original_count + 1
            hash_consistent = hash(str(sorted(test_data, key=lambda x: x.get('id', '')))) == original_hash
            
            success = count_consistent and hash_consistent
            duration = time.time() - start_time
            
            # Simulate power consumption
            power_used = self.simulator.simulate_power_consumption("data_consistency", len(test_data) * 100)
            
            return {
                'name': test_name,
                'success': success,
                'duration': round(duration, 3),
                'power_consumed': round(power_used, 3),
                'error': None,
                'details': {
                    'count_consistent': count_consistent,
                    'hash_consistent': hash_consistent
                }
            }
            
        except Exception as e:
            duration = time.time() - start_time
            return {
                'name': test_name,
                'success': False,
                'duration': round(duration, 3),
                'power_consumed': 0,
                'error': str(e)
            }
    
    def _test_performance(self, test_data: List[Dict]) -> Dict:
        """Test performance under current conditions."""
        test_name = "Performance Test"
        start_time = time.time()
        
        try:
            # Simulate network delay if applicable
            self.simulator.simulate_network_delay()
            
            # Test operation speed
            operations = 0
            for _ in range(min(100, len(test_data))):  # Limit to 100 operations
                operations += 1
                # Simulate some work
                time.sleep(0.001 * (1.0 / self.simulator.cpu_throttle))
            
            duration = time.time() - start_time
            operations_per_second = operations / duration if duration > 0 else 0
            
            # Simulate power consumption
            power_used = self.simulator.simulate_power_consumption("performance_test", operations * 50)
            
            return {
                'name': test_name,
                'success': True,
                'duration': round(duration, 3),
                'operations_per_second': round(operations_per_second, 2),
                'power_consumed': round(power_used, 3),
                'error': None
            }
            
        except Exception as e:
            duration = time.time() - start_time
            return {
                'name': test_name,
                'success': False,
                'duration': round(duration, 3),
                'power_consumed': 0,
                'error': str(e)
            }
    
    def get_test_summary(self) -> Dict:
        """Get a summary of all test results."""
        if not self.test_results:
            return {'message': 'No tests have been run yet'}
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results 
                             if all(test['success'] for test in result['tests']))
        
        all_individual_tests = []
        for result in self.test_results:
            all_individual_tests.extend(result['tests'])
        
        individual_success_rate = sum(1 for test in all_individual_tests if test['success']) / len(all_individual_tests) if all_individual_tests else 0
        
        return {
            'total_test_runs': total_tests,
            'successful_test_runs': successful_tests,
            'overall_success_rate': round(successful_tests / total_tests * 100, 1),
            'individual_test_success_rate': round(individual_success_rate * 100, 1),
            'latest_test': self.test_results[-1] if self.test_results else None
        }


# Global simulator instance
simulator = ConnectivitySimulator()
fallback_tester = DatabaseFallbackTester(simulator)
