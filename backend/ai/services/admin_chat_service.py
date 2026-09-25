"""AI Admin & Knowledge Chat Service

Comprehensive AI Crop Advisor & Database Management Service for Sunflower Expert System.
- Knows all 20 diseases, 62 symptoms, Bayesian rulesets, treatments, and prevention.
- Provides seamless system navigation to any page (catalog, diagnosis, history, feedback, admin).
- Performs role-based CRUD permissions (Admin: Full CRUD; Expert/Agronomist: Create/Update; Grower: View/Diagnose).
- Cross-references symptoms to identify possible diseases and offers interactive diagnosis actions.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from decimal import Decimal
from typing import Any

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ai.config import ai_config
from ai.schemas.ai_schemas import AIChatRequest, AIChatResponse
from ai.services.json_parser import extract_json_from_response
from ai.services.ollama_service import get_ollama_service
from app.models.disease import Disease, DiseaseSymptom
from app.models.enums import PathogenType
from app.models.symptom import Symptom, SymptomCategory
from app.models.translation import Translation

logger = logging.getLogger(__name__)

# Curated reference database for sunflower disease pathology
BOTANICAL_DISEASE_KB: dict[str, dict[str, Any]] = {
    "bacterial-soft-rot": {
        "name_en": "Bacterial Soft Rot",
        "name_km": "ជំងឺរលួយទន់ដោយបាក់តេរីលើផ្កាឈូករ័ត្ន",
        "scientific_name": "Pectobacterium carotovorum subsp. carotovorum",
        "pathogen_type": "bacterial",
        "description_en": "Bacterial soft rot is a destructive sunflower disease characterized by rapid maceration and pectolytic breakdown of parenchyma tissues in the lower stems and flowering heads. The pathogen penetrates through insect wounds, mechanical injuries, or natural openings under warm (28-35°C), high-humidity conditions, causing the internal stem pith to liquefy into a foul-smelling, water-soaked slimy mass.",
        "description_km": "ជំងឺរលួយទន់ដោយបាក់តេរី គឺជាជំងឺបំផ្លិចបំផ្លាញលើដំណាំផ្កាឈូករ័ត្ន ដែលបង្កឱ្យមានការរលួយជាលិកាដើម និងកញ្ចុំផ្កាយ៉ាងឆាប់រហ័ស។ បាក់តេរីជ្រាបចូលតាមរយៈរបួសដែលបណ្តាលមកពីសត្វល្អិត ឬការខូចខាតមេកានិកក្នុងលក្ខខណ្ឌក្តៅហើយសើមខ្លាំង ដែលធ្វើឱ្យបណ្តូលដើមរលួយទន់ និងមានក្លិនស្អុយ។",
        "symptoms": [
            "Water-soaked, dark olive to brown lesions expanding rapidly along the lower stem and petiole bases",
            "Internal pith disintegration turning into a soft, brownish, foul-smelling bacterial slime",
            "Hollow, mushy stem causing sudden lodging and whole-plant structural collapse during head filling",
            "Water-soaked rot on the back of the sunflower receptacle causing floral tissue decay",
            "Rapid canopy wilting and leaf desiccation without initial chlorosis"
        ],
        "causes": [
            "Infection by pectinolytic enterobacteria (Pectobacterium / Dickeya species)",
            "Prolonged warm, saturated soil conditions and high relative humidity (>85%)",
            "Mechanical damage from cultivation tools or stem-boring insect feeding wounds",
            "Excessive nitrogen application resulting in overly succulent, tender vegetative tissue"
        ],
        "treatment_en": "Apply preventative copper-based bactericides (copper hydroxide or copper oxychloride at 2.5-3.0 kg/ha) or kasugamycin spray during early vegetative and budding stages if weather is humid. Remove and safely destroy severely infected plants to halt field spread. Disinfect all machinery and pruning equipment with 10% sodium hypochlorite solution.",
        "treatment_km": "បាញ់ថ្នាំសម្លាប់បាក់តេរីដែលមានសមាសធាតុទង់ដែង (Copper Hydroxide ឬ Kasugamycin) នៅដំណាក់កាលលូតលាស់ដំបូង និងពេលចេញផ្កា ប្រសិនបើអាកាសធាតុសើម។ ដកដើមដែលឆ្លងជំងឺធ្ងន់ធ្ងរយកទៅដុតបំផ្លាញចោល។ សម្អាត និងសម្លាប់មេរោគលើឧបករណ៍កសិកម្មដោយប្រើទឹកថ្នាំសម្លាប់មេរោគ។",
        "prevention_en": "Practice strict 3 to 4-year crop rotation with non-host graminaceous crops (maize, sorghum, or pearl millet). Plant certified disease-free, high-vigor hybrid seeds treated with antimicrobial protectants. Ensure adequate field drainage and wider row spacing (60-75 cm) to optimize canopy aeration. Avoid overhead sprinkler irrigation during warm afternoons; utilize precision drip irrigation.",
        "prevention_km": "អនុវត្តការបង្វិលដំណាំពី ៣ ទៅ ៤ ឆ្នាំជាមួយដំណាំអំបូរស្មៅ (ពោត ឬពោតបារាំង)។ ប្រើប្រាស់គ្រាប់ពូជដែលបានបញ្ជាក់ថាគ្មានមេរោគ។ រៀបចំប្រព័ន្ធបង្ហូរទឹកឱ្យបានល្អ និងដាំក្នុងគម្លាតសមស្រប (៦០-៧៥ ស.ម) ដើម្បីឱ្យខ្យល់ចេញចូលបានល្អ។ ជៀសវាងការស្រោចស្រពពីលើនៅពេលថ្ងៃក្តៅ ដោយប្តូរមកប្រើប្រព័ន្ធដំណក់ទឹក។"
    },
    "bacterial-stalk-rot": {
        "name_en": "Bacterial Stalk Rot",
        "name_km": "ជំងឺរលួយដើមដោយបាក់តេរីលើផ្កាឈូករ័ត្ន",
        "scientific_name": "Dickeya dadantii (syn. Erwinia chrysanthemi)",
        "pathogen_type": "bacterial",
        "description_en": "Bacterial stalk rot causes rapid stem discoloration, pith maceration, and premature lodging in sunflowers. It thrives in high temperatures and flooded or poorly drained soils, producing brown water-soaked stem lesions that ooze bacterial exudate.",
        "description_km": "ជំងឺរលួយដើមដោយបាក់តេរី បង្កឱ្យមានការប្រែពណ៌ដើម ការរលួយបណ្តូល និងការដួលរលំដើមមុនអាយុ។ វាលូតលាស់ល្អក្នុងសីតុណ្ហភាពខ្ពស់ និងដីលិចទឹក ដោយបង្កើតដំបៅសើមពណ៌ត្នោតលើដើម។",
        "symptoms": [
            "Brownish, water-soaked streaks on the lower sunflower stem",
            "Pith dissolution leaving a hollow, collapsed stalk",
            "Foul-smelling bacterial ooze from infected stem nodes",
            "Sudden wilting of leaves despite moist soil conditions",
            "Stem breakage and lodging during seed development"
        ],
        "causes": [
            "Dickeya dadantii or Pectobacterium bacterial pathogen",
            "High temperature (above 30°C) with standing water or saturated soil",
            "Wounds caused by hail, machinery, or stem-boring insects"
        ],
        "treatment_en": "Foliar application of copper hydroxide (2.0-2.5 kg/ha) or copper sulfate pentahydrate at early detection. Rogue out infected plants to limit secondary spread by rain splash.",
        "treatment_km": "បាញ់ថ្នាំ Copper Hydroxide ឬ Copper Sulfate នៅពេលចាប់ផ្តើមកើតជំងឺដំបូង។ ដកដើមដែលឆ្លងជំងឺចេញដើម្បីការពារការឆ្លងរាលដាល។",
        "prevention_en": "Ensure excellent soil drainage and avoid planting in low-lying, flood-prone fields. Practice crop rotation with cereals. Control insect vectors and avoid field operations when foliage is wet.",
        "prevention_km": "រៀបចំដីឱ្យមានប្រព័ន្ធបង្ហូរទឹកល្អ និងជៀសវាងការដាំដុះនៅតំបន់ទំនាបលិចទឹក។ អនុវត្តការបង្វិលដំណាំជាមួយដំណាំធញ្ញជាតិ។"
    },
    "southern-blight": {
        "name_en": "Southern Blight (Stem Rot)",
        "name_km": "ជំងឺរលួយគល់ភាគខាងត្បូងលើផ្កាឈូករ័ត្ន",
        "scientific_name": "Athelia rolfsii (anamorph: Sclerotium rolfsii)",
        "pathogen_type": "fungal",
        "description_en": "Southern blight is a soilborne fungal disease causing crown and stem rot near the soil line. It is characterized by dense, fan-like white mycelium and mustard-seed-like sclerotia forming at the stem base during hot, humid weather, leading to sudden permanent wilting.",
        "description_km": "ជំងឺរលួយគល់ភាគខាងត្បូង គឺជាជំងឺបង្កដោយផ្សិតក្នុងដី ដែលបណ្តាលឱ្យរលួយគល់ និងដើមជិតផ្ទៃដី។ វាមានសរសៃផ្សិតពណ៌សក្រាស់ និងគ្រាប់ស្ក្លេរ៉ូតដូចគ្រាប់ស្ពៃនៅគល់ដើមក្នុងរដូវក្តៅហើយសើម ដែលបណ្តាលឱ្យដើមស្រពោនងាប់ភ្លាមៗ។",
        "symptoms": [
            "Water-soaked dark lesions around the sunflower stem base at the soil line",
            "Dense, white fan-like fungal mycelium covering the lower stem and surrounding soil",
            "Abundant spherical, brown to tan sclerotia resembling mustard seeds",
            "Sudden, irreversible wilting of the whole plant with leaves remaining attached",
            "Cortical decay and collar rot leading to stem snapping at the soil line"
        ],
        "causes": [
            "Soilborne fungus Sclerotium rolfsii surviving as sclerotia in topsoil",
            "High soil and ambient temperatures (28-35°C) with moist soil surface",
            "Presence of organic debris near plant collars"
        ],
        "treatment_en": "Apply targeted fungicides such as azoxystrobin, flutolanil, or PCNB directed at the stem base. Incorporate biological antagonists such as Trichoderma harzianum into the planting furrow.",
        "treatment_km": "បាញ់ថ្នាំផ្សិត Azoxystrobin ឬ Flutolanil នៅគល់ដើម។ ប្រើប្រាស់ផ្សិតមានប្រយោជន៍ Trichoderma harzianum ក្នុងដីដើម្បីកម្ចាត់មេរោគផ្សិត។",
        "prevention_en": "Deep plow crop residues to bury sclerotia below 15 cm. Rotate with non-susceptible crops like corn or sorghum for at least 3 years. Maintain good drainage and avoid piling soil against plant stems during cultivation.",
        "prevention_km": "ភ្ជួរដីឱ្យជ្រៅដើម្បីកប់កាកសំណល់ដំណាំ។ បង្វិលដំណាំជាមួយពោត ឬដំណាំមិនឆ្លងជំងឺយ៉ាងតិច ៣ ឆ្នាំ។ រៀបចំប្រព័ន្ធបង្ហូរទឹកឱ្យបានល្អ។"
    },
    "sunflower-mosaic-virus": {
        "name_en": "Sunflower Mosaic Virus",
        "name_km": "ជំងឺវីរុសម៉ូសេអ៊ិចផ្កាឈូករ័ត្ន",
        "scientific_name": "Sunflower Mosaic Virus (SMV)",
        "pathogen_type": "viral",
        "description_en": "Sunflower mosaic virus causes mottled chlorotic patterns, leaf crinkling, and stunting in sunflowers. Transmitted non-persistently by aphids, it reduces photosynthetic efficiency and significantly impairs seed yield.",
        "description_km": "ជំងឺវីរុសម៉ូសេអ៊ិចផ្កាឈូករ័ត្ន បង្កឱ្យមានស្នាមអុចៗពណ៌លឿងបៃតង ស្លឹកជ្រួញ និងដើមកន្តឿ។ វាឆ្លងតាមរយៈសត្វចៃស្លឹក (Aphids) និងកាត់បន្ថយទិន្នផលគ្រាប់យ៉ាងខ្លាំង។",
        "symptoms": [
            "Distinct light and dark green mosaic or mottled patterns on young leaves",
            "Leaf deformation, puckering, and crinkled margins",
            "Stunted plant growth and reduced flower head diameter",
            "Pale yellow vein clearing on newly emerging foliage",
            "Malformed seeds with poor oil content"
        ],
        "causes": [
            "Potyvirus transmitted primarily by aphid vectors (Aphis gossypii, Myzus persicae)",
            "Presence of alternate weed hosts around field margins",
            "Infected seed lots or volunteer sunflower seedlings"
        ],
        "treatment_en": "No direct virucide exists. Apply insecticidal soaps or systemic aphicides (imidacloprid, acetamiprid) to control vector aphid populations. Rogue and burn infected plants immediately upon detection.",
        "treatment_km": "គ្មានថ្នាំសម្លាប់វីរុសដោយផ្ទាល់ទេ។ ត្រូវបាញ់ថ្នាំកម្ចាត់សត្វចៃស្លឹក (Imidacloprid ឬ Acetamiprid)។ ដកដើមដែលកើតជំងឺយកទៅដុតបំផ្លាញចោលភ្លាមៗ។",
        "prevention_en": "Plant certified virus-tested seeds. Eradicate broadleaf weeds and volunteer sunflowers along field borders. Install yellow sticky traps for aphid monitoring and use reflective silver mulches.",
        "prevention_km": "ប្រើប្រាស់គ្រាប់ពូជដែលគ្មានមេរោគវីរុស។ សម្អាតស្មៅចង្រៃជុំវិញចំការ។ ដាក់អន្ទាក់ស្អិតពណ៌លឿងដើម្បីចាប់សត្វចៃ។"
    },
    "tobacco-streak-virus": {
        "name_en": "Sunflower Necrosis Disease (Tobacco Streak Virus)",
        "name_km": "ជំងឺងាប់ជាលិកាផ្កាឈូករ័ត្ន (Tobacco Streak Virus)",
        "scientific_name": "Tobacco Streak Virus (TSV)",
        "pathogen_type": "viral",
        "description_en": "Sunflower necrosis disease, caused by Tobacco Streak Virus, is an aggressive viral disease causing severe necrosis of leaves, petiole blackening, stem streaking, and terminal bud death. It is transmitted by thrips carrying infected pollen grains.",
        "description_km": "ជំងឺងាប់ជាលិកាផ្កាឈូករ័ត្ន បង្កឡើងដោយវីរុស Tobacco Streak Virus គឺជាជំងឺធ្ងន់ធ្ងរដែលបណ្តាលឱ្យស្លឹកស្ងួតងាប់ ដើមមានស្នាមខ្មៅ និងងាប់ត្រួយចុង។ វាឆ្លងតាមរយៈសត្វល្អិតកន្ត្រៃ (Thrips) ដែលនាំយកលំអងផ្កាឆ្លងមេរោគ។",
        "symptoms": [
            "Mosaic and chlorotic ring spots on leaves developing into dark brown necrosis",
            "Black necrotic streaks along the stem and leaf petioles",
            "Death and dieback of the terminal growing bud (apical necrosis)",
            "Unilateral stem bending and malformation",
            "Total plant stunting and failure to form flower heads"
        ],
        "causes": [
            "Tobacco Streak Ilarvirus (TSV) infection",
            "Transmission by thrips (Frankliniella and Thrips species) carrying pollen from weed hosts (Parthenium hysterophorus)",
            "Dry, hot weather favoring thrips population spikes"
        ],
        "treatment_en": "Control thrips vectors with targeted insecticides (spinosad, fipronil, or thiamethoxam). Immediately remove and destroy necrotic plants to prevent secondary transmission.",
        "treatment_km": "បាញ់ថ្នាំកម្ចាត់សត្វល្អិតកន្ត្រៃ (Spinosad ឬ Thiamethoxam)។ ដកដើមដែលស្ងួតងាប់យកទៅបំផ្លាញចោលភ្លាមៗ។",
        "prevention_en": "Eradicate Parthenium and other weed hosts within and around sunflower plots. Plant barrier crops (such as 3-4 rows of pearl millet or sorghum) to intercept windborne thrips. Use certified clean seed.",
        "prevention_km": "កម្ចាត់ស្មៅចង្រៃជុំវិញចំការ។ ដាំដំណាំរបាំងការពារ (ដូចជាពោត ឬពោតបារាំង ៣-៤ ជួរ) ដើម្បីទប់ស្កាត់សត្វល្អិតកន្ត្រៃ។"
    },
    "apical-chlorosis": {
        "name_en": "Apical Chlorosis",
        "name_km": "ជំងឺស្លេកត្រួយចុងលើផ្កាឈូករ័ត្ន",
        "scientific_name": "Pseudomonas syringae pv. tagetis",
        "pathogen_type": "bacterial",
        "description_en": "Apical chlorosis is a bacterial disorder causing vivid golden-yellow to bleached white discoloration of terminal sunflower leaves and floral buds. The causal bacterium produces tagetitoxin, which selectively arrests chloroplastic RNA polymerase and disrupts chlorophyll accumulation in expanding apical tissues.",
        "description_km": "ជំងឺស្លេកត្រួយចុង គឺជាជំងឺបង្កដោយបាក់តេរី ដែលបណ្តាលឱ្យស្លឹកចុងត្រួយ និងផ្កាប្រែពណ៌លឿងស្រស់ ឬសស្លេក។ បាក់តេរីផលិតសារធាតុពុល Tagetitoxin ដែលទប់ស្កាត់ការបង្កើតបៃតងស្លឹកលើត្រួយខ្ចី ខណៈស្លឹកចាស់នៅតែមានពណ៌បៃតង។",
        "symptoms": [
            "Vibrant golden-yellow to bleached white chlorosis strictly on upper terminal leaves",
            "Prominently contrasting dark green lower and middle canopy leaves",
            "Distorted, undersized flower heads and poor seed development",
            "Slight stunting of upper vegetative nodes without systemic necrosis",
            "Translucent yellowing of newly formed floral bracts"
        ],
        "causes": [
            "Infection by Pseudomonas syringae pv. tagetis",
            "Seedborne transmission in infected sunflower achenes",
            "Prolonged rain events and cool to moderate temperatures (18-24°C)",
            "Splash dispersal from infected weed hosts (marigolds, ragweed)"
        ],
        "treatment_en": "Apply foliar copper hydroxide (2.0 kg/ha) or kasugamycin upon first notice of apical chlorosis. Remove weed hosts belonging to Asteraceae family adjacent to crop borders.",
        "treatment_km": "បាញ់ថ្នាំ Copper Hydroxide ឬ Kasugamycin នៅពេលឃើញរោគសញ្ញាស្លេកត្រួយដំបូង។ កម្ចាត់ស្មៅចង្រៃអំបូរ Asteraceae ជុំវិញចំការ។",
        "prevention_en": "Utilize certified, pathogen-free hybrid seeds. Avoid planting in fields adjacent to marigold or composite weed reservoirs. Practice 2-year crop rotation.",
        "prevention_km": "ប្រើប្រាស់គ្រាប់ពូជដែលបានបញ្ជាក់ថាគ្មានមេរោគ។ ជៀសវាងការដាំជិតដំណាំផ្កាស្បៃរឿង។ អនុវត្តការបង្វិលដំណាំរយៈពេល ២ ឆ្នាំ។"
    },
    "texas-root-rot": {
        "name_en": "Texas Root Rot (Phymatotrichum Root Rot)",
        "name_km": "ជំងឺរលួយឫសតិចសាស់លើផ្កាឈូករ័ត្ន",
        "scientific_name": "Phymatotrichopsis omnivora",
        "pathogen_type": "fungal",
        "severity": "Critical",
        "description_en": "Texas root rot (Phymatotrichopsis omnivora) is a lethal soilborne fungal disease attacking the taproot system in warm, alkaline, calcareous soils. It destroys the root cambium, causing sudden midsummer wilting where dry bronze foliage remains firmly attached to the standing stalk.",
        "description_km": "ជំងឺរលួយឫសតិចសាស់ គឺជាជំងឺផ្សិតក្នុងដីដ៏កាចសាហាវ ដែលបំផ្លាញប្រព័ន្ធឫសផ្កាឈូករ័ត្ន ក្នុងតំបន់ដីកំបោរ និងដីអាល់កាឡាំង។ មេរោគបំផ្លាញជាលិកាឫស ធ្វើឱ្យដើមស្រពោនងាប់ភ្លាមៗក្នុងរដូវក្តៅ ដោយស្លឹកស្ងួតពណ៌សំរិទ្ធនៅជាប់នឹងដើម។",
        "symptoms": [
            "Sudden permanent wilting of entire sunflower plants during midsummer heat",
            "Dead bronze-colored dried leaves remaining attached to the standing stalk",
            "Easily pulled plants due to complete rot and decay of the taproot",
            "Cortical tissue of taproot sloughs off easily revealing brown necrotic cylinder",
            "Brown woolly mycelial strands on root surfaces under hand lens"
        ],
        "causes": [
            "Soilborne fungus Phymatotrichopsis omnivora surviving as deep sclerotia",
            "High summer temperatures (soil temperature above 28°C)",
            "Heavy calcareous, alkaline clay soils (pH > 7.3)"
        ],
        "treatment_en": "Spot drenches of flutriafol at planting can suppress early infection in known disease hot spots. Severely infected plants cannot be rescued.",
        "treatment_km": "ស្រោចថ្នាំ Flutriafol នៅពេលដាំក្នុងដីដែលមានប្រវត្តិជំងឺ។ ដើមដែលងាប់មិនអាចព្យាបាលបានទេ។",
        "prevention_en": "Rotate with monocotyledonous crops (sorghum, corn) for 4 to 5 years. Deep plow in late summer to expose soil. Incorporate organic green manure.",
        "prevention_km": "បង្វិលដំណាំជាមួយពោត ឬដំណាំធញ្ញជាតិ ៤-៥ ឆ្នាំ។ ភ្ជួរដីឱ្យជ្រៅនៅរដូវក្តៅ។ ដាក់ជីកំប៉ុស្ត ឬជីធម្មជាតិក្នុងដី។"
    },
    "boron-deficiency": {
        "name_en": "Boron Deficiency Disorder",
        "name_km": "បញ្ហាកង្វះជាតិបូរ៉ុនលើផ្កាឈូករ័ត្ន",
        "scientific_name": "Abiotic / Micronutrient Deficiency (B)",
        "pathogen_type": "abiotic",
        "description_en": "Sunflower has one of the highest boron requirements among field crops. Deficiency causes corky horizontal stem cracking, thick brittle cupped leaves, and abnormal downward head bending at 90 degrees with blank, unfilled center achenes.",
        "description_km": "ផ្កាឈូករ័ត្នជាដំណាំដែលត្រូវការជាតិបូរ៉ុន (Boron) ខ្ពស់បំផុត។ កង្វះបូរ៉ុនបណ្តាលឱ្យដើមប្រេះស្រទាប់ក្រៅ ស្លឹកក្រាស់ហើយផុយស្រួយ ក្បាលផ្កាកោងខុសប្រក្រតី ៩០ ដឺក្រេ និងគ្រាប់ស្កកមិនពេញ។",
        "symptoms": [
            "Superficial horizontal brown corky cracks and fissures along the upper stem",
            "Young leaves become thick, leathery, brittle, and cup downward",
            "Severe stem bending just below the head causing heads to face sideways or downward at 90° angle",
            "Deformed flower heads with missing or sterile disc florets and empty achenes",
            "Death of growing terminal point with multiple small secondary branches emerging"
        ],
        "causes": [
            "Low soil boron levels (<0.5 ppm hot water extractable boron)",
            "Coarse sandy soils subject to high leaching",
            "Alkaline or over-limed soils (pH > 7.0) restricting boron uptake",
            "Extended dry periods restricting boron mass flow"
        ],
        "treatment_en": "Apply foliar spray of soluble borate (Solubor at 1.0-1.5 kg/ha in 200 L water) at the 8-to-12 leaf stage (V8-V12) before flowering.",
        "treatment_km": "បាញ់ជីស្លឹក Solubor (១.០ - ១.៥ គ.ក្រ/ហ.ត ក្នុងទឹក ២០០ លីត្រ) នៅដំណាក់កាលស្លឹក ៨ ទៅ ១២ សន្លឹក មុនពេលចេញផ្កា។",
        "prevention_en": "Perform pre-plant soil tests. Apply broadcast soil boron (1.5-2.0 kg actual B/ha as borax) incorporated before sowing. Maintain organic matter.",
        "prevention_km": "ធ្វើតេស្តដីមុនពេលដាំ។ ដាក់ជីបូរ៉ុន (១.៥ - ២.០ គ.ក្រ/ហ.ត) ក្នុងដីមុនព្រោះគ្រាប់។ រក្សាជីជាតិសរីរាង្គក្នុងដី។"
    },
    "root-knot-nematode": {
        "name_en": "Root-Knot Nematode Disease",
        "name_km": "ជំងឺដង្កូវព្រូនឫសលើផ្កាឈូករ័ត្ន",
        "scientific_name": "Meloidogyne incognita",
        "pathogen_type": "other",
        "description_en": "Root-knot nematodes are microscopic obligate endoparasites invading feeder roots. They induce distinct spherical and elongated root galls (knots), impairing water and nutrient uptake and resulting in severe stunting, chlorosis, and midday wilting.",
        "description_km": "ដង្កូវព្រូនឫស គឺជាប៉ារ៉ាស៊ីតតូចៗដែលរស់នៅក្នុងដី និងវាយលុកឫសស្រូបជីរបស់ផ្កាឈូករ័ត្ន។ វាបណ្តាលឱ្យឫសហើមជាដុំពក បង្អាក់ការបឺតស្រូបទឹក និងជីជាតិ ធ្វើឱ្យដើមកន្តឿ និងលឿង។",
        "symptoms": [
            "Pronounced spherical and elongated swelling or galls (knots) on lateral and taproots",
            "Stunted, uneven patchy growth visible across the field",
            "General leaf yellowing and nutrient deficiency symptoms despite adequate fertilizer",
            "Severe midday wilting followed by temporary overnight recovery",
            "Premature plant senescence and significantly reduced seed yield"
        ],
        "causes": [
            "Soil infestation by Meloidogyne incognita / javanica",
            "Light, sandy to sandy-loam soils facilitating nematode motility",
            "Continuous monoculture of susceptible host crops"
        ],
        "treatment_en": "Apply bio-nematicides containing Paecilomyces lilacinus or Bacillus firmus to rhizosphere soil or targeted nematicides in drip irrigation.",
        "treatment_km": "ប្រើប្រាស់ថ្នាំជីវសាស្ត្រ Paecilomyces lilacinus ឬ Bacillus firmus ស្រោចគល់ដើម។",
        "prevention_en": "Rotate with antagonistic cover crops such as sunn hemp (Crotalaria juncea) or marigolds (Tagetes erecta). Practice clean summer fallow.",
        "prevention_km": "បង្វិលដំណាំជាមួយដំណាំកម្ចាត់ព្រូន ដូចជាផ្កាស្បៃរឿង ឬក្រចៅ។ ភ្ជួរហាលដីនៅរដូវក្តៅ។"
    }
}

# Global sunflower pathology reference catalog for uncataloged gap discovery
SUNFLOWER_GLOBAL_CATALOG: list[dict[str, Any]] = [
    {
        "slug": "southern-blight",
        "name_en": "Southern Blight (Stem Rot)",
        "name_km": "ជំងឺរលួយគល់ភាគខាងត្បូង",
        "scientific_name": "Athelia rolfsii (Sclerotium rolfsii)",
        "pathogen_type": "fungal",
        "severity": "High",
        "key_symptoms": "Collar rot at soil line, white fan mycelium, mustard-seed sclerotia, permanent wilt",
        "impact": "Causes sudden stem girdling and severe yield collapse in warm, humid weather."
    },
    {
        "slug": "bacterial-soft-rot",
        "name_en": "Bacterial Soft Rot",
        "name_km": "ជំងឺរលួយទន់ដោយបាក់តេរី",
        "scientific_name": "Pectobacterium carotovorum subsp. carotovorum",
        "pathogen_type": "bacterial",
        "severity": "High",
        "key_symptoms": "Water-soaked olive-brown lesions, internal pith liquefaction with foul odor, head decay",
        "impact": "Rapid stem lodging and flower receptacle breakdown following heavy rains or insect wounds."
    },
    {
        "slug": "sunflower-mosaic-virus",
        "name_en": "Sunflower Mosaic Virus (SMV)",
        "name_km": "ជំងឺវីរុសម៉ូសេអ៊ិចផ្កាឈូករ័ត្ន",
        "scientific_name": "Potyvirus / Sunflower Mosaic Virus",
        "pathogen_type": "viral",
        "severity": "Moderate to High",
        "key_symptoms": "Chlorotic mosaic mottle on young foliage, puckered margins, stunted flower heads",
        "impact": "Aphid-vectored potyvirus that significantly degrades seed fill and oil content."
    },
    {
        "slug": "tobacco-streak-virus",
        "name_en": "Sunflower Necrosis Disease (Tobacco Streak Virus)",
        "name_km": "ជំងឺងាប់ជាលិកាផ្កាឈូករ័ត្ន",
        "scientific_name": "Tobacco streak virus (TSV)",
        "pathogen_type": "viral",
        "severity": "Critical",
        "key_symptoms": "Necrotic ringspots, black petiole & stem streaks, terminal bud necrosis, stem bending",
        "impact": "Thrips-vectored viral disease capable of 100% crop destruction during early vegetative infection."
    },
    {
        "slug": "apical-chlorosis",
        "name_en": "Apical Chlorosis",
        "name_km": "ជំងឺស្លេកត្រួយចុងផ្កាឈូករ័ត្ន",
        "scientific_name": "Pseudomonas syringae pv. tagetis",
        "pathogen_type": "bacterial",
        "severity": "Moderate",
        "key_symptoms": "Bright golden-yellow or bleached apical leaves and bracts, dark green lower foliage",
        "impact": "Tagetitoxin blocks chlorophyll synthesis; seedborne transmission spreads infection."
    },
    {
        "slug": "texas-root-rot",
        "name_en": "Texas Root Rot (Cotton Root Rot)",
        "name_km": "ជំងឺរលួយឫសតិចសាស់",
        "scientific_name": "Phymatotrichopsis omnivora",
        "pathogen_type": "fungal",
        "severity": "Critical",
        "key_symptoms": "Sudden bronze wilt with dead leaves clinging to stem, cortical root decay, woolly mycelial strands",
        "impact": "Devastating in warm, alkaline calcareous soils; destroys taproot vascular bundle."
    },
    {
        "slug": "boron-deficiency",
        "name_en": "Boron Deficiency Disorder",
        "name_km": "បញ្ហាកង្វះជាតិបូរ៉ុន",
        "scientific_name": "Abiotic / Micronutrient Deficiency",
        "pathogen_type": "abiotic",
        "severity": "High",
        "key_symptoms": "Corky horizontal stem cracks, thick brittle cupped leaves, head bent 90°, blank seeds",
        "impact": "Sunflower has the highest boron demand of field crops; deficiency impairs seed formation."
    },
    {
        "slug": "root-knot-nematode",
        "name_en": "Root-Knot Nematode Disease",
        "name_km": "ជំងឺដង្កូវព្រូនឫស",
        "scientific_name": "Meloidogyne incognita",
        "pathogen_type": "other",
        "severity": "Moderate to High",
        "key_symptoms": "Distinct root swellings/galls, patchy yellowing, midday wilting despite moist soil",
        "impact": "Invades root system and reduces water and nutrient absorption across sandy soils."
    }
]


class AdminChatService:
    """Intelligent Assistant for Sunflower Knowledge Base & System Management."""

    def __init__(self):
        self.ollama = get_ollama_service()
        self.conversation_history: dict[str, list[dict]] = {}
        self.pending_drafts: dict[str, dict[str, Any]] = {}

    async def handle_admin_chat(
        self,
        request: AIChatRequest,
        db: AsyncSession,
        user_role: str = "grower",
    ) -> AIChatResponse:
        """Process chat message with full system knowledge, navigation, and role-based CRUD."""
        # Normalize user role alias (e.g. expert -> agronomist)
        clean_role = user_role.lower()
        if clean_role in ["expert", "researcher", "pathologist"]:
            user_role = "agronomist"

        conversation_id = request.conversation_id or "default"

        if conversation_id not in self.conversation_history:
            self.conversation_history[conversation_id] = []

        history = self.conversation_history[conversation_id]

        # Clean up any bogus or invalid pending drafts
        if conversation_id in self.pending_drafts:
            draft_name = self.pending_drafts[conversation_id].get("name_en", "")
            if self._is_bogus_draft_name(draft_name):
                logger.info(f"Purging bogus pending draft: '{draft_name}' for conversation {conversation_id}")
                del self.pending_drafts[conversation_id]

        # Check if conversation is responding to an unconfirmed disease draft
        pending_action = None
        if conversation_id in self.pending_drafts:
            pending_action = self._check_pending_draft_intent(request.message)

        if pending_action:
            action = pending_action
            intent = {"action": pending_action, "data": {}, "query": ""}
        else:
            # Analyze intent
            intent = await self._analyze_intent(request.message, request.locale, db)
            action = intent.get("action", "chat")

        response_message = ""
        actions_taken: list[dict[str, Any]] = []
        navigate_to: str | None = None
        suggested_actions: list[dict[str, Any]] | None = None
        needs_diagnosis = False
        extracted_symptoms: dict[str, Any] | None = None

        # --------------------------------------------------------------------
        # 1. NAVIGATION
        # --------------------------------------------------------------------
        if action == "navigate":
            target = intent.get("data", {}).get("target", "") or intent.get("query", "")
            response_message, actions_taken, navigate_to, suggested_actions = await self._navigate(
                target=target,
                user_role=user_role,
                locale=request.locale,
                db=db,
            )

        # --------------------------------------------------------------------
        # 2. CHECK SYMPTOMS / DIAGNOSIS MATCHING
        # --------------------------------------------------------------------
        elif action == "check_symptoms":
            query_text = intent.get("data", {}).get("query", "") or request.message
            response_message, actions_taken, navigate_to, suggested_actions, needs_diagnosis, extracted_symptoms = (
                await self._check_symptoms(
                    query_text=query_text,
                    db=db,
                    locale=request.locale,
                    user_role=user_role,
                )
            )

        # --------------------------------------------------------------------
        # 3. DISEASE DETAILS
        # --------------------------------------------------------------------
        elif action == "disease_details":
            name = intent.get("data", {}).get("name", "") or intent.get("query", "")
            response_message, actions_taken, navigate_to, suggested_actions = await self._get_disease_details(
                query=name,
                db=db,
                locale=request.locale,
                user_role=user_role,
            )

        # --------------------------------------------------------------------
        # 4. SYMPTOM DETAILS
        # --------------------------------------------------------------------
        elif action == "symptom_details":
            symptom_query = intent.get("data", {}).get("symptom", "") or intent.get("query", "")
            response_message, actions_taken, navigate_to, suggested_actions = await self._get_symptom_details(
                query=symptom_query,
                db=db,
                locale=request.locale,
            )

        # --------------------------------------------------------------------
        # 5. SYSTEM STATS & OVERVIEW
        # --------------------------------------------------------------------
        elif action == "system_stats":
            response_message, actions_taken, navigate_to, suggested_actions = await self._get_system_stats(
                db=db,
                locale=request.locale,
                user_role=user_role,
            )

        elif action == "count_symptoms":
            response_message, actions_taken, navigate_to, suggested_actions = await self._count_symptoms(
                db=db,
                locale=request.locale,
                user_role=user_role,
            )

        elif action == "count_diseases":
            response_message, actions_taken, navigate_to, suggested_actions = await self._count_diseases(
                db=db,
                locale=request.locale,
                user_role=user_role,
            )

        # --------------------------------------------------------------------
        # 6. LIST DATA
        # --------------------------------------------------------------------
        elif action == "list_diseases":
            response_message, actions_taken, navigate_to, suggested_actions = await self._list_diseases(
                db=db,
                locale=request.locale,
                user_role=user_role,
            )

        elif action == "list_symptoms":
            response_message, actions_taken, navigate_to, suggested_actions = await self._list_symptoms(
                db=db,
                locale=request.locale,
            )

        # --------------------------------------------------------------------
        # 7. ROLE-BASED CREATE DISEASE (WITH EXPERT CONFIRMATION FLOW)
        # --------------------------------------------------------------------
        elif action == "create_disease":
            if user_role not in ["admin", "agronomist"]:
                response_message = self._translate(
                    "Permission Denied: Creating diseases requires an Expert Agronomist or Administrator account. As a grower, you can explore published diseases or use the diagnosis checker.",
                    "ការអនុញ្ញាតត្រូវបានបដិសេធ៖ ការបង្កើតជំងឺតម្រូវឱ្យមានគណនីអ្នកជំនាញកសិកម្ម ឬអ្នកគ្រប់គ្រង។",
                    request.locale,
                )
                suggested_actions = [
                    {"label": "Browse Catalog", "path": "/diseases", "type": "navigate"},
                    {"label": "Symptom Checker", "path": "/check", "type": "navigate"},
                ]
            else:
                response_message, actions_taken, navigate_to, suggested_actions = await self._prepare_disease_draft(
                    data=intent.get("data", {}),
                    raw_message=request.message,
                    db=db,
                    locale=request.locale,
                    conversation_id=conversation_id,
                )

        elif action == "confirm_disease":
            if user_role not in ["admin", "agronomist"]:
                response_message = self._translate(
                    "Permission Denied: Confirming and saving diseases requires an Expert Agronomist or Administrator account.",
                    "ការអនុញ្ញាតត្រូវបានបដិសេធ៖ ការបន្ថែមជំងឺតម្រូវឱ្យមានគណនីអ្នកជំនាញកសិកម្ម ឬអ្នកគ្រប់គ្រង។",
                    request.locale,
                )
            else:
                response_message, actions_taken, navigate_to, suggested_actions = await self._commit_pending_disease(
                    conversation_id=conversation_id,
                    db=db,
                    locale=request.locale,
                    user_role=user_role,
                )

        elif action == "cancel_disease":
            response_message, actions_taken, navigate_to, suggested_actions = await self._cancel_pending_disease(
                conversation_id=conversation_id,
                locale=request.locale,
            )

        elif action == "edit_pending_disease":
            response_message, actions_taken, navigate_to, suggested_actions = await self._edit_pending_disease(
                conversation_id=conversation_id,
                instruction=request.message,
                db=db,
                locale=request.locale,
            )

        # --------------------------------------------------------------------
        # 8. ROLE-BASED UPDATE DISEASE
        # --------------------------------------------------------------------
        elif action == "update_disease":
            if user_role not in ["admin", "agronomist"]:
                response_message = self._translate(
                    "Permission Denied: Updating disease data requires an Expert Agronomist or Administrator account.",
                    "ការអនុញ្ញាតត្រូវបានបដិសេធ៖ ការកែប្រែទិន្នន័យជំងឺតម្រូវឱ្យមានគណនីអ្នកជំនាញកសិកម្ម ឬអ្នកគ្រប់គ្រង។",
                    request.locale,
                )
                suggested_actions = [{"label": "Browse Catalog", "path": "/diseases", "type": "navigate"}]
            else:
                response_message, actions_taken, navigate_to, suggested_actions = await self._update_disease(
                    intent.get("data", {}),
                    db,
                    request.locale,
                )

        # --------------------------------------------------------------------
        # 9. ROLE-BASED DELETE DISEASE (ADMIN ONLY)
        # --------------------------------------------------------------------
        elif action == "delete_disease":
            if user_role == "agronomist":
                disease_target = intent.get("data", {}).get("disease_name", "") or "this disease"
                response_message = self._translate(
                    f"Permission Notice: As an Expert Agronomist, you can create and edit diseases, but only System Administrators have permanent deletion authority. You can unpublish or modify '{disease_target}' in the disease editor.",
                    f"ការជូនដំណឹងអំពីសិទ្ធិ៖ ក្នុងនាមជាអ្នកជំនាញកសិកម្ម អ្នកអាចបង្កើត និងកែប្រែជំងឺបាន ប៉ុន្តែមានតែអ្នកគ្រប់គ្រងប្រព័ន្ធប៉ុណ្ណោះដែលអាចលុបជាអចិន្ត្រៃយ៍បាន។ អ្នកអាចកែប្រែ '{disease_target}' ក្នុងផ្ទាំងកែប្រែជំងឺ។",
                    request.locale,
                )
                suggested_actions = [
                    {"label": "Manage Diseases", "path": "/admin/diseases", "type": "navigate"},
                ]
            elif user_role != "admin":
                response_message = self._translate(
                    "Permission Denied: Only System Administrators can delete disease records.",
                    "ការអនុញ្ញាតត្រូវបានបដិសេធ៖ មានតែអ្នកគ្រប់គ្រងប្រព័ន្ធប៉ុណ្ណោះដែលអាចលុបជំងឺបាន។",
                    request.locale,
                )
                suggested_actions = [{"label": "Browse Catalog", "path": "/diseases", "type": "navigate"}]
            else:
                response_message, actions_taken, navigate_to, suggested_actions = await self._delete_disease(
                    intent.get("data", {}),
                    db,
                    request.locale,
                )

        # --------------------------------------------------------------------
        # 10. ROLE-BASED CREATE SYMPTOM
        # --------------------------------------------------------------------
        elif action == "create_symptom":
            if user_role not in ["admin", "agronomist"]:
                response_message = self._translate(
                    "Permission Denied: Creating symptoms requires an Expert Agronomist or Administrator account.",
                    "ការអនុញ្ញាតត្រូវបានបដិសេធ៖ ការបង្កើតរោគសញ្ញាតម្រូវឱ្យមានគណនីអ្នកជំនាញកសិកម្ម ឬអ្នកគ្រប់គ្រង។",
                    request.locale,
                )
                suggested_actions = [{"label": "Symptom Checker", "path": "/check", "type": "navigate"}]
            else:
                response_message, actions_taken, navigate_to, suggested_actions = await self._create_symptom(
                    intent.get("data", {}),
                    db,
                    request.locale,
                )

        # --------------------------------------------------------------------
        # 11. ROLE-BASED UPDATE SYMPTOM
        # --------------------------------------------------------------------
        elif action == "update_symptom":
            if user_role not in ["admin", "agronomist"]:
                response_message = self._translate(
                    "Permission Denied: Updating symptoms requires an Expert Agronomist or Administrator account.",
                    "ការអនុញ្ញាតត្រូវបានបដិសេធ៖ ការកែប្រែរោគសញ្ញាតម្រូវឱ្យមានគណនីអ្នកជំនាញកសិកម្ម ឬអ្នកគ្រប់គ្រង។",
                    request.locale,
                )
            else:
                response_message, actions_taken, navigate_to, suggested_actions = await self._update_symptom(
                    intent.get("data", {}),
                    db,
                    request.locale,
                )

        # --------------------------------------------------------------------
        # 12. ROLE-BASED DELETE SYMPTOM (ADMIN ONLY)
        # --------------------------------------------------------------------
        elif action == "delete_symptom":
            if user_role == "agronomist":
                response_message = self._translate(
                    "Permission Notice: Only System Administrators can permanently delete symptoms. As an agronomist, you can update symptom descriptions in the admin panel.",
                    "ការជូនដំណឹងអំពីសិទ្ធិ៖ មានតែអ្នកគ្រប់គ្រងប្រព័ន្ធប៉ុណ្ណោះដែលអាចលុបរោគសញ្ញាជាអចិន្ត្រៃយ៍បាន។",
                    request.locale,
                )
                suggested_actions = [{"label": "Manage Symptoms", "path": "/admin/symptoms", "type": "navigate"}]
            elif user_role != "admin":
                response_message = self._translate(
                    "Permission Denied: Only System Administrators can delete symptoms.",
                    "ការអនុញ្ញាតត្រូវបានបដិសេធ៖ មានតែអ្នកគ្រប់គ្រងប្រព័ន្ធប៉ុណ្ណោះដែលអាចលុបរោគសញ្ញាបាន។",
                    request.locale,
                )
            else:
                response_message, actions_taken, navigate_to, suggested_actions = await self._delete_symptom(
                    intent.get("data", {}),
                    db,
                    request.locale,
                )

        # --------------------------------------------------------------------
        # 13. KNOWLEDGE GAP DISCOVERY (FIND MISSING / UNRECORDED DISEASES)
        # --------------------------------------------------------------------
        elif action == "find_missing_data":
            try:
                response_message, actions_taken, navigate_to, suggested_actions = await self._find_missing_data(
                    db=db,
                    locale=request.locale,
                    user_role=user_role,
                )
            except Exception as e:
                logger.exception("Error in _find_missing_data: %s", e)
                response_message = self._translate(
                    f"⚠️ An error occurred while scanning for missing diseases: {e!s}. Please try again.",
                    f"⚠️ មានកំហុសក្នុងការស្កេនរកជំងឺដែលខ្វះ: {e!s}។ សូមព្យាយាមម្តងទៀត។",
                    request.locale,
                )

        # --------------------------------------------------------------------
        # 14. DATA MANAGEMENT & CRUD CONTROL GUIDE
        # --------------------------------------------------------------------
        elif action == "data_management_guide":
            response_message, actions_taken, navigate_to, suggested_actions = await self._data_management_guide(
                locale=request.locale,
                user_role=user_role,
            )

        # --------------------------------------------------------------------
        # 15. DIFFERENTIAL DISEASE COMPARISON
        # --------------------------------------------------------------------
        elif action == "compare_diseases":
            response_message, actions_taken, navigate_to, suggested_actions = await self._compare_diseases(
                query_text=intent.get("query", "") or request.message,
                db=db,
                locale=request.locale,
            )

        # --------------------------------------------------------------------
        # 16. GROWTH STAGE SCOUTING ADVISOR
        # --------------------------------------------------------------------
        elif action == "growth_stage_scout":
            response_message, actions_taken, navigate_to, suggested_actions = await self._growth_stage_scout(
                stage_query=intent.get("data", {}).get("stage", "") or request.message,
                locale=request.locale,
                db=db,
            )

        # --------------------------------------------------------------------
        # 17. TREATMENT PRESCRIPTION & FUNGICIDE ADVISOR
        # --------------------------------------------------------------------
        elif action == "treatment_prescription":
            response_message, actions_taken, navigate_to, suggested_actions = await self._get_treatment_prescription(
                disease_query=intent.get("data", {}).get("disease", "") or request.message,
                db=db,
                locale=request.locale,
            )

        # --------------------------------------------------------------------
        # 18. SEARCH
        # --------------------------------------------------------------------
        elif action == "search":
            response_message, actions_taken, navigate_to, suggested_actions = await self._search_data(
                intent.get("query", ""),
                db,
                request.locale,
                user_role,
            )

        # --------------------------------------------------------------------
        # 16. HELP
        # --------------------------------------------------------------------
        elif action == "help":
            response_message, suggested_actions = self._get_help_message(request.locale, user_role)

        # --------------------------------------------------------------------
        # GROWER HELP / HOW-TO-USE GUIDE
        # --------------------------------------------------------------------
        elif action == "grower_help":
            response_message, suggested_actions = self._get_grower_help(request.locale, user_role)

        # --------------------------------------------------------------------
        # 17. GENERAL CONVERSATION FALLBACK
        # --------------------------------------------------------------------
        else:
            response_message, suggested_actions = await self._general_chat(
                request.message,
                history,
                request.locale,
                user_role,
                db,
            )

        # If there is a pending draft and the action was not confirming/cancelling/editing it,
        # append a reminder note so the expert doesn't lose track of their unconfirmed draft
        if conversation_id in self.pending_drafts and action not in ["create_disease", "confirm_disease", "cancel_disease", "edit_pending_disease"]:
            draft_name = self.pending_drafts[conversation_id].get("name_en", "disease")
            if not self._is_bogus_draft_name(draft_name):
                reminder = self._translate(
                    f"\n\n*(Note: You still have an unconfirmed draft for '**{draft_name}**'. Reply '**confirm**' to save it to database or '**cancel**' to discard.)*",
                    f"\n\n*(សម្គាល់៖ អ្នកនៅតែមានសេចក្តីព្រាងជំងឺ '**{draft_name}**' ដែលមិនទាន់បានបញ្ជាក់។ សូមឆ្លើយ '**យល់ព្រម**' ដើម្បីរក្សាទុក ឬ '**បោះបង់**' ដើម្បីលុបចោល។)*",
                    request.locale,
                )
                response_message += reminder
            else:
                del self.pending_drafts[conversation_id]

        # Update conversation history
        history.append({"role": "user", "content": request.message})
        history.append({"role": "assistant", "content": response_message})
        if len(history) > 20:
            self.conversation_history[conversation_id] = history[-20:]

        return AIChatResponse(
            message=response_message,
            conversation_id=conversation_id,
            needs_diagnosis=needs_diagnosis,
            extracted_symptoms=extracted_symptoms,
            navigate_to=navigate_to,
            action_type=action,
            suggested_actions=suggested_actions,
            metadata={
                "intent": action,
                "actions_taken": actions_taken,
                "user_role": user_role,
            },
        )

    # ========================================================================
    # INTENT ANALYSIS
    # ========================================================================

    async def _analyze_intent(
        self,
        message: str,
        locale: str,
        db: AsyncSession,
    ) -> dict[str, Any]:
        """Analyze user message with keyword patterns and AI fallback."""
        message_lower = message.lower().strip()

        # 0. DATA MANAGEMENT & CRUD CONTROL GUIDE PATTERNS
        management_phrases = [
            "edit delete or add", "edit delete add", "help me edit delete",
            "edit or delete", "add or delete", "delete or add",
            "find new data to help me edit", "how to edit delete",
            "manage data", "manage diseases", "manage symptoms",
            "how to add delete", "how can i add", "how can i edit",
            "ជួយកែសម្រួល លុប ឬបន្ថែម", "គ្រប់គ្រងទិន្នន័យ"
        ]
        if any(phrase in message_lower for phrase in management_phrases) or (
            all(w in message_lower for w in ["edit", "delete", "add"])
        ):
            return {"action": "data_management_guide", "data": {}, "query": ""}

        # 0. FIND MISSING DATA / UNRECORDED DISEASES PATTERNS (Knowledge Gap Discovery)
        missing_data_phrases = [
            "not yet have", "not have yet", "not yet in", "not in system",
            "not in database", "missing disease", "missing diseases", "missing data",
            "find new 1 that my system not yet have", "find new disease", "find new diseases",
            "find new data", "suggest new disease", "suggest new diseases",
            "what diseases are missing", "what is missing", "uncataloged",
            "new diseases to add", "other diseases", "discover new",
            "ជំងឺដែលមិនទាន់មាន", "ជំងឺដែលខ្វះ", "ស្វែងរកជំងឺថ្មី", "ទិន្នន័យដែលមិនទាន់មាន"
        ]
        if any(phrase in message_lower for phrase in missing_data_phrases) or (
            ("find" in message_lower or "search" in message_lower or "suggest" in message_lower or "help" in message_lower) and
            any(w in message_lower for w in ["not yet", "missing", "new disease", "new 1", "new one", "unrecorded"])
        ):
            return {"action": "find_missing_data", "data": {}, "query": ""}

        # NAVIGATION PATTERNS
        nav_verbs = [
            "go to", "take me to", "bring me to", "open", "show page",
            "navigate to", "visit", "bring user to", "ទៅកាន់", "បើកទំព័រ", "បើក"
        ]
        for verb in nav_verbs:
            if message_lower.startswith(verb) or f" {verb} " in f" {message_lower} ":
                target = re.sub(
                    r"^(go\s+to|take\s+me\s+to|bring\s+me\s+to|bring\s+user\s+to|open|show\s+page|navigate\s+to|visit|ទៅកាន់|បើកទំព័រ|បើក)\s*",
                    "",
                    message,
                    flags=re.IGNORECASE,
                ).strip(" '\"?!.")
                return {"action": "navigate", "data": {"target": target}, "query": target}

        # COUNT SYMPTOMS (Singular and Plural, English and Khmer)
        if re.search(r"\b(how\s+many|count(\s+of)?|number\s+of|total)\s+symptoms?\b", message_lower) or any(
            k in message_lower for k in ["មានរោគសញ្ញាប៉ុន្មាន", "ចំនួនរោគសញ្ញា", "រោគសញ្ញាសរុប", "រោគសញ្ញាទាំងអស់មានប៉ុន្មាន"]
        ):
            return {"action": "count_symptoms", "data": {}, "query": ""}

        # COUNT DISEASES (Singular and Plural, English and Khmer)
        if re.search(r"\b(how\s+many|count(\s+of)?|number\s+of|total)\s+diseases?\b", message_lower) or any(
            k in message_lower for k in ["មានជំងឺប៉ុន្មាន", "ចំនួនជំងឺ", "ជំងឺសរុប", "ជំងឺទាំងអស់មានប៉ុន្មាន"]
        ):
            return {"action": "count_diseases", "data": {}, "query": ""}

        # SYSTEM STATS / OVERVIEW PATTERNS
        stats_keywords = [
            "system status", "system stats", "overview", "database stats", "database status",
            "knowledge base stats", "how many rules", "total rules", "ស្ថានភាពប្រព័ន្ធ", "ទិន្នន័យទាំងអស់", "ស្ថិតិប្រព័ន្ធ"
        ]
        if any(keyword in message_lower for keyword in stats_keywords):
            return {"action": "system_stats", "data": {}, "query": ""}

        # GROWER HELP / HOW-TO-USE PATTERNS
        grower_help_phrases = [
            "how to check symptom", "how to check symptoms", "how do i check",
            "how to use this", "how to use the system", "how does this work",
            "how can i diagnose", "how to diagnose", "what can you do",
            "how to upload", "how to send photo", "how to analyze",
            "guide me", "walk me through", "show me how", "teach me",
            "ប្រើប្រាស់ប្រព័ន្ធ", "តើត្រូវពិនិត្យយ៉ាងម៉េច", "តើត្រូវប្រើយ៉ាងម៉េច",
            "របៀបពិនិត្យរោគសញ្ញា", "របៀបប្រើ",
        ]
        if any(phrase in message_lower for phrase in grower_help_phrases):
            return {"action": "grower_help", "data": {}, "query": ""}

        # CHECK SYMPTOMS / DIAGNOSIS PATTERNS
        check_keywords = [
            "check symptom", "check symptoms", "diagnose", "my plant has",
            "sunflower has", "symptoms are", "what disease has", "which disease has",
            "i see", "symptom:", "symptoms:", "leaf spots", "cinnamon pustules",
            "white mold", "stem rot", "head rot", "apical chlorosis",
            "wilting leaves", "my leaves", "my sunflower", "my plant",
            "leaves are", "leaf is", "stem is", "roots are", "head is",
            "brown spots", "black spots", "yellow spots", "white spots",
            "yellow leaves", "brown leaves", "wilting", "drooping",
            "dying plant", "sick plant", "plant is sick", "plant is dying",
            "mold on", "fungus on", "rot on", "spots on",
            "stunted", "not growing", "discolored", "deformed",
            "pustules", "lesion", "necrosis", "chlorosis", "blight",
            "ពិនិត្យរោគសញ្ញា", "វិភាគរោគសញ្ញា", "រោគសញ្ញាគឺ",
            "ស្លឹកឡើងលឿង", "ស្លឹកមានចំណុច", "ដើមរលួយ", "ឫសរលួយ",
        ]
        if any(keyword in message_lower for keyword in check_keywords) and not any(
            x in message_lower for x in ["list all", "delete", "create", "update", "draft", "add", "new", "បង្កើត", "បន្ថែម"]
        ):
            return {"action": "check_symptoms", "data": {"query": message}, "query": message}

        # DIFFERENTIAL DISEASE COMPARISON PATTERNS
        if re.search(r"\b(compare|difference\s+between|vs\.?|versus)\b", message_lower) or any(k in message_lower for k in ["ប្រៀបធៀប", "ភាពខុសគ្នា"]):
            return {"action": "compare_diseases", "data": {"query": message}, "query": message}

        # GROWTH STAGE SCOUTING PATTERNS
        stage_keywords = [
            "growth stage", "growth stages", "flowering stage", "seedling stage", "vegetative stage",
            "bud stage", "budding stage", "ripening stage", "maturity stage", "r1", "r4", "r5", "v2", "v4", "v8",
            "scouting calendar", "scout diseases", "stage scout", "ដំណាក់កាលលូតលាស់", "ដំណាក់កាលចេញផ្កា"
        ]
        if any(keyword in message_lower for keyword in stage_keywords) and not any(k in message_lower for k in ["create", "delete", "edit", "draft", "add", "new"]):
            return {"action": "growth_stage_scout", "data": {"stage": message}, "query": message}

        # TREATMENT & PRESCRIPTION PATTERNS
        treat_keywords = [
            "how to treat", "treatment for", "how to cure", "chemical control", "fungicide for",
            "spray for", "management of", "how to control", "organic treatment", "prescription for",
            "active ingredient", "វិធីព្យាបាល", "ថ្នាំកម្ចាត់", "ថ្នាំសម្លាប់មេរោគ", "វិធីទប់ស្កាត់"
        ]
        if any(keyword in message_lower for keyword in treat_keywords) and not any(k in message_lower for k in ["create", "delete", "edit", "draft", "add", "new"]):
            return {"action": "treatment_prescription", "data": {"disease": message}, "query": message}

        # DISEASE DETAILS PATTERNS
        disease_info_keywords = [
            "tell me about", "what is", "information on", "details about",
            "explain disease", "explain", "រៀបរាប់អំពី", "ព័ត៌មានពី", "តើជំងឺ"
        ]
        for verb in disease_info_keywords:
            if verb in message_lower:
                target = re.sub(
                    r"^(tell\s+me\s+about|what\s+is|information\s+on|details\s+about|explain\s+disease|explain|រៀបរាប់អំពី|ព័ត៌មានពី|តើជំងឺ)\s*",
                    "",
                    message,
                    flags=re.IGNORECASE,
                ).strip(" '\"?!.")
                target = re.sub(r"^(the\s+disease|disease)\s+", "", target, flags=re.IGNORECASE).strip()
                return {"action": "disease_details", "data": {"name": target}, "query": target}

        # SYMPTOM DETAILS PATTERNS
        symptom_info_keywords = ["what causes", "which disease causes", "symptom details", "មូលហេតុនៃរោគសញ្ញា"]
        for verb in symptom_info_keywords:
            if verb in message_lower:
                target = re.sub(
                    r"^(what\s+causes|which\s+disease\s+causes|symptom\s+details|មូលហេតុនៃរោគសញ្ញា)\s*",
                    "",
                    message,
                    flags=re.IGNORECASE,
                ).strip(" '\"?!.")
                return {"action": "symptom_details", "data": {"symptom": target}, "query": target}

        # Guard against meta-discussions or general questions being treated as entity mutations
        is_meta_inquiry = any(
            phrase in message_lower
            for phrase in [
                "i want", "can u", "can you", "help me", "how to", "how do i", "how can i",
                "should", "would like", "before", "confirm before", "auto add", "autto add",
                "discussing", "what if", "when i", "if i", "tell me how", "my ai", "ai agent"
            ]
        )

        # DELETE PATTERNS
        if not is_meta_inquiry and (re.search(r"\b(delete|remove|drop)\b", message_lower) or any(k in message_lower for k in ["លុប"])):
            if "disease" in message_lower or "ជំងឺ" in message_lower:
                name = self._extract_entity_name(message, ["delete", "remove", "disease", "លុប", "ជំងឺ"])
                if self._is_valid_entity_name(name):
                    return {"action": "delete_disease", "data": {"disease_name": name, "name": name}, "query": ""}
            elif "symptom" in message_lower or "រោគសញ្ញា" in message_lower:
                name = self._extract_entity_name(message, ["delete", "remove", "symptom", "លុប", "រោគសញ្ញា"])
                if self._is_valid_entity_name(name):
                    return {"action": "delete_symptom", "data": {"symptom_label": name, "label": name}, "query": ""}

        # CREATE / DRAFT PATTERNS
        if not is_meta_inquiry and (re.search(r"\b(create|add|new|draft)\b", message_lower) or any(k in message_lower for k in ["បង្កើត", "បន្ថែម"])):
            if "disease" in message_lower or "ជំងឺ" in message_lower or "draft" in message_lower:
                name = self._extract_entity_name(message, ["create", "add", "new", "draft", "disease", "បង្កើត", "បន្ថែម", "ជំងឺ", "➕"])
                if self._is_valid_entity_name(name):
                    return {
                        "action": "create_disease",
                        "data": {
                            "name": name,
                            "pathogen_type": self._extract_pathogen_type(message),
                            "description": message,
                        },
                        "query": "",
                    }
            elif "symptom" in message_lower or "រោគសញ្ញា" in message_lower:
                name = self._extract_entity_name(message, ["create", "add", "new", "draft", "symptom", "បង្កើត", "បន្ថែម", "រោគសញ្ញា"])
                if self._is_valid_entity_name(name):
                    return {"action": "create_symptom", "data": {"label": name, "category": "leaf"}, "query": ""}

        # UPDATE PATTERNS
        if not is_meta_inquiry and (re.search(r"\b(update|edit|modify|change)\b", message_lower) or any(k in message_lower for k in ["កែសម្រួល", "ធ្វើបច្ចុប្បន្នភាព"])):
            if "disease" in message_lower or "ជំងឺ" in message_lower:
                name = self._extract_entity_name(message, ["update", "edit", "modify", "disease", "កែសម្រួល", "ជំងឺ"])
                if self._is_valid_entity_name(name):
                    return {
                        "action": "update_disease",
                        "data": {"disease_name": name, "name": name, "description": message},
                        "query": "",
                    }
            elif "symptom" in message_lower or "រោគសញ្ញា" in message_lower:
                name = self._extract_entity_name(message, ["update", "edit", "modify", "symptom", "កែសម្រួល", "រោគសញ្ញា"])
                if self._is_valid_entity_name(name):
                    return {"action": "update_symptom", "data": {"symptom_label": name, "label": name}, "query": ""}

        # LIST PATTERNS (word boundary so 'blisters' does not match 'list')
        if re.search(r"\b(list(\s+all)?|show\s+all|display\s+all)\b", message_lower) or any(
            k in message_lower for k in ["បង្ហាញទាំងអស់", "បញ្ជីទាំងអស់"]
        ):
            if "disease" in message_lower or "ជំងឺ" in message_lower:
                return {"action": "list_diseases", "data": {}, "query": ""}
            elif "symptom" in message_lower or "រោគសញ្ញា" in message_lower:
                return {"action": "list_symptoms", "data": {}, "query": ""}

        # SEARCH PATTERNS
        search_keywords = ["search", "find", "look for", "ស្វែងរក"]
        if any(keyword in message_lower for keyword in search_keywords):
            query = re.sub(r"^(search(\s+for)?|find|look\s+for|ស្វែងរក)\s*", "", message, flags=re.IGNORECASE).strip()
            query = query.strip("\"'?!. ")
            return {"action": "search", "data": {}, "query": query}

        # HELP PATTERNS
        help_keywords = ["help", "commands", "what can you do", "ជំនួយ"]
        if any(keyword in message_lower for keyword in help_keywords):
            return {"action": "help", "data": {}, "query": ""}

        # CHECK IF INPUT IS SIMPLY A KNOWN DISEASE NAME
        try:
            d_res = await db.execute(
                select(Disease.slug).where(
                    or_(
                        Disease.slug.ilike(f"%{message_lower.replace(' ', '-')}%"),
                        Disease.slug.ilike(f"%{message_lower}%"),
                    )
                ).limit(1)
            )
            found_slug = d_res.scalar_one_or_none()
            if found_slug and len(message_lower) > 3:
                return {"action": "disease_details", "data": {"name": message}, "query": message}
        except Exception:
            pass

        # AI FALLBACK INTENT DETECTION
        prompt = f"""Analyze this user message for a sunflower crop health & admin system:
