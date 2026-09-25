"""Quick test script for vision model image analysis.

This script tests the vision model by analyzing a plant disease image.
You can provide your own image or it will use a test pattern.
"""

import asyncio
import base64
import sys
from pathlib import Path

from ai.services.vision_service import get_vision_service


async def test_image_analysis(image_path: str | None = None):
    """Test vision model with an image."""
    
    if image_path and Path(image_path).exists():
        # Use provided image
        with open(image_path, "rb") as f:
            image_data = f.read()
        image_b64 = base64.b64encode(image_data).decode("utf-8")
        print(f"✓ Loaded image: {image_path}")
    else:
        # Create a simple test message
        print("❌ No image provided or image not found")
        print("\nUsage: python test_vision.py <path_to_image.jpg>")
        print("\nExample:")
        print("  python test_vision.py ~/Downloads/sunflower_disease.jpg")
        return
    
    print("\n🔍 Analyzing image with llama3.2-vision:11b...")
    print("-" * 60)
    
    vision_service = get_vision_service()
    
    try:
        result = await vision_service.analyze_plant_image(
            image_base64=image_b64,
            locale="en",
            additional_context="This is a sunflower plant"
        )
        
        print("\n📊 Analysis Results:")
        print("=" * 60)
        
        obs = result.observations
        
        if obs.crop_identified:
            print(f"\n🌱 Crop: {obs.crop_identified} (confidence: {obs.crop_confidence:.2f})")
        
        if obs.plant_parts:
            print(f"\n🍃 Plant parts visible: {', '.join(obs.plant_parts)}")
        
        if obs.visible_symptoms:
            print(f"\n⚠️  Symptoms: {', '.join(obs.visible_symptoms)}")
        
        if obs.color_abnormalities:
            print(f"\n🎨 Color changes: {', '.join(obs.color_abnormalities)}")
        
        if obs.spots_lesions:
            print(f"\n🔴 Spots/Lesions: {', '.join(obs.spots_lesions)}")
        
        if obs.pests_visible:
            print(f"\n🐛 Pests: {', '.join(obs.pests_visible)}")
        
        if obs.possible_diseases:
            print(f"\n🔬 Possible diseases: {', '.join(obs.possible_diseases)}")
        
        print(f"\n📷 Image quality: {obs.image_quality}")
        
        print("\n📝 Full Analysis:")
        print("-" * 60)
        print(result.analysis_text)
        
        print(f"\n⚠️  {result.warning}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    image_path = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(test_image_analysis(image_path))
