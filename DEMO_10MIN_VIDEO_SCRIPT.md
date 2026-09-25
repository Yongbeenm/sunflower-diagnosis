# 🌻 Sunflower Pathology Expert System — 10-Minute Master Video Demo Script

> **Video Title**: Sunflower Pathology Expert Diagnostic System — Full 10-Minute Clinical & Architectural Walkthrough  
> **Duration**: Exactly 10 Minutes (00:00 – 10:00)  
> **Resolution**: 1920 × 1080 Full HD (60 FPS)  
> **Target Audience**: Agronomists, Crop Scientists, Agricultural Extension Officers, Software Architects, and Agricultural Tech Evaluators.  
> **Automated Recording Script**: [`record_10min_demo.js`](file:///Users/menghokyongben/Downloads/Expert_sunflower-main/record_10min_demo.js)

---

## ⏱️ Master Timeline & Chapter Breakdown

| Chapter | Timecode | Duration | Focus Area / Key System Features |
|---|---|---|---|
| **Chapter 1** | `00:00 – 01:00` | 60 sec | **Platform Overview & Mission**: Hero metrics, modern architecture, dual-language, stack overview. |
| **Chapter 2** | `01:00 – 02:15` | 75 sec | **Curated Disease Knowledge Base**: 20 pathogens, botanical classification, FRAC chemical codes & clinical profiles. |
| **Chapter 3** | `02:15 – 03:15` | 60 sec | **Side-by-Side Lookalike Disease Comparison**: Differentiating mimics (e.g., Downy vs. Powdery Mildew), spray schedules. |
| **Chapter 4** | `03:15 – 04:45` | 90 sec | **Multimodal Vision AI ("Helio Crop Advisor")**: Natural language Q&A, lesion image recognition & database auto-match. |
| **Chapter 5** | `04:45 – 06:00` | 75 sec | **Multi-Step Diagnostic Symptom Checker**: 5 plant zones, pre-selected symptoms & live Bayesian probability ranker. |
| **Chapter 6** | `06:00 – 07:00` | 60 sec | **Clinical Diagnostic Scorecard & PDF Export**: Certainty tiers, treatments, branded PDF export & Web Share API. |
| **Chapter 7** | `07:00 – 07:45` | 45 sec | **Grower Diagnosis History & Field Feedback**: Historical crop tracking, session logs, unclassified symptom submission. |
| **Chapter 8** | `07:45 – 09:00` | 75 sec | **Agronomist & Admin Control Center**: Recharts visual analytics (30d trends), symptom manager, rulesets & RBAC. |
| **Chapter 9** | `09:00 – 09:35` | 35 sec | **100% Khmer Localization & Offline PWA**: Native Khmer (ភាសាខ្មែរ), Service Worker & IndexedDB auto-sync. |
| **Chapter 10** | `09:35 – 10:00` | 25 sec | **Summary & Agricultural Impact**: Field-to-laboratory bridge, food security & closing acknowledgments. |

---

## 🎬 Minute-by-Minute Script: Spoken Narration & On-Screen Choreography

---

### ⏱️ CHAPTER 1: Platform Overview & System Architecture (00:00 – 01:00)

- **On-Screen Display**: Landing Page (`http://localhost:5173/`)
- **Visual Cue**: Presenter Badge reads: `Chapter 1: Platform Overview • 00:00 / 10:00`
- **Actions**:
  - `00:00 – 00:15`: Static view of glowing hero section with sunflower imagery and CTA buttons.
  - `00:15 – 00:30`: Smooth scroll down to Platform Metrics: 20 Diseases, 62 Clinical Indicators, 8 Plant Zones.
  - `00:30 – 00:48`: Scroll down to the 4-step diagnostic pipeline: Inspection, Vision AI, Bayesian Inference, and Verified Prescription.
  - `00:48 – 01:00`: Smooth scroll back to top navigation.

#### 🎙️ Spoken Narration (Voiceover):
> "Welcome to the official demonstration of the Sunflower Pathology Expert Diagnostic System. 
> 
> Sunflower crops face severe yield losses annually from aggressive fungal pathogens, bacterial rots, and viral infections. Early, accurate diagnosis in the field is vital. 
> 
> Our platform bridges botanical plant pathology with state-of-the-art multimodal artificial intelligence. Built on a modern tech stack featuring FastAPI, Python 3.12, PostgreSQL 16, React 19, and Vite, the platform provides an enterprise-grade clinical diagnosis tool for growers, agricultural extension officers, and plant pathologists. 
> 
> Here on the landing page, users are immediately greeted with live repository statistics: over twenty standardized sunflower diseases, sixty-two curated clinical indicators across eight distinct anatomical plant zones, and instant access to our diagnostic pipeline."

---

### ⏱️ CHAPTER 2: Curated Pathology Knowledge Base & Deep Clinical Profiles (01:00 – 02:15)

- **On-Screen Display**: Disease Catalog (`/diseases`) ➔ Disease Detail (`/diseases/alternaria-leaf-spot` or `/diseases/sunflower-rust`)
- **Visual Cue**: Presenter Badge reads: `Chapter 2: Disease Knowledge Base • 01:00 / 10:00`
- **Actions**:
  - `01:00 – 01:25`: Click **"Diseases"** in top navbar. Browse the card grid showing high-resolution imagery, pathogen tags (Fungal, Bacterial, Viral, Phytoplasma), and short descriptions.
  - `01:25 – 01:45`: Click on **"Alternaria Leaf and Stem Spot"** (or **"Sunflower Rust"**).
  - `01:45 – 02:15`: Scroll through the Disease Profile page highlighting:
    - Botanical classification & Causal organism (`Alternaria helianthi`).
    - Characteristic hallmarks (target-board concentric rings, chlorotic halos).
    - FRAC Chemical Fungicides & Organic Biocontrols.
    - Preventative cultural practices and environmental risk factors.

#### 🎙️ Spoken Narration (Voiceover):
> "Let us navigate into the Disease Knowledge Base. 
> 
> This is not a static encyclopedia; it is a clinical repository verified against international phytopathological standards. Each disease entry includes full etiology, taxonomy, and verified high-resolution field photography.
> 
> Opening Alternaria Leaf and Stem Spot, you can examine its causal organism, Alternaria helianthi, alongside pathognomonic symptoms—such as circular-to-angular necrotic lesions with characteristic concentric target-board rings.
> 
> More importantly, agronomists have complete visibility into actionable management protocols: FRAC fungicide classifications, mode-of-action rotation to prevent chemical resistance, biological fungicides such as Bacillus subtilis, and cultural sanitation protocols to protect next season's crop."

---

### ⏱️ CHAPTER 3: Side-by-Side Lookalike Disease Comparison Tool (02:15 – 03:15)

- **On-Screen Display**: Disease Comparison Tool (`/diseases/compare`)
- **Visual Cue**: Presenter Badge reads: `Chapter 3: Lookalike Comparison Tool • 02:15 / 10:00`
- **Actions**:
  - `02:15 – 02:35`: Open `/diseases/compare`. The default comparison displays **Downy Mildew** (`Plasmopara halstedii`) side-by-side with **Powdery Mildew** (`Golovinomyces cichoracearum`).
  - `02:35 – 02:55`: Smooth scroll down the comparison table:
    - Comparing symptom locations (leaf undersides vs. leaf surfaces).
    - Comparing fungal structures (carpet-like dense white felt vs. superficial talcum powder).
    - Comparing systemic stunting versus localized foliar stress.
  - `02:55 – 03:15`: Highlight the chemical compatibility warning matrix showing why fungicides effective against Powdery Mildew will fail completely against Downy Mildew due to oomycete biology.

#### 🎙️ Spoken Narration (Voiceover):
> "One of the greatest challenges in agricultural field diagnostics is distinguishing between lookalike diseases. Misdiagnosing an infection can lead to applying the wrong pesticide class, wasting money and devastating the harvest.
> 
> To solve this, we created the Side-by-Side Disease Comparison Tool. 
> 
> Here, we compare Downy Mildew against Powdery Mildew. While both present white fungal growth on foliage, our system highlights the critical diagnostic differences: Downy Mildew is an oomycete causing systemic stunting with dense felt strictly on leaf undersides, whereas Powdery Mildew is an ascomycete producing powdery patches on upper leaf surfaces.
> 
> Notice the chemical management section: it alerts agronomists that standard powdery mildew triazoles are completely ineffective against Downy Mildew, requiring specialized phenylamides or strobilurins instead."

---

### ⏱️ CHAPTER 4: Multimodal Vision AI & Database Auto-Match (03:15 – 04:45)

- **On-Screen Display**: Landing Page / Floating Chat Widget (`AIChatWidget`)
- **Visual Cue**: Presenter Badge reads: `Chapter 4: Multimodal Vision AI • 03:15 / 10:00`
- **Actions**:
  - `03:15 – 03:30`: Click the floating **Helio AI Crop Advisor** button in the bottom right corner.
  - `03:30 – 03:45`: Type in natural language: *"What are the characteristic symptoms of Sunflower Rust?"* and press Enter. Helio answers in seconds with agronomic accuracy.
  - `03:45 – 04:15`: Attach a leaf photo (`sunflower_rust_sample.jpg`) showing cinnamon-colored pustules. Add text: *"Found on lower leaves in block 4 with cinnamon pustules"*, and hit Send.
  - `04:15 – 04:35`: The AI processes the image using vision analysis, recognizes the pustules, and performs an autonomous search against the backend PostgreSQL database.
  - `04:35 – 04:45`: Helio returns: *"Matched Disease: Sunflower Rust (92% Confidence)"* along with direct action buttons: *“Start Diagnosis with Photo”* and *“View Disease Profile”*.

#### 🎙️ Spoken Narration (Voiceover):
> "Now let us explore the platform’s conversational intelligence: the Helio AI Crop Advisor. 
> 
> Farmers and field officers in remote areas need instant answers. You can ask Helio complex agronomic questions directly in natural language.
> 
> Even more powerful is our multimodal vision capability. Suppose a grower spots an unfamiliar lesion in the field. They upload a photo directly into the chat.
> 
> The vision pipeline analyzes color distribution, lesion morphology, and anatomical tissue patterns. It immediately matches the specimen against our database, identifying Sunflower Rust with ninety-two percent confidence.
> 
> With a single click, the user is navigated directly into the verified disease profile and handed a seamless bridge into our clinical diagnostic engine."

---

### ⏱️ CHAPTER 5: Multi-Step Interactive Symptom Checker & Real-Time Bayesian Engine (04:45 – 06:00)

- **On-Screen Display**: Symptom Checker Wizard (`/check?disease=sunflower-rust&symptoms=42,43`)
- **Visual Cue**: Presenter Badge reads: `Chapter 5: Auto-Checked Symptom Wizard • 04:45 / 10:00`
- **Actions**:
  - `04:45 – 05:05`: Arrive at the Symptom Checker. Point out that the characteristic symptoms identified by the AI (*"Cinnamon-brown powdery pustules"* and *"Black, raised late-season pustules"*) are **already pre-checked** automatically.
  - `05:05 – 05:25`: Tour the plant anatomy zone navigation tabs: Leaves, Stems, Flower Heads/Inflorescence, Roots, and Whole Plant.
  - `05:25 – 05:45`: Direct attention to the right-hand panel: the **Live Real-Time Probability Candidate Ranker**.
  - `05:45 – 06:00`: Toggle an additional leaf symptom to "Yes". Watch the probability ranker recalculate live without refreshing the page, powered by our Bayesian inference weights.

#### 🎙️ Spoken Narration (Voiceover):
> "This brings us to the core of the system: the Interactive Diagnostic Symptom Checker.
> 
> Notice what happened: because we came from the AI diagnosis, the characteristic hallmark symptoms for Sunflower Rust are already pre-selected. There is no need for duplicate entry.
> 
> The checker organizes clinical indicators across five anatomical zones: Leaves, Stems, Heads, Roots, and Whole Plant. 
> 
> On the right, observe the dynamic candidate panel. Unlike black-box machine learning models, our engine uses transparent Bayesian inference with pathognomonic symptom weights. As you confirm or rule out symptoms in real time, the probability distribution updates instantly, giving agronomists total visibility into why a specific disease ranks highest."

---

### ⏱️ CHAPTER 6: Clinical Diagnostic Scorecard, PDF Export & Field Sharing (06:00 – 07:00)

- **On-Screen Display**: Diagnostic Result Scorecard (`/check/:sessionId`)
- **Visual Cue**: Presenter Badge reads: `Chapter 6: Clinical Diagnostic Report • 06:00 / 10:00`
- **Actions**:
  - `06:00 – 06:20`: Click **"Submit Diagnosis"**. View the generated clinical scorecard.
  - `06:20 – 06:40`: Scroll through the verified report:
    - Diagnostic Certainty Tier: **Definitive Diagnosis (94.2%)**.
    - Matched hallmarks versus ruled-out symptoms.
    - Dual-action prescription: FRAC Group 3 & 11 triazole/strobilurin fungicides + organic neem oil/potassium bicarbonate.
  - `06:40 – 07:00`: Click **"Download PDF Report"**. An official, branded PDF preview appears with formal diagnostic metadata, session ID, timestamps, and export button. Highlight the **Share** button utilizing the Web Share API.

#### 🎙️ Spoken Narration (Voiceover):
> "Submitting the evaluation produces a complete Clinical Diagnostic Scorecard. 
> 
> Here, the system confirms a Definitive Diagnosis of Sunflower Rust with ninety-four point two percent certainty. 
> 
> It provides a comprehensive pathology report: which hallmark symptoms were verified, which secondary symptoms were absent, and an immediate actionable prescription covering both commercial chemical remedies and certified organic alternatives.
> 
> For field workers who need to provide proof to farm owners or agricultural extension agencies, clicking 'Download PDF Report' compiles a publication-quality clinical report complete with QR codes, session identifiers, and official diagnostic timestamps."

---

### ⏱️ CHAPTER 7: Grower Diagnosis History & Field Feedback Reporting (07:00 – 07:45)

- **On-Screen Display**: Diagnosis History (`/history`) ➔ Field Feedback (`/feedback`)
- **Visual Cue**: Presenter Badge reads: `Chapter 7: Diagnosis History • 07:00 / 10:00`
- **Actions**:
  - `07:00 – 07:20`: Navigate to **History** (`/history`). Show the chronological audit trail of all previous field evaluations, status badges (Definitive, Probable, Inconclusive), and one-click reopening of past reports.
  - `07:20 – 07:45`: Navigate to **Feedback** (`/feedback`). Showcase the grower field feedback form where farmers can report emerging symptom variations, unclassified field outbreaks, or treatment efficacy.

#### 🎙️ Spoken Narration (Voiceover):
> "Next, we visit the Grower History dashboard. 
> 
> Every field scan performed by a registered grower is permanently logged. Farmers can track the progression of disease outbreaks across seasons, monitor which fields experienced recurring infections, and revisit past treatment recommendations at any time.
> 
> In addition, our Field Feedback module empowers extension workers to submit unclassified symptom patterns directly from the fields. If a farmer encounters a novel pathogen mutation or an atypical symptom pattern, they can submit field observations directly to our research team for laboratory review."

---

### ⏱️ CHAPTER 8: Agronomist & Admin Control Center (07:45 – 09:00)

- **On-Screen Display**: Admin Overview (`/admin`) ➔ Admin Diseases (`/admin/diseases`) ➔ Admin Symptoms (`/admin/symptoms`) ➔ Admin Roles (`/admin/roles`)
- **Visual Cue**: Presenter Badge reads: `Chapter 8: Agronomist Admin Control • 07:45 / 10:00`
- **Actions**:
  - `07:45 – 08:15`: Open `/admin`. Showcase the live **Recharts** Visual Analytics suite:
    - 30-Day Disease Outbreak Trend Area Chart (click `14d` and `30d` filters).
    - Symptom Observation Frequency (Donut and ranked Horizontal Bar charts).
    - Diagnostic Health Gauges (Match Rate, System Coverage).
  - `08:15 – 08:35`: Open `/admin/diseases` and show the Disease Knowledge Base Editor where agronomists manage pathogen taxonomy, symptom weights, and pathognomonic status.
  - `08:35 – 08:50`: Open `/admin/symptoms` showing the centralized botanical symptom catalog.
  - `08:50 – 09:00`: Open `/admin/roles` demonstrating enterprise Role-Based Access Control (RBAC) across Administrator, Agronomist, and Grower privileges.

#### 🎙️ Spoken Narration (Voiceover):
> "Now let us enter the Agronomist and Administrative Control Center. 
> 
> This portal transforms raw diagnostic data into regional epidemiological intelligence. Powered by Recharts, our interactive visual analytics track 30-day outbreak trends across multiple time horizons, display symptom observation frequencies, and monitor overall diagnostic accuracy.
> 
> Certified agronomists have full control over the knowledge base in the Disease and Symptom editors. Here, researchers can define pathognomonic indicators—symptoms that uniquely guarantee a specific pathogen—and tune Bayesian penalties to eliminate false positives.
> 
> Security is enforced through a granular Role-Based Access Control matrix, ensuring growers, agronomists, and system administrators operate with strictly defined permissions."

---

### ⏱️ CHAPTER 9: 100% Native Khmer Localization & Offline PWA Resilience (09:00 – 09:35)

- **On-Screen Display**: Language Switcher ➔ Khmer UI (`km`)
- **Visual Cue**: Presenter Badge reads: `Chapter 9: Native Khmer Localization • 09:00 / 10:00`
- **Actions**:
  - `09:00 – 09:15`: Click the language toggle to switch the entire application into **Khmer (ភាសាខ្មែរ)**.
  - `09:15 – 09:35`: Scroll through the Khmer interface showing that every single label, symptom description, treatment recommendation, and disease profile has been translated and adapted for Cambodian sunflower farming communities.
  - Point out that the Progressive Web App (PWA) caches all disease definitions via Service Workers and stores diagnoses in IndexedDB when internet is disconnected.

#### 🎙️ Spoken Narration (Voiceover):
> "Accessibility is central to our mission. Agricultural technology must reach farmers in their native language.
> 
> With a single click, our entire application instantly transforms into native Khmer (ភាសាខ្មែរ). Every anatomical term, symptom description, and chemical protocol is accurately localized.
> 
> Furthermore, because rural farming communities often lack reliable cellular coverage, the platform is engineered as an offline-first Progressive Web App. Field officers can conduct complete symptom evaluations completely offline; all records are safely queued in IndexedDB and automatically synchronized the moment internet connectivity is restored."

---

### ⏱️ CHAPTER 10: Summary, Agricultural Impact & Conclusion (09:35 – 10:00)

- **On-Screen Display**: Landing Page / Summary Banner
- **Visual Cue**: Presenter Badge reads: `Chapter 10: Summary & Agricultural Impact • 09:35 / 10:00`
- **Actions**:
  - `09:35 – 09:50`: Smooth camera pan over the system hero section.
  - `09:50 – 10:00`: Display closing banner: *"Sunflower Pathology Expert System — Clinical Diagnostic Platform. Thank you for watching!"*

#### 🎙️ Spoken Narration (Voiceover):
> "To summarize, the Sunflower Pathology Expert System combines the speed of multimodal vision AI with the clinical rigor of Bayesian botanical rule engines. 
> 
> By delivering side-by-side lookalike comparisons, offline resilience, native Khmer translation, and agronomist epidemiological tools, we provide a complete field-to-laboratory defense system for sunflower agriculture.
> 
> Thank you for watching our demonstration. For more details or to deploy this system in your region, please consult our project documentation."

---

## 🛠️ How to Record the Automated Video

To execute the automated 10-minute browser demonstration that follows this script word-for-word:

1. Ensure the backend and frontend are running:
   ```bash
   # In terminal
   docker compose up -d
   ```
2. Run the Playwright automated recorder:
   ```bash
   node record_10min_demo.js
   ```
3. The video will be saved automatically into:
   ```
   ./videos_10min/*.webm
   ```
4. To convert the recorded video to standard MP4 (optional):
   ```bash
   ffmpeg -i videos_10min/*.webm -c:v libx264 -crf 20 -preset slow sunflower_10min_demo.mp4
   ```
