-- ============================================================================
-- SUNFLOWER EXPERT SYSTEM: KNOWLEDGE BASE SEED SCRIPT (20 DISEASES)
-- Database Engine: PostgreSQL 13+
-- Locales: English ('en'), Khmer ('km')
-- Idempotency: Fully safe for multiple re-executions (ON CONFLICT DO NOTHING / UPDATE)
-- ============================================================================
-- NOTE ON ENUM CONSTRAINTS:
-- Per schema: pathogen_type ENUM ('fungal', 'bacterial', 'viral', 'abiotic', 'other')
-- 1. Phytoplasmas (Aster Yellows) are cell-wall-less bacteria -> mapped to 'bacterial'.
-- 2. Oomycetes (Downy Mildew, White Rust, Pythium) belong to Kingdom Stramenopila ->
--    mapped to 'other' to prevent ENUM violations.
-- ============================================================================

BEGIN;
-- SECTION 1: INSERT ALL 20 DISEASES
     -- ============================================================================
     INSERT INTO diseases (slug, pathogen_type, is_published, created_at, updated_at)
     VALUES
         ('sclerotinia-basal-stalk-rot', 'fungal',    true, NOW(), NOW()),
         ('sclerotinia-head-rot',        'fungal',    true, NOW(), NOW()),
         ('sunflower-rust',              'fungal',    true, NOW(), NOW()),
         ('downy-mildew',                'other',     true, NOW(), NOW()),
         ('phomopsis-stem-canker',       'fungal',    true, NOW(), NOW()),
         ('phoma-black-stem',            'fungal',    true, NOW(), NOW()),
         ('verticillium-wilt',           'fungal',    true, NOW(), NOW()),
         ('charcoal-rot',                'fungal',    true, NOW(), NOW()),
         ('fusarium-wilt',               'fungal',    true, NOW(), NOW()),
         ('alternaria-leaf-spot',        'fungal',    true, NOW(), NOW()),
         ('septoria-leaf-spot',          'fungal',    true, NOW(), NOW()),
         ('cercospora-leaf-spot',        'fungal',    true, NOW(), NOW()),
         ('powdery-mildew',              'fungal',    true, NOW(), NOW()),
         ('white-rust',                  'other',     true, NOW(), NOW()),
         ('rhizopus-head-rot',           'fungal',    true, NOW(), NOW()),
         ('botrytis-gray-mold',          'fungal',    true, NOW(), NOW()),
         ('bacterial-stalk-head-rot',    'bacterial', true, NOW(), NOW()),
         ('bacterial-leaf-spot',         'bacterial', true, NOW(), NOW()),
         ('pythium-damping-off',         'other',     true, NOW(), NOW()),
         ('aster-yellows',               'bacterial', true, NOW(), NOW())
     ON CONFLICT (slug) DO NOTHING;


     -- ============================================================================
     -- SECTION 2: INSERT TRANSLATIONS (EN & KM: NAME, DESCRIPTION, TREATMENT, PREVENTION)
     -- ============================================================================
     INSERT INTO translations (entity_type, entity_id, locale, field, value)
     VALUES
         -- 1. Sclerotinia Basal Stalk Rot
         ('disease', (SELECT id FROM diseases WHERE slug = 'sclerotinia-basal-stalk-rot'), 'en', 'name', 'Sclerotinia Basal Stalk Rot (White Mold)'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'sclerotinia-basal-stalk-rot'), 'en', 'description', 'Soilborne fungal infection causing water-soaked basal cankers, chalky bleached stems, shredded internal pith, and plant lodging during flowering and seed fill.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'sclerotinia-basal-stalk-rot'), 'en', 'treatment', 'Incurable post-infection once vascular bundles are girdled. Rogue out and incinerate or deeply bury infected stalks to prevent sclerotia return to soil.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'sclerotinia-basal-stalk-rot'), 'en', 'prevention', '4 to 5 year crop rotation with non-host monocots (corn, wheat, sorghum), avoid rotating with soybeans or canola, optimize plant spacing for canopy aeration.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'sclerotinia-basal-stalk-rot'), 'km', 'name', 'ជំងឺរលួយគល់ដើម Sclerotinia (ផ្សិតស)'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'sclerotinia-basal-stalk-rot'), 'km', 'description', 'ជំងឺផ្សិតក្នុងដីដែលបណ្តាលឱ្យគល់ដើមជាំទឹក សំបកដើមឡើងសស្លេកដូចដីស បណ្តូលដើមរលួយសរសៃស្វិត និងដើមបាក់រលំក្នុងដំណាក់កាលចេញផ្កានិងដាក់គ្រាប់។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'sclerotinia-basal-stalk-rot'), 'km', 'treatment', 'គ្មានថ្នាំគីមីព្យាបាលជាសះស្បើយពេលមេរោគចូលដើមឡើយ។ ត្រូវដកដើមឈឺដាក់ថង់ដុតចោល ឬកប់ឱ្យជ្រៅដើម្បីកុំឱ្យគ្រាប់កកផ្សិតធ្លាក់ចូលដី។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'sclerotinia-basal-stalk-rot'), 'km', 'prevention', 'ផ្លាស់ប្តូរមុខដំណាំ ៤ ទៅ ៥ ឆ្នាំជាមួយពោតឬស្រូវសាលី ចៀសវាងដាំឆ្លាស់ជាមួយសណ្តែកសៀងឬកាណូឡា និងរក្សាគម្លាតគុម្ពឱ្យមានខ្យល់ចេញចូលល្អ។'),

         -- 2. Sclerotinia Head Rot
         ('disease', (SELECT id FROM diseases WHERE slug = 'sclerotinia-head-rot'), 'en', 'name', 'Sclerotinia Head Rot'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'sclerotinia-head-rot'), 'en', 'description', 'Airborne fungal infection of blooming flower heads causing water-soaked soft rot of the receptacle, skeletonized fiber matrices, and internal black sclerotia.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'sclerotinia-head-rot'), 'en', 'treatment', 'Post-infection fungicide sprays are ineffective. Harvest early to salvage remaining clean seed and mechanically separate sclerotia using gravity tables.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'sclerotinia-head-rot'), 'en', 'prevention', 'Apply preventative fungicides (boscalid or fluopyram) at bloom onset (R5.1–R5.2), avoid overhead irrigation during flowering, and choose downward-nodding hybrids.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'sclerotinia-head-rot'), 'km', 'name', 'ជំងឺរលួយក្បាលផ្កា Sclerotinia'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'sclerotinia-head-rot'), 'km', 'description', 'ជំងឺផ្សិតហោះតាមខ្យល់ធ្លាក់លើក្បាលផ្ការីក បណ្តាលឱ្យខ្នងផ្ការលួយជាំទឹកទន់ ក្បាលផ្ការលួយសរសៃសុទ្ធដូចអំបោស និងកកើតគ្រាប់កកខ្មៅរឹងក្នុងក្បាលផ្កា។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'sclerotinia-head-rot'), 'km', 'treatment', 'ថ្នាំបាញ់ក្រោយពេលផ្ការលួយគ្មានប្រសិទ្ធភាពទេ។ ត្រូវប្រមូលផលឱ្យលឿនដើម្បីសង្គ្រោះគ្រាប់ រួចរែងញែកគ្រាប់កកខ្មៅចេញតាមម៉ាស៊ីនរែងទំនាញ។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'sclerotinia-head-rot'), 'km', 'prevention', 'បាញ់ថ្នាំការពារ (boscalid ឬ fluopyram) នៅពេលផ្កាចាប់ផ្តើមរីក (R5.1–R5.2) ចៀសវាងការស្រោចទឹកពីលើ និងជ្រើសរើសពូជដែលមានក្បាលផ្កាងក់ចុះក្រោម។'),

         -- 3. Sunflower Rust
         ('disease', (SELECT id FROM diseases WHERE slug = 'sunflower-rust'), 'en', 'name', 'Sunflower Rust'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'sunflower-rust'), 'en', 'description', 'Foliar fungal disease producing dusty cinnamon-brown pustules across leaves during summer that turn black in late season, causing severe leaf firing and defoliation.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'sunflower-rust'), 'en', 'treatment', 'Spray systemic triazoles (tebuconazole, difenoconazole) or strobilurins (pyraclostrobin) if rust pustules reach 1% leaf coverage on upper 4 leaves before bloom ends.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'sunflower-rust'), 'en', 'prevention', 'Plant hybrids carrying genetic rust resistance genes (R-genes), destroy wild sunflower reservoirs early in spring, and avoid late-season planting dates.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'sunflower-rust'), 'km', 'name', 'ជំងឺច្រែះផ្កាឈូករ័ត្ន'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'sunflower-rust'), 'km', 'description', 'ជំងឺផ្សិតលើស្លឹកដែលបង្កើតជាពងបែកម្សៅពណ៌ត្នោតច្រែះពេញផ្ទៃស្លឹកនៅរដូវក្តៅ រួចប្រែជាខ្មៅនៅចុងរដូវ បណ្តាលឱ្យស្លឹកឆេះក្រៀមនិងជ្រុះមុនអាយុ។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'sunflower-rust'), 'km', 'treatment', 'បាញ់ថ្នាំសម្លាប់ផ្សិតប្រភេទជ្រាប (tebuconazole, difenoconazole ឬ pyraclostrobin) នៅពេលពងបែកច្រែះកើតឡើងលើស ១% លើផ្ទៃស្លឹកកំពូលទាំង ៤ មុនពេលផ្ការីកចប់។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'sunflower-rust'), 'km', 'prevention', 'ដាំពូជកូនកាត់ដែលមានហ្សែនធន់ (R-genes) កម្ចាត់ផ្កាឈូករ័ត្នព្រៃក្បែរចម្ការតាំងពីដើមរដូវ និងចៀសវាងការដាំយឺតពេលក្នុងរដូវ។'),

         -- 4. Downy Mildew
         ('disease', (SELECT id FROM diseases WHERE slug = 'downy-mildew'), 'en', 'name', 'Downy Mildew'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'downy-mildew'), 'en', 'description', 'Soilborne oomycete disease causing extreme seedling stunting, chlorotic vein banding, thickened brittle leaves, white down on leaf undersides, and sterile flat heads.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'downy-mildew'), 'en', 'treatment', 'Incurable once systemic infection is established in seedling tissues. Rogue out and destroy stunted plants immediately to stop secondary airborne spread.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'downy-mildew'), 'en', 'prevention', 'Apply targeted oomycete seed treatments (metalaxyl, mefenoxam, oxathiapiprolin), avoid poorly drained or compacted seedbeds, and plant race-resistant hybrids.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'downy-mildew'), 'km', 'name', 'ជំងឺផ្សិតរោម (Downy Mildew)'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'downy-mildew'), 'km', 'description', 'ជំងឺផ្សិតទឹកក្នុងដីបណ្តាលឱ្យកូនដំណាំក្រិនខ្លាំង ស្លឹកឡើងឆ្នូតលឿងតាមទ្រនុងមេ ស្លឹកឡើងក្រាស់ស្រួយ មានស្រទាប់រោមសនៅបាតស្លឹក និងក្បាលផ្កាឈរត្រង់គ្មានគ្រាប់។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'downy-mildew'), 'km', 'treatment', 'ដើមឆ្លងប្រព័ន្ធមិនអាចព្យាបាលបានឡើយ។ ត្រូវដកដើមក្រិនៗកម្ទេចចោលជាបន្ទាន់ ដើម្បីការពារកុំឱ្យស្ប៉ោរាលដាលតាមខ្យល់ទៅគុម្ពជិតខាង។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'downy-mildew'), 'km', 'prevention', 'ប្រើថ្នាំស្រោបគ្រាប់ពូជការពារផ្សិតទឹក (metalaxyl, mefenoxam, oxathiapiprolin) ចៀសវាងដីទាបជាំទឹក និងដាំពូជដែលធន់នឹងពូជមេរោគក្នុងតំបន់។'),

         -- 5. Phomopsis Stem Canker
         ('disease', (SELECT id FROM diseases WHERE slug = 'phomopsis-stem-canker'), 'en', 'name', 'Phomopsis Stem Canker'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'phomopsis-stem-canker'), 'en', 'description', 'Destructive stalk disease causing large sunken tan-to-gray cankers centered at leaf nodes, hollowed pith, stem lodging, and triangular foliar necrotic blights.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'phomopsis-stem-canker'), 'en', 'treatment', 'Post-infection rescue sprays fail to halt pith destruction. Systemic fungicide sprays must be applied preventatively before cankers develop.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'phomopsis-stem-canker'), 'en', 'prevention', 'Apply protective systemic fungicides (strobilurins or triazoles) between V8 vegetative and early budding (R1–R2), deep-till crop residues, and practice 3-year crop rotations.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'phomopsis-stem-canker'), 'km', 'name', 'ជំងឺដំបៅដើម Phomopsis'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'phomopsis-stem-canker'), 'km', 'description', 'ជំងឺដើមដ៏កាចសាហាវដែលបណ្តាលឱ្យមានដំបៅ lõm ពណ៌ត្នោតលាយប្រផេះធំៗចំថ្នាំងដើម បណ្តូលប្រហោងស្ងួត ដើមបាក់រលំ និងស្លឹកងាប់រាងត្រីកោណពីចុងចូលមក។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'phomopsis-stem-canker'), 'km', 'treatment', 'ការបាញ់ថ្នាំសង្គ្រោះក្រោយពេលឃើញដំបៅលើដើមគ្មានប្រសិទ្ធភាពទេ ព្រោះបណ្តូលខាងក្នុងខូចរួចទៅហើយ។ ការបាញ់ថ្នាំត្រូវធ្វើឡើងជាមុនដើម្បីការពារ។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'phomopsis-stem-canker'), 'km', 'prevention', 'បាញ់ថ្នាំការពារផ្សិត (strobilurin ឬ triazole) នៅដំណាក់កាលលូតលាស់ V8 ដល់ដំណាក់កាលក្តឹបផ្កា R1–R2 ភ្ជួរកប់កាកសំណល់ចាស់ឱ្យជ្រៅ និងប្តូរមុខដំណាំ ៣ ឆ្នាំ។'),

         -- 6. Phoma Black Stem
         ('disease', (SELECT id FROM diseases WHERE slug = 'phoma-black-stem'), 'en', 'name', 'Phoma Black Stem'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'phoma-black-stem'), 'en', 'description', 'Stalk disease marked by superficial, jet-black, shiny lesions at petiole bases with embedded pycnidia, leaving the internal pith healthy and white.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'phoma-black-stem'), 'en', 'treatment', 'Rarely warrants chemical rescue sprays unless multiple lesions coalesce and prematurely girdle stalks in high-moisture production systems.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'phoma-black-stem'), 'en', 'prevention', 'Suppress stem-feeding weevils (Apion occidentale) that transmit spores into feeding wounds, chop and bury post-harvest sunflower stalks, and use 3-year rotations.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'phoma-black-stem'), 'km', 'name', 'ជំងឺដើមខ្មៅ Phoma'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'phoma-black-stem'), 'km', 'description', 'ជំងឺដើមដែលសម្គាល់ដោយស្នាមខ្មៅរលោងលើសំបកដើមត្រង់ប្រគាបធាងស្លឹក និងមានគ្រាប់ពងបែកខ្មៅតូចៗកប់ក្នុងដំបៅ ប៉ុន្តែបណ្តូលខាងក្នុងនៅសធម្មតា។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'phoma-black-stem'), 'km', 'treatment', 'កម្របណ្តាលឱ្យខាតបង់ធ្ងន់ធ្ងរដែលតម្រូវឱ្យបាញ់ថ្នាំសង្គ្រោះទេ លើកលែងតែស្នាមដំបៅខ្មៅរាលព័ទ្ធជុំវិញដើមទាំងមូលក្រោមសំណើមខ្ពស់។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'phoma-black-stem'), 'km', 'prevention', 'កម្ចាត់សត្វល្អិតដង្កូវចោះដើម (Apion occidentale) ដែលជាភ្នាក់ងារចម្លងមេរោគ ភ្ជួរលប់កាកសំណល់ដើមចាស់ និងអនុវត្តការប្តូរមុខដំណាំ ៣ ឆ្នាំ។'),

         -- 7. Verticillium Wilt
         ('disease', (SELECT id FROM diseases WHERE slug = 'verticillium-wilt'), 'en', 'name', 'Verticillium Wilt (Leaf Mottle)'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'verticillium-wilt'), 'en', 'description', 'Soilborne vascular fungus causing progressive interveinal chlorosis and browning (mottling) on lower foliage upward, paired with a solid dark vascular ring inside the lower stem.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'verticillium-wilt'), 'en', 'treatment', 'Incurable once the vascular xylem vessels are colonized. Chemical fungicides and soil drenches have zero therapeutic efficacy.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'verticillium-wilt'), 'en', 'prevention', 'Plant resistant commercial hybrids possessing the V-1 or V-2 resistance genes, and strictly avoid rotations with solanaceous crops (potatoes, tomatoes) or cotton.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'verticillium-wilt'), 'km', 'name', 'ជំងឺក្រៀមស្លោក Verticillium (ជំងឺស្លឹកអុជចន្លោះទ្រនុង)'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'verticillium-wilt'), 'km', 'description', 'ជំងឺផ្សិតសរសៃនាំក្នុងដីដែលបណ្តាលឱ្យស្លឹកឡើងលឿងនិងស្ងួតឆេះចន្លោះទ្រនុងស្លឹកពីក្រោមឡើងលើ រួមជាមួយសរសៃនាំខាងក្នុងគល់ដើមប្រែជាពណ៌ត្នោតចាស់ឬខ្មៅជារង្វង់។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'verticillium-wilt'), 'km', 'treatment', 'គ្មានថ្នាំគីមីណាអាចព្យាបាលបានទេពេលសរសៃនាំទឹកត្រូវស្ទះ។ ការស្រោចថ្នាំគីមីមិនអាចជួយសង្គ្រោះបានឡើយ។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'verticillium-wilt'), 'km', 'prevention', 'ដាំពូជកូនកាត់ដែលមានហ្សែនធន់ (V-1 ឬ V-2) និងចៀសវាងដាច់ខាតការដាំលើដីដែលធ្លាប់ដាំដំឡូងបារាំង ប៉េងប៉ោះ ឬកប្បាស។'),

         -- 8. Charcoal Rot
         ('disease', (SELECT id FROM diseases WHERE slug = 'charcoal-rot'), 'en', 'name', 'Charcoal Rot'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'charcoal-rot'), 'en', 'description', 'Heat- and drought-driven disease turning lower stalks ash-gray and shredding internal pith fibers that become packed with millions of microscopic, black, peppery microsclerotia.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'charcoal-rot'), 'en', 'treatment', 'No post-infection fungicide treatments exist. Harvest early to minimize catastrophic yield loss from stalk breakage and lodging.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'charcoal-rot'), 'en', 'prevention', 'Minimize crop water stress through timely irrigation during flowering and seed fill, avoid excessive plant populations, and balance nitrogen fertility.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'charcoal-rot'), 'km', 'name', 'ជំងឺរលួយធ្យូង (Charcoal Rot)'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'charcoal-rot'), 'km', 'description', 'ជំងឺផ្សិតដែលកកើតឡើងខ្លាំងក្នុងលក្ខខណ្ឌក្តៅនិងរាំងស្ងួត បណ្តាលឱ្យគល់ដើមប្រែជាពណ៌ប្រផេះដូចផេះ បណ្តូលដើមរលួយសរសៃស្វិត និងកកកុញដោយចំណុចខ្មៅល្អិតៗដូចគ្រាប់ម្រេច។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'charcoal-rot'), 'km', 'treatment', 'គ្មានថ្នាំគីមីព្យាបាលក្រោយពេលឆ្លងនោះទេ។ ត្រូវប្រមូលផលឱ្យបានលឿនដើម្បីកាត់បន្ថយការខាតបង់ពីការបាក់រលំដើម។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'charcoal-rot'), 'km', 'prevention', 'ស្រោចស្រពទឹកកុំឱ្យដំណាំខ្វះទឹកក្នុងដំណាក់កាលចេញផ្កានិងដាក់គ្រាប់ បន្ថយកម្រិតដង់ស៊ីតេដាំកុំឱ្យញឹកពេក និងដាក់ជីអាសូតក្នុងកម្រិតសមស្រប។'),

         -- 9. Fusarium Wilt and Root Rot
         ('disease', (SELECT id FROM diseases WHERE slug = 'fusarium-wilt'), 'en', 'name', 'Fusarium Wilt and Root Rot'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'fusarium-wilt'), 'en', 'description', 'Soilborne vascular infection leading to unilateral (one-sided) leaf yellowing and wilt, rotted feeder roots, and orange to reddish-brown vascular streaks within the lower stem.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'fusarium-wilt'), 'en', 'treatment', 'Incurable once established in plant vascular tissues. Remove and incinerate isolated infected plants in seed plots or market gardens.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'fusarium-wilt'), 'en', 'prevention', 'Plant seed treated with broad-spectrum fungicides (fludioxonil, sedaxane), plant into warm, aerated soils, and maintain soil pH within neutral levels (6.5–7.0).'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'fusarium-wilt'), 'km', 'name', 'ជំងឺក្រៀមស្លោក Fusarium និងរលួយឫស'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'fusarium-wilt'), 'km', 'description', 'ជំងឺផ្សិតសរសៃនាំក្នុងដីដែលបណ្តាលឱ្យស្លឹកស្វិតឬឡើងលឿងតែម្ខាងនៃទងស្លឹក ឫសរលួយ និងមានឆ្នូតពណ៌ទឹកក្រូចទៅត្នោតក្រហមក្នុងសរសៃនាំនៃគល់ដើម។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'fusarium-wilt'), 'km', 'treatment', 'មិនអាចព្យាបាលឱ្យជាសះស្បើយបានឡើយពេលមេរោគចូលសរសៃនាំ។ ត្រូវដកដើមឈឺចេញយកទៅដុតបំផ្លាញចោល។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'fusarium-wilt'), 'km', 'prevention', 'ប្រើថ្នាំសម្លាប់ផ្សិតស្រោបគ្រាប់ពូជ (fludioxonil, sedaxane) ដាំលើដីក្តៅឧណ្ហៗមានខ្យល់ចេញចូលល្អ និងរក្សា pH ដីចន្លោះ ៦.៥ ដល់ ៧.០។'),

         -- 10. Alternaria Leaf and Stem Spot
         ('disease', (SELECT id FROM diseases WHERE slug = 'alternaria-leaf-spot'), 'en', 'name', 'Alternaria Leaf and Stem Spot'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'alternaria-leaf-spot'), 'en', 'description', 'Fungal disease causing circular-to-angular dark brown spots with concentric target-board rings and yellow halos on leaves, elongated black streaks on stems, and premature leaf drop.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'alternaria-leaf-spot'), 'en', 'treatment', 'Apply protective fungicides (mancozeb, copper hydroxide) or systemic strobilurins (azoxystrobin) when lesions first appear on mid-canopy leaves before flowering.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'alternaria-leaf-spot'), 'en', 'prevention', 'Use certified pathogen-free seed, use drip or furrow irrigation to keep foliage completely dry, eliminate volunteer sunflowers, and widen row spacing.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'alternaria-leaf-spot'), 'km', 'name', 'ជំងឺអុជស្លឹក និងដើម Alternaria'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'alternaria-leaf-spot'), 'km', 'description', 'ជំងឺផ្សិតដែលបណ្តាលឱ្យមានស្នាមអុជមូលឬជ្រុងពណ៌ត្នោតចាស់ មានរង្វង់ជាន់គ្នាដូចផ្ទាំងស៊ីបព័ទ្ធដោយរង្វង់លឿងលើស្លឹក មានឆ្នូតខ្មៅលើដើម និងជ្រុះស្លឹកមុនអាយុ។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'alternaria-leaf-spot'), 'km', 'treatment', 'បាញ់ថ្នាំការពារ (mancozeb, copper hydroxide) ឬថ្នាំជ្រាប (azoxystrobin) នៅពេលឃើញស្នាមអុជកើតលើស្លឹកពាក់កណ្តាលដើមមុនពេលចេញផ្កា។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'alternaria-leaf-spot'), 'km', 'prevention', 'ប្រើប្រាស់គ្រាប់ពូជស្អាតគ្មានមេរោគ ស្រោចស្រពតាមដំណក់ទឹកកុំឱ្យសើមស្លឹក កម្ចាត់កូនផ្កាឈូករ័ត្នដុះឯង និងដាំឱ្យរង្វើលល្មម។'),

         -- 11. Septoria Leaf Spot
         ('disease', (SELECT id FROM diseases WHERE slug = 'septoria-leaf-spot'), 'en', 'name', 'Septoria Leaf Spot'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'septoria-leaf-spot'), 'en', 'description', 'Moisture-driven foliar disease producing circular-to-angular lesions with ash-gray centers, dark borders, and tiny embedded black pimple-like pycnidia.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'septoria-leaf-spot'), 'en', 'treatment', 'Apply broad-spectrum foliar fungicides (triazoles or strobilurins) if spotting advances into the upper canopy prior to flowering.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'septoria-leaf-spot'), 'en', 'prevention', 'Deep-till and bury infected crop residues to accelerate pycnidia decomposition, practice 2 to 3 year crop rotations, and control alternative weed hosts.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'septoria-leaf-spot'), 'km', 'name', 'ជំងឺអុជស្លឹក Septoria'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'septoria-leaf-spot'), 'km', 'description', 'ជំងឺផ្សិតលើស្លឹកដែលបណ្តាលឱ្យមានស្នាមអុជមូលឬជ្រុង កណ្តាលពណ៌ប្រផេះ គែមពណ៌ត្នោតចាស់ និងមានគ្រាប់ពងបែកខ្មៅតូចៗ (pycnidia) កប់នៅចំកណ្តាលស្នាមអុជ។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'septoria-leaf-spot'), 'km', 'treatment', 'បាញ់ថ្នាំសម្លាប់ផ្សិត (triazole ឬ strobilurin) ប្រសិនបើស្នាមអុជរាលដាលដល់ស្លឹកផ្នែកខាងលើមុនពេលចេញផ្កា។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'septoria-leaf-spot'), 'km', 'prevention', 'ភ្ជួរកប់កាកសំណល់ស្លឹកចាស់ចូលក្នុងដីឱ្យជ្រៅ ប្តូរមុខដំណាំពី ២ ទៅ ៣ ឆ្នាំ និងកម្ចាត់ស្មៅចង្រៃជុំវិញចម្ការ។'),

         -- 12. Cercospora Leaf Spot
         ('disease', (SELECT id FROM diseases WHERE slug = 'cercospora-leaf-spot'), 'en', 'name', 'Cercospora Leaf Spot'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'cercospora-leaf-spot'), 'en', 'description', 'Foliar fungal blight marked by circular-to-elliptical spots with pale gray centers and distinct reddish-purple to dark brown margins without internal pycnidia.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'cercospora-leaf-spot'), 'en', 'treatment', 'Apply copper-based fungicides, azoxystrobin, or pyraclostrobin at early symptom onset on lower canopy foliage during humid weather.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'cercospora-leaf-spot'), 'en', 'prevention', 'Maintain wide row spacing to optimize airflow, bury harvest debris, and avoid planting adjacent to unmanaged stubble fields.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'cercospora-leaf-spot'), 'km', 'name', 'ជំងឺអុជស្លឹក Cercospora'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'cercospora-leaf-spot'), 'km', 'description', 'ជំងឺផ្សិតដែលសម្គាល់ដោយស្នាមអុជរាងមូលទៅពងក្រពើ កណ្តាលពណ៌សស្លេក គែមពណ៌ស្វាយក្រហមឬត្នោតចាស់ដាច់ច្បាស់ និងគ្មានគ្រាប់ខ្មៅតូចៗនៅកណ្តាលឡើយ។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'cercospora-leaf-spot'), 'km', 'treatment', 'បាញ់ថ្នាំផ្សិតជាតិទង់ដែង (copper fungicides) ឬ azoxystrobin និង pyraclostrobin នៅពេលចាប់ផ្តើមឃើញស្នាមអុជលើស្លឹកផ្នែកខាងក្រោមក្នុងអាកាសធាតុក្តៅសើម។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'cercospora-leaf-spot'), 'km', 'prevention', 'ដាំឱ្យមានគម្លាតគុម្ពទូលាយដើម្បីឱ្យខ្យល់ចេញចូលបានល្អ ភ្ជួរកប់កាកសំណល់ចាស់ និងចៀសវាងដាំក្បែរចម្ការចាស់ដែលមិនបានសម្អាត។'),

         -- 13. Powdery Mildew
         ('disease', (SELECT id FROM diseases WHERE slug = 'powdery-mildew'), 'en', 'name', 'Powdery Mildew'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'powdery-mildew'), 'en', 'description', 'Biotrophic fungal infection forming superficial, white, talcum-powder-like patches over upper leaf surfaces, stems, and bracts, causing leaf chlorosis and premature senescence.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'powdery-mildew'), 'en', 'treatment', 'Apply wettable sulfur sprays, potassium bicarbonate, or systemic triazole fungicides at the first sign of powdery foliar colonies.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'powdery-mildew'), 'en', 'prevention', 'Plant in full sunlight, avoid excessive crop planting densities, and eliminate over-application of nitrogen fertilizers that generate dense, shaded foliar canopies.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'powdery-mildew'), 'km', 'name', 'ជំងឺផ្សិតម្សៅ (Powdery Mildew)'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'powdery-mildew'), 'km', 'description', 'ជំងឺផ្សិតលើផ្ទៃខាងក្រៅដែលបង្កើតជាស្រទាប់ម្សៅពណ៌សដូចម្សៅផាត់លើផ្ទៃខាងលើនៃស្លឹក ដើម និងត្របកផ្កា បណ្តាលឱ្យស្លឹកឡើងលឿងនិងស្ងួតមុនអាយុ។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'powdery-mildew'), 'km', 'treatment', 'បាញ់ថ្នាំស្ពាន់ធ័រ (wettable sulfur) ឬ potassium bicarbonate ឬថ្នាំ triazole នៅពេលចាប់ផ្តើមឃើញមានម្សៅសលើស្លឹក។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'powdery-mildew'), 'km', 'prevention', 'ដាំនៅកន្លែងដែលទទួលបានពន្លឺថ្ងៃពេញលេញ កុំដាំញឹកពេក និងកាត់បន្ថយការដាក់ជីអាសូតច្រើនជ្រុលដែលធ្វើឱ្យបែកស្លឹកច្រើនពេក។'),

         -- 14. White Rust
         ('disease', (SELECT id FROM diseases WHERE slug = 'white-rust'), 'en', 'name', 'White Rust (White Blister)'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'white-rust'), 'en', 'description', 'Obligate oomycete disease causing raised, smooth, porcelain-white to chalky blisters on lower leaf surfaces and corresponding chlorotic yellow swellings on the upper surface.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'white-rust'), 'en', 'treatment', 'Generally non-economic; severe localized outbreaks can be arrested with targeted foliar applications of mefenoxam or copper-based fungicides.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'white-rust'), 'en', 'prevention', 'Eradicate alternative Asteraceae weeds (cocklebur, wild sunflowers, ragweed) and maintain a 2-year rotation out of sunflower crops.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'white-rust'), 'km', 'name', 'ជំងឺពងបែកស (White Rust / White Blister)'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'white-rust'), 'km', 'description', 'ជំងឺផ្សិតទឹកដែលបង្កើតជាពងបែករលោងពណ៌សដូចកុលាលភាជន៍នៅផ្ទៃខាងក្រោមស្លឹក និងមានពកប៉ោងពណ៌លឿងនៅផ្ទៃខាងលើស្លឹកចំពីលើពងបែក។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'white-rust'), 'km', 'treatment', 'ជាទូទៅមិនបណ្តាលឱ្យខាតបង់សេដ្ឋកិច្ចធំដុំទេ ប្រសិនបើរាលដាលខ្លាំងអាចបាញ់ថ្នាំ mefenoxam ឬថ្នាំផ្សិតជាតិទង់ដែង។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'white-rust'), 'km', 'prevention', 'កម្ចាត់ស្មៅចង្រៃអំបូរតែមួយ (ដូចជាស្មៅកន្ត្រើយព្រៃ និងផ្កាឈូករ័ត្នព្រៃ) និងអនុវត្តការបង្វិលដាំដំណាំយ៉ាងតិច ២ ឆ្នាំ។'),

         -- 15. Rhizopus Head Rot
         ('disease', (SELECT id FROM diseases WHERE slug = 'rhizopus-head-rot'), 'en', 'name', 'Rhizopus Head Rot'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'rhizopus-head-rot'), 'en', 'description', 'Opportunistic wound-invading fungal infection causing wet, stringy brown rotting of the flower head accompanied by coarse gray "whisker-like" mold dotted with black pinhead sporangia.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'rhizopus-head-rot'), 'en', 'treatment', 'Fungicide sprays are ineffective once wound penetration and soft decay occur.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'rhizopus-head-rot'), 'en', 'prevention', 'Control head-boring caterpillars (sunflower head moth, banded sunflower moth), deploy bird-scaring devices to prevent beak punctures, and harvest promptly upon maturity.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'rhizopus-head-rot'), 'km', 'name', 'ជំងឺរលួយក្បាលផ្កា Rhizopus'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'rhizopus-head-rot'), 'km', 'description', 'ជំងឺផ្សិតឆ្លងចូលតាមមុខរបួសដែលបណ្តាលឱ្យក្បាលផ្ការលួយជាំទឹកពណ៌ត្នោតសរសៃៗ មានផ្សិតសរសៃវែងពណ៌ប្រផេះដូចពុកចង្កា និងមានក្បាលខ្មៅតូចៗដូចក្បាលម្ជុល។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'rhizopus-head-rot'), 'km', 'treatment', 'ការបាញ់ថ្នាំសម្លាប់ផ្សិតក្រោយពេលមេរោគចូលតាមមុខរបួសគឺគ្មានប្រសិទ្ធភាពឡើយ។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'rhizopus-head-rot'), 'km', 'prevention', 'បាញ់ថ្នាំការពារនិងកម្ចាត់ដង្កូវមេអំបៅចោះក្បាលផ្កា ប្រើវិធានការដេញសត្វស្លាបកុំឱ្យចឹកផ្កា និងប្រមូលផលឱ្យទាន់ពេលវេលាពេលគ្រាប់ទុំ។'),

         -- 16. Botrytis Gray Mold
         ('disease', (SELECT id FROM diseases WHERE slug = 'botrytis-gray-mold'), 'en', 'name', 'Botrytis Gray Mold (Head Rot)'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'botrytis-gray-mold'), 'en', 'description', 'Late-season fungal decay forming water-soaked brown head lesions covered in a dense, velvety, mouse-gray spore mat during cool, overcast, and continuously wet autumn periods.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'botrytis-gray-mold'), 'en', 'treatment', 'Chemical control is ineffective at late maturity. Harvest early and artificially dry seeds down to 9% moisture to stop internal fungal decay.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'botrytis-gray-mold'), 'en', 'prevention', 'Plant early-maturing cultivars to finish harvest before cool autumn rains, widen plant row spacing, and eliminate late-season overhead watering.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'botrytis-gray-mold'), 'km', 'name', 'ជំងឺរលួយផ្កាផ្សិតប្រផេះ (Botrytis Gray Mold)'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'botrytis-gray-mold'), 'km', 'description', 'ជំងឺផ្សិតចុងរដូវដែលបណ្តាលឱ្យក្បាលផ្ការលួយជាំទឹកពណ៌ត្នោត និងគ្របដណ្តប់ដោយស្រទាប់ផ្សិតកម្ញីពណ៌ប្រផេះដូចរោមសត្វក្នុងអាកាសធាតុត្រជាក់និងភ្លៀងរលឹមជាប់គ្នា។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'botrytis-gray-mold'), 'km', 'treatment', 'គ្មានថ្នាំគីមីបាញ់ព្យាបាលទាន់ពេលទេនៅដំណាក់កាលចុងក្រោយ។ ត្រូវប្រមូលផលជាបន្ទាន់ រួចយកគ្រាប់ទៅសម្ងួតដោយម៉ាស៊ីនឱ្យសំណើមចុះមកត្រឹម ៩%។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'botrytis-gray-mold'), 'km', 'prevention', 'ដាំពូជឆាប់ទុំដើម្បីប្រមូលផលមុនធ្លាក់ភ្លៀងរដូវត្រជាក់ ដាំឱ្យមានគម្លាតគុម្ពទូលាយ និងចៀសវាងការស្រោចទឹកពីលើនៅចុងរដូវ។'),

         -- 17. Bacterial Stalk and Head Rot
         ('disease', (SELECT id FROM diseases WHERE slug = 'bacterial-stalk-head-rot'), 'en', 'name', 'Bacterial Stalk and Head Rot'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'bacterial-stalk-head-rot'), 'en', 'description', 'Soft-rotting pectolytic bacterial infection resulting in greasy, water-soaked, black stem lesions, total slimy liquefaction of internal pith, and a putrid, foul odor.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'bacterial-stalk-head-rot'), 'en', 'treatment', 'Incurable. Cut down, bag, and burn diseased stalks immediately to stop sap transmission; sterilize cutting blades with disinfectant between plants.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'bacterial-stalk-head-rot'), 'en', 'prevention', 'Avoid overhead sprinkler irrigation, prevent mechanical stem wounding during cultivation, control chewing insects, and avoid excessive nitrogen application.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'bacterial-stalk-head-rot'), 'km', 'name', 'ជំងឺរលួយដើម និងផ្កាបង្កដោយបាក់តេរី'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'bacterial-stalk-head-rot'), 'km', 'description', 'ជំងឺបាក់តេរីរលួយជាលិកាដែលបណ្តាលឱ្យដើមជាំទឹកខ្មៅរអិល បណ្តូលខាងក្នុងរលួយក្លាយជាទឹករអិលដូចភក់ និងមានក្លិនស្អុយរលួយខ្លាំង។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'bacterial-stalk-head-rot'), 'km', 'treatment', 'មិនអាចព្យាបាលបានទេ។ ត្រូវកាត់ដើមឈឺដាក់ថង់ដុតចោលភ្លាមៗដើម្បីកុំឱ្យឆ្លងជ័រ និងលាងសម្អាតកាំបិតកាត់ដោយទឹកថ្នាំសម្លាប់មេរោគ។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'bacterial-stalk-head-rot'), 'km', 'prevention', 'ចៀសវាងការស្រោចទឹកបាញ់ពីលើ ការពារកុំឱ្យដើមមានរបួសពេលជ្រួយដី កម្ចាត់សត្វល្អិតស៊ីដើម និងកុំដាក់ជីអាសូតច្រើនហួសកំណត់។'),

         -- 18. Bacterial Leaf Spot and Apical Chlorosis
         ('disease', (SELECT id FROM diseases WHERE slug = 'bacterial-leaf-spot'), 'en', 'name', 'Bacterial Leaf Spot and Apical Chlorosis'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'bacterial-leaf-spot'), 'en', 'description', 'Seedborne and water-splashed bacterial infection producing angular, vein-delimited water-soaked spots, translucent lesions under light, and bright bleached yellow apical foliage.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'bacterial-leaf-spot'), 'en', 'treatment', 'Apply copper bactericides (copper hydroxide, basic copper sulfate) during early vegetative stages to limit canopy surface spread (ineffective against systemic apical chlorosis).'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'bacterial-leaf-spot'), 'en', 'prevention', 'Sow tested, certified pathogen-free seed lots, never cultivate or enter fields when foliage is wet with rain or dew, and eliminate overhead irrigation.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'bacterial-leaf-spot'), 'km', 'name', 'ជំងឺអុជស្លឹក និងស្លេកត្រួយបាក់តេរី'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'bacterial-leaf-spot'), 'km', 'description', 'ជំងឺបាក់តេរីឆ្លងតាមគ្រាប់ពូជនិងទឹកភ្លៀងខ្ទាត បង្កើតជាស្នាមអុជជ្រុងតាមក្រឡាសរសៃស្លឹក ជាំទឹកមើលឆ្លុះពន្លឺធ្លុះ និងធ្វើឱ្យចុងត្រួយឡើងលឿងស្លេកខ្លាំង។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'bacterial-leaf-spot'), 'km', 'treatment', 'បាញ់ថ្នាំបាក់តេរីជាតិទង់ដែង (copper hydroxide) នៅដំណាក់កាលលូតលាស់ដំបូងដើម្បីទប់ស្កាត់ការរាលដាលលើស្លឹក (ប៉ុន្តែមិនអាចជួយផ្នែកដែលចូលសរសៃក្នុងត្រួយបានទេ)។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'bacterial-leaf-spot'), 'km', 'prevention', 'ប្រើប្រាស់គ្រាប់ពូជសុទ្ធគ្មានមេរោគ កុំចុះធ្វើការក្នុងចម្ការពេលស្លឹកកំពុងទទឹកទឹកសន្សើមឬទឹកភ្លៀង និងចៀសវាងការស្រោចទឹកពីលើក្បាលស្លឹក។'),

         -- 19. Pythium Damping-Off & Seedling Blight
         ('disease', (SELECT id FROM diseases WHERE slug = 'pythium-damping-off'), 'en', 'name', 'Pythium Damping-Off and Seedling Blight'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'pythium-damping-off'), 'en', 'description', 'Soilborne oomycete disease in cold, water-saturated soils causing seed decay before emergence, pinched water-soaked brown stem collars, rotted feeder roots, and seedling collapse.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'pythium-damping-off'), 'en', 'treatment', 'Dead seedlings cannot be cured. Apply perimeter soil drenches of mefenoxam or metalaxyl around surviving seedling clusters to halt outward progression.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'pythium-damping-off'), 'en', 'prevention', 'Plant seeds coated with oomycete-targeted fungicide dressings (mefenoxam, ethaboxam), delay planting until soil temperatures reach >12°C, and ensure seedbed drainage.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'pythium-damping-off'), 'km', 'name', 'ជំងឺរលួយកូនដំណាំ Pythium (Damping-Off)'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'pythium-damping-off'), 'km', 'description', 'ជំងឺផ្សិតទឹកក្នុងដីត្រជាក់និងជាំទឹកខ្លាំង បណ្តាលឱ្យគ្រាប់រលួយក្នុងដីមុនដុះ កូនដំណាំដួលដេករលួយគល់កម្រិតដី និងប្រព័ន្ធឫសខ្មៅរលួយដាច់អស់។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'pythium-damping-off'), 'km', 'treatment', 'កូនដំណាំដែលដួលរលួយងាប់មិនអាចជួយបានឡើយ។ អាចស្រោចថ្នាំ mefenoxam ឬ metalaxyl នៅជុំវិញគុម្ពដែលនៅរស់ដើម្បីទប់ស្កាត់កុំឱ្យរាលដាលបន្ត។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'pythium-damping-off'), 'km', 'prevention', 'ប្រើគ្រាប់ពូជដែលបានស្រោបថ្នាំការពារ (mefenoxam, ethaboxam) ដាំនៅពេលដីក្តៅឧណ្ហៗ (លើស ១២°C) និងរៀបចំដីកុំឱ្យមានការដក់ជាំទឹក។'),

         -- 20. Aster Yellows
         ('disease', (SELECT id FROM diseases WHERE slug = 'aster-yellows'), 'en', 'name', 'Aster Yellows'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'aster-yellows'), 'en', 'description', 'Insect-transmitted phytoplasma disease inducing floral phyllody (transformation of petals into leafy green structures), virescence, asymmetrical floral heads, and witches'' broom proliferation.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'aster-yellows'), 'en', 'treatment', 'Phytoplasmas cannot be cured with chemical sprays. Immediately rogue out and burn symptomatic plants to destroy vector feeding sources.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'aster-yellows'), 'en', 'prevention', 'Monitor and suppress aster leafhopper populations (Macrosteles quadrilineatus) using contact or systemic insecticides, and clear perennial broadleaf weed reservoirs along field margins.'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'aster-yellows'), 'km', 'name', 'ជំងឺផ្កាក្លាយជាស្លឹក (Aster Yellows)'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'aster-yellows'), 'km', 'description', 'ជំងឺបង្កដោយមេរោគ phytoplasma ចម្លងដោយសត្វចៃផ្លោះ បណ្តាលឱ្យត្របកផ្កាក្លាយទៅជាស្លឹកបៃតង ផ្កាឡើងពណ៌បៃតង ក្បាលផ្កាវៀចក្រិនមួយចំហៀង និងបែកមែកញឹកដូចអំបោសធ្មប់។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'aster-yellows'), 'km', 'treatment', 'មិនអាចព្យាបាលបានដោយថ្នាំគីមីឡើយ។ ត្រូវដកដើមដែលចេញរោគសញ្ញាដុតកម្ទេចចោលភ្លាមៗ ដើម្បីកុំឱ្យសត្វចៃផ្លោះបឺតយកមេរោគទៅចម្លងដើមឯទៀត។'),
         ('disease', (SELECT id FROM diseases WHERE slug = 'aster-yellows'), 'km', 'prevention', 'តាមដាននិងបាញ់ថ្នាំកម្ចាត់សត្វចៃផ្លោះផ្កាឈូករ័ត្ន (Macrosteles quadrilineatus) និងកម្ចាត់ស្មៅចង្រៃស្លឹកធំៗជុំវិញចម្ការដែលជាជម្រកមេរោគ។')
     ON CONFLICT (entity_type, entity_id, locale, field)
     DO UPDATE SET value = EXCLUDED.value;


     -- ============================================================================

