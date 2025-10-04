#!/usr/bin/env python3
"""
Test script to verify OCR and document processing capabilities
"""
import sys
import os
sys.path.insert(0, '/app')

from backend.document_parser import parse_document
from PIL import Image, ImageDraw, ImageFont
import tempfile

def create_test_image_with_text():
    """Create a simple test image with text"""
    # Create a white image with text
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add text
    text = "This is a test document\nfor OCR verification.\nNeuralStark Backend Test."
    draw.text((20, 50), text, fill='black')
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name)
    return temp_file.name

def test_text_file():
    """Test plain text file parsing"""
    print("\n=== Testing Plain Text File ===")
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_file.write("This is a plain text file test.\nLine 2 of the document.")
    temp_file.close()
    
    result = parse_document(temp_file.name)
    print(f"✓ Text file parsed: {len(result) if result else 0} characters")
    os.unlink(temp_file.name)
    return result is not None

def test_image_ocr():
    """Test image OCR"""
    print("\n=== Testing Image OCR ===")
    try:
        image_file = create_test_image_with_text()
        result = parse_document(image_file)
        
        if result:
            print(f"✓ Image OCR successful: {len(result)} characters extracted")
            print(f"  Content preview: {result[:100]}...")
            success = True
        else:
            print("✗ Image OCR failed - no text extracted")
            success = False
            
        os.unlink(image_file)
        return success
    except Exception as e:
        print(f"✗ Image OCR error: {e}")
        return False

def test_csv_file():
    """Test CSV file parsing"""
    print("\n=== Testing CSV File ===")
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    temp_file.write("Name,Age,City\n")
    temp_file.write("John,30,Paris\n")
    temp_file.write("Jane,25,London\n")
    temp_file.close()
    
    result = parse_document(temp_file.name)
    print(f"✓ CSV file parsed: {len(result) if result else 0} characters")
    if result:
        print(f"  Content preview:\n{result[:200]}")
    os.unlink(temp_file.name)
    return result is not None

def test_json_file():
    """Test JSON file parsing"""
    print("\n=== Testing JSON File ===")
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    temp_file.write('{"name": "Test", "value": 123, "items": ["a", "b", "c"]}')
    temp_file.close()
    
    result = parse_document(temp_file.name)
    print(f"✓ JSON file parsed: {len(result) if result else 0} characters")
    os.unlink(temp_file.name)
    return result is not None

def main():
    print("=" * 60)
    print("NeuralStark Backend - Document Processing Test Suite")
    print("=" * 60)
    
    results = {
        "Text File": test_text_file(),
        "Image OCR": test_image_ocr(),
        "CSV File": test_csv_file(),
        "JSON File": test_json_file(),
    }
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:20s} : {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())