Message: "{message}"

Identify the most appropriate intent from:
- navigate: User wants to go to a page (extract target)
- check_symptoms: User describes crop symptoms, asks what disease fits (extract query)
- disease_details: User asks for full details of a disease (extract name)
- symptom_details: User asks which diseases cause a symptom (extract symptom)
- system_stats: User asks for system stats or overview
- list_diseases: List all diseases
- list_symptoms: List all symptoms
- create_disease: Create new disease
- update_disease: Update disease
- delete_disease: Delete disease
- create_symptom: Create symptom
- update_symptom: Update symptom
- delete_symptom: Delete symptom
- search: Search database
- help: Commands help
- chat: General conversation

Return JSON only:
{{
  "action": "action_name",
  "data": {{}},
  "query": ""
}}
"""
        try:
            response = await asyncio.wait_for(
                self.ollama.generate(prompt=prompt, temperature=0.1, json_mode=True),
                timeout=8.0,
            )
            return json.loads(response)
        except Exception:
            return {"action": "chat", "data": {}, "query": ""}

    # ========================================================================
    # 1. NAVIGATION HANDLER ("Bring user to any page")
    # ========================================================================

    async def _navigate(
        self,
        target: str,
        user_role: str,
        locale: str,
        db: AsyncSession,
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]]]:
        """Resolve navigation request and return destination path & action pills."""
        target_lower = target.lower().strip()

        # Public Routes
        if any(k in target_lower for k in ["catalog", "browse", "disease list", "បញ្ជីជំងឺ"]) or target_lower == "diseases":
            path = "/diseases"
            name = "Diseases Catalog"
            msg = self._translate(
                f"Opening the **{name}** page (`{path}`).",
                f"កំពុងបើកទំព័រ **កាតាឡុកជំងឺ** (`{path}`)។",
                locale,
            )
            return msg, [{"action": "navigate", "path": path}], path, [{"label": name, "path": path, "type": "navigate"}]

        if any(k in target_lower for k in ["compare", "comparison", "ប្រៀបធៀប"]):
            path = "/diseases/compare"
            name = "Disease Comparison"
            msg = self._translate(
                f"Opening **{name}** (`{path}`). You can compare symptoms and traits across sunflower diseases.",
                f"កំពុងបើកទំព័រ **ប្រៀបធៀបជំងឺ** (`{path}`)។",
                locale,
            )
            return msg, [{"action": "navigate", "path": path}], path, [{"label": name, "path": path, "type": "navigate"}]

        if any(k in target_lower for k in ["check", "checker", "diagnos", "ពិនិត្យ", "វិភាគ"]):
            path = "/check"
            name = "Diagnostic Symptom Checker"
            msg = self._translate(
                f"Taking you to the **{name}** (`{path}`). Select symptoms on the sunflower diagram to run interactive Bayesian diagnosis.",
                f"កំពុងនាំអ្នកទៅកាន់ **ការពិនិត្យរោគសញ្ញា** (`{path}`)។",
                locale,
            )
            return msg, [{"action": "navigate", "path": path}], path, [{"label": name, "path": path, "type": "navigate"}]

        if any(k in target_lower for k in ["history", "past", "record", "ប្រវត្តិ"]):
            path = "/history"
            name = "Diagnosis History"
            msg = self._translate(
                f"Navigating to your **{name}** (`{path}`).",
                f"កំពុងនាំអ្នកទៅកាន់ **ប្រវត្តិការវិភាគ** (`{path}`)។",
                locale,
            )
            return msg, [{"action": "navigate", "path": path}], path, [{"label": name, "path": path, "type": "navigate"}]

        if any(k in target_lower for k in ["feedback", "report", "review", "មតិ"]):
            path = "/feedback"
            name = "Feedback Submission"
            msg = self._translate(
                f"Opening the **{name}** page (`{path}`).",
                f"កំពុងបើកទំព័រ **មតិកែលម្អ** (`{path}`)។",
                locale,
            )
            return msg, [{"action": "navigate", "path": path}], path, [{"label": name, "path": path, "type": "navigate"}]

        if any(k in target_lower for k in ["profile", "account", "settings", "គណនី"]):
            path = "/profile"
            name = "User Profile"
            msg = self._translate(
                f"Navigating to **{name}** (`{path}`).",
                f"កំពុងនាំអ្នកទៅកាន់ **គណនីអ្នកប្រើប្រាស់** (`{path}`)។",
                locale,
            )
            return msg, [{"action": "navigate", "path": path}], path, [{"label": name, "path": path, "type": "navigate"}]

        # Admin Routes with Role Protection
        is_admin_or_expert = user_role in ["admin", "agronomist"]
        is_admin_only = user_role == "admin"

        if "admin" in target_lower or "manage" in target_lower or "ផ្ទាំងគ្រប់គ្រង" in target_lower:
            if not is_admin_or_expert:
                msg = self._translate(
                    "Access Restricted: Administrative pages require Expert Agronomist or Administrator credentials. You can explore public features below:",
                    "ការចូលប្រើត្រូវបានកម្រិត៖ ទំព័រអ្នកគ្រប់គ្រងតម្រូវឱ្យមានគណនីអ្នកជំនាញកសិកម្ម ឬអ្នកគ្រប់គ្រង។",
                    locale,
                )
                return msg, [], None, [
                    {"label": "Browse Catalog", "path": "/diseases", "type": "navigate"},
                    {"label": "Symptom Checker", "path": "/check", "type": "navigate"},
                ]

            if any(k in target_lower for k in ["new disease", "create disease", "add disease"]):
                path = "/admin/diseases/new"
                name = "New Disease Authoring"
                return (
                    self._translate(f"Opening **{name}** (`{path}`).", f"កំពុងបើក **បង្កើតជំងឺថ្មី** (`{path}`)។", locale),
                    [{"action": "navigate", "path": path}],
                    path,
                    [{"label": name, "path": path, "type": "navigate"}],
                )

            if "symptom" in target_lower:
                path = "/admin/symptoms"
                name = "Symptom Management"
                return (
                    self._translate(f"Opening **{name}** (`{path}`).", f"កំពុងបើក **ការគ្រប់គ្រងរោគសញ្ញា** (`{path}`)។", locale),
                    [{"action": "navigate", "path": path}],
                    path,
                    [{"label": name, "path": path, "type": "navigate"}],
                )

            if "feedback" in target_lower:
                path = "/admin/feedback"
                name = "Admin Feedback Review"
                return (
                    self._translate(f"Opening **{name}** (`{path}`).", f"កំពុងបើក **ការគ្រប់គ្រងមតិ** (`{path}`)។", locale),
                    [{"action": "navigate", "path": path}],
                    path,
                    [{"label": name, "path": path, "type": "navigate"}],
                )

            if "rule" in target_lower:
                path = "/admin/rulesets"
                name = "Ruleset Management"
                return (
                    self._translate(f"Opening **{name}** (`{path}`).", f"កំពុងបើក **ការគ្រប់គ្រងច្បាប់** (`{path}`)។", locale),
                    [{"action": "navigate", "path": path}],
                    path,
                    [{"label": name, "path": path, "type": "navigate"}],
                )

            if any(k in target_lower for k in ["user", "role", "permission"]):
                if not is_admin_only:
                    msg = self._translate(
                        "Permission Denied: User and role administration is restricted to System Administrators. As an agronomist, you can manage diseases and symptoms.",
                        "ការអនុញ្ញាតត្រូវបានបដិសេធ៖ ការគ្រប់គ្រងអ្នកប្រើប្រាស់ និងតួនាទីត្រូវបានកម្រិតសម្រាប់តែអ្នកគ្រប់គ្រងប្រព័ន្ធប៉ុណ្ណោះ។",
                        locale,
                    )
                    return msg, [], None, [
                        {"label": "Manage Diseases", "path": "/admin/diseases", "type": "navigate"},
                        {"label": "Manage Symptoms", "path": "/admin/symptoms", "type": "navigate"},
                    ]
                subpath = "/admin/roles" if "role" in target_lower or "permission" in target_lower else "/admin/users"
                name = "Role Permissions" if "role" in target_lower else "User Accounts"
                return (
                    self._translate(f"Opening **{name}** (`{subpath}`).", f"កំពុងបើក **{name}** (`{subpath}`)។", locale),
                    [{"action": "navigate", "path": subpath}],
                    subpath,
                    [{"label": name, "path": subpath, "type": "navigate"}],
                )

            # Default admin overview
            path = "/admin/diseases" if "disease" in target_lower else "/admin"
            name = "Disease Catalog Management" if "disease" in target_lower else "Admin Dashboard"
            return (
                self._translate(f"Opening **{name}** (`{path}`).", f"កំពុងបើក **{name}** (`{path}`)។", locale),
                [{"action": "navigate", "path": path}],
                path,
                [{"label": name, "path": path, "type": "navigate"}],
            )

        # Check for Specific Disease Navigation (e.g. "go to sunflower rust", "take me to downy mildew")
        clean_target = re.sub(r"^(disease|ជំងឺ)\s+", "", target_lower).strip()
        disease = await self._find_disease(clean_target, db)
        if disease:
            trans_res = await db.execute(
                select(Translation.value).where(
                    Translation.entity_type == "disease",
                    Translation.entity_id == disease.id,
                    Translation.field == "name",
                    Translation.locale == locale,
                )
            )
            d_name = trans_res.scalar_one_or_none() or disease.slug.replace("-", " ").title()
            path = f"/diseases/{disease.slug}"
            actions = [{"label": f"View {d_name}", "path": path, "type": "navigate"}]
            if is_admin_or_expert:
                actions.append({"label": "Edit in Admin", "path": f"/admin/diseases/{disease.id}", "type": "admin_edit"})

            msg = self._translate(
                f"Taking you directly to **{d_name}** (`{path}`).",
                f"កំពុងនាំអ្នកទៅកាន់ **{d_name}** (`{path}`)។",
                locale,
            )
            return msg, [{"action": "navigate", "path": path}], path, actions

        # Fallback if target page isn't matched
        msg = self._translate(
            f"I couldn't identify the specific page '{target}'. Here are the main system sections you can jump to:",
            f"មិនអាចកំណត់ទំព័រ '{target}' បានទេ។ ខាងក្រោមនេះជាផ្នែកសំខាន់ៗនៃប្រព័ន្ធ:",
            locale,
        )
        default_actions = [
            {"label": "Diseases Catalog", "path": "/diseases", "type": "navigate"},
            {"label": "Symptom Checker", "path": "/check", "type": "navigate"},
            {"label": "Compare Diseases", "path": "/diseases/compare", "type": "navigate"},
        ]
        if is_admin_or_expert:
            default_actions.append({"label": "Admin Panel", "path": "/admin", "type": "navigate"})
        return msg, [], None, default_actions

    # ========================================================================
    # 2. CHECK SYMPTOMS & CROSS-REFERENCE DISEASES ("Check symptom go to disease")
    # ========================================================================

    async def _check_symptoms(
        self,
        query_text: str,
        db: AsyncSession,
        locale: str,
        user_role: str,
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]], bool, dict[str, Any] | None]:
        """Correlate observable symptoms with disease knowledge base and Bayesian rules."""
        # 1. Fetch all symptoms with categories and translations
        symptom_res = await db.execute(
            select(Symptom)
            .options(selectinload(Symptom.category))
            .order_by(Symptom.category_id, Symptom.code)
        )
        all_symptoms = symptom_res.scalars().all()

        trans_res = await db.execute(
            select(Translation).where(
                Translation.entity_type == "symptom",
                Translation.field == "label",
            )
        )
        symptom_translations = trans_res.scalars().all()
        symptom_label_map: dict[int, dict[str, str]] = {}
        for t in symptom_translations:
            if t.entity_id not in symptom_label_map:
                symptom_label_map[t.entity_id] = {}
            symptom_label_map[t.entity_id][t.locale] = t.value

        query_lower = query_text.lower()

        # 2. Match symptoms against query text
        matched_symptoms: list[Symptom] = []
        for s in all_symptoms:
            labels = symptom_label_map.get(s.id, {})
            en_label = labels.get("en", "").lower()
            km_label = labels.get("km", "")
            code_parts = s.code.replace("_", " ").lower()

            # Word match or substring
            matched = False
            if s.code in query_lower:
                matched = True
            elif en_label and (en_label in query_lower or any(word in query_lower for word in en_label.split() if len(word) > 4)):
                matched = True
            elif km_label and km_label in query_text:
                matched = True
            elif any(part in query_lower for part in code_parts.split() if len(part) > 4 and part not in ["spots", "plant", "water"]):
                matched = True

            if matched:
                matched_symptoms.append(s)

        # Fallback: If no strict symptom matched, try symptom keywords
        if not matched_symptoms:
            keyword_symptom_map = {
                "rust": ["leaf_cinnamon_brown_powdery_pustules", "leaf_black_raised_late_season_pustules"],
                "pustule": ["leaf_cinnamon_brown_powdery_pustules"],
                "downy": ["leaf_angular_water_soaked_translucent_spots", "leaf_dense_white_felt_undersides"],
                "mycelium": ["stem_cottony_white_mycelium"],
                "white mold": ["stem_cottony_white_mycelium", "stem_large_black_sclerotia"],
                "sclerotia": ["stem_large_black_sclerotia", "head_black_crust_sclerotia"],
                "gray mold": ["head_mouse_gray_velvety_spore_mat"],
                "yellow": ["leaf_interveinal_chlorosis_mottling", "leaf_bright_bleached_apical_chlorosis"],
                "spot": ["leaf_circular_angular_necrotic_spots", "leaf_concentric_target_board_rings"],
                "streak": ["stem_elongated_black_streaks"],
                "wilt": ["whole_plant_sudden_canopy_wilting", "whole_plant_unilateral_wilting_yellowing"],
                "stunt": ["whole_plant_severe_stunting_dwarfism"],
                "odor": ["stem_foul_putrid_rotting_odor"],
                "damping": ["seedling_damping_off_collapse"],
            }
            matched_codes = set()
            for kw, codes in keyword_symptom_map.items():
                if kw in query_lower:
                    matched_codes.update(codes)
            matched_symptoms = [s for s in all_symptoms if s.code in matched_codes]

        if not matched_symptoms:
            msg = self._translate(
                f"Hmm, I wasn't able to match specific symptoms from what you described. No worries though — let me help you narrow it down! 🌻\n\n"
                "**Can you tell me more about what you're seeing?** Try describing things like:\n"
                "• What **color** are the spots or changes? (brown, yellow, black, white)\n"
                "• **Where** on the plant? (leaves, stem, flower head, roots)\n"
                "• Is the plant **wilting**, **stunted**, or **drooping**?\n"
                "• Do you see any **mold**, **powder**, or **fungal growth**?\n\n"
                "💡 **Pro tip:** You can also **upload a photo** of your plant using the 📷 button below — I can analyze the image and help identify what's going on!\n\n"
                "Or jump straight to the **Interactive Symptom Checker** where you can select symptoms visually:",
                f"អូ ខ្ញុំមិនអាចកំណត់រោគសញ្ញាជាក់លាក់ពីការពិពណ៌នារបស់អ្នកបានទេ។ កុំបារម្ភ — តោះខ្ញុំជួយអ្នកឱ្យជាក់លាក់ជាង! 🌻\n\n"
                "**តើអ្នកអាចប្រាប់ខ្ញុំបន្ថែមអំពីអ្វីដែលអ្នកឃើញបានទេ?** សាកល្បងពិពណ៌នាដូចជា:\n"
                "• ចំណុចមាន **ពណ៌** អ្វី? (ត្នោត, លឿង, ខ្មៅ, ស)\n"
                "• នៅ **ផ្នែកណា** នៃដើម? (ស្លឹក, ដើម, ក្បាលផ្កា, ឫស)\n"
                "• តើដើម **ស្រពោន**, **កន្តឿ**, ឬ **ជ្រុះ** ទេ?\n"
                "• តើអ្នកឃើញ **ផ្សិត**, **ម្សៅ**, ឬ **សរសៃផ្សិត** ទេ?\n\n"
                "💡 **គន្លឹះ:** អ្នកក៏អាច **បញ្ជូនរូបថត** នៃដើមរបស់អ្នកដោយចុចប៊ូតុង 📷 ខាងក្រោម — ខ្ញុំអាចវិភាគរូបភាព!\n\n"
                "ឬចូលទៅកាន់ **ការពិនិត្យរោគសញ្ញាអន្តរកម្ម** ដោយផ្ទាល់:",
                locale,
            )
            suggested = [
                {"label": "📷 Upload Plant Photo", "path": "I want to upload a photo of my plant", "type": "message"},
                {"label": "Interactive Symptom Checker", "path": "/check", "type": "diagnosis"},
                {"label": "Browse All Diseases", "path": "/diseases", "type": "navigate"},
            ]
            return msg, [], None, suggested, False, None

        # 3. Query disease associations
        matched_symptom_ids = [s.id for s in matched_symptoms]
        links_res = await db.execute(
            select(DiseaseSymptom)
            .where(DiseaseSymptom.symptom_id.in_(matched_symptom_ids))
            .options(
                selectinload(DiseaseSymptom.disease),
                selectinload(DiseaseSymptom.symptom),
            )
        )
        links = links_res.scalars().all()

        # Score diseases: weight + count + pathognomonic bonus
        disease_scores: dict[int, dict[str, Any]] = {}
        for link in links:
            d_id = link.disease_id
            if d_id not in disease_scores:
                disease_scores[d_id] = {
                    "disease": link.disease,
                    "matched_count": 0,
                    "total_weight": 0.0,
                    "is_pathognomonic": False,
                    "matched_symptoms": [],
                }
            disease_scores[d_id]["matched_count"] += 1
            disease_scores[d_id]["total_weight"] += float(link.weight)
            if link.is_pathognomonic:
                disease_scores[d_id]["is_pathognomonic"] = True
            disease_scores[d_id]["matched_symptoms"].append(link.symptom)

        # Sort ranked diseases
        ranked = sorted(
            disease_scores.values(),
            key=lambda x: (
                x["matched_count"] * 2.0
                + x["total_weight"]
                + (3.0 if x["is_pathognomonic"] else 0.0)
            ),
            reverse=True,
        )

        # Load localized disease names
        d_ids = [item["disease"].id for item in ranked[:4]]
        d_names: dict[int, str] = {}
        if d_ids:
            dt_res = await db.execute(
                select(Translation).where(
                    Translation.entity_type == "disease",
                    Translation.field == "name",
                    Translation.entity_id.in_(d_ids),
                    Translation.locale == locale,
                )
            )
            for t in dt_res.scalars().all():
                d_names[t.entity_id] = t.value

        # Format output message
        symptom_bullets = []
        for s in matched_symptoms[:5]:
            lbl = symptom_label_map.get(s.id, {}).get(locale) or symptom_label_map.get(s.id, {}).get("en") or s.code
            cat = s.category.code.upper() if s.category else "PLANT"
            symptom_bullets.append(f"• **{cat}:** {lbl}")

        disease_bullets = []
        suggested_actions = []
        top_disease_slug = None

        for item in ranked[:3]:
            dis = item["disease"]
            name = d_names.get(dis.id, dis.slug.replace("-", " ").title())
            patho = dis.pathogen_type.value if hasattr(dis.pathogen_type, "value") else str(dis.pathogen_type)
            if not top_disease_slug:
                top_disease_slug = dis.slug

            badge = " ⭐ *Primary Characteristic Match*" if item["is_pathognomonic"] else ""
            disease_bullets.append(
                f"1. **{name}** (`{dis.slug}`) - *{patho}*{badge}\n"
                f"   - Matched: {item['matched_count']} symptom(s) | Cumulative weight: {item['total_weight']:.2f}\n"
                f"   - [Open Disease Guide](/diseases/{dis.slug})"
            )
            suggested_actions.append({
                "label": f"View {name}",
                "path": f"/diseases/{dis.slug}",
                "type": "navigate",
            })

        suggested_actions.append({
            "label": "Start Comprehensive Diagnosis",
            "path": "/check",
            "type": "diagnosis",
        })

        symptoms_str = "\n".join(symptom_bullets)
        diseases_str = "\n\n".join(disease_bullets) if disease_bullets else "No published disease rules match all observed symptoms."

        if locale == "km":
            message = (
                f"🔍 **រោគសញ្ញាដែលបានកំណត់ក្នុងមូលដ្ឋានទិន្នន័យ:**\n{symptoms_str}\n\n"
                f"🌻 **ជំងឺដែលត្រូវគ្នានិងទំនងជាកើតមានបំផុត:**\n{diseases_str}\n\n"
                "💡 *អ្នកអាចចុចលើប៊ូតុងខាងក្រោមដើម្បីមើលព័ត៌មានលម្អិតនៃជំងឺ ឬបើកផ្ទាំងវិភាគពេញលេញ។*"
            )
        else:
            message = (
                f"🔍 **Detected Symptoms in Knowledge Base:**\n{symptoms_str}\n\n"
                f"🌻 **Top Matching Sunflower Diseases:**\n{diseases_str}\n\n"
                "💡 *Click any action pill below to inspect the full disease profile or run formal Bayesian diagnosis.*"
            )

        extracted_info = {
            "crop": "Sunflower (Helianthus annuus)",
            "plant_part": list({s.category.code for s in matched_symptoms if s.category}),
            "symptoms": [s.code for s in matched_symptoms],
            "color_changes": [],
            "spots": [],
            "pests": [],
            "environment": [],
            "confidence": 0.85 if ranked else 0.4,
        }

        return (
            message,
            [{"action": "checked_symptoms", "count": len(matched_symptoms)}],
            None,
            suggested_actions,
            True,
            extracted_info,
        )

    # ========================================================================
    # 3. DISEASE DETAILS ("Know every data about disease")
    # ========================================================================

    async def _get_disease_details(
        self,
        query: str,
        db: AsyncSession,
        locale: str,
        user_role: str,
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]]]:
        """Fetch comprehensive disease profile: symptoms, treatments, prevention, pathogen."""
        disease = await self._find_disease(query, db)
        if not disease:
            # Fall back to general AI chat so user still receives a helpful answer
            response_msg, actions = await self._general_chat(
                message=f"Tell me about {query} in sunflowers.",
                history=[],
                locale=locale,
                user_role=user_role,
                db=db,
            )
            return response_msg, [{"action": "disease_chat_fallback", "query": query}], None, actions

        # Fetch translations for this disease
        trans_res = await db.execute(
            select(Translation).where(
                Translation.entity_type == "disease",
                Translation.entity_id == disease.id,
            )
        )
        translations = trans_res.scalars().all()
        t_data: dict[str, dict[str, str]] = {}
        for t in translations:
            if t.field not in t_data:
                t_data[t.field] = {}
            t_data[t.field][t.locale] = t.value

        def get_field(f: str) -> str:
            return t_data.get(f, {}).get(locale) or t_data.get(f, {}).get("en") or "Not documented."

        name = get_field("name")
        description = get_field("description")
        treatment = get_field("treatment")
        prevention = get_field("prevention")

        # Fetch symptoms linked with weights
        links_res = await db.execute(
            select(DiseaseSymptom)
            .where(DiseaseSymptom.disease_id == disease.id)
            .options(
                selectinload(DiseaseSymptom.symptom).selectinload(Symptom.category)
            )
            .order_by(DiseaseSymptom.weight.desc())
        )
        links = links_res.scalars().all()

        # Fetch translations for these symptoms
        s_ids = [l.symptom_id for l in links]
        s_labels: dict[int, str] = {}
        if s_ids:
            st_res = await db.execute(
                select(Translation).where(
                    Translation.entity_type == "symptom",
                    Translation.field == "label",
                    Translation.entity_id.in_(s_ids),
                )
            )
            for t in st_res.scalars().all():
                if t.locale == locale or t.entity_id not in s_labels:
                    s_labels[t.entity_id] = t.value

        symptom_lines = []
        for l in links:
            lbl = s_labels.get(l.symptom_id, l.symptom.code)
            cat = l.symptom.category.code.capitalize() if l.symptom.category else "General"
            badge = " ⭐ *Key Indicator*" if l.is_pathognomonic else ""
            symptom_lines.append(f"• **[{cat}]** {lbl} (Weight: {l.weight:.2f}){badge}")

        symptoms_str = "\n".join(symptom_lines) if symptom_lines else "No symptoms linked yet."

        patho = disease.pathogen_type.value if hasattr(disease.pathogen_type, "value") else str(disease.pathogen_type)
        status_str = "Published" if disease.is_published else "Draft"

        if locale == "km":
            message = (
                f"### 🌻 {name} (`{disease.slug}`)\n"
                f"**ប្រភេទមេរោគ:** {patho} | **ស្ថានភាព:** {status_str}\n\n"
                f"📋 **ការពិពណ៌នាជំងឺ:**\n{description}\n\n"
                f"🔍 **រោគសញ្ញាសំខាន់ៗ (ទម្ងន់ Bayesian):**\n{symptoms_str}\n\n"
                f"💊 **ការព្យាបាល និងការគ្រប់គ្រង:**\n{treatment}\n\n"
                f"🛡️ **វិធានការបង្ការ:**\n{prevention}"
            )
        else:
            message = (
                f"### 🌻 {name} (`{disease.slug}`)\n"
                f"**Classification:** {patho.capitalize()} pathogen | **Status:** {status_str}\n\n"
                f"📋 **Overview & Pathology:**\n{description}\n\n"
                f"🔍 **Key Observable Symptoms (Diagnostic Weights):**\n{symptoms_str}\n\n"
                f"💊 **Recommended Treatment & Management:**\n{treatment}\n\n"
                f"🛡️ **Prevention & Cultural Control:**\n{prevention}"
            )

        actions = [
            {"label": f"Open {name} Page", "path": f"/diseases/{disease.slug}", "type": "navigate"},
            {"label": "Compare with Other Diseases", "path": "/diseases/compare", "type": "navigate"},
        ]
        if user_role in ["admin", "agronomist"]:
            actions.append({"label": "Edit in Admin Panel", "path": f"/admin/diseases/{disease.id}", "type": "admin_edit"})

        return message, [{"action": "viewed_disease", "disease_id": disease.id}], None, actions

    # ========================================================================
    # 4. SYMPTOM DETAILS
    # ========================================================================

    async def _get_symptom_details(
        self,
        query: str,
        db: AsyncSession,
        locale: str,
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]]]:
        """Fetch details of a symptom and which diseases cause it."""
        # Search symptom by code or translation
        trans_res = await db.execute(
            select(Translation.entity_id).where(
                Translation.entity_type == "symptom",
                Translation.field == "label",
                Translation.value.ilike(f"%{query}%"),
            )
        )
        s_id = trans_res.scalars().first()

        symptom = None
        if s_id:
            res = await db.execute(
                select(Symptom)
                .where(Symptom.id == s_id)
                .options(selectinload(Symptom.category))
            )
            symptom = res.scalar_one_or_none()

        if not symptom:
            res = await db.execute(
                select(Symptom)
                .where(Symptom.code.ilike(f"%{query.replace(' ', '_')}%"))
                .options(selectinload(Symptom.category))
            )
            symptom = res.scalar_one_or_none()

        if not symptom:
            # Fall back to general AI chat so user receives a direct answer explaining what causes this symptom
            response_msg, actions = await self._general_chat(
                message=f"What causes {query} in sunflowers and how can it be managed?",
                history=[],
                locale=locale,
                user_role="grower",
                db=db,
            )
            return response_msg, [{"action": "symptom_chat_fallback", "query": query}], None, actions

        # Get label
        label_res = await db.execute(
            select(Translation.value).where(
                Translation.entity_type == "symptom",
                Translation.field == "label",
                Translation.entity_id == symptom.id,
                Translation.locale == locale,
            )
        )
        label = label_res.scalar_one_or_none() or symptom.code

        # Get linked diseases
        links_res = await db.execute(
            select(DiseaseSymptom)
            .where(DiseaseSymptom.symptom_id == symptom.id)
            .options(selectinload(DiseaseSymptom.disease))
        )
        links = links_res.scalars().all()

        d_ids = [l.disease_id for l in links]
        d_names = {}
        if d_ids:
            dt_res = await db.execute(
                select(Translation).where(
                    Translation.entity_type == "disease",
                    Translation.field == "name",
                    Translation.entity_id.in_(d_ids),
                    Translation.locale == locale,
                )
            )
            for t in dt_res.scalars().all():
                d_names[t.entity_id] = t.value

        disease_lines = []
        suggested_actions = []
        for l in links:
            d_name = d_names.get(l.disease_id, l.disease.slug)
            badge = " ⭐ (Pathognomonic)" if l.is_pathognomonic else ""
            disease_lines.append(f"• **{d_name}** (`{l.disease.slug}`) - Weight: {l.weight:.2f}{badge}")
            suggested_actions.append({"label": f"View {d_name}", "path": f"/diseases/{l.disease.slug}", "type": "navigate"})

        cat_name = symptom.category.code.upper() if symptom.category else "PLANT"
        diseases_str = "\n".join(disease_lines) if disease_lines else "No diseases currently linked in database."

        if locale == "km":
            message = (
                f"### 🌿 រោគសញ្ញា: **{label}**\n"
                f"**លេខកូដ:** `{symptom.code}` | **តំបន់រុក្ខជាតិ:** {cat_name}\n\n"
                f"Sunflower diseases that exhibit this symptom:\n{diseases_str}"
            )
        else:
            message = (
                f"### 🌿 Symptom: **{label}**\n"
                f"**Code:** `{symptom.code}` | **Plant Part:** {cat_name} | **Environmental:** {symptom.is_environmental}\n\n"
                f"**Diseases associated with this symptom:**\n{diseases_str}"
            )

        return message, [{"action": "viewed_symptom", "symptom_id": symptom.id}], None, suggested_actions

    # ========================================================================
    # 5. SYSTEM STATS & OVERVIEW
    # ========================================================================

    async def _get_system_stats(
        self,
        db: AsyncSession,
        locale: str,
        user_role: str,
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]]]:
        """Provide detailed system health and knowledge base overview."""
        d_count = await db.scalar(select(func.count(Disease.id)))
        d_pub = await db.scalar(select(func.count(Disease.id)).where(Disease.is_published.is_(True)))
        s_count = await db.scalar(select(func.count(Symptom.id)))
        l_count = await db.scalar(select(func.count(DiseaseSymptom.disease_id)))
        cat_count = await db.scalar(select(func.count(SymptomCategory.id)))

        fungal = await db.scalar(select(func.count(Disease.id)).where(Disease.pathogen_type == PathogenType.FUNGAL))
        bacterial = await db.scalar(select(func.count(Disease.id)).where(Disease.pathogen_type == PathogenType.BACTERIAL))
        other = (d_count or 0) - (fungal or 0) - (bacterial or 0)

        if locale == "km":
            message = (
                f"### 🌻 ស្ថានភាពមូលដ្ឋានទិន្នន័យប្រព័ន្ធអ្នកជំនាញផ្កាឈូករ័ត្ន\n\n"
                f"• **ជំងឺសរុប:** {d_count} ជំងឺ ({d_pub} បានផ្សព្វផ្សាយជាសាធារណៈ)\n"
                f"  - ផ្សិត (Fungal): {fungal}\n"
                f"  - បាក់តេរី (Bacterial): {bacterial}\n"
                f"  - ផ្សេងៗ (Abiotic/Oomycete): {other}\n"
                f"• **រោគសញ្ញាសរុប:** {s_count} រោគសញ្ញា បែងចែកតាម {cat_count} ផ្នែកនៃរុក្ខជាតិ\n"
                f"• **ច្បាប់វិភាគ (Rules):** {l_count} ទំនាក់ទំនងជំងឺ-រោគសញ្ញា ភ្ជាប់ជាមួយទម្ងន់ Bayesian\n"
                f"• **ការបកប្រែ:** ភាសាអង់គ្លេស (`en`) និងភាសាខ្មែរ (`km`) ពេញលេញ\n"
                f"• **តួនាទីបច្ចុប្បន្នរបស់អ្នក:** `{user_role.upper()}`"
            )
        else:
            message = (
                f"### 🌻 Sunflower Expert Knowledge Base Status\n\n"
                f"• **Diseases:** {d_count} cataloged ({d_pub} published)\n"
                f"  - Fungal pathogens: {fungal}\n"
                f"  - Bacterial pathogens: {bacterial}\n"
                f"  - Other / Oomycetes: {other}\n"
                f"• **Symptoms:** {s_count} observable indicators across {cat_count} plant anatomy zones\n"
                f"• **Diagnostic Rules:** {l_count} Bayesian disease-symptom linkages active\n"
                f"• **Localization:** Full Dual-Language Support (English `en` & Khmer `km`)\n"
                f"• **Your Active Role:** `{user_role.upper()}`"
            )

        actions = [
            {"label": "Diseases Catalog", "path": "/diseases", "type": "navigate"},
            {"label": "Symptom Checker", "path": "/check", "type": "navigate"},
        ]
        if user_role in ["admin", "agronomist"]:
            actions.append({"label": "Admin Panel", "path": "/admin", "type": "navigate"})

        return message, [{"action": "viewed_stats"}], None, actions

    async def _count_symptoms(
        self,
        db: AsyncSession,
        locale: str,
        user_role: str,
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]]]:
        """Return exact count of symptoms and their anatomy breakdown."""
        s_count = await db.scalar(select(func.count(Symptom.id)))

        cat_res = await db.execute(
            select(SymptomCategory.id, SymptomCategory.code, func.count(Symptom.id))
            .join(Symptom, Symptom.category_id == SymptomCategory.id)
            .group_by(SymptomCategory.id, SymptomCategory.code)
            .order_by(func.count(Symptom.id).desc())
        )
        cat_rows = cat_res.all()

        cat_trans_res = await db.execute(
            select(Translation).where(
                Translation.entity_type == "category",
                Translation.field == "label",
                Translation.locale.in_([locale, "en"]),
            )
        )
        cat_translations = cat_trans_res.scalars().all()
        cat_label_map: dict[int, str] = {}
        for t in cat_translations:
            if t.locale == "en" or t.locale == locale:
                cat_label_map[t.entity_id] = t.value

        cat_breakdown = []
        icons = {"leaf": "🍃", "stem": "🌿", "head": "🌻", "whole_plant": "🪴", "seedling": "🌱", "root": "🌾"}
        for cat_id, cat_code, count in cat_rows:
            label = cat_label_map.get(cat_id, cat_code.replace("_", " ").title())
            icon = icons.get(cat_code, "•")
            cat_breakdown.append(f"{icon} **{label}:** {count} symptoms")

        breakdown_str = "\n".join(cat_breakdown)

        if locale == "km":
            message = (
                f"### 🌿 ចំនួនរោគសញ្ញាក្នុងប្រព័ន្ធ\n\n"
                f"បច្ចុប្បន្នប្រព័ន្ធមានរោគសញ្ញាសរុបចំនួន **{s_count} រោគសញ្ញា** បែងចែកតាមផ្នែករុក្ខជាតិដូចខាងក្រោម:\n\n"
                f"{breakdown_str}\n\n"
                f"រោគសញ្ញាទាំងអស់នេះត្រូវបានភ្ជាប់ទៅនឹងជំងឺទាំង ២០ តាមរយៈ **៧៤ ច្បាប់វិភាគ Bayesian**។"
            )
        else:
            message = (
                f"### 🌿 Total Symptoms in the System\n\n"
                f"There are currently **{s_count} observable symptoms** cataloged across 6 plant anatomy zones:\n\n"
                f"{breakdown_str}\n\n"
                f"All {s_count} symptoms are mapped to our 20 diseases through **74 Bayesian diagnostic rules**."
            )

        suggested = [
            {"label": "List All Symptoms", "path": "/admin/symptoms" if user_role in ["admin", "agronomist"] else "/check", "type": "navigate"},
            {"label": "Open Symptom Checker", "path": "/check", "type": "diagnosis"},
        ]
        return message, [{"action": "counted_symptoms", "count": s_count}], None, suggested

    async def _count_diseases(
        self,
        db: AsyncSession,
        locale: str,
        user_role: str,
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]]]:
        """Return exact count of diseases and pathogen breakdown."""
        d_count = await db.scalar(select(func.count(Disease.id)))
        d_pub = await db.scalar(select(func.count(Disease.id)).where(Disease.is_published.is_(True)))
        fungal = await db.scalar(select(func.count(Disease.id)).where(Disease.pathogen_type == PathogenType.FUNGAL))
        bacterial = await db.scalar(select(func.count(Disease.id)).where(Disease.pathogen_type == PathogenType.BACTERIAL))
        other = (d_count or 0) - (fungal or 0) - (bacterial or 0)

        if locale == "km":
            message = (
                f"### 🌻 ចំនួនជំងឺក្នុងប្រព័ន្ធ\n\n"
                f"ប្រព័ន្ធមានជំងឺផ្កាឈូករ័ត្នសរុបចំនួន **{d_count} ជំងឺ** (ផ្សព្វផ្សាយជាសាធារណៈ {d_pub}):\n\n"
                f"• 🍄 **ផ្សិត (Fungal):** {fungal} ជំងឺ (ឧ. Sunflower Rust, Downy Mildew, Sclerotinia)\n"
                f"• 🦠 **បាក់តេរី (Bacterial):** {bacterial} ជំងឺ (ឧ. Bacterial Leaf Spot, Bacterial Stalk Rot, Aster Yellows)\n"
                f"• 🌿 **ផ្សេងៗ / Oomycete:** {other} ជំងឺ (ឧ. White Rust, Pythium Damping-Off)\n\n"
                f"ជំងឺនីមួយៗមានឯកសាររោគសញ្ញា ការព្យាបាល និងវិធានការបង្ការពេញលេញ។"
            )
        else:
            message = (
                f"### 🌻 Total Diseases in the System\n\n"
                f"There are currently **{d_count} sunflower diseases** documented in the system ({d_pub} published):\n\n"
                f"• 🍄 **Fungal Pathogens:** {fungal} diseases (e.g. Sunflower Rust, Downy Mildew, Sclerotinia Basal Stalk Rot)\n"
                f"• 🦠 **Bacterial Pathogens:** {bacterial} diseases (e.g. Bacterial Leaf Spot, Bacterial Stalk & Head Rot, Aster Yellows)\n"
                f"• 🌿 **Other / Oomycetes:** {other} diseases (e.g. White Rust, Pythium Damping-Off)\n\n"
                f"Each disease includes documented symptoms, chemical/biological treatments, and cultural prevention measures."
            )

        suggested = [
            {"label": "Browse Diseases Catalog", "path": "/diseases", "type": "navigate"},
            {"label": "Compare Diseases", "path": "/diseases/compare", "type": "navigate"},
        ]
        return message, [{"action": "counted_diseases", "count": d_count}], None, suggested

    # ========================================================================
    # 6. LIST DATA
    # ========================================================================

    async def _list_diseases(
        self,
        db: AsyncSession,
        locale: str,
        user_role: str,
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]]]:
        """List all diseases with localized names and slugs."""
        result = await db.execute(select(Disease).order_by(Disease.slug))
        diseases = result.scalars().all()

        if not diseases:
            msg = self._translate("No diseases found in the database.", "រកមិនឃើញជំងឺក្នុងមូលដ្ឋានទិន្នន័យទេ។", locale)
            return msg, [], None, []

        d_ids = [d.id for d in diseases]
        trans_result = await db.execute(
            select(Translation).where(
                Translation.entity_type == "disease",
                Translation.field == "name",
                Translation.entity_id.in_(d_ids),
                Translation.locale.in_([locale, "en"]),
            )
        )
        translations = trans_result.scalars().all()
        name_map = {}
        for t in translations:
            if t.locale == "en":
                name_map[t.entity_id] = t.value
        for t in translations:
            if t.locale == locale:
                name_map[t.entity_id] = t.value

        items = []
        suggested_actions = []
        for d in diseases:
            d_name = name_map.get(d.id, d.slug.replace("-", " ").title())
            patho = d.pathogen_type.value if hasattr(d.pathogen_type, "value") else str(d.pathogen_type)
            items.append(f"• **{d_name}** (`{d.slug}`) - *{patho}*")

        for d in diseases[:4]:
            d_name = name_map.get(d.id, d.slug.replace("-", " ").title())
            suggested_actions.append({"label": d_name, "path": f"/diseases/{d.slug}", "type": "navigate"})

        total = len(diseases)
        disease_list = "\n".join(items)

        if locale == "km":
            message = f"រកឃើញជំងឺ {total}:\n\n{disease_list}"
        else:
            message = f"Found {total} diseases in database:\n\n{disease_list}"

        return message, [{"action": "listed_diseases", "count": total}], None, suggested_actions

    async def _list_symptoms(
        self,
        db: AsyncSession,
        locale: str,
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]]]:
        """List all symptoms grouped by plant part."""
        result = await db.execute(
            select(Symptom)
            .join(Symptom.category)
            .options(selectinload(Symptom.category))
            .order_by(SymptomCategory.sort_order, Symptom.code)
        )
        symptoms = result.scalars().all()

        if not symptoms:
            msg = self._translate("No symptoms found in the database.", "រកមិនឃើញរោគសញ្ញាក្នុងមូលដ្ឋានទិន្នន័យទេ។", locale)
            return msg, [], None, []

        trans_result = await db.execute(
            select(Translation).where(
                Translation.entity_type == "symptom",
                Translation.field == "label",
                Translation.locale.in_([locale, "en"]),
            )
        )
        translations = trans_result.scalars().all()
        label_map = {}
        for t in translations:
            if t.locale == "en":
                label_map[t.entity_id] = t.value
        for t in translations:
            if t.locale == locale:
                label_map[t.entity_id] = t.value

        cat_trans_result = await db.execute(
            select(Translation).where(
                Translation.entity_type == "category",
                Translation.field == "label",
                Translation.locale.in_([locale, "en"]),
            )
        )
        cat_translations = cat_trans_result.scalars().all()
        cat_map = {}
        for t in cat_translations:
            if t.locale == "en":
                cat_map[t.entity_id] = t.value
        for t in cat_translations:
            if t.locale == locale:
                cat_map[t.entity_id] = t.value

        grouped: dict[str, list[str]] = {}
        for s in symptoms:
            cat_code = s.category.code if s.category else "other"
            cat_label = cat_map.get(s.category_id, cat_code.upper())
            if cat_label not in grouped:
                grouped[cat_label] = []
            lbl = label_map.get(s.id, s.code)
            grouped[cat_label].append(f"  • {lbl} (`{s.code}`)")

        parts = []
        for cat_name, items in grouped.items():
            parts.append(f"**{cat_name.upper()}:**\n" + "\n".join(items))

        symptom_list = "\n\n".join(parts)
        total = len(symptoms)

        if locale == "km":
            message = f"រកឃើញរោគសញ្ញា {total}:\n\n{symptom_list}"
        else:
            message = f"Found {total} symptoms:\n\n{symptom_list}"

        suggested = [{"label": "Open Symptom Checker", "path": "/check", "type": "diagnosis"}]
        return message, [{"action": "listed_symptoms", "count": total}], None, suggested

    # ========================================================================
    # 7. ROLE-BASED CREATE DISEASE (WITH COMPLETE BOTANICAL DRAFT & CONFIRMATION)
    # ========================================================================

    def _check_pending_draft_intent(self, message: str) -> str | None:
        """Determine if a message is responding to a pending disease draft confirmation."""
        msg_clean = message.lower().strip()
        msg_words = set(re.findall(r"\b\w+\b", msg_clean))

        # Confirmation words
        confirm_exact = {
            "confirm", "yes", "save", "save it", "save disease", "add", "add it", "add disease",
            "ok", "okay", "sure", "proceed", "approve", "approved", "go ahead", "do it",
            "yes please", "please add", "please save", "confirm and save", "confirm & save",
            "យល់ព្រម", "រក្សាទុក", "បន្ថែម", "យល់ព្រមបន្ថែម", "ត្រឹមត្រូវ", "យល់ព្រមរក្សាទុក"
        }
        if msg_clean in confirm_exact or any(msg_clean.startswith(w) for w in ["confirm", "save disease", "yes save", "យល់ព្រម", "រក្សាទុក"]):
            return "confirm_disease"
        if bool(msg_words & {"confirm", "proceed", "approve", "approved"}):
            return "confirm_disease"

        # Cancellation words
        cancel_exact = {
            "cancel", "no", "discard", "abort", "don't save", "don't add", "stop", "reject",
            "no thanks", "cancel draft", "discard draft", "បោះបង់", "ទេ", "មិនបាច់", "ឈប់"
        }
        if msg_clean in cancel_exact or any(msg_clean.startswith(w) for w in ["cancel", "discard", "abort", "don't", "បោះបង់"]):
            return "cancel_disease"
        if bool(msg_words & {"cancel", "discard", "abort"}):
            return "cancel_disease"

        # Edit draft words
        if re.search(r"\b(change|modify|update|edit|set)\b", msg_clean) and any(
            f in msg_clean for f in ["pathogen", "name", "description", "symptom", "treatment", "prevention", "slug", "cause"]
        ):
            return "edit_pending_disease"

        return None

    async def _prepare_disease_draft(
        self,
        data: dict,
        raw_message: str,
        db: AsyncSession,
        locale: str,
        conversation_id: str,
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]]]:
        """Formulate complete botanical disease draft and request admin/expert confirmation before database insertion."""
        name = data.get("name") or ""
        if not name or name.lower() in ["disease", "a disease", "new disease", "this disease"]:
            m = re.search(r"(?:create|add|new|insert|draft|បន្ថែម|បង្កើត)\s+(?:disease|disorder|ជំងឺ)?\s*([a-zA-Z0-9\s\-]+?)(?:\s+(?:with|caused|pathogen|and|for|by|លើ|ដែល)|$)", raw_message, re.IGNORECASE)
            if m:
                name = m.group(1).strip()

        if not name or name.lower() in ["disease", "a disease", "new disease", "this disease"] or not self._is_valid_entity_name(name):
            msg = self._translate(
                "Please specify the name of the disease you would like to add. For example: `Add disease Bacterial Soft Rot` or `Draft Southern Blight`.\n\nYou can also explore uncataloged diseases using **[🔍 Discover Missing Diseases]**.",
                "សូមបញ្ជាក់ឈ្មោះជំងឺដែលអ្នកចង់បន្ថែម។ ឧទាហរណ៍៖ `Add disease Bacterial Soft Rot` ឬ `Draft Southern Blight`។",
                locale,
            )
            suggested = [
                {"label": "🔍 Discover Missing Diseases", "path": "find new data that my system not yet have", "type": "message"},
                {"label": "Draft Southern Blight", "path": "draft disease Southern Blight", "type": "message"},
                {"label": "Draft Bacterial Soft Rot", "path": "draft disease Bacterial Soft Rot", "type": "message"},
            ]
            return msg, [], None, suggested

        # Clean name and generate slug
        clean_name = " ".join([w.capitalize() for w in name.split()])
        slug = re.sub(r"[^a-z0-9]+", "-", clean_name.lower()).strip("-")

        # 1. Check if disease with this slug already exists in database
        res = await db.execute(select(Disease).where(Disease.slug == slug))
        existing = res.scalar_one_or_none()
        if existing:
            target_path = f"/diseases/{slug}"
            msg = self._translate(
                f"Disease '**{clean_name}**' (`{slug}`) already exists in the Sunflower Knowledge Base (ID: {existing.id}).",
                f"ជំងឺ '**{clean_name}**' (`{slug}`) មានរួចហើយនៅក្នុងប្រព័ន្ធផ្កាឈូករ័ត្ន (ID: {existing.id})។",
                locale,
            )
            suggested = [
                {"label": f"View {clean_name}", "path": target_path, "type": "navigate"},
                {"label": "Edit in Admin Panel", "path": f"/admin/diseases/{existing.id}", "type": "navigate"},
                {"label": "All Diseases", "path": "/admin/diseases", "type": "navigate"},
            ]
            return msg, [], target_path, suggested

        # 2. Determine pathogen type
        pathogen_str = data.get("pathogen_type") or self._extract_pathogen_type(raw_message)
        try:
            pathogen_type = PathogenType(pathogen_str.lower())
        except ValueError:
            pathogen_type = PathogenType.FUNGAL

        # 3. Retrieve or synthesize complete botanical disease profile
        matched_kb = BOTANICAL_DISEASE_KB.get(slug)
        if not matched_kb:
            # Check partial match in KB keys
            for kb_slug, kb_data in BOTANICAL_DISEASE_KB.items():
                if kb_slug in slug or slug in kb_slug:
                    matched_kb = kb_data
                    break

        if matched_kb:
            draft = dict(matched_kb)
            draft["slug"] = slug
        else:
            draft = await self._synthesize_disease_profile(
                name=clean_name,
                pathogen_type=pathogen_type,
                raw_message=raw_message,
                locale=locale,
            )

        # 4. Cross-match observable symptoms with existing database symptoms
        try:
            symptom_res = await db.execute(select(Symptom.id, Symptom.code).order_by(Symptom.id))
            all_db_symptoms = symptom_res.all()

            trans_res = await db.execute(
                select(Translation.entity_id, Translation.value).where(
                    Translation.entity_type == "symptom",
                    Translation.locale == "en",
                    Translation.field == "label",
                )
            )
            symptom_label_map = {r[0]: r[1] for r in trans_res.all()}

            search_corpus = f"{clean_name} {draft.get('description_en', '')} {' '.join(draft.get('symptoms', []))}".lower()
            matched_symptoms: list[dict[str, Any]] = []
            seen_ids: set[int] = set()

            for s_id, s_code in all_db_symptoms:
                s_lbl = symptom_label_map.get(s_id, s_code).lower()
                code_parts = s_code.replace("_", " ").lower()

                matched = False
                for w in s_lbl.split():
                    if len(w) > 4 and w in search_corpus:
                        matched = True
                        break
                if not matched:
                    for part in code_parts.split():
                        if len(part) > 4 and part not in ["whole", "plant", "water", "early", "stage", "leaf", "spot"] and part in search_corpus:
                            matched = True
                            break

                if matched and s_id not in seen_ids:
                    seen_ids.add(s_id)
                    matched_symptoms.append({
                        "symptom_id": s_id,
                        "code": s_code,
                        "label": symptom_label_map.get(s_id, s_code),
                        "weight": 0.85,
                        "is_required": False,
                        "is_pathognomonic": False,
                    })
                    if len(matched_symptoms) >= 5:
                        break

            draft["matched_symptoms"] = matched_symptoms
        except Exception as e:
            logger.warning(f"Error matching symptoms for draft: {e}")
            draft["matched_symptoms"] = []

        # Store pending draft keyed by conversation_id
        self.pending_drafts[conversation_id] = draft

        # Format complete preview card with confirmation call to action
        return self._format_draft_preview(draft, locale)

    def _format_draft_preview(
        self,
        draft: dict[str, Any],
        locale: str,
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]]]:
        """Format a rich markdown preview of the unconfirmed disease knowledge draft."""
        name_en = draft.get("name_en", "Unknown Disease")
        name_km = draft.get("name_km") or name_en
        slug = draft.get("slug", "")
        scientific_name = draft.get("scientific_name", "N/A")
        pathogen_type = str(draft.get("pathogen_type", "fungal"))
        description_en = draft.get("description_en", "")
        description_km = draft.get("description_km", "")
        symptoms = draft.get("symptoms", [])
        causes = draft.get("causes", [])
        treatment_en = draft.get("treatment_en", "")
        treatment_km = draft.get("treatment_km", "")
        prevention_en = draft.get("prevention_en", "")
        prevention_km = draft.get("prevention_km", "")
        matched_symptoms = draft.get("matched_symptoms", [])

        symptoms_str = "\n".join([f"• {s}" for s in symptoms]) if symptoms else "• Observable symptoms across foliage, stems, and flower heads."
        causes_str = "\n".join([f"• {c}" for c in causes]) if causes else "• Pathogen infection under warm and humid conditions."

        if matched_symptoms:
            matched_lines = [f"• `{m['label']}` (`{m['code']}`)" for m in matched_symptoms]
            matched_section = f"\n\n**🔗 Correlated Database Symptoms ({len(matched_symptoms)} matched):**\n" + "\n".join(matched_lines)
            matched_section_km = f"\n\n**🔗 រោគសញ្ញាដែលត្រូវគ្នាក្នុងប្រព័ន្ធ ({len(matched_symptoms)} ត្រូវគ្នា):**\n" + "\n".join(matched_lines)
        else:
            matched_section = ""
            matched_section_km = ""

        # Format standardized database entry payload
        db_payload = {
            "entity_type": "disease_record",
            "disease_name": f"{name_en} ({scientific_name})" if scientific_name else name_en,
            "category": pathogen_type.capitalize(),
            "affected_parts": ["Leaf", "Stem", "Head", "Root"],
            "growth_stages_vulnerable": ["Seedling", "Vegetative", "Bud", "Flowering", "Maturity"],
            "primary_symptoms": symptoms[:5] if symptoms else ["Visual foliar lesions and wilting"],
            "environmental_conditions": causes[0] if causes else "Warm and humid conditions (>25°C, high RH)",
            "preventative_measures": [prevention_en] if prevention_en else ["Crop rotation", "Clean seed"],
            "curative_treatments": [treatment_en] if treatment_en else ["Targeted chemical or biological controls"]
        }
        json_payload_str = json.dumps(db_payload, indent=2, ensure_ascii=False)

        if locale == "km":
            msg = (
                f"### 📋 សេចក្តីព្រាងព័ត៌មានជំងឺថ្មី (រង់ចាំការបញ្ជាក់ពីអ្នកជំនាញ)\n\n"
                f"Helio បានចងក្រងទិន្នន័យរោគសាស្ត្ររុក្ខជាតិពេញលេញសម្រាប់ជំងឺ **{name_km}**:\n\n"
                f"• **ឈ្មោះជំងឺ (អង់គ្លេស):** {name_en}\n"
                f"• **ឈ្មោះជំងឺ (ខ្មែរ):** {name_km}\n"
                f"• **ឈ្មោះវិទ្យាសាស្ត្រ (Scientific Name):** *{scientific_name}*\n"
                f"• **ប្រភេទមេរោគ:** `{pathogen_type.capitalize()}`\n"
                f"• **Slug ប្រព័ន្ធ:** `{slug}`\n"
                f"• **ស្ថានភាពបច្ចុប្បន្ន:** `សេចក្តីព្រាង (មិនទាន់រក្សាទុកក្នុងប្រព័ន្ធ)`\n\n"
                f"```json\n{json_payload_str}\n```\n\n"
                f"---\n"
                f"#### 📖 ការពិពណ៌នាអំពីរុក្ខសាស្ត្រ\n"
                f"{description_km or description_en}\n\n"
                f"#### 🔍 រោគសញ្ញាដែលអាចសង្កេតឃើញបាន\n"
                f"{symptoms_str}{matched_section_km}\n\n"
                f"#### 🔬 មូលហេតុ និងកត្តាជំរុញ\n"
                f"{causes_str}\n\n"
                f"#### 💊 វិធីព្យាបាល និងថ្នាំការពារកម្ចាត់\n"
                f"{treatment_km or treatment_en}\n\n"
                f"#### 🛡️ វិធានការបង្ការ និងការគ្រប់គ្រង\n"
                f"{prevention_km or prevention_en}\n\n"
                f"---\n"
                f"⚠️ **ការបញ្ជាក់តម្រូវជាចាំបាច់:**\n"
                f"ជំងឺនេះ **មិនទាន់** ត្រូវបានបញ្ចូលទៅក្នុងមូលដ្ឋានទិន្នន័យនៅឡើយទេ។ សូមពិនិត្យព័ត៌មានខាងលើដោយប្រុងប្រយ័ត្ន។\n\n"
                f"• ដើម្បីបន្ថែមជំងឺនេះទៅក្នុងមូលដ្ឋានទិន្នន័យ សូមឆ្លើយ **'យល់ព្រម'** ឬចុចប៊ូតុង **✅ យល់ព្រម & រក្សាទុកជំងឺ** ខាងក្រោម។\n"
                f"• ដើម្បីកែប្រែក្នុងផ្ទាំងគ្រប់គ្រង សូមចុច **📝 បើកទម្រង់បង្កើតជំងឺ**។\n"
                f"• ដើម្បីបោះបង់ សូមឆ្លើយ **'បោះបង់'** ឬចុច **❌ បោះបង់សេចក្តីព្រាង**។"
            )
            suggested_actions = [
                {"label": "✅ យល់ព្រម & រក្សាទុកជំងឺ", "path": "confirm", "type": "message"},
                {"label": "📝 បើកទម្រង់បង្កើតជំងឺ", "path": "/admin/diseases/new", "type": "navigate"},
                {"label": "❌ បោះបង់សេចក្តីព្រាង", "path": "cancel", "type": "message"},
            ]
        else:
            msg = (
                f"### 📋 Proposed Disease Knowledge Entry (Pending Confirmation)\n\n"
                f"**Helio** has formulated a standardized botanical and pathological profile for **{name_en}**:\n\n"
                f"• **Disease Name (EN):** {name_en}\n"
                f"• **Disease Name (KM):** {name_km}\n"
                f"• **Scientific Causal Agent:** *{scientific_name}*\n"
                f"• **Pathogen Classification:** `{pathogen_type.capitalize()}`\n"
                f"• **System Slug:** `{slug}`\n"
                f"• **Status:** `Draft (Not yet saved to database)`\n\n"
                f"#### 📦 Standardized Database Entry Payload\n"
                f"```json\n{json_payload_str}\n```\n\n"
                f"---\n"
                f"#### 📖 Botanical Description\n"
                f"{description_en}\n\n"
                f"#### 🔍 Observable Symptoms Across Plant Zones\n"
                f"{symptoms_str}{matched_section}\n\n"
                f"#### 🔬 Causes & Epidemiology\n"
                f"{causes_str}\n\n"
                f"#### 💊 Curative Treatments & Chemical Control\n"
                f"{treatment_en}\n\n"
                f"#### 🛡️ Cultural Prevention & Field Management\n"
                f"{prevention_en}\n\n"
                f"---\n"
                f"⚠️ **Confirmation Required:**\n"
                f"This disease has **NOT** been added to PostgreSQL yet. Please review the standardized payload above.\n\n"
                f"• To save this disease now, reply **'confirm'** or click **✅ Confirm & Save Disease** below.\n"
                f"• To edit or configure manually, click **📝 Open Disease Form**.\n"
                f"• To discard this draft, reply **'cancel'** or click **❌ Discard Draft**."
            )
            suggested_actions = [
                {"label": "✅ Confirm & Save Disease", "path": "confirm", "type": "message"},
                {"label": "📝 Open Disease Form", "path": "/admin/diseases/new", "type": "navigate"},
                {"label": "❌ Discard Draft", "path": "cancel", "type": "message"},
            ]

        actions_taken = [{
            "action": "prepared_disease_draft",
            "disease_name": name_en,
            "slug": slug,
            "pathogen_type": pathogen_type,
            "status": "awaiting_confirmation",
        }]

        return msg, actions_taken, None, suggested_actions

    async def _commit_pending_disease(
        self,
        conversation_id: str,
        db: AsyncSession,
        locale: str,
        user_role: str,
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]]]:
        """Commit the pending disease draft to the database after expert confirmation."""
        draft = self.pending_drafts.get(conversation_id)
        if not draft:
            msg = self._translate(
                "No pending disease draft found awaiting confirmation. To create a disease, try: `Add disease Bacterial Soft Rot`",
                "រកមិនឃើញសេចក្តីព្រាងជំងឺដែលកំពុងរង់ចាំការបញ្ជាក់ទេ។ ដើម្បីបង្កើតជំងឺ សូមសាកល្បង៖ `Add disease Bacterial Soft Rot`",
                locale,
            )
            return msg, [], None, []

        try:
            # Check or ensure unique slug
            slug = draft.get("slug") or re.sub(r"[^a-z0-9]+", "-", draft["name_en"].lower()).strip("-")
            res = await db.execute(select(Disease).where(Disease.slug == slug))
            if res.scalar_one_or_none():
                slug = f"{slug}-{int(time.time()) % 10000}"

            pathogen_val = str(draft.get("pathogen_type", "fungal")).lower()
            try:
                pathogen = PathogenType(pathogen_val)
            except ValueError:
                pathogen = PathogenType.FUNGAL

            # 1. Insert Disease record
            new_disease = Disease(
                slug=slug,
                pathogen_type=pathogen,
                is_published=False,  # Un-published draft for safety
            )
            db.add(new_disease)
            await db.flush()

            # 2. Insert Translations
            name_en = draft.get("name_en", "Unknown Disease")
            db.add(Translation(entity_type="disease", entity_id=new_disease.id, locale="en", field="name", value=name_en))
            if draft.get("name_km"):
                db.add(Translation(entity_type="disease", entity_id=new_disease.id, locale="km", field="name", value=draft["name_km"]))

            if draft.get("description_en"):
                db.add(Translation(entity_type="disease", entity_id=new_disease.id, locale="en", field="description", value=draft["description_en"]))
            if draft.get("description_km"):
                db.add(Translation(entity_type="disease", entity_id=new_disease.id, locale="km", field="description", value=draft["description_km"]))

            causes_en = "; ".join(draft.get("causes", [])) if isinstance(draft.get("causes"), list) else str(draft.get("causes", ""))
            if causes_en:
                db.add(Translation(entity_type="disease", entity_id=new_disease.id, locale="en", field="cause", value=causes_en))

            if draft.get("treatment_en"):
                db.add(Translation(entity_type="disease", entity_id=new_disease.id, locale="en", field="treatment", value=draft["treatment_en"]))
            if draft.get("treatment_km"):
                db.add(Translation(entity_type="disease", entity_id=new_disease.id, locale="km", field="treatment", value=draft["treatment_km"]))

            if draft.get("prevention_en"):
                db.add(Translation(entity_type="disease", entity_id=new_disease.id, locale="en", field="prevention", value=draft["prevention_en"]))
            if draft.get("prevention_km"):
                db.add(Translation(entity_type="disease", entity_id=new_disease.id, locale="km", field="prevention", value=draft["prevention_km"]))

            # 3. Associate matched symptoms into DiseaseSymptom
            matched_symptoms = draft.get("matched_symptoms", [])
            for sym in matched_symptoms:
                db.add(DiseaseSymptom(
                    disease_id=new_disease.id,
                    symptom_id=sym["symptom_id"],
                    weight=Decimal(str(sym.get("weight", 0.80))),
                    is_required=sym.get("is_required", False),
                    is_pathognomonic=sym.get("is_pathognomonic", False),
                ))

            await db.commit()
            await db.refresh(new_disease)

            # Clear pending draft
            del self.pending_drafts[conversation_id]

            target_path = f"/admin/diseases/{new_disease.id}"
            catalog_path = f"/diseases/{slug}"

            if locale == "km":
                name_display = draft.get("name_km") or name_en
                msg = (
                    f"✅ **បានបង្កើត និងរក្សាទុកជំងឺដោយជោគជ័យ!**\n\n"
                    f"ជំងឺ **{name_display}** (`{slug}`) ត្រូវបានបន្ថែមទៅក្នុងមូលដ្ឋានទិន្នន័យចំណេះដឹងផ្កាឈូករ័ត្ន:\n\n"
                    f"• **អត្តសញ្ញាណ (ID):** `{new_disease.id}`\n"
                    f"• **Slug ប្រព័ន្ធ:** `{slug}`\n"
                    f"• **ប្រភេទមេរោគ:** `{pathogen.value.capitalize()}`\n"
                    f"• **ទិន្នន័យដែលបានរក្សាទុក:** ភាសាអង់គ្លេស និងខ្មែរ (ឈ្មោះ, ការពិពណ៌នា, មូលហេតុ, ការព្យាបាល, ការការពារ)\n"
                    f"• **រោគសញ្ញាដែលបានភ្ជាប់:** {len(matched_symptoms)} រោគសញ្ញាភ្ជាប់ជាមួយម៉ាស៊ីនវិភាគ Bayesian\n"
                    f"• **ស្ថានភាព:** `សេចក្តីព្រាង (មិនទាន់ផ្សាយ)` — រួចរាល់សម្រាប់ការត្រួតពិនិត្យបន្ថែម និងផ្សព្វផ្សាយ។"
                )
            else:
                msg = (
                    f"✅ **Disease Successfully Added to Knowledge Base!**\n\n"
                    f"The disease **{name_en}** (`{slug}`) has been confirmed and saved to PostgreSQL:\n\n"
                    f"• **Database ID:** `{new_disease.id}`\n"
                    f"• **System Slug:** `{slug}`\n"
                    f"• **Pathogen Type:** `{pathogen.value.capitalize()}`\n"
                    f"• **Translations Saved:** English & Khmer (Name, Description, Causes, Treatment, Prevention)\n"
                    f"• **Linked Symptoms:** {len(matched_symptoms)} symptoms associated with Bayesian rules\n"
                    f"• **Publication Status:** `Draft (Unpublished)` — Ready for expert review and publishing.\n\n"
                    f"You can now view it in the disease catalog or configure additional symptoms in the admin panel."
                )

            actions_taken = [{
                "action": "confirmed_and_created_disease",
                "disease_id": new_disease.id,
                "disease_name": name_en,
                "slug": slug,
                "matched_symptoms_count": len(matched_symptoms),
            }]

            suggested_actions = [
                {"label": "🔍 View in Catalog", "path": catalog_path, "type": "navigate"},
                {"label": "⚙️ Edit in Admin Panel", "path": target_path, "type": "navigate"},
                {"label": "📋 All Diseases", "path": "/admin/diseases", "type": "navigate"},
            ]

            return msg, actions_taken, target_path, suggested_actions

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to commit pending disease: {e}", exc_info=True)
            msg = self._translate(f"❌ Failed to save disease to database: {e!s}", f"❌ បរាជ័យក្នុងការរក្សាទុកជំងឺ: {e!s}", locale)
            return msg, [], None, []

    async def _cancel_pending_disease(
        self,
        conversation_id: str,
        locale: str,
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]]]:
        """Cancel and discard the pending disease draft."""
        draft = self.pending_drafts.pop(conversation_id, None)
        if not draft:
            msg = self._translate(
                "No pending disease draft was awaiting confirmation.",
                "គ្មានសេចក្តីព្រាងជំងឺណាមួយកំពុងរង់ចាំការបញ្ជាក់ទេ។",
                locale,
            )
            return msg, [], None, []

        name = draft.get("name_en", "Disease")
        if locale == "km":
            name = draft.get("name_km") or name
            msg = (
                f"❌ **បានបោះបង់សេចក្តីព្រាងជំងឺ**\n\n"
                f"សេចក្តីព្រាងសម្រាប់ជំងឺ **{name}** ត្រូវបានបោះបង់។ គ្មានទិន្នន័យត្រូវបានបន្ថែមទៅក្នុងប្រព័ន្ធទេ។"
            )
        else:
            msg = (
                f"❌ **Disease Draft Discarded**\n\n"
                f"The proposed knowledge entry for **{name}** has been cancelled. No records were added to the database."
            )

        actions_taken = [{"action": "cancelled_disease_draft", "disease_name": name}]
        suggested_actions = [
            {"label": "🌻 Browse Diseases", "path": "/diseases", "type": "navigate"},
            {"label": "⚙️ Manage Diseases", "path": "/admin/diseases", "type": "navigate"},
        ]
        return msg, actions_taken, None, suggested_actions

    async def _edit_pending_disease(
        self,
        conversation_id: str,
        instruction: str,
        db: AsyncSession,
        locale: str,
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]]]:
        """Modify fields in the pending disease draft per user instructions."""
        draft = self.pending_drafts.get(conversation_id)
        if not draft:
            msg = self._translate(
                "No pending disease draft found to edit. To start a new disease draft, try: `Add disease Bacterial Soft Rot`",
                "រកមិនឃើញសេចក្តីព្រាងជំងឺដើម្បីកែសម្រួលទេ។",
                locale,
            )
            return msg, [], None, []

        inst_lower = instruction.lower()

        # Update pathogen type if requested
        if "pathogen" in inst_lower or "bacterial" in inst_lower or "fungal" in inst_lower or "viral" in inst_lower:
            new_pathogen = self._extract_pathogen_type(instruction)
            draft["pathogen_type"] = new_pathogen

        # Update name if requested
        if "name" in inst_lower:
            name_m = re.search(r"name\s+(?:to|is|=)\s+([a-zA-Z0-9\s\-]+?)(?:\.|$)", instruction, re.IGNORECASE)
            if name_m:
                new_name = name_m.group(1).strip()
                draft["name_en"] = new_name
                draft["slug"] = re.sub(r"[^a-z0-9]+", "-", new_name.lower()).strip("-")

        # Update treatment if requested
        if "treatment" in inst_lower:
            treat_m = re.search(r"treatment\s*(?:to|is|=)\s*(.+?)(?:\.|$)", instruction, re.IGNORECASE)
            if treat_m:
                draft["treatment_en"] = treat_m.group(1).strip()

        # Update prevention if requested
        if "prevention" in inst_lower:
            prev_m = re.search(r"prevention\s*(?:to|is|=)\s*(.+?)(?:\.|$)", instruction, re.IGNORECASE)
            if prev_m:
                draft["prevention_en"] = prev_m.group(1).strip()

        # Re-render preview card
        return self._format_draft_preview(draft, locale)

    async def _synthesize_disease_profile(
        self,
        name: str,
        pathogen_type: PathogenType,
        raw_message: str,
        locale: str,
    ) -> dict[str, Any]:
        """Synthesize a complete botanical profile using Ollama or pathologically grounded fallback."""
        clean_name = " ".join([w.capitalize() for w in name.split()])
        slug = re.sub(r"[^a-z0-9]+", "-", clean_name.lower()).strip("-")

        # First, try generating with Ollama if available
        system_prompt = (
            "You are an expert plant pathologist and agronomist for sunflowers (Helianthus annuus). "
            "Generate complete botanical and pathological knowledge for a sunflower disease. "
            "Return ONLY valid JSON with keys: "
            "disease_name_en, disease_name_km, scientific_name, pathogen_type, "
            "description_en, description_km, symptoms (list of 5 strings), causes (list of 3 strings), "
            "treatment_en, treatment_km, prevention_en, prevention_km."
        )
        user_prompt = f"Disease: {clean_name}\nPathogen Type: {pathogen_type.value}\nContext: {raw_message}"

        try:
            ollama_resp = await asyncio.wait_for(
                self.ollama.generate(prompt=user_prompt, system=system_prompt, temperature=0.3, json_mode=True),
                timeout=30.0,
            )
            data = extract_json_from_response(ollama_resp)
            if data and data.get("description_en") and data.get("symptoms"):
                return {
                    "name_en": data.get("disease_name_en") or clean_name,
                    "name_km": data.get("disease_name_km") or f"ជំងឺ {clean_name}",
                    "slug": slug,
                    "scientific_name": data.get("scientific_name") or f"{clean_name} sp.",
                    "pathogen_type": pathogen_type.value,
                    "description_en": data.get("description_en"),
                    "description_km": data.get("description_km") or f"ការពិពណ៌នាអំពីជំងឺ {clean_name} លើដំណាំផ្កាឈូករ័ត្ន។",
                    "symptoms": data.get("symptoms") if isinstance(data.get("symptoms"), list) else [str(data.get("symptoms"))],
                    "causes": data.get("causes") if isinstance(data.get("causes"), list) else [str(data.get("causes"))],
                    "treatment_en": data.get("treatment_en") or "Apply registered bactericides/fungicides according to extension recommendations.",
                    "treatment_km": data.get("treatment_km") or "អនុវត្តការបាញ់ថ្នាំការពារជំងឺតាមការណែនាំរបស់អ្នកជំនាញកសិកម្ម។",
                    "prevention_en": data.get("prevention_en") or "Practice 3-4 year crop rotation with non-hosts and use certified disease-free seeds.",
                    "prevention_km": data.get("prevention_km") or "អនុវត្តការបង្វិលដំណាំពី ៣ ទៅ ៤ ឆ្នាំ និងប្រើប្រាស់គ្រាប់ពូជដែលគ្មានមេរោគ។",
                }
        except Exception as e:
            logger.debug(f"Ollama draft synthesis fallback: {e}")

        # Intelligent botanical synthesizer fallback
        if pathogen_type == PathogenType.BACTERIAL:
            sci = f"Xanthomonas / Pseudomonas / Pectobacterium ({clean_name})"
            km_name = f"ជំងឺ {clean_name} ដោយបាក់តេរី"
            desc_en = (
                f"{clean_name} is a bacterial disorder of sunflowers causing vascular discoloration, leaf spotting, and tissue breakdown. "
                "The bacterial pathogen gains entry through stomata, hydathodes, or insect feeding wounds during periods of high humidity and warm temperatures (26-34°C). "
                "Unchecked infections can cause rapid collapse of vascular flow, leading to premature leaf drop and stunted flower heads."
            )
            desc_km = f"{clean_name} គឺជាជំងឺបាក់តេរីលើដំណាំផ្កាឈូករ័ត្ន ដែលបង្កឱ្យមានស្នាមអុចលើស្លឹក និងការរលួយជាលិកា។ បាក់តេរីឆ្លងតាមរយៈរបួស ឬរន្ធខ្យល់ស្លឹកក្នុងអាកាសធាតុក្តៅហើយសើម។"
            symptoms = [
                f"Water-soaked dark lesions on sunflower leaves and petioles characteristic of {clean_name}",
                "Bacterial exudate or slimy oozing visible at infection sites during moist morning hours",
                "Marginal chlorosis turning into necrotic dry leaf patches",
                "Stem vascular darkening causing localized lodging or wilting",
                "Reduced flower head diameter and compromised seed formation"
            ]
            causes = [
                "Bacterial pathogen infection favored by high relative humidity (>80%) and warm weather",
                "Entry through hail damage, insect feeding punctures, or farm machinery wounds",
                "Overhead irrigation and splashing rain spreading bacterial cells across the canopy"
            ]
            treat_en = "Apply copper hydroxide or copper oxychloride bactericide (2.5 kg/ha) at first sign of symptoms. Remove heavily diseased plants to prevent secondary splash dispersal. Disinfect pruning and harvesting tools."
            treat_km = "បាញ់ថ្នាំសម្លាប់បាក់តេរី Copper Hydroxide (២.៥ គ.ក្រ/ហ.ត) នៅពេលចាប់ផ្តើមកើតរោគសញ្ញា។ ដកដើមដែលកើតជំងឺធ្ងន់ធ្ងរចេញ និងសម្អាតឧបករណ៍កសិកម្ម។"
            prev_en = "Maintain 3-4 year crop rotation with non-host cereals (maize, sorghum). Plant certified pathogen-tested sunflower hybrids with good air-circulation spacing (60-70 cm). Use drip irrigation instead of overhead sprinklers."
            prev_km = "អនុវត្តការបង្វិលដំណាំ ៣-៤ ឆ្នាំជាមួយពោត ឬស្រូវសាលី។ ប្រើគ្រាប់ពូជដែលបានបញ្ជាក់ថាគ្មានមេរោគ និងដាំក្នុងគម្លាតសមស្របដើម្បីឱ្យខ្យល់ចេញចូលបានល្អ។"

        elif pathogen_type == PathogenType.VIRAL:
            sci = f"{clean_name} Virus"
            km_name = f"ជំងឺវីរុស {clean_name}"
            desc_en = (
                f"{clean_name} is a viral sunflower disease leading to systemic leaf mottle, stunting, and reduced seed yields. "
                "It is vectored predominantly by sap-sucking insects like aphids or thrips. Infected plants show abnormal foliage morphology and diminished photosynthetic capacity."
            )
            desc_km = f"{clean_name} គឺជាជំងឺវីរុសលើផ្កាឈូករ័ត្នដែលបណ្តាលឱ្យស្លឹកឡើងស្នាមអុចៗ ដើមកន្តឿ និងថយចុះទិន្នផលគ្រាប់។ វាឆ្លងតាមរយៈសត្វល្អិតបឺតជញ្ជក់ដូចជាចៃស្លឹក ឬកន្ត្រៃ។"
            symptoms = [
                f"Systemic mosaic patterns, chlorotic mottling, or ring spots associated with {clean_name}",
                "Leaf puckering, distortion, and rugosity on young developing leaves",
                "Plant stunting and shortened internodes",
                "Vein clearing and localized necrotic spotting",
                "Abnormal flower head formation with empty or malformed achenes"
            ]
            causes = [
                "Viral infection transmitted by insect vectors (aphids, thrips, or whiteflies)",
                "Proximity to reservoir weed hosts along field perimeters",
                "Use of uncertified, virus-contaminated seed lots"
            ]
            treat_en = "No direct curative virucide exists. Control insect vector populations using selective systemic insecticides (spinosad, imidacloprid) or organic neem formulations. Rogue out infected plants immediately."
            treat_km = "គ្មានថ្នាំសម្លាប់វីរុសដោយផ្ទាល់ទេ។ ត្រូវបាញ់ថ្នាំកម្ចាត់សត្វល្អិតចៃស្លឹក ឬកន្ត្រៃ (Spinosad ឬ Imidacloprid) និងដកដើមដែលកើតជំងឺយកទៅដុតបំផ្លាញចោល។"
            prev_en = "Plant certified virus-free seeds. Clear surrounding solanaceous and asteraceous weed hosts. Deploy yellow sticky traps for insect monitoring, and plant protective cereal barrier rows around fields."
            prev_km = "ប្រើប្រាស់គ្រាប់ពូជដែលគ្មានមេរោគវីរុស។ សម្អាតស្មៅចង្រៃជុំវិញចំការ។ ដាក់អន្ទាក់ស្អិតពណ៌លឿងដើម្បីចាប់សត្វល្អិត។"

        else:  # FUNGAL or OTHER
            sci = f"{clean_name} sp. (Pathogen)"
            km_name = f"ជំងឺ {clean_name} ដោយផ្សិត"
            desc_en = (
                f"{clean_name} is a fungal sunflower disease causing foliage lesions, stem deterioration, and yield losses. "
                "Fungal spores overwinter in crop residue or soil, germinating under humid conditions and penetrating plant epidermal cells. "
                "Severe attacks lead to premature defoliation and compromised sunflower stem integrity."
            )
            desc_km = f"{clean_name} គឺជាជំងឺផ្សិតលើផ្កាឈូករ័ត្នដែលបង្កឱ្យមានដំបៅលើស្លឹក ការខូចខាតដើម និងការបាត់បង់ទិន្នផល។ មេរោគផ្សិតរស់នៅក្នុងកាកសំណល់ដំណាំ ឬដី ហើយលូតលាស់ក្នុងអាកាសធាតុសើម។"
            symptoms = [
                f"Distinct fungal lesions with concentric rings or chlorotic halos typical of {clean_name}",
                "Foliar leaf spots coalescing into large necrotic blights",
                "Stem lesions or basal cankers leading to stalk weakening",
                "Premature yellowing and drying of lower canopy leaves",
                "Dark fungal sporulation or fruiting bodies visible on infected plant surfaces"
            ]
            causes = [
                "Fungal spore germination driven by free moisture on leaves and moderate temperatures (20-28°C)",
                "Survival of inoculum in sunflower stubble from preceding seasons",
                "High canopy density restricting sunlight penetration and airflow"
            ]
            treat_en = "Apply targeted fungicides (azoxystrobin, pyraclostrobin, boscalid, or tebuconazole) at early disease onset. Ensure thorough canopy coverage and rotate fungicide modes of action to prevent resistance."
            treat_km = "បាញ់ថ្នាំផ្សិត (Azoxystrobin, Pyraclostrobin ឬ Tebuconazole) នៅពេលចាប់ផ្តើមកើតជំងឺដំបូង។ បាញ់ឱ្យសព្វលើស្លឹក និងដើម។"
            prev_en = "Rotate with non-host crops (corn, wheat, sorghum) for 3-4 years. Plant certified disease-resistant sunflower hybrids. Deep-plow crop residues and maintain proper plant spacing (60-75 cm)."
            prev_km = "បង្វិលដំណាំ ៣-៤ ឆ្នាំជាមួយពោត ឬស្រូវសាលី។ ប្រើគ្រាប់ពូជធន់នឹងជំងឺ និងដាំក្នុងគម្លាតត្រឹមត្រូវដើម្បីឱ្យខ្យល់ចេញចូលបានល្អ។"

        return {
            "name_en": clean_name,
            "name_km": km_name,
            "slug": slug,
            "scientific_name": sci,
            "pathogen_type": pathogen_type.value,
            "description_en": desc_en,
            "description_km": desc_km,
            "symptoms": symptoms,
            "causes": causes,
            "treatment_en": treat_en,
            "treatment_km": treat_km,
            "prevention_en": prev_en,
            "prevention_km": prev_km,
        }

    async def _create_disease(
        self,
        data: dict,
        db: AsyncSession,
        locale: str,
        conversation_id: str = "default",
        raw_message: str = "",
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]]]:
        """Wrapper for _prepare_disease_draft for backwards compatibility."""
        return await self._prepare_disease_draft(
            data=data,
            raw_message=raw_message or data.get("name", ""),
            db=db,
            locale=locale,
            conversation_id=conversation_id,
        )

    # ========================================================================
    # 8. ROLE-BASED UPDATE DISEASE
    # ========================================================================

    async def _update_disease(
        self,
        data: dict,
        db: AsyncSession,
        locale: str,
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]]]:
        """Update an existing disease."""
        disease_name = data.get("disease_name") or data.get("name")
        disease = await self._find_disease(disease_name, db)
        if not disease:
            msg = self._translate(f"Disease '{disease_name}' not found.", f"រកមិនឃើញជំងឺ '{disease_name}' ទេ។", locale)
            return msg, [], None, []

        try:
            if "description" in data:
                res = await db.execute(
                    select(Translation).where(
                        Translation.entity_type == "disease",
                        Translation.entity_id == disease.id,
                        Translation.field == "description",
                        Translation.locale == locale,
                    )
                )
                existing = res.scalar_one_or_none()
                if existing:
                    existing.value = data["description"]
                else:
                    db.add(Translation(entity_type="disease", entity_id=disease.id, locale=locale, field="description", value=data["description"]))

            if "pathogen_type" in data:
                try:
                    disease.pathogen_type = PathogenType(data["pathogen_type"].lower())
                except ValueError:
                    pass

            await db.commit()
            target_path = f"/admin/diseases/{disease.id}"
            msg = self._translate(
                f"✅ Successfully updated disease `{disease.slug}` (ID: {disease.id}).",
                f"✅ បានធ្វើបច្ចុប្បន្នភាពជំងឺ `{disease.slug}` ដោយជោគជ័យ។",
                locale,
            )
            return (
                msg,
                [{"action": "updated_disease", "disease_id": disease.id}],
                target_path,
                [{"label": "View Disease in Admin", "path": target_path, "type": "navigate"}],
            )
        except Exception as e:
            await db.rollback()
            msg = self._translate(f"❌ Failed to update disease: {e!s}", f"❌ បរាជ័យក្នុងការធ្វើបច្ចុប្បន្នភាពជំងឺ: {e!s}", locale)
            return msg, [], None, []

    # ========================================================================
    # 9. ROLE-BASED DELETE DISEASE (ADMIN ONLY)
    # ========================================================================

    async def _delete_disease(
        self,
        data: dict,
        db: AsyncSession,
        locale: str,
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]]]:
        """Delete disease record and all associated translations."""
        disease_name = data.get("disease_name") or data.get("name")
        disease = await self._find_disease(disease_name, db)
        if not disease:
            msg = self._translate(f"Disease '{disease_name}' not found.", f"រកមិនឃើញជំងឺ '{disease_name}' ទេ។", locale)
            return msg, [], None, []

        try:
            d_id = disease.id
            d_slug = disease.slug
            await db.execute(delete(Translation).where(Translation.entity_type == "disease", Translation.entity_id == d_id))
            await db.delete(disease)
            await db.commit()

            target_path = "/admin/diseases"
            msg = self._translate(
                f"✅ Successfully deleted disease '{d_slug}' (ID: {d_id}).",
                f"✅ បានលុបជំងឺ '{d_slug}' (ID: {d_id}) ដោយជោគជ័យ។",
                locale,
            )
            return (
                msg,
                [{"action": "deleted_disease", "disease_id": d_id, "disease_name": d_slug}],
                target_path,
                [{"label": "Manage Diseases", "path": target_path, "type": "navigate"}],
            )
        except Exception as e:
            await db.rollback()
            msg = self._translate(f"❌ Failed to delete disease: {e!s}", f"❌ បរាជ័យក្នុងការលុបជំងឺ: {e!s}", locale)
            return msg, [], None, []

    # ========================================================================
    # 10. CREATE / UPDATE / DELETE SYMPTOM
    # ========================================================================

    async def _create_symptom(
        self,
        data: dict,
        db: AsyncSession,
        locale: str,
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]]]:
        """Create a new symptom in database."""
        label = data.get("label") or data.get("description")
        if not label:
            msg = self._translate("Please provide symptom label/description.", "សូមផ្តល់ការពិពណ៌នារោគសញ្ញា។", locale)
            return msg, [], None, []

        try:
            code = data.get("code")
            category_code = data.get("category", "leaf").lower()
            cat_res = await db.execute(select(SymptomCategory).where(SymptomCategory.code == category_code))
            category = cat_res.scalar_one_or_none()
            if not category:
                cat_res = await db.execute(select(SymptomCategory).order_by(SymptomCategory.id))
                category = cat_res.scalars().first()

            if not code:
                base_code = re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")
                prefix = category.code if category else "plant"
                code = f"{prefix}_{base_code}"[:60]

            symptom = Symptom(code=code, category_id=category.id, is_environmental=False)
            db.add(symptom)
            await db.flush()

            db.add(Translation(entity_type="symptom", entity_id=symptom.id, locale="en", field="label", value=label))
            if locale == "km":
                db.add(Translation(entity_type="symptom", entity_id=symptom.id, locale="km", field="label", value=label))
            await db.commit()

            target_path = "/admin/symptoms"
            msg = self._translate(
                f"✅ Successfully created symptom '{code}' (ID: {symptom.id}).",
                f"✅ បានបង្កើតរោគសញ្ញា '{code}' ដោយជោគជ័យ។",
                locale,
            )
            return (
                msg,
                [{"action": "created_symptom", "symptom_id": symptom.id}],
                target_path,
                [{"label": "Manage Symptoms", "path": target_path, "type": "navigate"}],
            )
        except Exception as e:
            await db.rollback()
            msg = self._translate(f"❌ Failed to create symptom: {e!s}", f"❌ បរាជ័យក្នុងការបង្កើតរោគសញ្ញា: {e!s}", locale)
            return msg, [], None, []

    async def _update_symptom(
        self,
        data: dict,
        db: AsyncSession,
        locale: str,
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]]]:
        """Update an existing symptom."""
        label = data.get("symptom_label") or data.get("label")
        symptom = await self._find_symptom(label, db)
        if not symptom:
            msg = self._translate(f"Symptom '{label}' not found.", f"រកមិនឃើញរោគសញ្ញា '{label}' ទេ។", locale)
            return msg, [], None, []

        try:
            if "new_label" in data or "label" in data:
                new_val = data.get("new_label") or data.get("label")
                res = await db.execute(
                    select(Translation).where(
                        Translation.entity_type == "symptom",
                        Translation.entity_id == symptom.id,
                        Translation.field == "label",
                        Translation.locale == locale,
                    )
                )
                trans = res.scalar_one_or_none()
                if trans:
                    trans.value = new_val
                else:
                    db.add(Translation(entity_type="symptom", entity_id=symptom.id, locale=locale, field="label", value=new_val))
            await db.commit()

            target_path = "/admin/symptoms"
            msg = self._translate(
                f"✅ Successfully updated symptom `{symptom.code}` (ID: {symptom.id}).",
                f"✅ បានធ្វើបច្ចុប្បន្នភាពរោគសញ្ញា `{symptom.code}` ដោយជោគជ័យ។",
                locale,
            )
            return (
                msg,
                [{"action": "updated_symptom", "symptom_id": symptom.id}],
                target_path,
                [{"label": "Manage Symptoms", "path": target_path, "type": "navigate"}],
            )
        except Exception as e:
            await db.rollback()
            msg = self._translate(f"❌ Failed to update symptom: {e!s}", f"❌ បរាជ័យក្នុងការធ្វើបច្ចុប្បន្នភាពរោគសញ្ញា: {e!s}", locale)
            return msg, [], None, []

    async def _delete_symptom(
        self,
        data: dict,
        db: AsyncSession,
        locale: str,
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]]]:
        """Delete symptom record (admin only)."""
        label = data.get("symptom_label") or data.get("label")
        symptom = await self._find_symptom(label, db)
        if not symptom:
            msg = self._translate(f"Symptom '{label}' not found.", f"រកមិនឃើញរោគសញ្ញា '{label}' ទេ។", locale)
            return msg, [], None, []

        try:
            s_id = symptom.id
            s_code = symptom.code
            await db.execute(delete(Translation).where(Translation.entity_type == "symptom", Translation.entity_id == s_id))
            await db.delete(symptom)
            await db.commit()

            target_path = "/admin/symptoms"
            msg = self._translate(
                f"✅ Successfully deleted symptom '{s_code}' (ID: {s_id}).",
                f"✅ បានលុបរោគសញ្ញា '{s_code}' ដោយជោគជ័យ។",
                locale,
            )
            return (
                msg,
                [{"action": "deleted_symptom", "symptom_id": s_id}],
                target_path,
                [{"label": "Manage Symptoms", "path": target_path, "type": "navigate"}],
            )
        except Exception as e:
            await db.rollback()
            msg = self._translate(f"❌ Failed to delete symptom: {e!s}", f"❌ បរាជ័យក្នុងការលុបរោគសញ្ញា: {e!s}", locale)
            return msg, [], None, []

    # ========================================================================
    # 13. SEARCH DATA
    # ========================================================================

    async def _search_data(
        self,
        query: str,
        db: AsyncSession,
        locale: str,
        user_role: str,
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]]]:
        """Search diseases and symptoms."""
        d_trans = await db.execute(
            select(Translation.entity_id).where(
                Translation.entity_type == "disease",
                Translation.value.ilike(f"%{query}%"),
            )
        )
        d_ids = set(d_trans.scalars().all())

        d_res = await db.execute(
            select(Disease).where(
                or_(
                    Disease.id.in_(d_ids) if d_ids else False,
                    Disease.slug.ilike(f"%{query}%"),
                )
            ).limit(10)
        )
        diseases = d_res.scalars().all()

        s_trans = await db.execute(
            select(Translation.entity_id).where(
                Translation.entity_type == "symptom",
                Translation.value.ilike(f"%{query}%"),
            )
        )
        s_ids = set(s_trans.scalars().all())

        s_res = await db.execute(
            select(Symptom).where(
                or_(
                    Symptom.id.in_(s_ids) if s_ids else False,
                    Symptom.code.ilike(f"%{query}%"),
                )
            ).limit(10)
        )
        symptoms = s_res.scalars().all()

        d_names = {}
        if diseases:
            dt = await db.execute(
                select(Translation).where(
                    Translation.entity_type == "disease",
                    Translation.field == "name",
                    Translation.entity_id.in_([d.id for d in diseases]),
                    Translation.locale.in_([locale, "en"]),
                )
            )
            for t in dt.scalars().all():
                d_names[t.entity_id] = t.value

        s_labels = {}
        if symptoms:
            st = await db.execute(
                select(Translation).where(
                    Translation.entity_type == "symptom",
                    Translation.field == "label",
                    Translation.entity_id.in_([s.id for s in symptoms]),
                    Translation.locale.in_([locale, "en"]),
                )
            )
            for t in st.scalars().all():
                s_labels[t.entity_id] = t.value

        suggested_actions = []
        parts = []
        if diseases:
            d_list = "\n".join([f"• **{d_names.get(d.id, d.slug)}** (`{d.slug}`)" for d in diseases])
            parts.append(f"**Diseases ({len(diseases)}):**\n{d_list}")
            for d in diseases[:3]:
                suggested_actions.append({"label": f"View {d_names.get(d.id, d.slug)}", "path": f"/diseases/{d.slug}", "type": "navigate"})

        if symptoms:
            s_list = "\n".join([f"• {s_labels.get(s.id, s.code)} (`{s.code}`)" for s in symptoms])
            parts.append(f"**Symptoms ({len(symptoms)}):**\n{s_list}")

        if not parts:
            msg = self._translate(f"No results found for '{query}'.", f"រកមិនឃើញលទ្ធផលសម្រាប់ '{query}' ទេ។", locale)
            return msg, [], None, []

        return "\n\n".join(parts), [{"action": "searched", "query": query}], None, suggested_actions

    # ========================================================================
    # 14. HELP MESSAGE
    # ========================================================================

    def _get_help_message(self, locale: str, user_role: str) -> tuple[str, list[dict[str, Any]]]:
        """Return comprehensive role-aware command guide."""
        if locale == "km":
            msg = f"""🤖 **ជំនួយការ AI នៃប្រព័ន្ធអ្នកជំនាញផ្កាឈូករ័ត្ន**
