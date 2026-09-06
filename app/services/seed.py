import json
import os
from pathlib import Path

from extensions import db
from app.models.disease import Disease
from app.models.rbac import Permission, Role
from app.models.symptom_catalog import SymptomCatalog
from app.models.user import User
from app.services import diagnosis
from app.services.symptom_admin import save_disease_items


DISEASE_KM_LOCALIZATION = {
    "downy-mildew": {
        "name_km": "ជំងឺរោគផ្សិតទន់",
        "symptoms_km": (
            "• ដំណាំក្មេងលូតលាស់យឺត ឬអាចងាប់ភ្លាមៗបន្ទាប់ពីដុះ\n"
            "• មានបន្ទះពណ៌លឿងស្លេកនៅចន្លោះសរសៃស្លឹក\n"
            "• មានស្រទាប់ផ្សិតពណ៌ស ឬប្រផេះនៅផ្នែកខាងក្រោមស្លឹក\n"
            "• ដើមនៅខ្លី ស្លឹកតូច និងក្បាលផ្កាអភិវឌ្ឍមិនល្អ"
        ),
        "cause_km": (
            "• បង្កដោយអូមីស៊ីត Plasmopara halstedii\n"
            "• អាចមកជាមួយគ្រាប់ពូជដែលមានមេរោគ ឬរស់នៅក្នុងដីជាស្ព័របានយូរ\n"
            "• កើតខ្លាំងនៅសីតុណ្ហភាពត្រជាក់ដល់មធ្យម និងដីសើមឬលូទឹកមិនល្អ"
        ),
        "treatment_km": (
            "• ដក និងបំផ្លាញដំណាំក្មេងដែលឆ្លងខ្លាំង ប្រសិនបើកើតតែជាចំណុចតូចៗ\n"
            "• ប្រសិនបើអនុញ្ញាតក្នុងតំបន់ អាចប្រើថ្នាំលាបគ្រាប់ពូជ ឬថ្នាំផ្សិតសមស្របសម្រាប់អូមីស៊ីត\n"
            "• ជៀសវាងការនាំដីកខ្វក់ពីកន្លែងមួយទៅកន្លែងមួយ"
        ),
        "prevention_km": (
            "• ប្រើពូជធន់ជំងឺ និងគ្រាប់ពូជដែលបានបញ្ជាក់គុណភាព\n"
            "• កែលម្អប្រព័ន្ធបង្ហូរទឹក និងកុំដាំក្នុងដីត្រជាក់សើមខ្លាំង\n"
            "• បង្វិលដំណាំចេញពីផ្កាឈូករ័ត្នរយៈពេល 3–4 ឆ្នាំ ឬយូរជាងនេះនៅតំបន់ហានិភ័យខ្ពស់\n"
            "• សម្អាតឧបករណ៍កសិកម្មដើម្បីកាត់បន្ថយការផ្ទេរដីដែលមានមេរោគ"
        ),
    },
    "alternaria-leaf-spot": {
        "name_km": "ជំងឺចំណុចស្លឹកអាល់ធឺណារៀ",
        "symptoms_km": (
            "• មានចំណុចត្នោតខ្មៅតូចៗលើស្លឹក ហើយធំឡើងជារង្វង់ស្រទាប់ៗ\n"
            "• ចំណុចអាចរួមបញ្ចូលគ្នា បង្កឱ្យផ្ទៃស្លឹកស្ងួតខូចធំៗ\n"
            "• ស្លឹកលឿង និងជ្រុះមុនពេល ធ្វើឱ្យដើមខ្សោយ និងទិន្នផលថយចុះ"
        ),
        "cause_km": (
            "• បង្កដោយផ្សិត Alternaria helianthi និងប្រភេទ Alternaria ពាក់ព័ន្ធ\n"
            "• ផ្សិតរស់នៅលើសំណល់ដំណាំ ហើយស្ព័ររីករាលដាលតាមខ្យល់ និងទឹកសាច់\n"
            "• កើតខ្លាំងនៅអាកាសធាតុក្តៅ សើម និងពេលស្លឹកសើមញឹកញាប់"
        ),
        "treatment_km": (
            "• ត្រួតពិនិត្យចម្ការជាប្រចាំ និងប្រើថ្នាំផ្សិតតែពេលចាំបាច់តាមស្លាកណែនាំ\n"
            "• កាត់បន្ថយការសើមលើស្លឹក ដូចជាជៀសវាងស្រោចទឹកពីលើនៅពេលល្ងាច\n"
            "• ប្រមូលសំណល់ដំណាំដែលឆ្លងខ្លាំងចេញបន្ទាប់ពីប្រមូលផល"
        ),
        "prevention_km": (
            "• បង្វិលដំណាំ និងគ្រប់គ្រងសំណល់ដំណាំឆ្លងឱ្យបានល្អ\n"
            "• បង្កើនការហូរខ្យល់ដោយរក្សាចម្ងាយដាំ និងកម្ចាត់ស្មៅ\n"
            "• ដាក់ជីឱ្យសមស្រប កុំឱ្យអាសូតច្រើនពេក\n"
            "• ជ្រើសរើសពូជធន់ ប្រសិនបើមាន"
        ),
    },
    "rust": {
        "name_km": "ជំងឺច្រេះ",
        "symptoms_km": (
            "• មានចំណុចលឿងតូចៗ ដែលបន្ទាប់មកក្លាយជាដុំម្សៅពណ៌ទឹកក្រូចត្នោត\n"
            "• ជាញឹកញាប់កើតលើស្លឹកក្រោមមុន ហើយរាលដាលឡើងលើ\n"
            "• បើឆ្លងខ្លាំង ស្លឹកជ្រុះមុនពេល និងគ្រាប់ពូជពេញមិនល្អ"
        ),
        "cause_km": (
            "• បង្កដោយផ្សិត Puccinia helianthi\n"
            "• ស្ព័រអាចធ្វើដំណើរឆ្ងាយតាមខ្យល់\n"
            "• កើតខ្លាំងនៅថ្ងៃក្តៅ យប់ត្រជាក់ និងសំណើមខ្ពស់"
        ),
        "treatment_km": (
            "• ប្រសិនបើជំងឺកើតពីដំបូង និងកំពុងរាលដាល ត្រូវប្រើថ្នាំផ្សិតដែលមានស្លាកអនុញ្ញាតឱ្យបានទាន់ពេល\n"
            "• កម្ចាត់ដើមផ្កាឈូករ័ត្នស្ម័គ្រចិត្ត និងស្មៅដែលអាចជាម្ចាស់មេរោគ\n"
            "• បន្តត្រួតពិនិត្យដើម្បីសម្រេចថាតើត្រូវបាញ់ថ្នាំបន្ថែមឬអត់"
        ),
        "prevention_km": (
            "• ដាំពូជធន់ជំងឺច្រេះ ប្រសិនបើមាន\n"
            "• បង្វិលដំណាំ និងគ្រប់គ្រងដំណាំស្ម័គ្រចិត្តឱ្យបានល្អ\n"
            "• កុំឱ្យដើមដុះកកស្ទះពេក ដោយគ្រប់គ្រងចម្ងាយដាំ និងជីអាសូត"
        ),
    },
    "charcoal-rot": {
        "name_km": "ជំងឺរលួយធ្យូង",
        "symptoms_km": (
            "• ដំណាំស្រពោនភ្លាមៗនៅពេលចេញផ្កា ឬពេលបំពេញគ្រាប់ ជាពិសេសនៅអាកាសក្តៅស្ងួត\n"
            "• ផ្នែកខាងក្រោមដើមមានពណ៌ប្រផេះទៅខ្មៅ\n"
            "• ខួរដើមខ្ទេច និងមានចំណុចខ្មៅតូចៗជាច្រើន\n"
            "• ដើមអាចដួល ឬបាក់ជិតមូលដើម"
        ),
        "cause_km": (
            "• បង្កដោយផ្សិត Macrophomina phaseolina\n"
            "• ផ្សិតរស់នៅក្នុងដី និងសំណល់ដំណាំ ហើយអាចឆ្លងដំណាំជាច្រើនប្រភេទ\n"
            "• ជំងឺនេះពាក់ព័ន្ធខ្លាំងនឹងភាពរាំងស្ងួត និងសីតុណ្ហភាពខ្ពស់"
        ),
        "treatment_km": (
            "• មិនមានថ្នាំព្យាបាលដែលមានប្រសិទ្ធភាពច្បាស់លាស់បន្ទាប់ពីរោគសញ្ញាបង្ហាញ\n"
            "• កាត់បន្ថយស្ត្រេសរុក្ខជាតិ ដូចជាគ្រប់គ្រងទឹកស្រោច ប្រសិនបើអាចធ្វើបាន\n"
            "• ប្រមូលផលឱ្យបានទាន់ពេល ប្រសិនបើមានហានិភ័យដើមដួលខ្ពស់"
        ),
        "prevention_km": (
            "• ជ្រើសរើសពូជធន់ និងកុំដាំក្រាស់ពេក\n"
            "• បង្វិលដំណាំដើម្បីកាត់បន្ថយមេរោគក្នុងដី ប្រសិនបើអាចធ្វើបាន\n"
            "• ថែរក្សាសុខភាពដី និងសំណើមឱ្យសមស្រប និងគ្រប់គ្រងស្មៅម្ចាស់មេរោគ\n"
            "• ជៀសវាងវិធីដាំដុះដែលធ្វើឱ្យដំណាំខ្វះទឹកខ្លាំង"
        ),
    },
    "white-mold": {
        "name_km": "ជំងឺផ្សិតស",
        "symptoms_km": (
            "• មានដំបៅសើមលើដើម ឬក្បាលផ្កា ហើយបន្ទាប់មកប្រែជាពណ៌សស្លេក\n"
            "• មានសរសៃផ្សិតពណ៌សដូចកប្បាសលើកន្លែងឆ្លង\n"
            "• មានគ្រាប់រឹងពណ៌ខ្មៅកើតនៅខាងក្នុងដើម ឬក្បាលផ្កា\n"
            "• ដើមអាចដួល និងក្បាលផ្ការលួយ ធ្វើឱ្យទិន្នផល និងគុណភាពថយចុះ"
        ),
        "cause_km": (
            "• បង្កដោយផ្សិត Sclerotinia sclerotiorum\n"
            "• ផ្សិតអាចរស់នៅក្នុងដីជាគ្រាប់រឹងបានជាច្រើនឆ្នាំ\n"
            "• កើតខ្លាំងនៅអាកាសធាតុត្រជាក់សើម និងពេលដើមដុះកកស្ទះក្នុងរដូវចេញផ្កា"
        ),
        "treatment_km": (
            "• ដកដំណាំដែលឆ្លងខ្លាំងចេញ ប្រសិនបើជាចម្ការតូច ឬអាចធ្វើបាន\n"
            "• ក្នុងចម្ការធំ ពេលវេលាបាញ់ថ្នាំផ្សិតមានសារៈសំខាន់ ជាពិសេសនៅដំណាក់កាលផ្កាចាប់ផ្ដើមរីក\n"
            "• កាត់បន្ថយសំណើមក្នុងគម្របដើម ដោយបង្កើនការហូរខ្យល់"
        ),
        "prevention_km": (
            "• បង្វិលជាមួយដំណាំមិនមែនជាម្ចាស់មេរោគ ដូចជាស្មៅ ឬធញ្ញជាតិ\n"
            "• ជៀសវាងដាំក្រាស់ពេក និងគ្រប់គ្រងស្មៅដើម្បីបង្កើនការហូរខ្យល់\n"
            "• គ្រប់គ្រងការស្រោចទឹក ដើម្បីកុំឱ្យស្លឹកសើមយូរពេលចេញផ្កា\n"
            "• ប្រើពូជធន់ និងសម្អាតឧបករណ៍ដើម្បីកាត់បន្ថយការរាលដាល"
        ),
    },
    "bacterial-head-rot": {
        "name_km": "ជំងឺរលួយក្បាលដោយបាក់តេរី",
        "symptoms_km": (
            "• ក្បាលផ្ការលួយសើម ទន់ ហើយជាលិកាប្រែជាពណ៌ត្នោតទន់លាយទឹក\n"
            "• ជាញឹកញាប់មានក្លិនស្អុយ\n"
            "• ជំងឺច្រើនកើតចាប់ពីកន្លែងរបួស ដូចជាសត្វល្អិតកកិត ភ្លៀងព្រិល ឬបក្សីខូច\n"
            "• ក្បាលផ្កាអាចលេចទឹក និងទាក់ទាញសត្វល្អិត"
        ),
        "cause_km": (
            "• បាក់តេរីដែលពាក់ព័ន្ធនឹងជំងឺរលួយទន់ ដូចជា Pectobacterium species\n"
            "• ចូលតាមរបួស ហើយរាលដាលនៅលក្ខខណ្ឌក្តៅសើម\n"
            "• សត្វល្អិតអាចបង្កើតច្រកចូល និងជួយផ្ទេរបាក់តេរី"
        ),
        "treatment_km": (
            "• ជាទូទៅ មិនមានថ្នាំបាញ់ព្យាបាលមានប្រសិទ្ធភាពបន្ទាប់ពីឆ្លងហើយ\n"
            "• ដក និងបំផ្លាញក្បាលផ្កាដែលឆ្លងក្នុងសួន ឬចម្ការតូចៗ\n"
            "• គ្រប់គ្រងសត្វល្អិត និងកាត់បន្ថយរបួសដើម្បីទប់ស្កាត់ការឆ្លងថ្មី"
        ),
        "prevention_km": (
            "• ការពារក្បាលផ្កាពីការខូចខាតដោយសត្វល្អិត ដោយតាមដានមេអំបៅផ្កាឈូករ័ត្ន និងសត្វល្អិតផ្សេងៗ\n"
            "• កាត់បន្ថយការខូចខាតពីការងារកសិកម្ម និងកុំចូលធ្វើការពេលដំណាំសើម\n"
            "• លើកកម្ពស់អនាម័យចម្ការ និងបង្កើនការហូរខ្យល់\n"
            "• ប្រមូលផលឱ្យបានទាន់ពេល ដើម្បីកុំឱ្យប៉ះពាល់នឹងអាកាសធាតុសើមយូរ"
        ),
    },
    "phoma-black-stem": {
        "name_km": "ជំងឺផូម៉ាដើមខ្មៅ",
        "symptoms_km": (
            "• មានដំបៅខ្មៅតូចៗលើដើម\n"
            "• ដំបៅជាញឹកញាប់កើតជុំវិញគល់ទងស្លឹក\n"
            "• កើតខ្លាំងក្រោយភ្លៀងញឹកញាប់ និងសំណើមខ្ពស់"
        ),
        "cause_km": (
            "• បង្កដោយផ្សិត Phoma macdonaldii\n"
            "• ផ្សិតរស់នៅលើសំណល់ដំណាំ និងរាលដាលដោយភ្លៀង និងទឹកសាច់\n"
            "• កើតច្រើននៅអាកាសត្រជាក់ដល់មធ្យម និងមានសំណើមលើស្លឹកញឹកញាប់"
        ),
        "treatment_km": (
            "• ត្រួតពិនិត្យចម្ការឱ្យបានញឹកញាប់ និងរក្សាដំណាំឱ្យមានសុខភាពល្អ\n"
            "• ប្រសិនបើតំបន់របស់អ្នកអនុញ្ញាត អាចប្រើថ្នាំផ្សិតតាមស្លាកណែនាំនៅពេលជំងឺកើតខ្លាំង\n"
            "• កាត់បន្ថយសំណល់ដំណាំឆ្លងបន្ទាប់ពីប្រមូលផល"
        ),
        "prevention_km": (
            "• បង្វិលដំណាំ និងគ្រប់គ្រងសំណល់ដំណាំឱ្យបានល្អ\n"
            "• ជ្រើសរើសពូជធន់ ប្រសិនបើមាន\n"
            "• រក្សាចម្ងាយដាំសមស្រប និងកម្ចាត់ស្មៅ ដើម្បីបង្កើនការហូរខ្យល់"
        ),
    },
    "phomopsis-stem-canker": {
        "name_km": "ជំងឺដំបៅដើមផូម៉ុបស៊ីស",
        "symptoms_km": (
            "• ស្លឹកប្រែជាពណ៌សំរិទ្ធ ឬលឿងត្នោត\n"
            "• ដើមខាងក្នុងក្លាយជាប្រហោង និងខ្សោយ\n"
            "• មានដំបៅត្នោតធំៗលើដើម\n"
            "• ជំងឺកើតច្រើននៅពេលមានភ្លៀងញឹកញាប់ និងសំណល់ដំណាំនៅសល់ក្នុងចម្ការ"
        ),
        "cause_km": (
            "• បង្កដោយផ្សិត Phomopsis helianthi និងប្រភេទពាក់ព័ន្ធ\n"
            "• ផ្សិតរស់នៅលើសំណល់ដំណាំ ហើយរាលដាលដោយភ្លៀង និងខ្យល់\n"
            "• កើតខ្លាំងនៅសំណើមខ្ពស់ និងពេលដំណាំសើមយូរ"
        ),
        "treatment_km": (
            "• ត្រួតពិនិត្យដំណាំតាំងពីដំបូង និងដកដំណាំឆ្លងខ្លាំង ប្រសិនបើអាចធ្វើបាន\n"
            "• ប្រើថ្នាំផ្សិតតាមស្លាកណែនាំ ប្រសិនបើមានហានិភ័យខ្ពស់\n"
            "• កាត់បន្ថយសំណល់ដំណាំឆ្លងបន្ទាប់ពីប្រមូលផល"
        ),
        "prevention_km": (
            "• បង្វិលដំណាំ និងគ្រប់គ្រងសំណល់ដំណាំឱ្យបានល្អ\n"
            "• កុំដាំក្រាស់ពេក និងកម្ចាត់ស្មៅ ដើម្បីបង្កើនខ្យល់ចេញចូល\n"
            "• ជ្រើសរើសគ្រាប់ពូជស្អាត និងពូជដែលអាចទ្រាំទ្រជំងឺបាន"
        ),
    },
    "rhizopus-head-rot": {
        "name_km": "ជំងឺរលួយក្បាល Rhizopus",
        "symptoms_km": (
            "• មានរចនាសម្ព័ន្ធខ្មៅតូចៗដូចម្ជុលលើក្បាលផ្កា\n"
            "• មានសរសៃផ្សិតពណ៌ប្រផេះដូចខ្សែលើផ្ទៃក្បាលផ្កា\n"
            "• ក្បាលផ្ការលួយសើម ទន់ និងខូចរហ័ស"
        ),
        "cause_km": (
            "• បង្កដោយផ្សិត Rhizopus species\n"
            "• ជំងឺច្រើនចូលតាមរបួសពីសត្វល្អិត បក្សី ឬការខូចខាតផ្នែកមេកានិច\n"
            "• កើតខ្លាំងនៅលក្ខខណ្ឌក្តៅសើម"
        ),
        "treatment_km": (
            "• ដក និងបំផ្លាញក្បាលផ្កាដែលឆ្លង ដើម្បីកុំឱ្យរាលដាលបន្ថែម\n"
            "• គ្រប់គ្រងសត្វល្អិត និងកាត់បន្ថយការខូចខាតលើក្បាលផ្កា\n"
            "• ប្រមូលផលឱ្យបានទាន់ពេល ប្រសិនបើជំងឺកំពុងកើនឡើង"
        ),
        "prevention_km": (
            "• ការពារក្បាលផ្កាពីរបួសដោយសត្វល្អិត និងបក្សី\n"
            "• បង្កើនការហូរខ្យល់ក្នុងចម្ការ និងកុំឱ្យសំណើមកកកុញ\n"
            "• រក្សាអនាម័យចម្ការ និងកម្ចាត់សំណល់ឆ្លង"
        ),
    },
    "sclerotinia-head-rot": {
        "name_km": "ជំងឺរលួយក្បាល Sclerotinia",
        "symptoms_km": (
            "• មានផ្សិតពណ៌ស និងគ្រាប់រឹងពណ៌ខ្មៅនៅលើក្បាលផ្កា\n"
            "• កើតច្រើនពេលមានភ្លៀងញឹកញាប់ ឬទឹកសន្សើមច្រើនក្នុងដំណាក់កាលចេញផ្កា\n"
            "• ក្បាលផ្ការលួយ ទន់ និងខូចគ្រាប់ខាងក្នុង"
        ),
        "cause_km": (
            "• បង្កដោយផ្សិត Sclerotinia sclerotiorum ដែលវាយប្រហារក្បាលផ្កា\n"
            "• ផ្សិតរស់នៅក្នុងដី និងសំណល់ដំណាំជាគ្រាប់រឹងបានយូរ\n"
            "• កើតខ្លាំងនៅអាកាសត្រជាក់សើម និងពេលចេញផ្កាមានទឹកសើមយូរ"
        ),
        "treatment_km": (
            "• ប្រើថ្នាំផ្សិតតាមស្លាកណែនាំនៅដំណាក់កាលដំបូងនៃការចេញផ្កា ប្រសិនបើហានិភ័យខ្ពស់\n"
            "• កាត់បន្ថយសំណើមក្នុងគម្របដើម និងគ្រប់គ្រងស្មៅ\n"
            "• ដកក្បាលផ្កាដែលឆ្លងខ្លាំងក្នុងចម្ការតូចៗ"
        ),
        "prevention_km": (
            "• បង្វិលដំណាំជាមួយដំណាំមិនមែនជាម្ចាស់មេរោគ\n"
            "• រក្សាចម្ងាយដាំសមស្រប និងបង្កើនខ្យល់ចេញចូល\n"
            "• គ្រប់គ្រងការស្រោចទឹក និងសំណល់ដំណាំឱ្យបានល្អ"
        ),
    },
}


