#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for chara_situation expansion logic
"""

import os
import sys
import yaml
import random
import re

# Mock modules.scripts for standalone testing
class MockScript:
    pass

class MockScripts:
    AlwaysVisible = True
    Script = MockScript

sys.modules['modules'] = type(sys)('modules')
sys.modules['modules.scripts'] = MockScripts()

# Add scripts directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, 'scripts'))

from chara_situation import CharaSituationScript

def test_expansion():
    """Test prompt expansion with various inputs"""

    # Create script instance
    script = CharaSituationScript()

    # Test cases
    test_cases = [
        {
            'name': 'Basic character + situation',
            'prompt': '@characters:reimu @situations:beach masterpiece, best quality',
            'seed': 12345,
        },
        {
            'name': 'Character only',
            'prompt': '@characters:reimu masterpiece, best quality',
            'seed': 12345,
        },
        {
            'name': 'Random character + random situation',
            'prompt': '@characters:random @situations:random masterpiece, best quality',
            'seed': 12345,
        },
        {
            'name': 'Multiple situations (classroom)',
            'prompt': '@characters:marisa @situations:classroom masterpiece, best quality',
            'seed': 12345,
        },
    ]

    print("=" * 80)
    print("Testing Chara Situation Expansion")
    print("=" * 80)

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['name']}")
        print(f"Input:  {test['prompt']}")

        result = script.expand_prompt(test['prompt'], test['seed'])

        print(f"Output: {result}")
        print("-" * 80)

    # Verify exclude functionality
    print("\n" + "=" * 80)
    print("Verifying EXCLUDE functionality")
    print("=" * 80)

    # Test: beach should exclude top, bottom, shoes, accessory
    prompt = '@characters:reimu @situations:beach'
    result = script.expand_prompt(prompt, 12345)

    print(f"\nInput: {prompt}")
    print(f"Output: {result}")

    # Check that excluded items are NOT in the output
    excluded_items = ['white blouse', 'red vest', 'red hakama', 'brown boots', 'hair ribbon', 'detached sleeves', 'yellow ascot']
    included_items = ['1girl', 'black hair', 'hair tubes', 'red eyes', 'medium breasts', 'bikini', 'barefoot']

    print("\nExclude verification:")
    for item in excluded_items:
        if item in result:
            print(f"  [FAIL] '{item}' should be EXCLUDED but found in output")
        else:
            print(f"  [PASS] '{item}' correctly excluded")

    print("\nInclude verification:")
    for item in included_items:
        if item in result:
            print(f"  [PASS] '{item}' correctly included")
        else:
            print(f"  [FAIL] '{item}' should be INCLUDED but not found in output")

    print("\n" + "=" * 80)
    print("Test Complete")
    print("=" * 80)

if __name__ == '__main__':
    test_expansion()