(តួនាទីរបស់អ្នក: `{user_role.upper()}`)

🧭 **ការនាំផ្លូវទៅកាន់គ្រប់ទំព័រ (Navigation):**
• "ទៅកាន់កាតាឡុកជំងឺ" &rarr; `/diseases`
• "ទៅកាន់ជំងឺ Sunflower Rust" &rarr; `/diseases/sunflower-rust`
• "ទៅកាន់ការវិភាគរោគសញ្ញា" &rarr; `/check`
• "ទៅកាន់ប្រវត្តិវិភាគ" &rarr; `/history`
• "ទៅកាន់ផ្ទាំងគ្រប់គ្រង" &rarr; `/admin`

🔬 **ការពិនិត្យរោគសញ្ញា និងជំងឺ (Symptom Matching):**
• "ពិនិត្យរោគសញ្ញា៖ ស្លឹកឡើងលឿង និងមានស្នាមអុជ"
• "តើជំងឺអ្វីខ្លះដែលបណ្តាលឱ្យមានសរសៃផ្សិតពណ៌សកប្បាស?"
• "រៀបរាប់អំពីជំងឺ Downy Mildew"

🛠️ **ការគ្រប់គ្រងទិន្នន័យតាមតួនាទី (CRUD):**
• **កសិករ (Grower):** មើលទិន្នន័យ, វិភាគរោគសញ្ញា, នាំផ្លូវ
• **អ្នកជំនាញ (Agronomist):** បង្កើតជំងឺ, កែប្រែជំងឺ, បង្កើតរោគសញ្ញា
• **អ្នកគ្រប់គ្រង (Admin):** សិទ្ធិពេញលេញ បង្កើត, កែប្រែ, លុប (CRUD)
"""
        else:
            msg = f"""🤖 **Sunflower Expert AI Assistant Guide**