def _has_khmer_text(value: str | None) -> bool:
    text = str(value or "")
    return any("\u1780" <= ch <= "\u17ff" for ch in text)


def _apply_disease_km_localizations() -> None:
    for disease in Disease.query.all():
        localized = DISEASE_KM_LOCALIZATION.get(disease.slug)
        if not localized:
            continue

        if not _has_khmer_text(disease.name_km) or (disease.name_km or "").strip() == disease.name:
            disease.name_km = localized["name_km"]
        if not _has_khmer_text(disease.symptoms_km) or (disease.symptoms_km or "").strip() == disease.symptoms:
            disease.symptoms_km = localized["symptoms_km"]
        if not _has_khmer_text(disease.cause_km) or (disease.cause_km or "").strip() == disease.cause:
            disease.cause_km = localized["cause_km"]
        if not _has_khmer_text(disease.treatment_km) or (disease.treatment_km or "").strip() == disease.treatment:
            disease.treatment_km = localized["treatment_km"]
        if not _has_khmer_text(disease.prevention_km) or (disease.prevention_km or "").strip() == disease.prevention:
            disease.prevention_km = localized["prevention_km"]


def _load_km_phrase_translations() -> dict[str, str]:
    seed_path = Path(__file__).resolve().parents[1] / "i18n_seed" / "km_phrases.json"
    if not seed_path.exists():
        return {}
    try:
        data = json.loads(seed_path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}

    return {
        str(key or "").strip(): str(value or "").strip()
        for key, value in data.items()
        if str(key or "").strip() and str(value or "").strip()
    }


