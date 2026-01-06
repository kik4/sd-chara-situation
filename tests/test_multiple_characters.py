#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for multiple characters expansion
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
test_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(test_dir)
sys.path.insert(0, os.path.join(project_dir, 'scripts'))

from chara_situation import CharaSituationScript

def test_multiple_characters_with_situation():
    """Test multiple characters with a situation"""
    print("=" * 80)
    print("Testing Multiple Characters with Situation")
    print("=" * 80)

    script = CharaSituationScript()

    # Test case 1: Two characters with beach situation
    prompt = '@characters:reimu @characters:marisa @situations:beach masterpiece, best quality'
    result = script.expand_prompt(prompt, 12345)

    print(f"\nTest 1: Two characters at the beach")
    print(f"Input:  {prompt}")
    print(f"Output: {result}")

    # Verify that both characters' base elements are included
    reimu_base_items = ['1girl', 'black hair', 'hair tubes', 'red eyes', 'medium breasts']
    marisa_base_items = ['blonde hair', 'long hair', 'yellow eyes', 'small breasts']

    # Verify that excluded items are NOT present
    excluded_items = [
        'white blouse', 'red vest',  # reimu's top
        'red hakama',  # reimu's bottom
        'brown boots',  # reimu's shoes
        'hair ribbon', 'detached sleeves', 'yellow ascot',  # reimu's accessories
        'white shirt', 'black vest',  # marisa's top
        'black skirt',  # marisa's bottom
        'black boots',  # marisa's shoes
        'witch hat', 'mini-hakkero'  # marisa's accessories
    ]

    # Verify situation prompt is included
    situation_items = ['bikini', 'barefoot', 'beach', 'ocean']

    print("\n--- Reimu's base elements verification ---")
    for item in reimu_base_items:
        if item in result:
            print(f"  [PASS] '{item}' correctly included")
        else:
            print(f"  [FAIL] '{item}' should be INCLUDED")

    print("\n--- Marisa's base elements verification ---")
    for item in marisa_base_items:
        if item in result:
            print(f"  [PASS] '{item}' correctly included")
        else:
            print(f"  [FAIL] '{item}' should be INCLUDED")

    print("\n--- Excluded items verification (both characters) ---")
    fail_count = 0
    for item in excluded_items:
        if item in result:
            print(f"  [FAIL] '{item}' should be EXCLUDED but found")
            fail_count += 1
        else:
            print(f"  [PASS] '{item}' correctly excluded")

    if fail_count == 0:
        print(f"\n  [OK] All clothing items correctly excluded from both characters")

    print("\n--- Situation elements verification ---")
    for item in situation_items:
        if item in result:
            print(f"  [PASS] '{item}' correctly included")
        else:
            print(f"  [FAIL] '{item}' should be INCLUDED")

    print("-" * 80)

def test_multiple_characters_without_situation():
    """Test multiple characters without situation"""
    print("\n" + "=" * 80)
    print("Testing Multiple Characters WITHOUT Situation")
    print("=" * 80)

    script = CharaSituationScript()

    prompt = '@characters:reimu @characters:marisa masterpiece, best quality'
    result = script.expand_prompt(prompt, 12345)

    print(f"\nTest 2: Two characters without situation")
    print(f"Input:  {prompt}")
    print(f"Output: {result}")

    # Without situation, all elements should be included
    reimu_items = ['1girl', 'black hair', 'hair tubes', 'red eyes', 'white blouse', 'red vest',
                   'red hakama', 'brown boots', 'hair ribbon', 'detached sleeves', 'yellow ascot',
                   'medium breasts']
    marisa_items = ['blonde hair', 'long hair', 'braid', 'side braid', 'yellow eyes',
                    'white shirt', 'black vest', 'black skirt', 'black boots',
                    'witch hat', 'mini-hakkero', 'small breasts']

    print("\n--- Reimu's full elements verification ---")
    for item in reimu_items:
        if item in result:
            print(f"  [PASS] '{item}' correctly included")
        else:
            print(f"  [FAIL] '{item}' should be INCLUDED")

    print("\n--- Marisa's full elements verification ---")
    for item in marisa_items:
        if item in result:
            print(f"  [PASS] '{item}' correctly included")
        else:
            print(f"  [FAIL] '{item}' should be INCLUDED")

    print("-" * 80)