(Your active role: `{user_role.upper()}`)

🧭 **System Navigation (Jump to Any Page):**
• *"Take me to Sunflower Rust"* &rarr; `/diseases/sunflower-rust`
• *"Go to symptom checker"* &rarr; `/check`
• *"Open disease catalog"* &rarr; `/diseases`
• *"Compare diseases"* &rarr; `/diseases/compare`
• *"Go to admin dashboard"* &rarr; `/admin`
• *"Go to manage symptoms"* &rarr; `/admin/symptoms`

🔬 **Diagnostic & Knowledge Intelligence:**
• *"Check symptoms: yellowing leaves and dark necrotic spots"*
• *"Tell me about Downy Mildew"*
• *"What causes cottony white mycelium on stem?"*
• *"System status"*

🛠️ **Role-Based Data Management:**
• **Grower / Farmer:** View catalog, check symptoms, interactive diagnosis
• **Agronomist (Expert):** Create & update diseases/symptoms
• **Admin:** Full CRUD (Create, Read, Update, Delete) on diseases, symptoms, rules
"""
        actions = [
            {"label": "Diseases Catalog", "path": "/diseases", "type": "navigate"},
            {"label": "Symptom Checker", "path": "/check", "type": "diagnosis"},
        ]
        if user_role in ["admin", "agronomist"]:
            actions.append({"label": "Admin Panel", "path": "/admin", "type": "navigate"})
        return msg, actions

    def _get_grower_help(self, locale: str, user_role: str) -> tuple[str, list[dict[str, Any]]]:
        """Return a friendly step-by-step guide for growers on how to use the system."""
        if locale == "km":
            msg = """🌻 **សួស្តី! ខ្ញុំជា Helio ជំនួយការ AI សម្រាប់ផ្កាឈូករ័ត្នរបស់អ្នក!**