-- ============================================================================
-- SUPPLEMENTARY SYMPTOMS: Ensure any specific symptoms exist
-- ============================================================================
INSERT INTO symptoms (code, category_id, is_environmental, created_at, updated_at)
VALUES
    ('stem_pith_intact_white', (SELECT id FROM symptom_categories WHERE code = 'stem'), false, NOW(), NOW()),
    ('stem_white_powdery_coating', (SELECT id FROM symptom_categories WHERE code = 'stem'), false, NOW(), NOW())
ON CONFLICT (code) DO NOTHING;

INSERT INTO translations (entity_type, entity_id, locale, field, value)
VALUES
    ('symptom', (SELECT id FROM symptoms WHERE code = 'stem_pith_intact_white'), 'en', 'label', 'Intact, firm white pith inside stem beneath surface lesions'),
    ('symptom', (SELECT id FROM symptoms WHERE code = 'stem_pith_intact_white'), 'km', 'label', 'បណ្តូលខាងក្នុងដើមនៅសល្អធម្មតា មិនរលួយនៅក្រោមដំបៅផ្ទៃក្រៅ'),
    ('symptom', (SELECT id FROM symptoms WHERE code = 'stem_white_powdery_coating'), 'en', 'label', 'White powdery coating extending onto stem and bracts'),
    ('symptom', (SELECT id FROM symptoms WHERE code = 'stem_white_powdery_coating'), 'km', 'label', 'ស្រទាប់ម្សៅពណ៌សរាលដាលដល់ដើមនិងត្របកផ្កា')
