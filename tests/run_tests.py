import os
import sys
import pytest
from datetime import datetime

def run_tests():
    """Run all tests with coverage reporting."""
    # Add project root to Python path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    
    # Create coverage directory if it doesn't exist
    coverage_dir = os.path.join(os.path.dirname(__file__), 'coverage')
    if not os.path.exists(coverage_dir):
        os.makedirs(coverage_dir)
    
    # Generate timestamp for report filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = os.path.join(coverage_dir, f'coverage_report_{timestamp}.html')
    
    # Run pytest with coverage
    args = [
        '--cov=src',
        '--cov-report=html',
        '--cov-report=term-missing',
        f'--cov-report=html:{report_file}',
        'tests/unit',
        'tests/integration',
        'tests/ui'
    ]
    
    # Add any command line arguments
    args.extend(sys.argv[1:])
    
    # Run the tests
    result = pytest.main(args)
    
    # Print report location
    print(f"\nCoverage report generated at: {report_file}")
    
    return result

if __name__ == '__main__':
    sys.exit(run_tests()) 