តោះខ្ញុំបង្ហាញអ្នកពីរបៀបដែលខ្ញុំអាចជួយអ្នកបាន៖

### 📝 វិធីទី ១៖ ប្រាប់ខ្ញុំពីអ្វីដែលអ្នកឃើញ
សូមពិពណ៌នារោគសញ្ញានៅក្នុងប្រអប់ chat នេះ។ ឧទាហរណ៍៖
• *"ស្លឹកខ្ញុំមានចំណុចពណ៌ត្នោត"*
• *"ដើមខ្ញុំស្រពោន និងមានក្លិនស្អុយ"*
• *"ស្លឹកឡើងលឿង"*
ខ្ញុំនឹងវិភាគ និងប្រាប់អ្នកអំពីជំងឺដែលអាចកើតមាន!

### 📸 វិធីទី ២៖ ផ្ញើរូបថតដើមរបស់អ្នក
ចុចប៊ូតុង **📷** នៅខាងក្រោម រើសរូបភាពនៃដើមដែលមានបញ្ហា។ AI ខ្ញុំនឹង៖
1. វិភាគរូបថត 🔍
2. កំណត់រោគសញ្ញាដែលមើលឃើញ
3. ណែនាំជំងឺដែលអាចកើតមាន 🌿
4. ណែនាំជំហានបន្ទាប់សម្រាប់ការព្យាបាល