ON CONFLICT (entity_type, entity_id, locale, field) DO UPDATE SET value = EXCLUDED.value;
-- SECTION 3: CONNECT DISEASES TO SYMPTOMS WITH AGRONOMIC WEIGHTS
     -- ============================================================================
     INSERT INTO disease_symptoms (disease_id, symptom_id, weight, is_required, is_pathognomonic)
     VALUES
         -- 1. Sclerotinia Basal Stalk Rot
         ((SELECT id FROM diseases WHERE slug = 'sclerotinia-basal-stalk-rot'), (SELECT id FROM symptoms WHERE code = 'stem_chalky_white_bleached_surface'),      0.95, true,  false),
         ((SELECT id FROM diseases WHERE slug = 'sclerotinia-basal-stalk-rot'), (SELECT id FROM symptoms WHERE code = 'stem_large_black_sclerotia'),     0.99, false, true),
         ((SELECT id FROM diseases WHERE slug = 'sclerotinia-basal-stalk-rot'), (SELECT id FROM symptoms WHERE code = 'whole_plant_sudden_canopy_wilting'),     0.85, true,  false),
         ((SELECT id FROM diseases WHERE slug = 'sclerotinia-basal-stalk-rot'), (SELECT id FROM symptoms WHERE code = 'stem_pith_disintegration_hollow_stalk'),          0.80, false, false),

         -- 2. Sclerotinia Head Rot
         ((SELECT id FROM diseases WHERE slug = 'sclerotinia-head-rot'),        (SELECT id FROM symptoms WHERE code = 'head_water_soaked_soft_brown_decay'),         0.95, true,  false),
         ((SELECT id FROM diseases WHERE slug = 'sclerotinia-head-rot'),        (SELECT id FROM symptoms WHERE code = 'head_white_mycelium_black_sclerotia'),     0.99, false, true),
         ((SELECT id FROM diseases WHERE slug = 'sclerotinia-head-rot'),        (SELECT id FROM symptoms WHERE code = 'head_shredded_skeletonized_matrix'),     0.90, false, false),
         ((SELECT id FROM diseases WHERE slug = 'sclerotinia-head-rot'),        (SELECT id FROM symptoms WHERE code = 'head_premature_seed_shattering'),   0.70, false, false),

         -- 3. Sunflower Rust
         ((SELECT id FROM diseases WHERE slug = 'sunflower-rust'),              (SELECT id FROM symptoms WHERE code = 'leaf_cinnamon_brown_powdery_pustules'),       0.98, true,  true),
         ((SELECT id FROM diseases WHERE slug = 'sunflower-rust'),              (SELECT id FROM symptoms WHERE code = 'leaf_black_raised_late_season_pustules'),          0.85, false, false),
         ((SELECT id FROM diseases WHERE slug = 'sunflower-rust'),              (SELECT id FROM symptoms WHERE code = 'leaf_premature_defoliation_drop'),  0.80, false, false),
         ((SELECT id FROM diseases WHERE slug = 'sunflower-rust'),              (SELECT id FROM symptoms WHERE code = 'head_reduced_seed_size_shriveled'),        0.75, false, false),

         -- 4. Downy Mildew
         ((SELECT id FROM diseases WHERE slug = 'downy-mildew'),                (SELECT id FROM symptoms WHERE code = 'leaf_dense_white_felt_undersides'), 0.99, true, true),
         ((SELECT id FROM diseases WHERE slug = 'downy-mildew'),                (SELECT id FROM symptoms WHERE code = 'whole_plant_severe_stunting_dwarfism'),    0.95, true, false),
         ((SELECT id FROM diseases WHERE slug = 'downy-mildew'),                (SELECT id FROM symptoms WHERE code = 'leaf_systemic_chlorosis_banding'),   0.90, true, false),
         ((SELECT id FROM diseases WHERE slug = 'downy-mildew'),                (SELECT id FROM symptoms WHERE code = 'head_abnormal_upright_flat_rigid'),      0.85, false, false),

         -- 5. Phomopsis Stem Canker
         ((SELECT id FROM diseases WHERE slug = 'phomopsis-stem-canker'),       (SELECT id FROM symptoms WHERE code = 'stem_sunken_tan_gray_cankers'),  0.98, true,  true),
         ((SELECT id FROM diseases WHERE slug = 'phomopsis-stem-canker'),       (SELECT id FROM symptoms WHERE code = 'stem_easily_crushed_thumb_pressure'),    0.90, false, false),
         ((SELECT id FROM diseases WHERE slug = 'phomopsis-stem-canker'),       (SELECT id FROM symptoms WHERE code = 'leaf_triangular_marginal_necrotic_lesions'), 0.85, false, false),
         ((SELECT id FROM diseases WHERE slug = 'phomopsis-stem-canker'),       (SELECT id FROM symptoms WHERE code = 'whole_plant_stalk_lodging_collapse'),    0.80, false, false),

         -- 6. Phoma Black Stem
         ((SELECT id FROM diseases WHERE slug = 'phoma-black-stem'),            (SELECT id FROM symptoms WHERE code = 'stem_jet_black_shiny_patches'), 0.95, true,  true),
         ((SELECT id FROM diseases WHERE slug = 'phoma-black-stem'),            (SELECT id FROM symptoms WHERE code = 'stem_pycnidia_embedded_lesions'),       0.85, false, false),
         ((SELECT id FROM diseases WHERE slug = 'phoma-black-stem'),            (SELECT id FROM symptoms WHERE code = 'stem_pith_intact_white'),       0.80, false, false),

         -- 7. Verticillium Wilt
         ((SELECT id FROM diseases WHERE slug = 'verticillium-wilt'),           (SELECT id FROM symptoms WHERE code = 'leaf_interveinal_chlorosis_mottling'), 0.95, true, true),
         ((SELECT id FROM diseases WHERE slug = 'verticillium-wilt'),           (SELECT id FROM symptoms WHERE code = 'whole_plant_dark_vascular_ring'),     0.95, true,  false),
         ((SELECT id FROM diseases WHERE slug = 'verticillium-wilt'),           (SELECT id FROM symptoms WHERE code = 'whole_plant_premature_death_drying'), 0.85, false, false),
         ((SELECT id FROM diseases WHERE slug = 'verticillium-wilt'),           (SELECT id FROM symptoms WHERE code = 'head_reduced_seed_size_shriveled'),        0.70, false, false),

         -- 8. Charcoal Rot
         ((SELECT id FROM diseases WHERE slug = 'charcoal-rot'),                (SELECT id FROM symptoms WHERE code = 'stem_silvery_ash_gray_discoloration'),          0.95, true,  false),
         ((SELECT id FROM diseases WHERE slug = 'charcoal-rot'),                (SELECT id FROM symptoms WHERE code = 'stem_peppery_microsclerotia_shredded_pith'), 0.99, true, true),
         ((SELECT id FROM diseases WHERE slug = 'charcoal-rot'),                (SELECT id FROM symptoms WHERE code = 'stem_pith_disintegration_hollow_stalk'),          0.85, false, false),
         ((SELECT id FROM diseases WHERE slug = 'charcoal-rot'),                (SELECT id FROM symptoms WHERE code = 'whole_plant_stalk_lodging_collapse'),    0.80, false, false),

         -- 9. Fusarium Wilt and Root Rot
         ((SELECT id FROM diseases WHERE slug = 'fusarium-wilt'),               (SELECT id FROM symptoms WHERE code = 'whole_plant_unilateral_wilting_yellowing'),      0.90, true,  false),
         ((SELECT id FROM diseases WHERE slug = 'fusarium-wilt'),               (SELECT id FROM symptoms WHERE code = 'whole_plant_orange_reddish_vascular_streaks'), 0.95, true, true),
         ((SELECT id FROM diseases WHERE slug = 'fusarium-wilt'),               (SELECT id FROM symptoms WHERE code = 'root_decay_feeder_tips'),       0.85, false, false),
         ((SELECT id FROM diseases WHERE slug = 'fusarium-wilt'),               (SELECT id FROM symptoms WHERE code = 'whole_plant_severe_stunting_dwarfism'), 0.75, false, false),

         -- 10. Alternaria Leaf and Stem Spot
         ((SELECT id FROM diseases WHERE slug = 'alternaria-leaf-spot'),        (SELECT id FROM symptoms WHERE code = 'leaf_concentric_target_board_rings'),      0.95, true,  true),
         ((SELECT id FROM diseases WHERE slug = 'alternaria-leaf-spot'),        (SELECT id FROM symptoms WHERE code = 'leaf_circular_angular_necrotic_spots'),     0.90, true,  false),
         ((SELECT id FROM diseases WHERE slug = 'alternaria-leaf-spot'),        (SELECT id FROM symptoms WHERE code = 'stem_elongated_black_streaks'), 0.85, false, false),
         ((SELECT id FROM diseases WHERE slug = 'alternaria-leaf-spot'),        (SELECT id FROM symptoms WHERE code = 'leaf_premature_defoliation_drop'),  0.75, false, false),

         -- 11. Septoria Leaf Spot
         ((SELECT id FROM diseases WHERE slug = 'septoria-leaf-spot'),          (SELECT id FROM symptoms WHERE code = 'leaf_spots_ash_gray_pycnidia'), 0.95, true,  true),
         ((SELECT id FROM diseases WHERE slug = 'septoria-leaf-spot'),          (SELECT id FROM symptoms WHERE code = 'leaf_circular_angular_necrotic_spots'),     0.85, true,  false),
         ((SELECT id FROM diseases WHERE slug = 'septoria-leaf-spot'),          (SELECT id FROM symptoms WHERE code = 'leaf_premature_defoliation_drop'),  0.75, false, false),

         -- 12. Cercospora Leaf Spot
         ((SELECT id FROM diseases WHERE slug = 'cercospora-leaf-spot'),        (SELECT id FROM symptoms WHERE code = 'leaf_spots_pale_center_reddish_margin'), 0.95, true,  true),
         ((SELECT id FROM diseases WHERE slug = 'cercospora-leaf-spot'),        (SELECT id FROM symptoms WHERE code = 'leaf_circular_angular_necrotic_spots'),     0.85, true,  false),
         ((SELECT id FROM diseases WHERE slug = 'cercospora-leaf-spot'),        (SELECT id FROM symptoms WHERE code = 'whole_plant_premature_death_drying'), 0.70, false, false),

         -- 13. Powdery Mildew
         ((SELECT id FROM diseases WHERE slug = 'powdery-mildew'),              (SELECT id FROM symptoms WHERE code = 'leaf_white_talcum_powder_patches'), 0.98, true, true),
         ((SELECT id FROM diseases WHERE slug = 'powdery-mildew'),              (SELECT id FROM symptoms WHERE code = 'stem_white_powdery_coating'),   0.85, false, false),
         ((SELECT id FROM diseases WHERE slug = 'powdery-mildew'),              (SELECT id FROM symptoms WHERE code = 'leaf_chlorotic_yellow_halos'), 0.75, false, false),

         -- 14. White Rust
         ((SELECT id FROM diseases WHERE slug = 'white-rust'),                  (SELECT id FROM symptoms WHERE code = 'leaf_porcelain_white_chalky_blisters'), 0.98, true, true),
         ((SELECT id FROM diseases WHERE slug = 'white-rust'),                  (SELECT id FROM symptoms WHERE code = 'leaf_chlorotic_swellings_upper_surface'),   0.90, true,  false),
         ((SELECT id FROM diseases WHERE slug = 'white-rust'),                  (SELECT id FROM symptoms WHERE code = 'leaf_distortion_puckering_ragged_margins'),    0.75, false, false),

         -- 15. Rhizopus Head Rot
         ((SELECT id FROM diseases WHERE slug = 'rhizopus-head-rot'),           (SELECT id FROM symptoms WHERE code = 'head_coarse_gray_whisker_mold'), 0.98, true, true),
         ((SELECT id FROM diseases WHERE slug = 'rhizopus-head-rot'),           (SELECT id FROM symptoms WHERE code = 'head_rot_initiating_around_wounds'),    0.95, true,  false),
         ((SELECT id FROM diseases WHERE slug = 'rhizopus-head-rot'),           (SELECT id FROM symptoms WHERE code = 'head_water_soaked_soft_brown_decay'),         0.85, true,  false),
         ((SELECT id FROM diseases WHERE slug = 'rhizopus-head-rot'),           (SELECT id FROM symptoms WHERE code = 'head_premature_seed_shattering'),   0.80, false, false),

         -- 16. Botrytis Gray Mold
         ((SELECT id FROM diseases WHERE slug = 'botrytis-gray-mold'),          (SELECT id FROM symptoms WHERE code = 'head_mouse_gray_velvety_spore_mat'), 0.98, true,  true),
         ((SELECT id FROM diseases WHERE slug = 'botrytis-gray-mold'),          (SELECT id FROM symptoms WHERE code = 'head_water_soaked_soft_brown_decay'),         0.85, true,  false),
         ((SELECT id FROM diseases WHERE slug = 'botrytis-gray-mold'),          (SELECT id FROM symptoms WHERE code = 'head_black_crust_sclerotia'),        0.80, false, false),
         ((SELECT id FROM diseases WHERE slug = 'botrytis-gray-mold'),          (SELECT id FROM symptoms WHERE code = 'head_premature_seed_shattering'),   0.75, false, false),

         -- 17. Bacterial Stalk and Head Rot
         ((SELECT id FROM diseases WHERE slug = 'bacterial-stalk-head-rot'),    (SELECT id FROM symptoms WHERE code = 'stem_slimy_mushy_pith_dissolution'),        0.98, true,  true),
         ((SELECT id FROM diseases WHERE slug = 'bacterial-stalk-head-rot'),    (SELECT id FROM symptoms WHERE code = 'stem_foul_putrid_rotting_odor'),        0.98, true,  true),
         ((SELECT id FROM diseases WHERE slug = 'bacterial-stalk-head-rot'),    (SELECT id FROM symptoms WHERE code = 'stem_water_soaked_greasy_lesions'), 0.90, true, false),
         ((SELECT id FROM diseases WHERE slug = 'bacterial-stalk-head-rot'),    (SELECT id FROM symptoms WHERE code = 'whole_plant_sudden_canopy_wilting'),     0.85, false, false),

         -- 18. Bacterial Leaf Spot and Apical Chlorosis
         ((SELECT id FROM diseases WHERE slug = 'bacterial-leaf-spot'),         (SELECT id FROM symptoms WHERE code = 'leaf_angular_water_soaked_translucent_spots'), 0.98, true, true),
         ((SELECT id FROM diseases WHERE slug = 'bacterial-leaf-spot'),         (SELECT id FROM symptoms WHERE code = 'leaf_bright_bleached_apical_chlorosis'), 0.95, false, true),
         ((SELECT id FROM diseases WHERE slug = 'bacterial-leaf-spot'),         (SELECT id FROM symptoms WHERE code = 'leaf_distortion_puckering_ragged_margins'),    0.75, false, false),

         -- 19. Pythium Damping-Off & Seedling Blight
         ((SELECT id FROM diseases WHERE slug = 'pythium-damping-off'),         (SELECT id FROM symptoms WHERE code = 'seedling_damping_off_collapse'), 0.98, true, true),
         ((SELECT id FROM diseases WHERE slug = 'pythium-damping-off'),         (SELECT id FROM symptoms WHERE code = 'seedling_pinched_water_soaked_collar'), 0.95, true,  false),
         ((SELECT id FROM diseases WHERE slug = 'pythium-damping-off'),         (SELECT id FROM symptoms WHERE code = 'root_decay_feeder_tips'),       0.90, true,  false),
         ((SELECT id FROM diseases WHERE slug = 'pythium-damping-off'),         (SELECT id FROM symptoms WHERE code = 'seedling_uneven_emergence_bare_patches'),    0.80, false, false),

         -- 20. Aster Yellows
         ((SELECT id FROM diseases WHERE slug = 'aster-yellows'),               (SELECT id FROM symptoms WHERE code = 'head_phyllody_floral_transformation'), 0.99, true,  true),
         ((SELECT id FROM diseases WHERE slug = 'aster-yellows'),               (SELECT id FROM symptoms WHERE code = 'head_virescence_green_discoloration'), 0.95, true,  true),
         ((SELECT id FROM diseases WHERE slug = 'aster-yellows'),               (SELECT id FROM symptoms WHERE code = 'head_asymmetrical_distorted_wedge_sector'), 0.90, false, false),
         ((SELECT id FROM diseases WHERE slug = 'aster-yellows'),               (SELECT id FROM symptoms WHERE code = 'whole_plant_witches_broom_proliferation'),    0.85, false, false)
     ON CONFLICT (disease_id, symptom_id)
     DO UPDATE SET
         weight = EXCLUDED.weight,
         is_required = EXCLUDED.is_required,
         is_pathognomonic = EXCLUDED.is_pathognomonic;


