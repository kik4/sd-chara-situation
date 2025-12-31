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

def test_include_functionality():
    """Test include functionality"""
    import tempfile
    import shutil

    print("\n" + "=" * 80)
    print("Testing INCLUDE functionality")
    print("=" * 80)

    # Create script instance
    script = CharaSituationScript()

    # Backup original data directory
    original_data_dir = script.data_dir
    temp_dir = tempfile.mkdtemp()

    try:
        # Set temporary data directory
        script.data_dir = temp_dir

        # Create test characters.yaml
        chars_content = """reimu:
  base: 1girl
  hair: black hair, hair tubes
  eye: red eyes
  top: white blouse, red vest
  bottom: red hakama
  body: medium breasts
"""
        with open(os.path.join(temp_dir, 'characters.yaml'), 'w', encoding='utf-8') as f:
            f.write(chars_content)

        # Create test situations.yaml with include
        sits_content = """silhouette:
  prompt: silhouette, backlight, dramatic lighting
  include:
    - base
    - body
"""
        with open(os.path.join(temp_dir, 'situations.yaml'), 'w', encoding='utf-8') as f:
            f.write(sits_content)

        # Test include functionality
        prompt = '@characters:reimu @situations:silhouette'
        result = script.expand_prompt(prompt, 12345)

        print(f"\nInput: {prompt}")
        print(f"Output: {result}")

        # Check that only included items are in the output
        included_items = ['1girl', 'medium breasts']
        excluded_items = ['black hair', 'hair tubes', 'red eyes', 'white blouse', 'red vest', 'red hakama']

        print("\nInclude verification (only base and body should be included):")
        for item in included_items:
            if item in result:
                print(f"  [PASS] '{item}' correctly included")
            else:
                print(f"  [FAIL] '{item}' should be INCLUDED but not found")

        print("\nExclude verification (other elements should be excluded):")
        for item in excluded_items:
            if item in result:
                print(f"  [FAIL] '{item}' should be EXCLUDED but found in output")
            else:
                print(f"  [PASS] '{item}' correctly excluded")

        # Test that silhouette prompt is included
        if 'silhouette' in result and 'backlight' in result:
            print(f"\n  [PASS] Situation prompt correctly included")
        else:
            print(f"\n  [FAIL] Situation prompt not found")

    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        script.data_dir = original_data_dir

    print("\n" + "=" * 80)
    print("Include Test Complete")
    print("=" * 80)

def test_mixed_include_exclude_error():
    """Test that mixing include and exclude produces an error"""
    import tempfile
    import shutil

    print("\n" + "=" * 80)
    print("Testing MIXED INCLUDE/EXCLUDE error detection")
    print("=" * 80)

    # Create script instance
    script = CharaSituationScript()

    # Backup original data directory
    original_data_dir = script.data_dir
    temp_dir = tempfile.mkdtemp()

    try:
        # Set temporary data directory
        script.data_dir = temp_dir

        # Create test characters.yaml
        chars_content = """reimu:
  base: 1girl
  hair: black hair
  body: medium breasts
"""
        with open(os.path.join(temp_dir, 'characters.yaml'), 'w', encoding='utf-8') as f:
            f.write(chars_content)

        # Create test sits1.yaml with exclude
        sits1_content = """beach:
  prompt: beach scene
  exclude:
    - hair
"""
        with open(os.path.join(temp_dir, 'sits1.yaml'), 'w', encoding='utf-8') as f:
            f.write(sits1_content)

        # Create test sits2.yaml with include
        sits2_content = """silhouette:
  prompt: silhouette
  include:
    - base
"""
        with open(os.path.join(temp_dir, 'sits2.yaml'), 'w', encoding='utf-8') as f:
            f.write(sits2_content)

        # Test mixed include/exclude (should produce error)
        prompt = '@characters:reimu @sits1:beach @sits2:silhouette'
        result = script.expand_prompt(prompt, 12345)

        print(f"\nInput: {prompt}")
        print(f"Output: {result}")

        # Check that the prompt was NOT expanded (error case)
        if result == prompt:
            print(f"\n  [PASS] Mixed include/exclude correctly rejected (prompt unchanged)")
        else:
            print(f"\n  [FAIL] Mixed include/exclude should have been rejected")

    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        script.data_dir = original_data_dir

    print("\n" + "=" * 80)
    print("Mixed Include/Exclude Test Complete")
    print("=" * 80)

if __name__ == '__main__':
    test_expansion()
    test_include_functionality()
    test_mixed_include_exclude_error()
