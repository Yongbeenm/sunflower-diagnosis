# 🛡️ Sunflower Pathology Expert System — Admin Features Demonstration Script

> **Video Title**: Sunflower Pathology Expert System — Complete Administrator & Agronomist Command Center Walkthrough  
> **Target Audience**: Agronomists, Agricultural Extension Administrators, Researchers & System Admins  
> **Automated Recording Runner**: [`record_admin_demo.js`](file:///Users/menghokyongben/Downloads/Expert_sunflower-main/record_admin_demo.js)  
> **Output Video File**: `videos_admin/admin_features_demo.mp4`

---

## ⏱️ Admin Feature Breakdown & Presentation Guide

---

### **PART 1: Admin Overview & Interactive Recharts Analytics**
- **Screen**: `/admin`
- **Actions**:
  - Point cursor to metric scorecards: Total Diseases (20), Total Symptoms (62), Published Diseases, Grower Feedback queue.
  - Interact with 30-Day Disease Outbreak Trend: click `14d` and `30d` time horizon toggles.
  - Hover over trend curves to reveal glassmorphic Recharts tooltips with daily session counts.
  - Scroll down to Symptom Distribution Donut & Ranked Horizontal Bar observation frequency charts.
  - Inspect Diagnostic Confidence Distribution bar charts and system quality gauges.
- **🎙️ Spoken Narration**:
  > "Welcome to the Administrator and Agronomist Control Center of the Sunflower Pathology Expert System. This portal turns raw field evaluations into regional epidemiological surveillance. 
  > 
  > Here on the Overview dashboard, agronomists can track active disease trends across seven, fourteen, and thirty-day windows using interactive Recharts analytics. Below, our observation charts show which symptoms are most prevalent across regional farms, and our diagnostic health gauges monitor match certainty and system coverage."

---

### **PART 2: Disease Knowledge Base Catalog**
- **Screen**: `/admin/diseases`
- **Actions**:
  - Browse master disease catalog table displaying scientific taxonomy, causal organisms, and pathogen classifications.
  - Demonstrate search filter by typing *"Rust"* to filter immediately.
  - Highlight the publication status toggles (Published / Draft).
- **🎙️ Spoken Narration**:
  > "In the Disease Knowledge Base Catalog, administrators manage the entire repository of twenty sunflower pathogens. Agronomists can search, filter by pathogen type—fungal, bacterial, or viral—and instantly toggle disease publication status between live and draft modes."

---

### **PART 3: Disease Creation Form Wizard**
- **Screen**: `/admin/diseases/new`
- **Actions**:
  - Show the new disease creation form.
  - Highlight fields for common name, scientific name, causal organism, pathogen type, and risk severity.
- **🎙️ Spoken Narration**:
  > "When emerging crop pathogens or regional strains are discovered, administrators can register new diseases through this creation wizard, specifying scientific classifications, environmental triggers, and disease cycle stages."

---

### **PART 4: Deep Disease Knowledge Editor (Symptoms, Weights & FRAC Codes)**
- **Screen**: `/admin/diseases/sunflower-rust`
- **Actions**:
  - **Tab 1: Symptoms & Weights**: Inspect symptom associations, weight sliders, and pathognomonic marker toggles.
  - **Tab 2: Content & Biology**: Scroll through causal biology, FRAC chemical fungicide groups, organic bio-controls, and cultural sanitation practices.
  - **Tab 3: Media & Photography**: Review high-resolution clinical lesion photography.
- **🎙️ Spoken Narration**:
  > "This is our Deep Disease Knowledge Editor—the scientific brain of the platform. Under the Symptoms tab, agronomists calibrate Bayesian symptom weights and designate 'pathognomonic' indicators—hallmarks that uniquely identify a specific infection. 
  > 
  > Under the Content tab, administrators manage FRAC fungicide codes to prevent chemical resistance and configure certified organic alternatives. Under Media, high-resolution clinical photography is maintained to power both human inspection and multimodal AI vision matching."

---

### **PART 5: Centralized Botanical Symptom Catalog**
- **Screen**: `/admin/symptoms`
- **Actions**:
  - Filter across the 5 plant anatomical zones: Leaves, Stems, Heads, Roots, and Whole Plant.
  - Click **"+ Add Symptom"** to open the registration modal, displaying bilingual English and Khmer labels and auto-generated symptom codes. Close modal.
- **🎙️ Spoken Narration**:
  > "Here in the Botanical Symptom Catalog, over sixty clinical indicators are organized across five anatomical zones. Administrators can register new symptoms with standardized codes and bilingual English and Khmer definitions to guarantee complete field accessibility."

---

### **PART 6: Diagnostic Rulesets & Bayesian Tuning**
- **Screen**: `/admin/rulesets`
- **Actions**:
  - Review active diagnostic ruleset version.
  - Inspect mathematical Bayesian penalty parameters, absence penalties, sensitivity, and specificity thresholds.
- **🎙️ Spoken Narration**:
  > "The Ruleset Engine allows researchers to fine-tune the mathematical parameters driving our diagnostic scoring—adjusting symptom absence penalties, sensitivity thresholds, and mathematical certainty formulas."

---

### **PART 7: Farmer Field Feedback Moderation Queue**
- **Screen**: `/admin/feedback`
- **Actions**:
  - Review incoming feedback submissions from field officers and growers.
  - Filter by status: Open, In Review, and Resolved.
- **🎙️ Spoken Narration**:
  > "Our Feedback Moderation Queue bridges remote farmers directly to expert agronomists. Field officers who spot unusual lesion patterns or treatment failures can submit field reports, allowing researchers to triage and investigate emerging crop issues."

---

### **PART 8: User Accounts & Role Management**
- **Screen**: `/admin/users`
- **Actions**:
  - View user directory with email addresses, usernames, and roles.
  - Demonstrate role selection dropdown (Grower, Agronomist, Administrator) and user account status activation/deactivation.
- **🎙️ Spoken Narration**:
  > "In the User Management module, administrators oversee accounts, manage active statuses, and assign roles—promoting trusted agronomists and researchers to privileged administrative roles."

---

### **PART 9: Role-Based Access Control (RBAC) Matrix**
- **Screen**: `/admin/roles`
- **Actions**:
  - Scroll through the enterprise capability permissions matrix.
  - Hover over granular permission checkboxes (disease authoring, publishing, symptom creation, feedback moderation).
- **🎙️ Spoken Narration**:
  > "Security and data integrity are governed by our enterprise Role-Based Access Control matrix. Capabilities are divided strictly across Administrator, Agronomist, and Grower roles, ensuring only verified researchers can modify clinical diagnostic rules."

---

### **PART 10: Admin Conversational AI Assistant & Database Commands**
- **Screen**: Bottom right AI Assistant widget (Admin Mode)
- **Actions**:
  - Open AI Assistant displaying the golden shield badge: *"Admin Mode - Can modify data"*.
  - Type administrative query: *"List all diseases in the database"*.
  - Show response returning database records with pathogen groupings.
- **🎙️ Spoken Narration**:
  > "Finally, administrators have access to an enhanced AI Assistant in Admin Mode. Marked with a golden shield, the AI can query the database directly in natural language, enabling rapid inspections and administrative navigation."

---

### **PART 11: Summary & Conclusion**
- **Screen**: `/admin` Overview
- **🎙️ Spoken Narration**:
  > "With interactive epidemiological analytics, deep botanical rule authoring, granular RBAC security, and conversational database intelligence, the Sunflower Pathology Expert System provides a comprehensive command center for agricultural health research."
