#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for LORA tags inside YAML definitions
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

def test_lora_in_yaml():
    """Test that LORA tags inside YAML definitions are preserved"""

    # Create temporary directory for test data
    temp_dir = tempfile.mkdtemp()
    data_dir = os.path.join(temp_dir, 'data')
    os.makedirs(data_dir)

    try:
        # Create test character file with LORA in value
        char_content = """alice:
  base: 1girl, <lora:alice_style:0.8>
  hair: blonde hair
  eye: blue eyes
"""
        with open(os.path.join(data_dir, 'test_chars.yaml'), 'w', encoding='utf-8') as f:
            f.write(char_content)

        # Create test situation with LORA in prompt
        sit_content = """magical:
  prompt: magical aura, sparkles, <lora:magic_effect:0.5>
"""
        with open(os.path.join(data_dir, 'test_sits.yaml'), 'w', encoding='utf-8') as f:
            f.write(sit_content)

        # Create script instance with custom data directory
        script = CharaSituationScript()
        script.data_dir = data_dir

        print("=" * 80)
        print("Testing LORA Tags Inside YAML Definitions")
        print("=" * 80)

        # Test 1: LORA in character definition
        print("\nTest 1: LORA tag in character definition")
        prompt1 = "@test_chars:alice masterpiece"
        result1 = script.expand_prompt(prompt1, 12345)
        print(f"Input:  {prompt1}")
        print(f"Output: {result1}")

        if "<lora:alice_style:0.8>" in result1:
            print("  [PASS] LORA tag from character definition preserved")
        else:
            print("  [FAIL] LORA tag from character definition missing")
            print(f"        Expected '<lora:alice_style:0.8>' in output")

        print("-" * 80)

        # Test 2: LORA in situation definition
        print("\nTest 2: LORA tag in situation definition")
        prompt2 = "@test_chars:alice @test_sits:magical masterpiece"
        result2 = script.expand_prompt(prompt2, 12345)
        print(f"Input:  {prompt2}")
        print(f"Output: {result2}")

        if "<lora:alice_style:0.8>" in result2:
            print("  [PASS] LORA tag from character definition preserved")
        else:
            print("  [FAIL] LORA tag from character definition missing")

        if "<lora:magic_effect:0.5>" in result2:
            print("  [PASS] LORA tag from situation definition preserved")
        else:
            print("  [FAIL] LORA tag from situation definition missing")
            print(f"        Expected '<lora:magic_effect:0.5>' in output")

        print("-" * 80)

        # Test 3: Array value with LORA
        char_content2 = """bob:
  base: 1boy
  effects:
    - <lora:effect1:0.3>
    - <lora:effect2:0.4>
    - glowing
"""
        with open(os.path.join(data_dir, 'test_chars2.yaml'), 'w', encoding='utf-8') as f:
            f.write(char_content2)

        print("\nTest 3: LORA tags in array values")
        prompt3 = "@test_chars2:bob test"
        result3 = script.expand_prompt(prompt3, 12345)
        print(f"Input:  {prompt3}")
        print(f"Output: {result3}")

        if "<lora:effect1:0.3>" in result3:
            print("  [PASS] First LORA tag in array preserved")
        else:
            print("  [FAIL] First LORA tag in array missing")

        if "<lora:effect2:0.4>" in result3:
            print("  [PASS] Second LORA tag in array preserved")
        else:
            print("  [FAIL] Second LORA tag in array missing")

        print("-" * 80)

        print("\n" + "=" * 80)
        print("LORA in YAML Test Complete")
        print("=" * 80)

    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)

if __name__ == '__main__':
    test_lora_in_yaml()