def test_multiple_characters_with_include():
    """Test multiple characters with include-based situation"""
    import tempfile
    import shutil

    print("\n" + "=" * 80)
    print("Testing Multiple Characters with INCLUDE-based Situation")
    print("=" * 80)

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

marisa:
  base: 1girl
  hair: blonde hair, long hair
  eye: yellow eyes
  top: white shirt, black vest
  bottom: black skirt
  body: small breasts
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

        # Test include functionality with multiple characters
        prompt = '@characters:reimu @characters:marisa @situations:silhouette'
        result = script.expand_prompt(prompt, 12345)

        print(f"\nTest 3: Two characters with include-based situation")
        print(f"Input:  {prompt}")
        print(f"Output: {result}")

        # Only base and body should be included for both characters
        included_items = ['1girl', 'medium breasts', 'small breasts', 'silhouette', 'backlight']
        excluded_items = ['black hair', 'hair tubes', 'blonde hair', 'long hair',
                         'red eyes', 'yellow eyes', 'white blouse', 'red vest',
                         'white shirt', 'black vest', 'red hakama', 'black skirt']

        print("\n--- Include verification (only base and body) ---")
        for item in included_items:
            if item in result:
                print(f"  [PASS] '{item}' correctly included")
            else:
                print(f"  [FAIL] '{item}' should be INCLUDED")

        print("\n--- Exclude verification (other elements) ---")
        fail_count = 0
        for item in excluded_items:
            if item in result:
                print(f"  [FAIL] '{item}' should be EXCLUDED but found")
                fail_count += 1
            else:
                print(f"  [PASS] '{item}' correctly excluded")

        if fail_count == 0:
            print(f"\n  [OK] All non-included elements correctly excluded from both characters")

    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        script.data_dir = original_data_dir

    print("-" * 80)

def test_three_or_more_characters():
    """Test three or more characters"""
    import tempfile
    import shutil

    print("\n" + "=" * 80)
    print("Testing THREE or More Characters")
    print("=" * 80)

    script = CharaSituationScript()

    # Backup original data directory
    original_data_dir = script.data_dir
    temp_dir = tempfile.mkdtemp()

    try:
        # Set temporary data directory
        script.data_dir = temp_dir

        # Create test characters.yaml with 3 characters
        chars_content = """char1:
  base: 1girl
  hair: red hair
  body: large breasts

char2:
  base: 1girl
  hair: blue hair
  body: medium breasts

char3:
  base: 1girl
  hair: green hair
  body: small breasts
"""
        with open(os.path.join(temp_dir, 'characters.yaml'), 'w', encoding='utf-8') as f:
            f.write(chars_content)

        # Create test situations.yaml
        sits_content = """test_sit:
  prompt: test situation
  exclude:
    - hair
"""
        with open(os.path.join(temp_dir, 'situations.yaml'), 'w', encoding='utf-8') as f:
            f.write(sits_content)

        # Test with 3 characters
        prompt = '@characters:char1 @characters:char2 @characters:char3 @situations:test_sit'
        result = script.expand_prompt(prompt, 12345)

        print(f"\nTest 4: Three characters with exclude")
        print(f"Input:  {prompt}")
        print(f"Output: {result}")

        # All base and body should be included, hair should be excluded
        included_items = ['1girl', 'large breasts', 'medium breasts', 'small breasts', 'test situation']
        excluded_items = ['red hair', 'blue hair', 'green hair']

        print("\n--- Verification ---")
        for item in included_items:
            if item in result:
                print(f"  [PASS] '{item}' correctly included")
            else:
                print(f"  [FAIL] '{item}' should be INCLUDED")

        for item in excluded_items:
            if item in result:
                print(f"  [FAIL] '{item}' should be EXCLUDED but found")
            else:
                print(f"  [PASS] '{item}' correctly excluded")

    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        script.data_dir = original_data_dir

    print("-" * 80)

if __name__ == '__main__':
    test_multiple_characters_with_situation()
    test_multiple_characters_without_situation()
    test_multiple_characters_with_include()
    test_three_or_more_characters()

    print("\n" + "=" * 80)
    print("All Multiple Characters Tests Complete")
    print("=" * 80)
