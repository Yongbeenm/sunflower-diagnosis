"""Import sample sunflower diseases and symptoms to production database.

This script creates:
- 5 common sunflower diseases with English and Khmer translations
- 20 symptoms across different categories
- Disease-symptom associations with weights
"""

from __future__ import annotations

import asyncio
import sys
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.models.disease import Disease, DiseaseSymptom
from app.models.symptom import Symptom, SymptomCategory
from app.models.translation import Translation

# Sample symptoms data
SYMPTOMS = [
    # Leaf symptoms
    {"code": "leaf_yellow_spots", "category": "leaf", "en": "Yellow spots on leaves", "km": "ស្នាមពណ៌លឿងលើស្លឹក"},
    {"code": "leaf_brown_lesions", "category": "leaf", "en": "Brown lesions on leaves", "km": "ដំបៅពណ៌ត្នោតលើស្លឹក"},
    {"code": "leaf_wilting", "category": "leaf", "en": "Wilting leaves", "km": "ស្លឹករួញ"},
    {"code": "leaf_powdery_white", "category": "leaf", "en": "Powdery white coating on leaves", "km": "ស្រទាប់ម្សៅពណ៌សលើស្លឹក"},
    {"code": "leaf_rust_pustules", "category": "leaf", "en": "Orange-rust pustules on leaves", "km": "ដំបៅពណ៌ទឹកក្រូចលើស្លឹក"},
    
    # Stem symptoms
    {"code": "stem_rot", "category": "stem", "en": "Stem rotting at base", "km": "ដើមរលួយនៅគល់"},
    {"code": "stem_cankers", "category": "stem", "en": "Cankers on stem", "km": "ដំបៅលើដើម"},
    {"code": "stem_discoloration", "category": "stem", "en": "Stem discoloration", "km": "ដើមប្រែពណ៌"},
    
    # Head symptoms  
    {"code": "head_rot", "category": "head", "en": "Head rotting", "km": "ក្បាលផ្ការលួយ"},
    {"code": "head_mold_growth", "category": "head", "en": "Mold growth on head", "km": "ផ្សិតលូតលាស់លើក្បាលផ្កា"},
    {"code": "head_discolored_seeds", "category": "head", "en": "Discolored seeds", "km": "គ្រាប់ប្រែពណ៌"},
    {"code": "head_drooping", "category": "head", "en": "Head drooping prematurely", "km": "ក្បាលផ្កាទម្រេតមុនពេល"},
    
    # Whole plant symptoms
    {"code": "plant_stunted", "category": "whole_plant", "en": "Stunted growth", "km": "ការលូតលាស់យឺត"},
    {"code": "plant_yellowing", "category": "whole_plant", "en": "Overall yellowing", "km": "ពណ៌លឿងទាំងមូល"},
    {"code": "plant_wilting", "category": "whole_plant", "en": "Whole plant wilting", "km": "រុក្ខជាតិទាំងមូលរួញ"},
    
    # Root symptoms
    {"code": "root_rot", "category": "root", "en": "Root rot", "km": "ឫសរលួយ"},
    {"code": "root_galls", "category": "root", "en": "Galls on roots", "km": "ដុំលើឫស"},
    
    # Seedling symptoms
    {"code": "seedling_damping_off", "category": "seedling", "en": "Damping off", "km": "កូនដំណាំស្រក"},
    {"code": "seedling_poor_emergence", "category": "seedling", "en": "Poor emergence", "km": "ការលេចមិនល្អ"},
    
    # Environmental
    {"code": "env_high_humidity", "category": "environment", "en": "High humidity conditions", "km": "សំណើមខ្ពស់"},
]

# Sample diseases
DISEASES = [
    {
        "slug": "downy-mildew",
        "pathogen_type": "fungal",
        "en_name": "Downy Mildew",
        "km_name": "ប្រេះស្លឹក",
        "en_description": "Fungal disease causing yellow spots and downy growth on leaf undersides. Thrives in cool, wet conditions.",
        "km_description": "ជំងឺផ្សិតបណ្តាលឱ្យមានស្នាមពណ៌លឿង និងផ្សិតលើផ្នែកខាងក្រោមស្លឹក។ រីកលូតលាស់ក្នុងលក្ខខណ្ឌត្រជាក់ និងសើម។",
        "symptoms": [
            ("leaf_yellow_spots", 0.9, True),
            ("leaf_wilting", 0.6, False),
            ("env_high_humidity", 0.7, False),
        ],
    },
    {
        "slug": "rust",
        "pathogen_type": "fungal",
        "en_name": "Rust",
        "km_name": "ច្រែះ",
        "en_description": "Fungal disease characterized by orange-rust colored pustules on leaves. Can cause premature leaf drop.",
        "km_description": "ជំងឺផ្សិតដែលមានលក្ខណៈដុំពណ៌ទឹកក្រូច-ច្រែះលើស្លឹក។ អាចបណ្តាលឱ្យស្លឹករ្តាស់មុនពេល។",
        "symptoms": [
            ("leaf_rust_pustules", 0.95, True),
            ("plant_stunted", 0.4, False),
        ],
    },
    {
        "slug": "powdery-mildew",
        "pathogen_type": "fungal",
        "en_name": "Powdery Mildew",
        "km_name": "ម្សៅស",
        "en_description": "White powdery fungal growth on leaves and stems. Reduces photosynthesis and plant vigor.",
        "km_description": "ផ្សិតពណ៌សដូចម្សៅលើស្លឹក និងដើម។ បន្ថយការធ្វើរស្មីសំយោគ និងកម្លាំងរុក្ខជាតិ។",
        "symptoms": [
            ("leaf_powdery_white", 0.95, True),
            ("leaf_wilting", 0.5, False),
            ("plant_stunted", 0.6, False),
        ],
    },
    {
        "slug": "head-rot",
        "pathogen_type": "fungal",
        "en_name": "Head Rot (Sclerotinia)",
        "km_name": "ក្បាលរលួយ",
        "en_description": "Fungal disease that rots sunflower heads, often starting from the back. Causes significant yield loss.",
        "km_description": "ជំងឺផ្សិតធ្វើឱ្យក្បាលផ្ការលួយ ជាញឹកញាប់ចាប់ផ្តើមពីខាងក្រោយ។ បណ្តាលឱ្យបាត់បង់ទិន្នផលច្រើន។",
        "symptoms": [
            ("head_rot", 0.95, True),
            ("head_mold_growth", 0.8, False),
            ("stem_discoloration", 0.6, False),
            ("head_drooping", 0.7, False),
        ],
    },
    {
        "slug": "verticillium-wilt",
        "pathogen_type": "fungal",
        "en_name": "Verticillium Wilt",
        "km_name": "ជំងឺរួញ Verticillium",
        "en_description": "Soil-borne fungal disease causing wilting, yellowing, and vascular discoloration. Often fatal.",
        "km_description": "ជំងឺផ្សិតក្នុងដីបណ្តាលឱ្យរួញ លឿង និងសរសៃឈាមប្រែពណ៌។ ជាញឹកញាប់សំលាប់។",
        "symptoms": [
            ("plant_wilting", 0.9, True),
            ("plant_yellowing", 0.8, True),
            ("stem_discoloration", 0.7, False),
            ("leaf_wilting", 0.8, False),
        ],
    },
]


