#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for subdirectory support
"""

import os
import sys

# Mock modules.scripts for standalone testing
class MockScript:
    pass

class MockScripts:
    AlwaysVisible = True
    Script = MockScript

sys.modules['modules'] = type(sys)('modules')
sys.modules['modules.scripts'] = MockScripts()

# Add scripts directory to path
test_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(test_dir)
sys.path.insert(0, os.path.join(project_dir, 'scripts'))

from chara_situation import CharaSituationScript

def test_subdirectory_support():
    """Test that YAML files in subdirectories can be loaded"""

    # Create script instance
    script = CharaSituationScript()

    # Test cases with subdirectory paths
    test_cases = [
        {
            'name': 'Subdirectory with slash',
            'prompt': '@characters/touhou:reimu test',
            'seed': 12345,
        },
    ]

    print("=" * 80)
    print("Testing Subdirectory Support")
    print("=" * 80)

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['name']}")
        print(f"Input:  {test['prompt']}")

        result = script.expand_prompt(test['prompt'], test['seed'])

        print(f"Output: {result}")

        if '1girl' in result and 'black hair' in result:
            print(f"  [PASS] Subdirectory file loaded successfully")
        else:
            print(f"  [FAIL] Subdirectory file not loaded")

        print("-" * 80)

    print("\n" + "=" * 80)
    print("Subdirectory Test Complete")
    print("=" * 80)

if __name__ == '__main__':
    test_subdirectory_support()