### ✅ វិធីទី ៣៖ ប្រើ Symptom Checker អន្តរកម្ម
ចូលទៅកាន់ **ការពិនិត្យរោគសញ្ញា** ដើម្បីជ្រើសរើសរោគសញ្ញាលើរូបភាពផ្កាឈូករ័ត្ន — ប្រព័ន្ធនឹងវិភាគ Bayesian ដោយស្វ័យប្រវត្តិ!

---
💬 **តើអ្នកចង់ចាប់ផ្តើមរបៀបណា?**"""
        else:
            msg = f"""🌻 **Hey there! I'm Helio, your sunflower crop advisor!**

Let me walk you through how I can help you diagnose plant problems:

### 📝 Option 1: Describe What You See
Just type what you're observing in this chat. For example:
• *"My leaves have brown spots with yellow halos"*
• *"The stem is rotting and smells bad"*  
• *"Yellow leaves and the plant is wilting"*
I'll analyze your description and tell you which diseases match!

### 📸 Option 2: Upload a Photo of Your Plant
Click the **📷 button** below the text box, select a photo of the affected plant. My AI will:
1. Analyze the image visually 🔍
2. Identify visible symptoms
3. Suggest the most likely diseases 🌿
4. Recommend next steps for treatment

### ✅ Option 3: Use the Interactive Symptom Checker
Go to the **Symptom Checker** page — you can select symptoms on a sunflower diagram and the expert system runs a Bayesian diagnosis automatically!

---
💬 **How would you like to start?** Describe your symptoms, upload a photo, or jump to the checker:"""

        actions = [
            {"label": "📸 Upload Plant Photo", "path": "I want to upload a photo of my plant", "type": "message"},
            {"label": "🔍 Symptom Checker", "path": "/check", "type": "diagnosis"},
            {"label": "📖 Browse All Diseases", "path": "/diseases", "type": "navigate"},
        ]
        if user_role in ["admin", "agronomist"]:
            actions.append({"label": "🛠️ Admin Panel", "path": "/admin", "type": "navigate"})
        return msg, actions

    # ========================================================================
    # 15. GENERAL CONVERSATION FALLBACK
    # ========================================================================

    async def _general_chat(
        self,
        message: str,
        history: list[dict],
        locale: str,
        user_role: str,
        db: AsyncSession,
    ) -> tuple[str, list[dict[str, Any]]]:
        """Handle conversational queries with live sunflower system knowledge."""
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history[-4:]])

        # Fetch LIVE dynamic counts directly from PostgreSQL database
        d_count = await db.scalar(select(func.count(Disease.id))) or 20
        s_count = await db.scalar(select(func.count(Symptom.id))) or 62
        r_count = await db.scalar(select(func.count(DiseaseSymptom.disease_id))) or 74

        is_grower = user_role not in ["admin", "agronomist"]
        grower_guidance = """

GROWER INTERACTION STYLE:
- Talk like a friendly, experienced farming advisor — warm, practical, encouraging.
- When a grower describes a problem, ALWAYS:
  1. Acknowledge their concern empathetically ("That sounds concerning" / "Good that you noticed that early")
  2. Ask 1-2 specific follow-up questions to narrow down the issue (plant part, color, timing, spread)
  3. If you can identify likely diseases, explain them simply with treatment steps
  4. ALWAYS suggest they can upload a photo using the camera button (📷) for better analysis
  5. Guide them to the Interactive Symptom Checker (/check) for formal Bayesian diagnosis
- Never be robotic. Use phrases like "Based on what you're telling me...", "That sounds like it could be...", "Let me help you figure this out"
- Keep medical/scientific terms simple: say "rusty brown powder on leaves" not "urediniospore sporulation"
""" if is_grower else ""

        prompt = f"""You are "Helio", the embedded AI crop advisor for the Sunflower Expert System.
You help growers, agronomists, and admins with sunflower disease diagnosis and system management.

YOUR PERSONALITY: You talk like a knowledgeable farming friend — warm, practical, never robotic. You genuinely care about helping growers protect their crops.

CORE OPERATING MODES:
1. Grower Mode (when user_role is "grower"):
   - Be conversational and supportive. Use simple language.
   - When they describe symptoms: acknowledge → ask follow-ups → suggest likely diseases → recommend Symptom Checker
   - ALWAYS mention they can upload a crop photo (📷 button) for visual AI analysis
   - Guide them step by step: "describe what you see" → "let me check the database" → "here's what I think" → "run the Symptom Checker to confirm"

2. Admin/Expert Mode (when user_role is "admin" or "agronomist"):
   - Knowledge base management (CRUD) with high data integrity
   - Propose or create new records, confirm changes before saving
   - Professional but still approachable tone
{grower_guidance}
LIVE SYSTEM KNOWLEDGE BASE:
- {d_count} cataloged diseases, {s_count} symptoms across 6 plant zones, {r_count} Bayesian diagnostic rules
- System pages: /diseases (catalog), /check (symptom checker), /diseases/compare, /history, /feedback, /admin