async def get_or_create_symptom(
    session: AsyncSession,
    symptom_data: dict[str, Any],
    categories: dict[str, SymptomCategory],
) -> Symptom:
    """Get existing symptom or create new one with translations."""
    result = await session.execute(select(Symptom).where(Symptom.code == symptom_data["code"]))
    symptom = result.scalar_one_or_none()

    if symptom is None:
        category = categories[symptom_data["category"]]
        symptom = Symptom(
            code=symptom_data["code"],
            category_id=category.id,
        )
        session.add(symptom)
        await session.flush()

        # Add translations
        for locale, field in [("en", "label"), ("km", "label")]:
            key = "en" if locale == "en" else "km"
            session.add(
                Translation(
                    entity_type="symptom",
                    entity_id=symptom.id,
                    locale=locale,
                    field=field,
                    value=symptom_data[key],
                )
            )

    return symptom


async def create_disease_with_symptoms(
    session: AsyncSession,
    disease_data: dict[str, Any],
    symptoms_map: dict[str, Symptom],
) -> None:
    """Create disease with translations and symptom associations."""
    from app.models.enums import PathogenType
    
    # Check if disease already exists
    result = await session.execute(select(Disease).where(Disease.slug == disease_data["slug"]))
    existing = result.scalar_one_or_none()

    if existing:
        print(f"  ⚠️  Disease {disease_data['slug']} already exists, skipping...")
        return

    # Create disease
    disease = Disease(
        slug=disease_data["slug"],
        pathogen_type=PathogenType(disease_data["pathogen_type"]),
        is_published=True,
    )
    session.add(disease)
    await session.flush()

    # Add translations
    for locale, name_key, desc_key in [
        ("en", "en_name", "en_description"),
        ("km", "km_name", "km_description"),
    ]:
        session.add(
            Translation(
                entity_type="disease",
                entity_id=disease.id,
                locale=locale,
                field="name",
                value=disease_data[name_key],
            )
        )
        session.add(
            Translation(
                entity_type="disease",
                entity_id=disease.id,
                locale=locale,
                field="description",
                value=disease_data[desc_key],
            )
        )

    # Add symptom associations
    for symptom_code, weight, is_required in disease_data["symptoms"]:
        symptom = symptoms_map[symptom_code]
        session.add(
            DiseaseSymptom(
                disease_id=disease.id,
                symptom_id=symptom.id,
                weight=weight,
                is_required=is_required,
            )
        )

    print(f"  ✓ Created disease: {disease_data['en_name']}")


async def import_sample_data(session: AsyncSession) -> None:
    """Import all sample diseases and symptoms."""
    print("🌻 Importing sample sunflower diseases...")
    print()

    # Get symptom categories
    result = await session.execute(select(SymptomCategory))
    categories = {cat.code: cat for cat in result.scalars().all()}

    print("📝 Creating symptoms...")
    symptoms_map = {}
    for symptom_data in SYMPTOMS:
        symptom = await get_or_create_symptom(session, symptom_data, categories)
        symptoms_map[symptom.code] = symptom
    print(f"  ✓ Created {len(symptoms_map)} symptoms")
    print()

    print("🦠 Creating diseases...")
    for disease_data in DISEASES:
        await create_disease_with_symptoms(session, disease_data, symptoms_map)

    await session.commit()
    print()
    print("✅ Import complete!")
    print()
    print("Created:")
    print(f"  - {len(SYMPTOMS)} symptoms")
    print(f"  - {len(DISEASES)} diseases")
    print()


async def main() -> None:
    """CLI entry point."""
    async with async_session_factory() as session:
        await import_sample_data(session)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"❌ Error: {exc}", file=sys.stderr)
        sys.exit(1)
