#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for newline preservation in prompts
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

def test_newline_preservation():
    """Test that newlines in prompts are preserved"""

    # Create script instance
    script = CharaSituationScript()

    print("=" * 80)
    print("Testing Newline Preservation in Prompts")
    print("=" * 80)

    # Test 1: Newline after tag
    print("\nTest 1: Newline after tag")
    prompt1 = "@characters:reimu\nmasterpiece, best quality"
    result1 = script.expand_prompt(prompt1, 12345)
    print(f"Input:\n{repr(prompt1)}")
    print(f"Output:\n{repr(result1)}")

    if '\n' in result1:
        print("  [PASS] Newline preserved")
    else:
        print("  [FAIL] Newline lost")

    print("-" * 80)

    # Test 2: Multiple newlines
    print("\nTest 2: Multiple newlines")
    prompt2 = "@characters:reimu\n@situations:beach\nmasterpiece, best quality\ndetailed background"
    result2 = script.expand_prompt(prompt2, 12345)
    print(f"Input:\n{repr(prompt2)}")
    print(f"Output:\n{repr(result2)}")

    newline_count_input = prompt2.count('\n')
    newline_count_output = result2.count('\n')
    print(f"  Input newlines: {newline_count_input}")
    print(f"  Output newlines: {newline_count_output}")

    if newline_count_output == newline_count_input:
        print("  [PASS] All newlines preserved")
    else:
        print("  [FAIL] Some newlines lost")

    print("-" * 80)

    # Test 3: Tag in middle of line
    print("\nTest 3: Tag in middle of line")
    prompt3 = "masterpiece, @characters:reimu, best quality"
    result3 = script.expand_prompt(prompt3, 12345)
    print(f"Input:\n{repr(prompt3)}")
    print(f"Output:\n{repr(result3)}")
    print("-" * 80)

    print("\n" + "=" * 80)
    print("Newline Test Complete")
    print("=" * 80)

if __name__ == '__main__':
    test_newline_preservation()
