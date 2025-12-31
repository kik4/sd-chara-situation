#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for LORA tag preservation
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
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, 'scripts'))

from chara_situation import CharaSituationScript

def test_lora_preservation():
    """Test that LORA tags are preserved in the output"""

    # Create script instance
    script = CharaSituationScript()

    # Test cases with LORA tags
    test_cases = [
        {
            'name': 'LORA before character tag',
            'prompt': '<lora:test:0.8> @characters:reimu @situations:beach masterpiece, best quality',
            'seed': 12345,
        },
        {
            'name': 'LORA after character tag',
            'prompt': '@characters:reimu <lora:test:0.8> @situations:beach masterpiece, best quality',
            'seed': 12345,
        },
        {
            'name': 'LORA at the end',
            'prompt': '@characters:reimu @situations:beach masterpiece, best quality, <lora:test:0.8>',
            'seed': 12345,
        },
        {
            'name': 'Multiple LORA tags',
            'prompt': '<lora:style:0.5> @characters:reimu @situations:beach <lora:quality:0.7> masterpiece',
            'seed': 12345,
        },
    ]

    print("=" * 80)
    print("Testing LORA Tag Preservation")
    print("=" * 80)

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['name']}")
        print(f"Input:  {test['prompt']}")

        result = script.expand_prompt(test['prompt'], test['seed'])

        print(f"Output: {result}")

        # Check if LORA tags are preserved
        import re
        lora_pattern = r'<lora:[^>]+>'
        input_loras = re.findall(lora_pattern, test['prompt'])
        output_loras = re.findall(lora_pattern, result)

        if input_loras == output_loras:
            print(f"  [PASS] All LORA tags preserved: {input_loras}")
        else:
            print(f"  [FAIL] LORA tags lost!")
            print(f"        Input had:  {input_loras}")
            print(f"        Output has: {output_loras}")

        print("-" * 80)

    print("\n" + "=" * 80)
    print("LORA Test Complete")
    print("=" * 80)

if __name__ == '__main__':
    test_lora_preservation()