Current user role: {user_role.upper()}

Conversation history:
{context}

User: {message}

{"Respond fluently in Khmer (ភាសាខ្មែរ)." if locale == "km" else "Respond in English."}
Use exact numbers ({d_count} diseases, {s_count} symptoms, {r_count} rules).
Keep under 150 words. Be helpful, specific, and actionable.
"""
        try:
            response = await asyncio.wait_for(
                self.ollama.generate(prompt=prompt, temperature=0.7),
                timeout=float(ai_config.AI_TIMEOUT),
            )
            actions = [
                {"label": "Browse Catalog", "path": "/diseases", "type": "navigate"},
                {"label": "Symptom Checker", "path": "/check", "type": "navigate"},
            ]
            return response, actions
        except Exception as e:
            logger.warning(f"Ollama chat timeout or error: {e}. Returning smart fallback.")
            if locale == "km":
                fallback_msg = (
                    f"សួស្តី! ខ្ញុំគឺ Helio ជាជំនួយការ AI ឯកទេសផ្កាឈូករ័ត្ន។ ប្រព័ន្ធបច្ចុប្បន្នមានជំងឺចំនួន {d_count} "
                    f"រោគសញ្ញាចំនួន {s_count} និងវិធានវិភាគចំនួន {r_count}។ តើលោកអ្នកចង់ពិនិត្យរោគសញ្ញា ឬស្វែងយល់អំពីជំងឺអ្វីដែរ?"
                )
            else:
                fallback_msg = (
                    f"Hello! I am Helio, your Sunflower AI Assistant. Our knowledge base currently catalogs {d_count} diseases, "
                    f"{s_count} symptoms, and {r_count} diagnostic rules. Feel free to describe any plant symptoms, ask about disease treatments, or explore the catalog."
                )
            return fallback_msg, [
                {"label": "Browse Catalog", "path": "/diseases", "type": "navigate"},
                {"label": "Symptom Checker", "path": "/check", "type": "navigate"},
            ]

    # ========================================================================
    # 13. KNOWLEDGE GAP DISCOVERY (FIND UNRECORDED DISEASES)
    # ========================================================================

    async def _find_missing_data(
        self,
        db: AsyncSession,
        locale: str,
        user_role: str,
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]]]:
        """Cross-reference database against global sunflower pathology compendium to identify uncataloged diseases."""
        res = await db.execute(select(Disease.slug, Disease.id))
        existing_rows = res.all()
        existing_slugs = {row[0].lower() for row in existing_rows}
        db_count = len(existing_rows)

        missing_candidates = [
            item for item in SUNFLOWER_GLOBAL_CATALOG
            if item["slug"].lower() not in existing_slugs
        ]

        if not missing_candidates:
            msg = self._translate(
                f"### 🌿 Knowledge Base is Comprehensive!\n\nAll **{len(SUNFLOWER_GLOBAL_CATALOG)}** major reference sunflower diseases and disorders are fully cataloged in your database (total active diseases: **{db_count}**).\n\nIf you have a novel field pathogen or emerging strain to add, you can propose it at any time with `Add disease [Name]`.",
                f"### 🌿 មូលដ្ឋានទិន្នន័យមានភាពពេញលេញ!\n\nជំងឺផ្កាឈូករ័ត្នសំខាន់ៗទាំង **{len(SUNFLOWER_GLOBAL_CATALOG)}** ត្រូវបានកត់ត្រាទុកយ៉ាងពេញលេញក្នុងប្រព័ន្ធ (សរុបជំងឺទាំងអស់៖ **{db_count}**)។",
                locale,
            )
            suggested = [
                {"label": "Browse Catalog", "path": "/diseases", "type": "navigate"},
                {"label": "System Stats", "path": "system stats", "type": "message"},
            ]
            return msg, [], None, suggested

        # Format bilingual agronomic gap report
        if locale == "km":
            lines = [
                "### 🔬 ការវិភាគរកទិន្នន័យជំងឺដែលមិនទាន់មានក្នុងប្រព័ន្ធ (Knowledge Gap Discovery)",
                f"បច្ចុប្បន្ន ប្រព័ន្ធមានជំងឺផ្លូវការចំនួន **{db_count} ជំងឺ**។",
                f"តាមការផ្ទៀងផ្ទាត់ជាមួយ **កាតាឡុកជំងឺផ្កាឈូករ័ត្នអន្តរជាតិ (USDA, FAO & EPPO)** យើងបានរកឃើញជំងឺ និងបញ្ហាដំណាំសំខាន់ៗចំនួន **{len(missing_candidates)}** ដែលមិនទាន់ត្រូវបានកត់ត្រាក្នុងប្រព័ន្ធរបស់អ្នកនៅឡើយទេ៖\n",
            ]
            for idx, c in enumerate(missing_candidates, 1):
                icon = "🍄" if c["pathogen_type"] == "fungal" else "🧫" if c["pathogen_type"] == "bacterial" else "🦠" if c["pathogen_type"] == "viral" else "🌾"
                lines.append(f"#### {idx}. {icon} **{c['name_km']}** ({c['name_en']})")
                lines.append(f"- **ឈ្មោះវិទ្យាសាស្ត្រ:** *{c['scientific_name']}* | **ប្រភេទ:** `{c['pathogen_type']}`")
                lines.append(f"- **រោគសញ្ញាសំខាន់ៗ:** {c['key_symptoms']}")
                lines.append(f"- **កម្រិតធ្ងន់ធ្ងរ:** {c['severity']} — {c['impact']}")
                lines.append(f"- **សកម្មភាព:** វាយពាក្យ `draft disease {c['name_en']}` ឬចុចប៊ូតុងខាងក្រោម។\n")

            if user_role in ["admin", "agronomist"]:
                lines.append("---")
                lines.append("💡 **សម្រាប់ Admin / អ្នកជំនាញ:** ចុចលើប៊ូតុង **[➕ បង្កើតសេចក្តីព្រាង ...]** ខាងក្រោម។ ប្រព័ន្ធនឹងរៀបចំទិន្នន័យពេញលេញ (ការបកប្រែ ១០ ភាសា រោគសញ្ញា Bayesian និងវិធីព្យាបាល) សម្រាប់លោកអ្នកត្រួតពិនិត្យ និងបញ្ជាក់មុននឹងរក្សាទុកក្នុងមូលដ្ឋានទិន្នន័យ។")
            else:
                lines.append("---")
                lines.append("💡 **សម្គាល់:** អ្នកប្រើប្រាស់ទូទៅអាចស្នើសុំអ្នកជំនាញ ឬ Admin ដើម្បីបញ្ចូលជំងឺទាំងនេះ។")
        else:
            lines = [
                "### 🔬 Sunflower Pathology Knowledge Gap Analysis",
                f"Our system currently catalogs **{db_count} official sunflower diseases**.",
                f"Cross-referencing against the **International Sunflower Pathology Compendium (USDA-ARS, FAO & EPPO)** identified **{len(missing_candidates)} candidate diseases & disorders** not yet recorded in your database:\n",
            ]
            for idx, c in enumerate(missing_candidates, 1):
                icon = "🍄" if c["pathogen_type"] == "fungal" else "🧫" if c["pathogen_type"] == "bacterial" else "🦠" if c["pathogen_type"] == "viral" else "🌾"
                lines.append(f"#### {idx}. {icon} **{c['name_en']}** (*{c['scientific_name']}*)")
                lines.append(f"- **Pathogen Classification:** `{c['pathogen_type']}` | **Severity:** {c['severity']}")
                lines.append(f"- **Key Diagnostic Symptoms:** {c['key_symptoms']}")
                lines.append(f"- **Agronomic Impact:** {c['impact']}")
                lines.append(f"- **Quick Draft:** Click **[➕ Draft {c['name_en']}]** below or type `draft disease {c['name_en']}`.\n")

            if user_role in ["admin", "agronomist"]:
                lines.append("---")
                lines.append("💡 **Next Step for Expert/Admin:**")
                lines.append("Click any of the **[➕ Draft ...]** buttons below. I will synthesize the full botanical profile (10 language translations, Bayesian rulesets, treatments, and prevention) and present a preview for your confirmation before saving to the database.")
            else:
                lines.append("---")
                lines.append("💡 **Note:** Role permissions indicate you are logged in as a grower. Contact an Administrator or Expert Agronomist to approve new additions.")

        response_message = "\n".join(lines)

        suggested_actions = []
        if user_role in ["admin", "agronomist"]:
            for c in missing_candidates[:4]:
                suggested_actions.append({
                    "label": f"➕ Draft {c['name_en']}",
                    "path": f"draft disease {c['name_en']}",
                    "type": "message",
                })
        suggested_actions.append({"label": "All Diseases (Admin)", "path": "/admin/diseases", "type": "navigate"})
        suggested_actions.append({"label": "System Stats", "path": "system stats", "type": "message"})

        return response_message, [{"action": "find_missing_data", "count": len(missing_candidates)}], None, suggested_actions

    # ========================================================================
    # 14. DATA MANAGEMENT & CRUD CONTROL GUIDE
    # ========================================================================

    async def _data_management_guide(
        self,
        locale: str,
        user_role: str,
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]]]:
        """Comprehensive guide for finding new data, adding, editing, and deleting records with role permissions."""
        is_admin_or_expert = user_role in ["admin", "agronomist"]
        role_label = "Administrator" if user_role == "admin" else "Expert Agronomist" if user_role == "agronomist" else "Grower"

        if locale == "km":
            msg = f"""### 🌾 មគ្គុទ្ទេសក៍គ្រប់គ្រងទិន្នន័យ និងជំនួយការឆ្លាតវៃ

ខ្ញុំអាចជួយលោកអ្នកក្នុងការ **ស្វែងរកទិន្នន័យដែលមិនទាន់មាន**, **បន្ថែមជំងឺ និងរោគសញ្ញាថ្មី**, **កែសម្រួលទិន្នន័យចាស់**, និង **លុបទិន្នន័យ** ដោយផ្អែកលើសិទ្ធិគណនីបច្ចុប្បន្នរបស់អ្នក (**{role_label}**)៖

---
#### 1. 🔍 ស្វែងរកទិន្នន័យថ្មីដែលប្រព័ន្ធមិនទាន់មាន (Discover Missing Data)
- **មុខងារ:** ស្វែងរក និងផ្ទៀងផ្ទាត់ជំងឺផ្កាឈូករ័ត្នជាសកលដែលមិនទាន់មានក្នុងមូលដ្ឋានទិន្នន័យរបស់អ្នក។
- **របៀបប្រើ:** វាយពាក្យ `"find new diseases"`, `"តើមានជំងឺអ្វីខ្លះដែលមិនទាន់មាន"`, ឬចុច **[🔍 រកជំងឺដែលមិនទាន់មាន]** ខាងក្រោម។

#### 2. ➕ បន្ថែមជំងឺថ្មី (ដោយមានការបញ្ជាក់ទិន្នន័យជាមុន)
- **សិទ្ធិអនុញ្ញាត:** **Admin** ឬ **អ្នកជំនាញកសិកម្ម (Agronomist)**។
- **របៀបដំណើរការ:** 
  1. ស្នើសុំបន្ថែម៖ `Add disease Southern Blight` ឬ `Draft Bacterial Soft Rot`។
  2. AI នឹងបង្កើតទិន្នន័យលម្អិតពេញលេញ (ឈ្មោះវិទ្យាសាស្ត្រ ការបកប្រែ ១០ ភាសា រោគសញ្ញា Bayesian វិធីព្យាបាល និងការពារ)។
  3. **ប្រព័ន្ធបញ្ជាក់ទិន្នន័យ (Confirmation Guard):** AI នឹងបង្ហាញសេចក្តីព្រាងឱ្យលោកអ្នកត្រួតពិនិត្យជាមុន។ លុះត្រាតែលោកអ្នកឆ្លើយ `"យល់ព្រម"` (ឬ `"confirm"`) ទើបទិន្នន័យត្រូវបានរក្សាទុកចូលក្នុងប្រព័ន្ធ។

#### 3. ✏️ កែសម្រួលទិន្នន័យ (Edit & Update Data)
- **សិទ្ធិអនុញ្ញាត:** **Admin** ឬ **អ្នកជំនាញកសិកម្ម**។
- **ផ្ទាំងគ្រប់គ្រង Admin:**
  - 📋 [គ្រប់គ្រងជំងឺ](/admin/diseases) — កែសម្រួលរោគសញ្ញា ប្រភេទមេរោគ និងវិធីព្យាបាល។
  - 🌿 [គ្រប់គ្រងរោគសញ្ញា](/admin/symptoms) — កែសម្រួលស្លាកឈ្មោះ និងទម្ងន់រោគសញ្ញា។
- **តាមរយៈ Chat:** វាយពាក្យ `Edit disease Rust` ឬ `Update symptom Leaf Spots`។

#### 4. 🗑️ លុបទិន្នន័យ (Delete Data)
- **សិទ្ធិអនុញ្ញាត:** **Admin តែប៉ុណ្ណោះ** (មានសុវត្ថិភាពខ្ពស់ និងការពារទិន្នន័យពាក់ព័ន្ធ)។
- **តាមរយៈផ្ទាំងគ្រប់គ្រង:** ចូលទៅកាន់ [តារាងជំងឺ](/admin/diseases)។
- **តាមរយៈ Chat:** វាយពាក្យ `Delete disease [ឈ្មោះជំងឺ]`។

---
💡 **តើលោកអ្នកចង់ធ្វើអ្វីបន្ត?** សូមជ្រើសរើសជម្រើសខាងក្រោម៖"""
        else:
            msg = f"""### 🌾 Sunflower Expert System — Data Management & Assistant Guide

I am fully equipped to help you **discover missing data**, **add new diseases & symptoms**, **edit existing records**, and **safely delete data** according to your current role permissions (**{role_label}**).

---
#### 1. 🔍 Find New Data (Knowledge Gap Discovery)
- **What it does:** Scans your database against global sunflower pathology compendiums (USDA-ARS, FAO, EPPO) to identify uncataloged diseases, symptoms, and physiological disorders.
- **How to use:** Say `"find new diseases"`, `"what diseases are missing"`, or click **[🔍 Discover Missing Diseases]** below.
- **Instant Drafting:** Offers 1-click drafting for candidates like *Southern Blight*, *Bacterial Soft Rot*, *Apical Chlorosis*, etc.

#### 2. ➕ Add New Disease (With Expert Confirmation Workflow)
- **Permission Required:** **Administrator** or **Expert Agronomist**.
- **How it works:**
  1. **Request:** Type `Add disease Southern Blight` or `Draft Bacterial Soft Rot`.
  2. **Automated Botanical Synthesis:** The AI formulates the complete profile including scientific name, pathogen classification, key symptoms, treatments, prevention, and 10 language translations.
  3. **Confirmation Guard:** The AI presents an interactive preview. Nothing is written to the database until you explicitly reply `"confirm"` (or click **[✅ Confirm & Save]**). You can also reply `"cancel"` to discard.

#### 3. ✏️ Edit & Update Existing Data
- **Permission Required:** **Administrator** or **Expert Agronomist**.
- **Direct Admin Interfaces:**
  - 📋 [Manage Diseases](/admin/diseases) — Edit pathogen classification, descriptions, symptoms, and treatment guidelines.
  - 🌿 [Manage Symptoms](/admin/symptoms) — Edit symptom labels, plant parts, and diagnostic weights.
- **Via Chat:** Say `"Edit disease Rust"` or `"Update symptom Yellowing"`.

#### 4. 🗑️ Delete Data (Protected Operation)
- **Permission Required:** **Administrator Only**.
- **Safety Protocol:** Deletions perform relational cascade checks to preserve system integrity.
- **Direct Admin Interface:** Visit the [Disease Management Table](/admin/diseases).
- **Via Chat:** Say `"Delete disease [Name]"`.

---
💡 **What would you like to do right now?** Click one of the shortcuts below:"""

        suggested = [
            {"label": "🔍 Discover Missing Diseases", "path": "find new data that my system not yet have", "type": "message"},
        ]
        if is_admin_or_expert:
            suggested.append({"label": "➕ Draft Southern Blight", "path": "draft disease Southern Blight", "type": "message"})
            suggested.append({"label": "📋 Manage Diseases", "path": "/admin/diseases", "type": "navigate"})
            suggested.append({"label": "🌿 Manage Symptoms", "path": "/admin/symptoms", "type": "navigate"})
        else:
            suggested.append({"label": "Browse Diseases", "path": "/diseases", "type": "navigate"})
            suggested.append({"label": "Symptom Checker", "path": "/check", "type": "navigate"})
        suggested.append({"label": "📊 System Overview", "path": "system stats", "type": "message"})

        return msg, [{"action": "data_management_guide"}], None, suggested

    # ========================================================================
    # CLINICAL AGRONOMY & PATHOLOGY CAPABILITIES
    # ========================================================================

    async def _fetch_consolidated_disease_profile(
        self,
        disease: Disease,
        locale: str,
        db: AsyncSession,
    ) -> dict[str, Any]:
        """Fetch consolidated disease details, localized translations, and weighted symptoms."""
        t_res = await db.execute(
            select(Translation).where(
                Translation.entity_type == "disease",
                Translation.entity_id == disease.id,
            )
        )
        translations = t_res.scalars().all()
        trans_map: dict[str, dict[str, str]] = {}
        for t in translations:
            if t.locale not in trans_map:
                trans_map[t.locale] = {}
            trans_map[t.locale][t.field] = t.value

        loc_data = trans_map.get(locale, {})
        en_data = trans_map.get("en", {})

        name = loc_data.get("name") or en_data.get("name") or disease.slug.replace("-", " ").title()
        desc = loc_data.get("description") or en_data.get("description") or ""
        treatment = loc_data.get("treatment") or en_data.get("treatment") or ""
        prevention = loc_data.get("prevention") or en_data.get("prevention") or ""
        cause = loc_data.get("cause") or en_data.get("cause") or ""

        # Fetch associated symptoms with weights
        ds_res = await db.execute(
            select(DiseaseSymptom, Symptom)
            .join(Symptom, DiseaseSymptom.symptom_id == Symptom.id)
            .where(DiseaseSymptom.disease_id == disease.id)
            .order_by(DiseaseSymptom.weight.desc())
        )
        symptom_pairs = ds_res.all()

        symptoms_list = []
        if symptom_pairs:
            s_ids = [s.id for _, s in symptom_pairs]
            st_res = await db.execute(
                select(Translation).where(
                    Translation.entity_type == "symptom",
                    Translation.entity_id.in_(s_ids),
                    Translation.field == "label",
                    Translation.locale == locale,
                )
            )
            s_trans = {t.entity_id: t.value for t in st_res.scalars().all()}
            for ds, s in symptom_pairs:
                lbl = s_trans.get(s.id) or s.code.replace("_", " ").title()
                symptoms_list.append({
                    "id": s.id,
                    "code": s.code,
                    "label": lbl,
                    "weight": float(ds.weight),
                    "is_pathognomonic": ds.is_pathognomonic,
                    "is_required": ds.is_required,
                })

        p_type = disease.pathogen_type.value if hasattr(disease.pathogen_type, "value") else str(disease.pathogen_type)
        return {
            "id": disease.id,
            "slug": disease.slug,
            "name": name,
            "pathogen_type": p_type,
            "description": desc,
            "treatment": treatment,
            "prevention": prevention,
            "cause": cause,
            "symptoms": symptoms_list,
        }

    async def _compare_diseases(
        self,
        query_text: str,
        db: AsyncSession,
        locale: str,
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]]]:
        """Differential comparison matrix between two or more sunflower diseases."""
        cleaned_text = re.sub(
            r"\b(compare|difference\s+between|vs\.?|versus|and|between|disease|diseases|ប្រៀបធៀប|ភាពខុសគ្នា|ជំងឺ)\b",
            " ",
            query_text,
            flags=re.IGNORECASE,
        ).strip()

        # Split candidates
        tokens = [p.strip() for p in re.split(r"[\s,;&]+", cleaned_text) if len(p.strip()) >= 3]

        found_diseases: list[Disease] = []
        found_ids: set[int] = set()

        # Try to find diseases matching tokens
        for token in tokens:
            d = await self._find_disease(token, db)
            if d and d.id not in found_ids:
                found_diseases.append(d)
                found_ids.add(d.id)
            if len(found_diseases) >= 2:
                break

        # If we couldn't find 2 diseases, scan DB diseases against original query
        if len(found_diseases) < 2:
            all_res = await db.execute(select(Disease).order_by(Disease.id))
            all_db_diseases = all_res.scalars().all()
            q_lower = query_text.lower()
            for d in all_db_diseases:
                if d.id not in found_ids:
                    if d.slug.replace("-", " ") in q_lower or d.slug.split("-")[0] in q_lower:
                        found_diseases.append(d)
                        found_ids.add(d.id)
                        if len(found_diseases) >= 2:
                            break

        # Fallback if only 1 disease found: pair with clinically common counterpart
        counterparts = {
            "sunflower-rust": "downy-mildew",
            "downy-mildew": "sunflower-rust",
            "white-mold": "charcoal-rot",
            "charcoal-rot": "white-mold",
            "verticillium-wilt": "bacterial-wilt",
            "phoma-black-stem": "phomopsis-stem-canker",
            "alternaria-leaf-blight": "septoria-leaf-spot",
        }
        if len(found_diseases) == 1:
            target_slug = counterparts.get(found_diseases[0].slug, "downy-mildew" if found_diseases[0].slug != "downy-mildew" else "sunflower-rust")
            counterpart = await self._find_disease(target_slug, db)
            if counterpart and counterpart.id not in found_ids:
                found_diseases.append(counterpart)

        # Fallback if 0 diseases found: pick top 2 published diseases
        if len(found_diseases) < 2:
            res_top = await db.execute(select(Disease).limit(2))
            top_diseases = res_top.scalars().all()
            for td in top_diseases:
                if td.id not in found_ids:
                    found_diseases.append(td)
                    found_ids.add(td.id)
                    if len(found_diseases) >= 2:
                        break

        if len(found_diseases) < 2:
            return (
                self._translate(
                    "Please specify at least two diseases to compare (e.g., `Compare Rust and Downy Mildew`).",
                    "សូមបញ្ជាក់ឈ្មោះជំងឺយ៉ាងហោចណាស់ពីរដើម្បីប្រៀបធៀប (ឧទាហរណ៍ `ប្រៀបធៀប Rust និង Downy Mildew`)។",
                    locale,
                ),
                [],
                None,
                [{"label": "Compare Rust vs Downy Mildew", "path": "compare rust and downy mildew", "type": "message"}],
            )

        d1 = found_diseases[0]
        d2 = found_diseases[1]
        info1 = await self._fetch_consolidated_disease_profile(d1, locale, db)
        info2 = await self._fetch_consolidated_disease_profile(d2, locale, db)

        s1_top = [s["label"] for s in info1["symptoms"][:3]] or ["Leaf and stem lesions"]
        s2_top = [s["label"] for s in info2["symptoms"][:3]] or ["Leaf and stem lesions"]

        if locale == "km":
            msg = f"""### 🔬 តារាងវិភាគប្រៀបធៀបជំងឺ៖ **{info1['name']}** vs. **{info2['name']}**

| លក្ខណៈវិនិច្ឆ័យ | **{info1['name']}** | **{info2['name']}** |
| :--- | :--- | :--- |
| **ប្រភេទមេរោគ** | {info1['pathogen_type'].capitalize()} | {info2['pathogen_type'].capitalize()} |
| **រោគសញ្ញាសំខាន់ៗ** | {', '.join(s1_top)} | {', '.join(s2_top)} |
| **ផ្នែករុក្ខជាតិប៉ះពាល់** | ស្លឹក និងដើម | ស្លឹក, ដើម ឬកញ្ចុំផ្កា |
| **យុទ្ធសាស្ត្រព្យាបាល** | {info1['treatment'][:120] if info1['treatment'] else 'ប្រើប្រាស់ថ្នាំកម្ចាត់ផ្សិតសមស្រប'}... | {info2['treatment'][:120] if info2['treatment'] else 'ប្រើប្រាស់ថ្នាំកម្ចាត់ផ្សិតសមស្រប'}... |

---
#### 💡 ចំណុចសម្គាល់ខុសគ្នានៅក្នុងចម្ការ (Field Diagnostic Key)
- **{info1['name']}:** {info1['description'][:180]}...
- **{info2['name']}:** {info2['description'][:180]}...
"""
        else:
            msg = f"""### 🔬 Differential Diagnosis Matrix: **{info1['name']}** vs. **{info2['name']}**

| Clinical Feature | **{info1['name']}** | **{info2['name']}** |
| :--- | :--- | :--- |
| **Pathogen Class** | `{info1['pathogen_type'].capitalize()}` | `{info2['pathogen_type'].capitalize()}` |
| **Key Hallmark Symptoms** | {', '.join(s1_top)} | {', '.join(s2_top)} |
| **Primary Plant Organs** | Leaves, petioles, and stem surfaces | Leaves, vascular stem, root crown, or floral disk |
| **Fungicide / Clinical Control** | {info1['treatment'][:140] if info1['treatment'] else 'Targeted protective or systemic fungicide protocol'}... | {info2['treatment'][:140] if info2['treatment'] else 'Targeted protective or systemic fungicide protocol'}... |
| **Cultural Prevention** | {info1['prevention'][:140] if info1['prevention'] else 'Certified seed, sanitation, crop rotation'}... | {info2['prevention'][:140] if info2['prevention'] else 'Certified seed, sanitation, crop rotation'}... |

