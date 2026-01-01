#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for trailing comma preservation
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

def test_trailing_comma():
    """Test that trailing commas on lines are preserved"""

    # Create script instance
    script = CharaSituationScript()

    print("=" * 80)
    print("Testing Trailing Comma Preservation")
    print("=" * 80)

    # Test 1: Trailing comma before newline
    print("\nTest 1: Trailing comma before newline")
    prompt1 = "@characters:reimu,\nmasterpiece, best quality"
    result1 = script.expand_prompt(prompt1, 12345)
    print(f"Input:\n{repr(prompt1)}")
    print(f"Output:\n{repr(result1)}")

    if ',\n' in result1:
        print("  [PASS] Trailing comma before newline preserved")
    else:
        print("  [FAIL] Trailing comma before newline lost")

    print("-" * 80)

    # Test 2: Multiple lines with trailing commas
    print("\nTest 2: Multiple lines with trailing commas")
    prompt2 = "masterpiece,\n@characters:reimu,\nbest quality"
    result2 = script.expand_prompt(prompt2, 12345)
    print(f"Input:\n{repr(prompt2)}")
    print(f"Output:\n{repr(result2)}")

    comma_newline_count = result2.count(',\n')
    if comma_newline_count >= 1:
        print(f"  [PASS] Found {comma_newline_count} trailing comma+newline sequences")
    else:
        print("  [FAIL] No trailing comma+newline sequences found")

    print("-" * 80)

    # Test 3: Tag at end of line with comma
    print("\nTest 3: Tag at end of line with comma")
    prompt3 = "masterpiece, @characters:reimu,\nbest quality"
    result3 = script.expand_prompt(prompt3, 12345)
    print(f"Input:\n{repr(prompt3)}")
    print(f"Output:\n{repr(result3)}")

    if ',\n' in result3:
        print("  [PASS] Trailing comma preserved after tag expansion")
    else:
        print("  [FAIL] Trailing comma lost after tag expansion")

    print("-" * 80)

    print("\n" + "=" * 80)
    print("Trailing Comma Test Complete")
    print("=" * 80)

if __name__ == '__main__':
    test_trailing_comma()