COMMIT;

-- ============================================================================
-- VERIFICATION QUERY 1: DETAILED TABULAR AUDIT (INSPECT ALL LOADED ATTRIBUTES)
-- ============================================================================
SELECT
    d.slug,
    d.pathogen_type,
    t_name_en.value AS name_en,
    t_name_km.value AS name_km,
    s.code          AS symptom_code,
    ds.weight,
    ds.is_required,
    ds.is_pathognomonic
FROM diseases d
JOIN disease_symptoms ds ON ds.disease_id = d.id
JOIN symptoms s          ON s.id = ds.symptom_id
LEFT JOIN translations t_name_en
    ON t_name_en.entity_type = 'disease'
   AND t_name_en.entity_id = d.id
   AND t_name_en.locale = 'en'
   AND t_name_en.field = 'name'
LEFT JOIN translations t_name_km
    ON t_name_km.entity_type = 'disease'
   AND t_name_km.entity_id = d.id
   AND t_name_km.locale = 'km'
   AND t_name_km.field = 'name'
ORDER BY d.slug ASC, ds.weight DESC;

-- ============================================================================
-- VERIFICATION QUERY 2: SUMMARY HEALTH CHECK (VERIFIES TRANSLATIONS & COUNTS)
-- ============================================================================
SELECT
    d.slug,
    d.pathogen_type,
    MAX(CASE WHEN t.locale = 'en' AND t.field = 'name' THEN t.value END) AS name_en,
    MAX(CASE WHEN t.locale = 'km' AND t.field = 'name' THEN t.value END) AS name_km,
    COUNT(DISTINCT (t.locale, t.field)) AS total_translations_count, -- Expected: 8 (4 fields * 2 locales)
    COUNT(DISTINCT ds.symptom_id) AS linked_symptoms_count
FROM diseases d
LEFT JOIN translations t ON t.entity_type = 'disease' AND t.entity_id = d.id
LEFT JOIN disease_symptoms ds ON ds.disease_id = d.id
GROUP BY d.id, d.slug, d.pathogen_type
ORDER BY d.slug ASC;