---
#### 🔍 Field Distinction Guide (How to Tell Them Apart on Site)
- **{info1['name']} Tell:** {info1['description'][:200]}...
- **{info2['name']} Tell:** {info2['description'][:200]}...
- **Diagnostic Advice:** When distinguishing foliar blights from systemic wilts, check whether rubbing a clean tissue picks up loose powder/spores, or if vascular discoloration is visible when slicing open the lower stem.
"""

        suggested = [
            {"label": f"View {info1['name']}", "path": f"/diseases/{info1['slug']}", "type": "navigate"},
            {"label": f"View {info2['name']}", "path": f"/diseases/{info2['slug']}", "type": "navigate"},
            {"label": "🔬 Symptom Checker", "path": "/check", "type": "navigate"},
            {"label": "Compare White Mold vs Charcoal Rot", "path": "compare white mold and charcoal rot", "type": "message"},
        ]

        return msg, [{"action": "compare_diseases", "diseases": [info1["slug"], info2["slug"]]}], None, suggested

    async def _growth_stage_scout(
        self,
        stage_query: str,
        locale: str,
        db: AsyncSession,
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]]]:
        """Growth stage disease scouting calendar and risk assessment."""
        q = stage_query.lower()

        # Identify stage
        if any(k in q for k in ["seedling", "emergence", "early", "ve", "v1", "v2", "v4", "កូនដំណាំ"]):
            stage_key = "seedling"
            stage_title = "Stage 1: Seedling & Emergence (VE - V4)"
            stage_title_km = "ដំណាក់កាលទី ១៖ កូនដំណាំ និងដុះពន្លក (VE - V4)"
            risks_en = [
                "**Downy Mildew (*Plasmopara halstedii*)**: Systemic stunting, chlorotic pale-green leaves with white downy fungal growth on lower leaf surfaces.",
                "**Damping-Off & Seedling Blight (*Pythium / Rhizoctonia*)**: Water-soaked hypocotyl collapse at soil level, poor stand establishment.",
                "**Wireworms / Cutworms**: Cut stems just below or at ground level."
            ]
            risks_km = [
                "**ជំងឺស្រពោន ឬ Downy Mildew**: កូនដំណាំក្រិន ស្លឹកមានពណ៌លឿងស្លេក និងមានកោសិកាផ្សិតពណ៌សនៅក្រោមស្លឹក។",
                "**ជំងឺរលួយកូនដំណាំ (Damping-off)**: រលួយគល់កម្រិតដី ធ្វើឱ្យដើមដួលងាប់។",
            ]
            scout_en = "Inspect 10 random 20-foot row sections. Look closely under the lowest true leaves for white cottony sporulation on dewy mornings. Check root collar for brown girdling."
            scout_km = "ពិនិត្យផ្ទៃក្រោមស្លឹកនៅពេលព្រឹកព្រលឹមដែលមានទឹកសន្សើម រកមើលផ្សិតពណ៌ស និងពិនិត្យគល់ដើមរកស្នាមរលួយពណ៌ត្នោត។"
            rec_en = "Use certified mefenoxam/metalaxyl treated seed. Ensure well-drained soil. If downy mildew is systemic (>10% field infected), rogue out plants early."
            rec_km = "ប្រើគ្រាប់ពូជដែលបានលាយថ្នាំការពារ (Mefenoxam/Metalaxyl) និងរៀបចំប្រព័ន្ធបង្ហូរទឹកកុំឱ្យជាំទឹក។"

        elif any(k in q for k in ["flower", "flowering", "bloom", "bud", "r1", "r2", "r3", "r4", "r5", "anthesis", "ចេញផ្កា"]):
            stage_key = "flowering"
            stage_title = "Stage 3: Bud Development to Flowering (R1 - R5)"
            stage_title_km = "ដំណាក់កាលទី ៣៖ ចាប់ផ្តើមកកើតផ្កា ដល់រីកពេញលេញ (R1 - R5)"
            risks_en = [
                "**Sclerotinia Head Rot (*Sclerotinia sclerotiorum*)**: Water-soaked bleached spots on back of head, disintegrating floral disks with dense white mycelium and black rat-dropping sclerotia.",
                "**Sunflower Rust (*Puccinia helianthi*)**: Cinnamon-brown to chocolate-brown pustules spreading from lower to upper leaves rapidly.",
                "**Verticillium Wilt (*Verticillium dahliae*)**: Interveinal chlorosis and necrosis ('mottled leaves') beginning on lower canopy.",
                "**Bacterial Head Rot (*Pectobacterium*)**: Soft, water-soaked, foul-smelling collapse of floral disk."
            ]
            risks_km = [
                "**ជំងឺរលួយក្បាលផ្កា Sclerotinia**: ស្នាមជាំទឹករីករាលដាលលើខ្នងផ្កា មានកោសិកាផ្សិតពណ៌ស និងគ្រាប់ខ្មៅ (Sclerotia)។",
                "**ជំងឺច្រែះផ្កាឈូករ័ត្ន (Rust)**: ពងបែកម្សៅពណ៌ត្នោតក្រម៉ៅរាលដាលលើស្លឹកយ៉ាងលឿន។",
                "**ជំងឺក្រៀមស្លឹក Verticillium**: ស្លឹកមានស្នាមលឿង និងក្រៀមចន្លោះទ្រនុងស្លឹក។",
            ]
            scout_en = "Critical threshold period! Walk a 'W' pattern across field. Invert sunflower heads to examine back of receptacle for softening or bleached lesions. Check upper leaves for rust pustules."
            scout_km = "ដំណាក់កាលប្រុងប្រយ័ត្នខ្ពស់បំផុត! ត្រឡប់ក្បាលផ្កាពិនិត្យផ្នែកខាងក្រោយរកស្នាមរលួយជាំទឹក និងពិនិត្យស្លឹកលើរកពងបែកច្រែះ។"
            rec_en = "If humid weather (>80% RH) coincides with bloom (R5.1), consider prophylactic fungicide application (Boscalid, Fluopyram, or Azoxystrobin). Spray during dusk or dawn to protect pollinating bees."
            rec_km = "ប្រសិនបើមានភ្លៀង ឬសំណើមខ្ពស់ពេលផ្ការីក ត្រូវបាញ់ថ្នាំការពារផ្សិតសមស្រប។ ជៀសវាងបាញ់ពេលថ្ងៃត្រង់ដើម្បីកុំឱ្យប៉ះពាល់ដល់សត្វឃ្មុំក្រេបលម្អង។"

        elif any(k in q for k in ["ripening", "seed fill", "maturity", "harvest", "r6", "r7", "r8", "r9", "desiccation", "ទុំ", "ប្រមូលផល"]):
            stage_key = "ripening"
            stage_title = "Stage 4: Seed Filling to Physiological Maturity (R6 - R9)"
            stage_title_km = "ដំណាក់កាលទី ៤៖ បំពេញគ្រាប់ ដល់ទុំពេញលេញ (R6 - R9)"
            risks_en = [
                "**Charcoal Rot (*Macrophomina phaseolina*)**: Ash-gray stem discoloration at soil line; shredded pith filled with pepper-like black microsclerotia; accelerated senescence under hot, drought conditions.",
                "**Rhizopus Head Rot (*Rhizopus oryzae*)**: Brown, spongy head rot typically triggered by bird damage or hail puncture wounds.",
                "**Phomopsis Stem Canker (*Diaporthe helianthi*)**: Sunken brownish-tan lesions around petiole leaf insertions; hollow, easily crushable stems."
            ]
            risks_km = [
                "**ជំងឺរលួយធ្យូង (Charcoal Rot)**: គល់ដើមឡើងពណ៌ប្រផេះដូចផេះ ពេលពុះដើមឃើញបណ្តូលដូចកម្ទេចធ្យូង ងាយកើតពេលក្តៅស្ងួតខ្លាំង។",
                "**ជំងឺរលួយក្បាលផ្កា Rhizopus**: ក្បាលផ្ការលួយស្ពោតៗ បណ្តាលមកពីសត្វស្លាបចឹក ឬមានរបួស។",
            ]
            scout_en = "Tap stems at base to check structural rigidity. Split stems of prematurely drying plants to inspect pith color and presence of microsclerotia. Examine seed heads for spongy rot."
            scout_km = "សង្កត់គល់ដើមពិនិត្យមើលថាតើរឹងមាំឬស្ពោត។ ពុះដើមពិនិត្យបណ្តូលដើមរកម្សៅខ្មៅ និងពិនិត្យគ្រាប់ក្នុងក្បាលផ្កា។"
            rec_en = "Mitigate charcoal rot with supplemental irrigation during seed fill if available. Harvest promptly once back of head turns lemon-yellow to brown and seed moisture drops to ~10%."
            rec_km = "ផ្តល់ការស្រោចស្រពបន្ថែមបើជួបគ្រោះរាំងស្ងួត។ ប្រមូលផលភ្លាមៗនៅពេលខ្នងក្បាលផ្កាឡើងពណ៌លឿងក្រូចឆ្មា និងគ្រាប់ស្ងួតល្អ។"

        else:
            stage_key = "vegetative"
            stage_title = "Stage 2: Vegetative Growth & Stem Elongation (V4 - R1)"
            stage_title_km = "ដំណាក់កាលទី ២៖ ការលូតលាស់ដើម និងស្លឹក (V4 - R1)"
            risks_en = [
                "**Phoma Black Stem (*Phoma macdonaldii*)**: Jet-black circular lesions originating at leaf petiole nodes on the stem; premature leaf death.",
                "**Septoria & Alternaria Leaf Blights**: Irregular circular brown lesions with concentric rings or yellow halos on lower leaves.",
                "**Sunflower Rust Early Inoculum**: First generation of rust pustules appearing on lower canopy leaves."
            ]
            risks_km = [
                "**ជំងឺស្នាមខ្មៅលើដើម (Phoma Black Stem)**: ស្នាមអុចខ្មៅដិតនៅត្រង់ថ្នាំងទងស្លឹកលើដើម។",
                "**ជំងឺរលាកស្លឹក Alternaria & Septoria**: ស្នាមអុចពណ៌ត្នោតជារង្វង់លើស្លឹកចាស់ៗផ្នែកខាងក្រោម។",
            ]
            scout_en = "Inspect mid-to-lower leaves and leaf petiole attachment points along the main stem. Count lesions per leaf to evaluate economic treatment threshold."
            scout_km = "ពិនិត្យស្លឹកផ្នែកកណ្តាល និងផ្នែកខាងក្រោម ព្រមទាំងគល់ទងស្លឹកដែលភ្ជាប់នឹងដើម។"
            rec_en = "Maintain balanced nitrogen fertility (avoid excessive N that promotes rank succulent canopy). Manage weed competition. If rust severity exceeds 3% on upper leaves before bud stage, apply triazole/strobilurin fungicide."
            rec_km = "ដាក់ជីឱ្យមានតុល្យភាព (កុំដាក់ជីអាសូតច្រើនហួសហេតុ)។ បើមានជំងឺច្រែះរាលដាលលើស្លឹកលើសពី ៣% ត្រូវបាញ់ថ្នាំការពារ។"

        if locale == "km":
            risks_md = "\n".join(f"- {r}" for r in risks_km)
            msg = f"""### 🌻 ប្រតិទិនត្រួតពិនិត្យជំងឺតាមដំណាក់កាល៖ **{stage_title_km}**

#### ⚠️ ជំងឺប្រឈមហានិភ័យខ្ពស់ក្នុងដំណាក់កាលនេះ៖
{risks_md}

#### 🔍 វិធីសាស្ត្រចុះត្រួតពិនិត្យផ្ទាល់ក្នុងចម្ការ (Field Scouting Protocol):
{scout_km}

#### 🛡️ វិធានការគ្រប់គ្រង និងអនុសាសន៍៖
{rec_km}

---
💡 **ជ្រើសរើសដំណាក់កាលផ្សេងទៀតដើម្បីត្រួតពិនិត្យ៖**"""
        else:
            risks_md = "\n".join(f"- {r}" for r in risks_en)
            msg = f"""### 🌻 Sunflower Growth Stage Scouting Advisor: **{stage_title}**

#### ⚠️ High-Risk Pathogens & Target Diseases:
{risks_md}

#### 🔍 Field Scouting Protocol & What to Look For:
{scout_en}

#### 🛡️ Management Recommendations & Action Thresholds:
{rec_en}

---
💡 **Scout other critical growth stages:**"""

        suggested = [
            {"label": "🌱 Scout Seedling Stage", "path": "scout seedling stage diseases", "type": "message"},
            {"label": "🌿 Scout Vegetative Stage", "path": "scout vegetative stage diseases", "type": "message"},
            {"label": "🌻 Scout Flowering Stage", "path": "scout flowering stage diseases", "type": "message"},
            {"label": "🌾 Scout Ripening Stage", "path": "scout ripening stage diseases", "type": "message"},
            {"label": "🔬 Symptom Checker", "path": "/check", "type": "navigate"},
        ]

        return msg, [{"action": "growth_stage_scout", "stage": stage_key}], None, suggested

    async def _get_treatment_prescription(
        self,
        disease_query: str,
        db: AsyncSession,
        locale: str,
    ) -> tuple[str, list[dict[str, Any]], str | None, list[dict[str, Any]]]:
        """Generate structured 3-tier clinical prescription and fungicide advisory for a disease."""
        cleaned = re.sub(
            r"\b(how\s+to\s+treat|treatment\s+for|how\s+to\s+cure|cure|chemical\s+control|fungicide\s+for|spray\s+for|management\s+of|how\s+to\s+control|organic\s+treatment|prescription\s+for|active\s+ingredient|disease|sunflower|វិធីព្យាបាល|ថ្នាំកម្ចាត់|ថ្នាំសម្លាប់មេរោគ|វិធីទប់ស្កាត់|ជំងឺ)\b",
            " ",
            disease_query,
            flags=re.IGNORECASE,
        ).strip()

        disease = await self._find_disease(cleaned, db) if cleaned else None

        if not disease:
            all_res = await db.execute(select(Disease))
            for d in all_res.scalars().all():
                if d.slug.replace("-", " ") in disease_query.lower() or d.slug.split("-")[0] in disease_query.lower():
                    disease = d
                    break

        if not disease:
            d_list_res = await db.execute(select(Disease).limit(8))
            diseases = d_list_res.scalars().all()
            chips = [{"label": f"Treat {d.slug.replace('-', ' ').title()}", "path": f"how to treat {d.slug.replace('-', ' ')}", "type": "message"} for d in diseases[:4]]
            chips.append({"label": "🔬 Run Diagnosis", "path": "/check", "type": "navigate"})

            if locale == "km":
                msg = """### 💊 វេជ្ជបញ្ជាព្យាបាលជំងឺផ្កាឈូករ័ត្នទូទៅ (Integrated Pest Management Protocol)

ដើម្បីផ្តល់វេជ្ជបញ្ជាជាក់លាក់ សូមបញ្ជាក់ឈ្មោះជំងឺដែលលោកអ្នកចង់ព្យាបាល (ឧទាហរណ៍ `វិធីព្យាបាល sunflower rust` ឬ `treatment for downy mildew`)។

**គោលការណ៍ទូទៅ ៣ កម្រិត (3-Tier Protocol)៖**
1. **កម្រិតទី ១ (អនាម័យចម្ការ):** បង្វិលដំណាំ ៣-៤ ឆ្នាំ, កម្ចាត់កាកសំណល់រុក្ខជាតិចាស់ៗ និងដាំក្នុងគម្លាតសមរម្យ។
2. **កម្រិតទី ២ (ជីវសាស្ត្រ):** ប្រើប្រាស់ជីវផលិតផល *Bacillus subtilis* ឬ *Trichoderma harzianum*។
3. **កម្រិតទី ៣ (គីមីកសិកម្ម):** បាញ់ថ្នាំសម្លាប់ផ្សិត (Fungicide) តាមក្រុម FRAC ដើម្បីការពារការស៊ាំថ្នាំ។"""
            else:
                msg = """### 💊 Sunflower Clinical Treatment Prescription & IPM Framework

Please specify which disease you need a targeted prescription for (e.g., `how to treat Sunflower Rust` or `fungicide for Downy Mildew`).

**Standard 3-Tier Clinical Strategy:**
1. **Tier 1: Cultural & Agronomic Sanitations** (Crop rotation 3-4 years, plant spacing, residue management, precision drip irrigation).
2. **Tier 2: Biological & Bio-Fungicide Controls** (*Bacillus subtilis*, *Trichoderma harzianum*, copper octanoate).
3. **Tier 3: Targeted Chemical Protocols** (FRAC rotation: Triazoles [FRAC 3], Strobilurins [FRAC 11], SDHI [FRAC 7])."""
            return msg, [], None, chips

        info = await self._fetch_consolidated_disease_profile(disease, locale, db)

        p_type = info["pathogen_type"]
        is_bacterial = p_type == "bacterial"

        if is_bacterial:
            tier2_en = "**Biological & Copper Bactericides:** Copper Hydroxide (2.5 kg/ha) or Kasugamycin formulations. Apply at first sign of water-soaking."
            tier2_km = "**ថ្នាំជីវសាស្ត្រ និងទង់ដែង:** ប្រើ Copper Hydroxide ឬ Kasugamycin នៅពេលឃើញស្នាមជាំទឹកដំបូង។"
            tier3_en = "**Chemical Bactericide Protocols:** Note that synthetic fungal fungicides are INEFFECTIVE against bacterial pathogens. Use certified copper bactericides or oxytetracycline formulations if authorized locally. Disinfect pruning and harvesting tools with 10% sodium hypochlorite."
            tier3_km = "**វិធានការគីមី:** ថ្នាំកម្ចាត់ផ្សិតធម្មតាមិនមានប្រសិទ្ធភាពលើបាក់តេរីទេ។ ត្រូវប្រើថ្នាំសម្លាប់បាក់តេរីដែលមានសមាសធាតុទង់ដែង និងសម្លាប់មេរោគលើឧបករណ៍កសិកម្ម។"
        else:
            tier2_en = "**Bio-Fungicides & Organic Protectants:** Preventive applications of *Bacillus subtilis* (Serenade ASO) or *Trichoderma harzianum* (T-22) in furrow or early foliar. High-grade potassium bicarbonate or horticultural mineral oils for foliar suppression."
            tier2_km = "**ថ្នាំជីវសាស្ត្រ និងការពារធម្មជាតិ:** ប្រើ *Bacillus subtilis* ឬ *Trichoderma harzianum* បាញ់ការពារមុនពេលជំងឺរាលដាលខ្លាំង។"
            tier3_en = """**Targeted Fungicide Regimen (FRAC Resistance Management):**
- **FRAC 11 (QoI / Strobilurins):** Azoxystrobin (200-250 g/ha) or Pyraclostrobin — high preventive barrier.
- **FRAC 3 (DMI / Triazoles):** Tebuconazole (125 g a.i./ha) or Difenoconazole — excellent curative translaminar activity.
- **FRAC 7 (SDHI):** Boscalid or Fluopyram — highly effective during flowering for head rots.
- *Rule:* Always tank-mix or alternate FRAC groups across successive applications to prevent fungicide resistance."""
            tier3_km = """**ពិធីសារប្រើប្រាស់ថ្នាំកម្ចាត់ផ្សិត (FRAC Groups):**
- **ក្រុម FRAC 11 (Strobilurins):** Azoxystrobin ការពារមិនឱ្យមេរោគឆ្លងចូលកោសិកា។
- **ក្រុម FRAC 3 (Triazoles):** Tebuconazole ឬ Difenoconazole ជួយព្យាបាល និងជ្រាបចូលខាងក្នុងជាលិការុក្ខជាតិ។
- **ក្រុម FRAC 7 (SDHI):** Boscalid មានប្រសិទ្ធភាពខ្ពស់លើក្បាលផ្កា។
- *បម្រាម:* ត្រូវផ្លាស់ប្តូរក្រុមថ្នាំឆ្លាស់គ្នាជានិច្ច ដើម្បីកុំឱ្យមេរោគស៊ាំនឹងថ្នាំ។"""

        if locale == "km":
            msg = f"""### 💊 វេជ្ជបញ្ជាព្យាបាលរោគរុក្ខជាតិ៖ **{info['name']}**
*(ប្រភេទមេរោគ៖ {p_type.capitalize()} | កម្រិតហានិភ័យ៖ ខ្ពស់)*

---
#### 🌿 កម្រិតទី ១៖ វិធានការក្សេត្រសាស្ត្រ និងអនាម័យចម្ការ (Tier 1: Cultural Sanitation)
- **ការបង្វិលដំណាំ:** {info['prevention'] if info['prevention'] else 'បង្វិលដំណាំយ៉ាងតិច ៣ ទៅ ៤ ឆ្នាំជាមួយដំណាំអំបូរស្មៅ (ពោត ឬស្រូវ)'}
- **ការគ្រប់គ្រងទឹក:** ជៀសវាងការស្រោចស្រពពីលើស្លឹកនៅពេលល្ងាច។ ប្រើប្រព័ន្ធដំណក់ទឹកដើម្បីកាត់បន្ថយសំណើមលើស្លឹក។
- **គម្លាតគុម្ព:** រក្សាគម្លាត ៦០-៧៥ ស.ម ដើម្បីឱ្យពន្លឺថ្ងៃ និងខ្យល់ចេញចូលបានល្អ។

#### 🍃 កម្រិតទី ២៖ វិធានការជីវសាស្ត្រ និងសរីរាង្គ (Tier 2: Biological & Bio-Controls)
{tier2_km}

#### 🧪 កម្រិតទី ៣៖ វិធានការគីមីកសិកម្មតាមស្តង់ដារ (Tier 3: Targeted Chemical Protocol)
{tier3_km}
- **ការណែនាំពីប្រព័ន្ធ:** {info['treatment'] if info['treatment'] else 'បាញ់ថ្នាំនៅពេលព្រឹកព្រលឹម ឬពេលល្ងាចត្រជាក់។'}

---
#### ⚠️ សុវត្ថិភាពបរិស្ថាន និងការការពារសត្វល្អិតផ្តល់ផល (Safety & Stewardship)
- **ការពារសត្វឃ្មុំ:** ហាមបាញ់ថ្នាំពេលផ្ការីកនៅពេលថ្ងៃត្រង់ (បាញ់តែពេលព្រលឹមមុនម៉ោង ៧ ឬពេលល្ងាចក្រោយម៉ោង ៥)។
- **រយៈពេលរង់ចាំមុនប្រមូលផល (PHI):** រង់ចាំយ៉ាងតិច ២១ ទៅ ៣០ ថ្ងៃបន្ទាប់ពីបាញ់ថ្នាំលើកចុងក្រោយ។
"""
        else:
            msg = f"""### 💊 Clinical Treatment Prescription: **{info['name']}**
*(Etiological Agent: `{p_type.capitalize()}` | Knowledge Base Record: `#{info['id']}`)*

---
#### 🌿 Tier 1: Cultural & Agronomic Sanitations (Preventive Foundation)
- **Crop Rotation & Soil Resting:** {info['prevention'] if info['prevention'] else 'Enforce a strict 3-to-4-year rotation with non-host poaceous crops (maize, sorghum, small grains) to exhaust soil inoculum.'}
- **Canopy Microclimate Management:** Optimize planting density (45,000–55,000 plants/ha) with row spacing of 70–75 cm to maximize lower canopy aeration and rapid leaf drying.
- **Irrigation Protocol:** Avoid overhead sprinkler irrigation during late afternoon; utilize precision drip irrigation to eliminate free moisture on leaves and flower heads.

#### 🍃 Tier 2: Biological & Bio-Fungicide Countermeasures
{tier2_en}

#### 🧪 Tier 3: Targeted Chemical Protocols & FRAC Management
{tier3_en}
- **Specific Clinical Recommendation:** {info['treatment'] if info['treatment'] else 'Apply targeted translaminar fungicide at early onset before economic injury level is exceeded.'}

---
#### ⚠️ Environmental Stewardship & Pollinator Protection
- **Pollinator Safety:** Sunflowers depend heavily on honeybees and native pollinators for seed set. **NEVER** apply broad-spectrum sprays during active bee foraging hours. Spray exclusively at dusk or before dawn.
- **Pre-Harvest Interval (PHI):** Adhere strictly to the 21–30 day PHI for seed and oil sunflowers.
- **Personal Protective Equipment (PPE):** Wear chemical-resistant gloves, protective eye goggles, and an organic vapor respirator during mixing and application.
"""

        suggested = [
            {"label": f"View {info['name']} in Catalog", "path": f"/diseases/{info['slug']}", "type": "navigate"},
            {"label": "🔬 Symptom Checker", "path": "/check", "type": "navigate"},
            {"label": "🌻 Scouting Calendar", "path": "growth stage scouting calendar", "type": "message"},
            {"label": f"Compare {info['name']}", "path": f"compare {info['slug']} with another disease", "type": "message"},
        ]

        return msg, [{"action": "treatment_prescription", "disease": info["slug"]}], None, suggested

    # ========================================================================
    # HELPERS
    # ========================================================================

    async def _find_disease(self, name_or_slug: str, db: AsyncSession) -> Disease | None:
        """Find disease by ID, slug, or translation name."""
        if not name_or_slug:
            return None
        cleaned = name_or_slug.strip()
        if cleaned.isdigit():
            res = await db.execute(select(Disease).where(Disease.id == int(cleaned)))
            return res.scalar_one_or_none()

        # By slug
        clean_slug = re.sub(r"[^a-z0-9]+", "-", cleaned.lower()).strip("-")
        res = await db.execute(
            select(Disease).where(
                or_(
                    Disease.slug == clean_slug,
                    Disease.slug.ilike(f"%{clean_slug}%"),
                )
            ).limit(1)
        )
        disease = res.scalar_one_or_none()
        if disease:
            return disease

        # By translation name
        t_res = await db.execute(
            select(Translation.entity_id).where(
                Translation.entity_type == "disease",
                Translation.field == "name",
                Translation.value.ilike(f"%{cleaned}%"),
            ).limit(1)
        )
        d_id = t_res.scalar_one_or_none()
        if d_id:
            res = await db.execute(select(Disease).where(Disease.id == d_id))
            return res.scalar_one_or_none()

        return None

    async def _find_symptom(self, label_or_code: str, db: AsyncSession) -> Symptom | None:
        """Find symptom by ID, code, or label."""
        if not label_or_code:
            return None
        cleaned = label_or_code.strip()
        if cleaned.isdigit():
            res = await db.execute(select(Symptom).where(Symptom.id == int(cleaned)))
            return res.scalar_one_or_none()

        res = await db.execute(select(Symptom).where(Symptom.code.ilike(f"%{cleaned}%")).limit(1))
        symptom = res.scalar_one_or_none()
        if symptom:
            return symptom

        t_res = await db.execute(
            select(Translation.entity_id).where(
                Translation.entity_type == "symptom",
                Translation.field == "label",
                Translation.value.ilike(f"%{cleaned}%"),
            ).limit(1)
        )
        s_id = t_res.scalar_one_or_none()
        if s_id:
            res = await db.execute(select(Symptom).where(Symptom.id == s_id))
            return res.scalar_one_or_none()

        return None

    def _extract_entity_name(self, message: str, keywords: list[str]) -> str:
        """Extract entity name from message by removing keywords."""
        words = message.split()
        filtered = [w for w in words if w.lower() not in keywords]
        extracted = " ".join(filtered).strip(" '\"?!.")
        cleaned = re.sub(
            r"\s+(?:with|caused\s+by|pathogen|and|for|by|លើ|ដែល)\s+.*$",
            "",
            extracted,
            flags=re.IGNORECASE,
        ).strip(" '\"?!.")
        return cleaned if cleaned else extracted

    def _is_valid_entity_name(self, name: str) -> bool:
        """Validate if extracted entity name is a valid botanical/disease/symptom candidate, not conversational text."""
        if not name or len(name.strip()) < 3:
            return False
        name_clean = name.lower().strip()
        if name_clean in [
            "disease", "a disease", "new disease", "this disease",
            "symptom", "a symptom", "new symptom", "data", "system"
        ]:
            return False
        invalid_tokens = {
            "want", "help", "system", "1", "one", "expert", "admin", "comfirm", "confirm",
            "before", "auto", "autto", "how", "what", "which", "data", "can", "you", "please",
            "like", "find", "new", "edit", "delete", "add", "my", "ai", "agent", "that", "this",
            "with", "and", "or", "have", "not", "yet", "database", "page", "user", "crop", "plant"
        }
        words = re.findall(r"\b[a-z0-9]+\b", name_clean)
        if not words or len(words) > 5:
            return False
        invalid_count = sum(1 for w in words if w in invalid_tokens)
        if invalid_count >= max(1, len(words) / 2):
            return False
        return True

    def _is_bogus_draft_name(self, name: str) -> bool:
        """Check if a draft name was created from conversational inquiries or filler tokens."""
        if not name or len(name.strip()) < 3:
            return True
        name_lower = name.lower().strip()
        if name_lower in ["disease", "a disease", "new disease", "this disease"]:
            return True
        bogus_words = {
            "want", "help", "system", "1", "one", "expert", "admin", "comfirm", "confirm",
            "before", "auto", "autto", "how", "what", "which", "data", "can", "you", "please",
            "like", "find", "new", "edit", "delete", "add", "agent"
        }
        tokens = set(re.findall(r"\b[a-z0-9]+\b", name_lower))
        if tokens & bogus_words:
            return True
        return False

    def _extract_pathogen_type(self, message: str) -> str:
        """Extract pathogen type from message."""
        msg_lower = message.lower()
        if "bacterial" in msg_lower or "bacteria" in msg_lower:
            return "bacterial"
        elif "viral" in msg_lower or "virus" in msg_lower:
            return "viral"
        elif "abiotic" in msg_lower or "deficiency" in msg_lower or "drought" in msg_lower:
            return "abiotic"
        elif "fungal" in msg_lower or "fungus" in msg_lower or "mildew" in msg_lower or "rust" in msg_lower:
            return "fungal"
        return "fungal"

    def _translate(self, en: str, km: str, locale: str) -> str:
        return km if locale == "km" else en


_admin_chat_service: AdminChatService | None = None


def get_admin_chat_service() -> AdminChatService:
    global _admin_chat_service
    if _admin_chat_service is None:
        _admin_chat_service = AdminChatService()
    return _admin_chat_service
