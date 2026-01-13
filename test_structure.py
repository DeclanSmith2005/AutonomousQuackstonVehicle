"""
Simple tests to verify code structure and imports
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        # Test picarx imports
        from picarx import Picarx
        print("✓ PiCar-X modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_picarx_initialization():
    """Test PiCar-X initialization"""
    print("\nTesting PiCar-X initialization...")
    
    try:
        from picarx import Picarx
        car = Picarx()
        print("✓ PiCar-X initialized successfully")
        
        # Test basic methods
        car.set_dir_servo_angle(0)
        car.set_cam_tilt_angle(0)
        car.set_cam_pan_angle(0)
        car.stop()
        print("✓ Basic methods work")
        
        return True
    except Exception as e:
        print(f"✗ Initialization error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("ELEC 392 PiCar-X Code Structure Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_imports,
        test_picarx_initialization
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
