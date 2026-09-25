"""Optimize symptom data for faster, more accurate diagnosis.

This script:
1. Removes unused symptoms (not linked to any disease)
2. Identifies and marks "key symptoms" (pathognomonic and required)
3. Assigns intelligent weights based on symptom discrimination power
4. Generates a report of changes

Run with: python -m scripts.optimize_symptoms
"""

from __future__ import annotations

import asyncio
import sys
from collections import defaultdict
from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import async_session_factory
from app.models.disease import Disease, DiseaseSymptom
from app.models.symptom import Symptom


async def analyze_symptom_discrimination(session: AsyncSession) -> dict[int, dict]:
    """Analyze how well each symptom discriminates between diseases."""
    
    # Get all disease-symptom associations
    query = select(DiseaseSymptom).options(
        selectinload(DiseaseSymptom.symptom),
        selectinload(DiseaseSymptom.disease)
    )
    result = await session.execute(query)
    associations = result.scalars().all()
    
    # Build symptom usage map
    symptom_usage = defaultdict(lambda: {
        'diseases': set(),
        'is_unique': False,
        'discrimination_score': 0.0
    })
    
    for assoc in associations:
        symptom_usage[assoc.symptom_id]['diseases'].add(assoc.disease_id)
    
    # Get total disease count
    total_diseases_result = await session.execute(select(Disease.id))
    total_diseases = len(total_diseases_result.scalars().all())
    
    # Calculate discrimination scores
    for symptom_id, data in symptom_usage.items():
        disease_count = len(data['diseases'])
        
        # Symptoms that appear in exactly 1 disease are unique (pathognomonic)
        data['is_unique'] = disease_count == 1
        
        # Discrimination score: symptoms that appear in 2-5 diseases are best
        # (not too common, not too rare)
        if disease_count == 1:
            # Unique symptoms are very valuable
            data['discrimination_score'] = 1.0
        elif 2 <= disease_count <= 5:
            # Good discriminators
            data['discrimination_score'] = 0.9
        elif 6 <= disease_count <= 10:
            # Moderate discriminators
            data['discrimination_score'] = 0.7
        else:
            # Too common - less useful
            data['discrimination_score'] = 0.5
    
    return symptom_usage


async def optimize_symptoms(session: AsyncSession, dry_run: bool = False) -> None:
    """Optimize symptom weights and flags for better diagnosis."""
    
    print("🔍 ANALYZING SYMPTOM DATA...")
    print("=" * 70)
    
    # Step 1: Remove unused symptoms
    unused_query = select(Symptom).outerjoin(
        DiseaseSymptom, Symptom.id == DiseaseSymptom.symptom_id
    ).where(DiseaseSymptom.symptom_id.is_(None))
    
    unused_result = await session.execute(unused_query)
    unused_symptoms = unused_result.scalars().all()
    
    print(f"\n📊 Found {len(unused_symptoms)} unused symptoms")
    
    if unused_symptoms:
        if dry_run:
            print("   [DRY RUN] Would delete:")
            for symptom in unused_symptoms[:10]:
                print(f"      • {symptom.code}")
            if len(unused_symptoms) > 10:
                print(f"      ... and {len(unused_symptoms) - 10} more")
        else:
            unused_ids = [s.id for s in unused_symptoms]
            await session.execute(delete(Symptom).where(Symptom.id.in_(unused_ids)))
            print(f"   ✅ Deleted {len(unused_symptoms)} unused symptoms")
    
    # Step 2: Analyze discrimination
    print("\n🎯 ANALYZING SYMPTOM DISCRIMINATION...")
    symptom_usage = await analyze_symptom_discrimination(session)
    
    # Step 3: Update weights and flags
    print("\n⚖️  OPTIMIZING WEIGHTS...")
    
    # Get all disease-symptom associations
    query = select(DiseaseSymptom).options(
        selectinload(DiseaseSymptom.symptom),
        selectinload(DiseaseSymptom.disease)
    )
    result = await session.execute(query)
    associations = result.scalars().all()
    
    updates = {
        'pathognomonic': 0,
        'required': 0,
        'high_weight': 0,
        'medium_weight': 0,
        'low_weight': 0,
    }
    
    for assoc in associations:
        symptom_id = assoc.symptom_id
        usage = symptom_usage[symptom_id]
        
        # Set pathognomonic flag for unique symptoms
        if usage['is_unique'] and not assoc.is_pathognomonic:
            if not dry_run:
                assoc.is_pathognomonic = True
            updates['pathognomonic'] += 1
        
        # Set weights based on discrimination score
        new_weight = Decimal(str(usage['discrimination_score']))
        
        if new_weight != assoc.weight:
            if not dry_run:
                assoc.weight = new_weight
            
            if new_weight >= Decimal('0.9'):
                updates['high_weight'] += 1
            elif new_weight >= Decimal('0.7'):
                updates['medium_weight'] += 1
            else:
                updates['low_weight'] += 1
    
    if not dry_run:
        await session.commit()
    
    # Print summary
    print(f"\n{'[DRY RUN] ' if dry_run else ''}OPTIMIZATION SUMMARY:")
    print("-" * 70)
    print(f"  Pathognomonic symptoms marked: {updates['pathognomonic']}")
    print(f"  High-value symptoms (0.9-1.0):  {updates['high_weight']}")
    print(f"  Medium-value symptoms (0.7-0.9): {updates['medium_weight']}")
    print(f"  Low-value symptoms (<0.7):      {updates['low_weight']}")
    
    # Show top discriminating symptoms
    print("\n🌟 TOP 15 MOST DISCRIMINATING SYMPTOMS:")
    print("-" * 70)
    
    # Get symptom details
    symptom_query = select(Symptom)
    symptom_result = await session.execute(symptom_query)
    symptoms_by_id = {s.id: s for s in symptom_result.scalars().all()}
    
    sorted_symptoms = sorted(
        symptom_usage.items(),
        key=lambda x: (x[1]['discrimination_score'], len(x[1]['diseases'])),
        reverse=True
    )[:15]
    
    for symptom_id, data in sorted_symptoms:
        if symptom_id in symptoms_by_id:
            symptom = symptoms_by_id[symptom_id]
            disease_count = len(data['diseases'])
            score = data['discrimination_score']
            unique_flag = " [UNIQUE]" if data['is_unique'] else ""
            
            print(f"  • {symptom.code[:50]:50} → {disease_count:2} diseases, "
                  f"score: {score:.2f}{unique_flag}")


async def main() -> None:
    """Main entry point."""
    
    dry_run = "--dry-run" in sys.argv
    
    print("🧹 SUNFLOWER SYMPTOM OPTIMIZER")
    print("=" * 70)
    
    if dry_run:
        print("ℹ️  DRY RUN MODE - No changes will be saved")
    else:
        print("⚠️  This will modify symptom weights and flags in the database")
        confirm = input("\nContinue? [y/N]: ")
        if confirm.lower() != "y":
            print("❌ Cancelled")
            sys.exit(0)
    
    print()
    
    async with async_session_factory() as session:
        await optimize_symptoms(session, dry_run=dry_run)
    
    print("\n" + "=" * 70)
    if dry_run:
        print("✅ DRY RUN COMPLETE - Run without --dry-run to apply changes")
    else:
        print("✅ OPTIMIZATION COMPLETE!")
        print("\n📝 Next steps:")
        print("   1. Test diagnosis with the new weights")
        print("   2. The 'next_best_questions' algorithm will now prioritize")
        print("      high-discrimination symptoms")
        print("   3. Users should see diagnoses with fewer questions!")


if __name__ == "__main__":
    asyncio.run(main())