def _backfill_symptom_km_labels() -> None:
    translations = _load_km_phrase_translations()
    if not translations:
        return

    for disease in Disease.query.all():
        items = disease.checklist_items() or []
        changed = False
        for item in items:
            label = str(item.get("label") or "").strip()
            label_km = str(item.get("label_km") or "").strip()
            translated = translations.get(label, "")
            if not label or not translated or translated == label:
                continue
            if _has_khmer_text(label_km) and label_km != label:
                continue
            item["label_km"] = translated
            changed = True

        if changed:
            save_disease_items(disease, items)

    for symptom in SymptomCatalog.query.all():
        label = (symptom.label or "").strip()
        label_km = (symptom.label_km or "").strip()
        translated = translations.get(label, "")
        if not label or not translated or translated == label:
            continue
        if _has_khmer_text(label_km) and label_km != label:
            continue
        symptom.label_km = translated


def seed_if_empty():
    """Seed core data.

    - Roles + Permissions (RBAC)
    - Ensure one admin user exists
    - Seed the 6 diseases (only if diseases table empty)
    """

    # --- RBAC seed (safe to run multiple times) ---
    permissions = {
        # Admin area
        "access_admin": "Access the admin dashboard",
        "manage_diseases": "Create/update disease information",
        "delete_diseases": "Delete disease information",
        "manage_users": "View/edit/delete users",
        "view_symptom_checks": "View symptom checker history",
        # User features
        "edit_own_profile": "Edit own profile",
        "use_symptom_checker": "Use the symptom checker",
    }

    perm_objs = {}
    for name, desc in permissions.items():
        p = Permission.query.filter_by(name=name).first()
        if not p:
            p = Permission(name=name, description=desc)
            db.session.add(p)
        perm_objs[name] = p

    # Create roles
    user_role = Role.query.filter_by(name="user").first()
    if not user_role:
        user_role = Role(name="user", description="Regular user")
        db.session.add(user_role)

    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        admin_role = Role(name="admin", description="System administrator")
        db.session.add(admin_role)

    doctor_role = Role.query.filter_by(name="doctor").first()
    if not doctor_role:
        doctor_role = Role(name="doctor", description="Expert Sunflower (can create/update disease reports)")
        db.session.add(doctor_role)
    elif doctor_role.description == "Doctor (can create/update disease reports)":
        doctor_role.description = "Expert Sunflower (can create/update disease reports)"

    db.session.flush()

    # Assign default permissions only on first run.
    # If you later edit Role/Permission mappings in the database, we do NOT overwrite them.
    def set_defaults_if_empty(role, perm_names: list[str]):
        if role.permissions:
            return
        role.permissions = [perm_objs[n] for n in perm_names if n in perm_objs]

    set_defaults_if_empty(
        user_role,
        [
            "edit_own_profile",
            "use_symptom_checker",
        ],
    )

    set_defaults_if_empty(
        doctor_role,
        [
            "edit_own_profile",
            "use_symptom_checker",
            "manage_diseases",
            "view_symptom_checks",
        ],
    )

    # Admin should always have all permissions (add missing without removing existing)
    existing_admin = {p.name for p in (admin_role.permissions or [])}
    for p in perm_objs.values():
        if p.name not in existing_admin:
            admin_role.permissions.append(p)

    # Ensure doctors can review symptom checks (add missing without removing existing)
    if "view_symptom_checks" in perm_objs:
        existing_doctor = {p.name for p in (doctor_role.permissions or [])}
        if "view_symptom_checks" not in existing_doctor:
            doctor_role.permissions.append(perm_objs["view_symptom_checks"])


    db.session.commit()


    # Backfill users.role_id based on legacy users.role string (best effort).
    try:
        for u in User.query.filter(User.role_id.is_(None)).all():
            r = Role.query.filter_by(name=u.role).first()
            if r:
                u.role_id = r.id
        db.session.commit()
    except Exception:
        db.session.rollback()

    # Ensure an admin account exists
    if not User.query.filter_by(role="admin").first():
        admin_username = os.environ.get("ADMIN_USERNAME", "admin")
        admin_email = os.environ.get("ADMIN_EMAIL", "admin@local.test")
        admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")

        # Avoid collisions if a user already took that username/email
        if User.query.filter((User.username == admin_username) | (User.email == admin_email)).first():
            admin_username = f"{admin_username}_1"
            admin_email = "admin1@local.test"

        admin = User(username=admin_username, email=admin_email, role="admin", role_id=admin_role.id)
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()


    # Ensure a doctor account exists
    if not User.query.filter_by(role="doctor").first():
        doctor_username = os.environ.get("DOCTOR_USERNAME", "doctor")
        doctor_email = os.environ.get("DOCTOR_EMAIL", "doctor@local.test")
        doctor_password = os.environ.get("DOCTOR_PASSWORD", "doctor123")

        # Avoid collisions if a user already took that username/email
        if User.query.filter((User.username == doctor_username) | (User.email == doctor_email)).first():
            doctor_username = f"{doctor_username}_1"
            doctor_email = "doctor1@local.test"

        doctor = User(username=doctor_username, email=doctor_email, role="doctor", role_id=doctor_role.id)
        doctor.set_password(doctor_password)
        db.session.add(doctor)
        db.session.commit()

    # --- Seed diseases (only if empty) ---
    if not Disease.query.first():
        diseases = [
            Disease(
                slug="downy-mildew",
                name="Downy Mildew",
                symptoms=(
                    "• Seedlings may be stunted or collapse soon after emergence\n"
                    "• Pale yellow patches between leaf veins (chlorosis)\n"
                    "• White/gray ‘downy’ growth on the underside of leaves (early morning is easiest to see)\n"
                    "• Plants remain short with small leaves and poor head development"
                ),
                cause=(
                    "• Oomycete pathogen: Plasmopara halstedii\n"
                    "• Can be introduced by infected seed or survive in soil as long‑lasting spores\n"
                    "• Favored by cool to mild temperatures and wet soils / poor drainage"
                ),
                treatment=(
                    "• Remove and destroy heavily infected young plants if outbreaks are localized\n"
                    "• If permitted locally, consider labeled seed treatments or fungicides aimed at oomycetes\n"
                    "• Focus on stopping spread: avoid moving contaminated soil between fields"
                ),
                prevention=(
                    "• Plant resistant hybrids and use certified, treated seed\n"
                    "• Improve drainage; avoid planting in cold, waterlogged soils\n"
                    "• Rotate away from sunflower for 3–4 years (or longer where pressure is high)\n"
                    "• Clean equipment to reduce soil movement"
                ),
                image_filename="downy_mildew.png",
            ),
            Disease(
                slug="alternaria-leaf-spot",
                name="Alternaria Leaf Spot",
                symptoms=(
                    "• Small dark brown spots that expand with concentric rings (target spots)\n"
                    "• Spots may merge, causing large blighted areas\n"
                    "• Premature yellowing and leaf drop, reducing plant vigor and yield"
                ),
                cause=(
                    "• Fungus: Alternaria helianthi (and related Alternaria species)\n"
                    "• Survives on crop residue; spores spread by wind and splashing water\n"
                    "• Favored by warm, humid weather and frequent leaf wetness"
                ),
                treatment=(
                    "• Scout early; apply fungicides only when needed and follow local labels\n"
                    "• Reduce leaf wetness where possible (avoid overhead irrigation late in the day)\n"
                    "• Remove severely infected plant debris after harvest"
                ),
                prevention=(
                    "• Crop rotation and residue management (bury or remove infected debris)\n"
                    "• Improve airflow with appropriate spacing and weed control\n"
                    "• Balanced fertilization (avoid excessive nitrogen)\n"
                    "• Choose tolerant varieties when available"
                ),
                image_filename="alternaria.png",
            ),
            Disease(
                slug="rust",
                name="Rust",
                symptoms=(
                    "• Tiny yellow flecks that develop into orange‑brown powdery pustules\n"
                    "• Pustules often appear first on lower leaves and spread upward\n"
                    "• Heavy infections cause early defoliation and reduced seed fill"
                ),
                cause=(
                    "• Fungus: Puccinia helianthi\n"
                    "• Spores travel long distances on wind\n"
                    "• Favored by warm days, cool nights, and humid conditions"
                ),
                treatment=(
                    "• If rust appears early and is increasing, use a labeled fungicide promptly\n"
                    "• Remove volunteer sunflowers and control weeds that can host the pathogen\n"
                    "• Continue scouting to decide if additional sprays are justified"
                ),
                prevention=(
                    "• Plant rust‑resistant hybrids where available\n"
                    "• Rotate crops and manage volunteer plants\n"
                    "• Avoid overly dense canopies (spacing and nitrogen management)"
                ),
                image_filename="rust.png",
            ),
            Disease(
                slug="charcoal-rot",
                name="Charcoal Rot",
                symptoms=(
                    "• Sudden wilting during flowering or grain fill, especially in hot/dry periods\n"
                    "• Gray to dark discoloration at the lower stem\n"
                    "• Stem pith becomes ‘shredded’ and packed with tiny black specks (sclerotia)\n"
                    "• Plants may lodge or snap near the base"
                ),
                cause=(
                    "• Fungus: Macrophomina phaseolina\n"
                    "• Survives in soil and plant residue; has a wide host range\n"
                    "• Disease is strongly linked to drought stress and high temperatures"
                ),
                treatment=(
                    "• No reliable curative fungicide once symptoms appear\n"
                    "• Reduce stress: manage irrigation (if available) and avoid severe moisture deficit\n"
                    "• Harvest promptly if lodging risk increases"
                ),
                prevention=(
                    "• Choose tolerant hybrids and avoid overly high plant populations\n"
                    "• Use rotations that reduce inoculum pressure where possible\n"
                    "• Maintain soil health and moisture; manage weeds that can host the fungus\n"
                    "• Avoid practices that intensify drought stress"
                ),
                image_filename="charcoal_rot.png",
            ),
            Disease(
                slug="white-mold",
                name="White Mold",
                symptoms=(
                    "• Water‑soaked lesions on stems or heads that quickly turn pale\n"
                    "• White cottony fungal growth on affected tissue\n"
                    "• Hard black structures (sclerotia) form inside stems/heads\n"
                    "• Plants may lodge and heads can rot, reducing yield and quality"
                ),
                cause=(
                    "• Fungus: Sclerotinia sclerotiorum\n"
                    "• Survives in soil as sclerotia for years\n"
                    "• Favored by cool, moist conditions and dense canopies during flowering"
                ),
                treatment=(
                    "• Remove severely diseased plants where practical (small plantings)\n"
                    "• In commercial fields, fungicide timing is critical—often at early bloom in high‑risk fields\n"
                    "• Reduce canopy humidity by improving airflow if feasible"
                ),
                prevention=(
                    "• Rotate with non‑host crops (often grasses/cereals)\n"
                    "• Avoid dense stands; improve airflow with spacing and weed control\n"
                    "• Manage irrigation to reduce prolonged leaf wetness during bloom\n"
                    "• Use tolerant varieties and clean equipment to limit spread"
                ),
                image_filename="white_mold.png",
            ),
            Disease(
                slug="bacterial-head-rot",
                name="Bacterial Head Rot",
                symptoms=(
                    "• Soft, watery decay of the head; tissue becomes brown and mushy\n"
                    "• Foul smell is common\n"
                    "• Often starts at injured areas (insect feeding, hail, bird damage)\n"
                    "• Heads may leak fluids and attract insects"
                ),
                cause=(
                    "• Bacteria commonly linked to soft rot (e.g., Pectobacterium species)\n"
                    "• Enters through wounds and spreads under warm, wet conditions\n"
                    "• Insects can create entry points and help move bacteria"
                ),
                treatment=(
                    "• There is usually no effective curative spray after infection\n"
                    "• Remove and destroy infected heads in gardens/small plots\n"
                    "• Manage insects and reduce wounding to limit new infections"
                ),
                prevention=(
                    "• Protect heads from insect damage (monitor sunflower moth and other pests)\n"
                    "• Reduce mechanical injury and avoid working plants when wet\n"
                    "• Improve field sanitation and promote good air movement\n"
                    "• Harvest on time to avoid prolonged exposure to wet weather"
                ),
                image_filename="bacterial_head_rot.png",
            ),
        ]

        db.session.add_all(diseases)
        db.session.commit()


    # Seed Symptoms + Disease<->Symptom checklist (only if symptoms table empty)
    # Seed checklist directly into each disease (no extra tables)
    # We reuse the original diagnosis.py catalog and rules, but store them as JSON text on the disease.
    symptom_meta = {s.key: {"key": s.key, "label": s.label, "category": s.category} for s in diagnosis.SYMPTOMS}
    for rule in diagnosis.RULES:
        disease = Disease.query.filter_by(slug=rule.disease_key).first()
        if not disease:
            continue
        keys = list((rule.weights or {}).keys())
        items = [symptom_meta[k] for k in keys if k in symptom_meta]
        disease.symptom_checklist_json = json.dumps(items)

    _apply_disease_km_localizations()
    _backfill_symptom_km_labels()

    # Backfill Khmer text columns for legacy rows (fallback = English text).
    for disease in Disease.query.all():
        if not (disease.name_km or "").strip():
            disease.name_km = disease.name
        if not (disease.symptoms_km or "").strip():
            disease.symptoms_km = disease.symptoms
        if not (disease.cause_km or "").strip():
            disease.cause_km = disease.cause
        if not (disease.treatment_km or "").strip():
            disease.treatment_km = disease.treatment
        if not (disease.prevention_km or "").strip():
            disease.prevention_km = disease.prevention
    db.session.commit()
