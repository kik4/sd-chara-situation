#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for array value support in character definitions
"""

import os
import sys
import tempfile
import shutil

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

def test_array_values():
    """Test that character definitions can use array values"""

    # Create temporary directory for test data
    temp_dir = tempfile.mkdtemp()
    data_dir = os.path.join(temp_dir, 'data')
    os.makedirs(data_dir)

    try:
        # Create test character file with array values
        char_content = """alice:
  base: 1girl
  hair:
    - blonde hair
    - short hair
    - blue ribbon
  eye: blue eyes
  outfit:
    - blue dress
    - white apron
    - hairband
  body: medium breasts
"""
        with open(os.path.join(data_dir, 'test_chars.yaml'), 'w', encoding='utf-8') as f:
            f.write(char_content)

        # Create test situation with exclude
        sit_content = """casual:
  prompt: outdoors, street, sunny
  exclude:
    - outfit
"""
        with open(os.path.join(data_dir, 'test_sits.yaml'), 'w', encoding='utf-8') as f:
            f.write(sit_content)

        # Create script instance with custom data directory
        script = CharaSituationScript()
        script.data_dir = data_dir

        print("=" * 80)
        print("Testing Array Value Support in Character Definitions")
        print("=" * 80)

        # Test 1: Character with array values (no exclude)
        print("\nTest 1: Character with array values (no exclude)")
        prompt1 = "@test_chars:alice masterpiece"
        result1 = script.expand_prompt(prompt1, 12345)
        print(f"Input:  {prompt1}")
        print(f"Output: {result1}")

        # Check that array values are properly joined
        if "blonde hair, short hair, blue ribbon" in result1:
            print("  [PASS] hair array correctly joined with commas")
        else:
            print("  [FAIL] hair array not properly joined")
            print(f"        Expected 'blonde hair, short hair, blue ribbon' in output")

        if "blue dress, white apron, hairband" in result1:
            print("  [PASS] outfit array correctly joined with commas")
        else:
            print("  [FAIL] outfit array not properly joined")
            print(f"        Expected 'blue dress, white apron, hairband' in output")

        if "['blonde" not in result1 and "['" not in result1:
            print("  [PASS] No Python list representation in output")
        else:
            print("  [FAIL] Python list representation found in output")

        print("-" * 80)

        # Test 2: Character with array values (with exclude)
        print("\nTest 2: Character with array values + exclude situation")
        prompt2 = "@test_chars:alice @test_sits:casual masterpiece"
        result2 = script.expand_prompt(prompt2, 12345)
        print(f"Input:  {prompt2}")
        print(f"Output: {result2}")

        # Check that array values are properly joined
        if "blonde hair, short hair, blue ribbon" in result2:
            print("  [PASS] hair array correctly joined")
        else:
            print("  [FAIL] hair array not properly joined")

        # Check that outfit is excluded
        if "blue dress" not in result2 and "white apron" not in result2:
            print("  [PASS] outfit array correctly excluded")
        else:
            print("  [FAIL] outfit array not excluded")

        # Check that situation prompt is included
        if "outdoors" in result2:
            print("  [PASS] situation prompt included")
        else:
            print("  [FAIL] situation prompt not included")

        print("-" * 80)

        print("\n" + "=" * 80)
        print("Array Value Test Complete")
        print("=" * 80)

    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)

if __name__ == '__main__':
    test_array_values()
