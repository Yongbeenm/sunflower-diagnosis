/**
 * Admin Features Demonstration Recorder — Human Presentation Engine
 * 
 * Demonstrates ALL features available to Administrators & Agronomists:
 * 1. Admin Overview Dashboard & Interactive Recharts Analytics (30d outbreak trends, filters, symptom donut & bar charts, confidence tiers)
 * 2. Disease Knowledge Base Catalog (search, pathogen filters, publication toggle)
 * 3. Disease Creation Wizard (/admin/diseases/new)
 * 4. Deep Disease Knowledge Editor (/admin/diseases/:id with Symptoms, Weights, Pathognomonic markers, Content, FRAC & Media tabs)
 * 5. Centralized Botanical Symptom Catalog (/admin/symptoms with 5 anatomy zones & Add Symptom modal)
 * 6. Diagnostic Rulesets & Bayesian Parameter Configuration (/admin/rulesets)
 * 7. Farmer Feedback Moderation Queue (/admin/feedback)
 * 8. User Account Administration & Role Management (/admin/users)
 * 9. Role-Based Access Control (RBAC) Permission Matrix (/admin/roles)
 * 10. Admin Conversational AI Assistant & Database Commands
 * 11. Conclusion & Administrator Control Summary
 */

const { chromium } = require('./frontend/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

let currentMouse = { x: 960, y: 540 };

/**
 * Injects a glowing golden presenter cursor and click-ripple effect into the page.
 */
async function ensureVirtualCursor(page) {
  try {
    await page.evaluate(({ initX, initY }) => {
      if (document.getElementById('demo-human-cursor')) return;

      const cursor = document.createElement('div');
      cursor.id = 'demo-human-cursor';
      cursor.style.cssText = `
        position: fixed;
        left: ${initX}px;
        top: ${initY}px;
        width: 22px;
        height: 22px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(251, 191, 36, 0.95) 0%, rgba(245, 158, 11, 0.8) 70%);
        border: 2.5px solid #ffffff;
        box-shadow: 0 0 16px rgba(245, 158, 11, 0.9), 0 4px 12px rgba(0,0,0,0.5);
        pointer-events: none;
        z-index: 99999999;
        transform: translate(-50%, -50%);
        transition: width 0.15s ease, height 0.15s ease, background 0.15s ease;
      `;
      document.body.appendChild(cursor);

      window.addEventListener('mousemove', (e) => {
        cursor.style.left = e.clientX + 'px';
        cursor.style.top = e.clientY + 'px';
      });

      window.addEventListener('mousedown', (e) => {
        cursor.style.width = '18px';
        cursor.style.height = '18px';
        cursor.style.background = '#f59e0b';

        const ripple = document.createElement('div');
        ripple.style.cssText = `
          position: fixed;
          left: ${e.clientX}px;
          top: ${e.clientY}px;
          width: 12px;
          height: 12px;
          border-radius: 50%;
          border: 2px solid #fbbf24;
          background: rgba(251, 191, 36, 0.35);
          pointer-events: none;
          z-index: 99999998;
          transform: translate(-50%, -50%) scale(1);
          opacity: 1;
          transition: transform 0.45s cubic-bezier(0, 0, 0.2, 1), opacity 0.45s ease-out;
        `;
        document.body.appendChild(ripple);
        requestAnimationFrame(() => {
          ripple.style.transform = 'translate(-50%, -50%) scale(4.5)';
          ripple.style.opacity = '0';
        });
        setTimeout(() => ripple.remove(), 500);
      });

      window.addEventListener('mouseup', () => {
        cursor.style.width = '22px';
        cursor.style.height = '22px';
        cursor.style.background = 'radial-gradient(circle, rgba(251, 191, 36, 0.95) 0%, rgba(245, 158, 11, 0.8) 70%)';
      });
    }, { initX: currentMouse.x, initY: currentMouse.y });
  } catch (e) {}
}

async function humanMoveTo(page, targetX, targetY, durationMs = 1000) {
  await ensureVirtualCursor(page);
  const startX = currentMouse.x;
  const startY = currentMouse.y;
  const steps = 28;
  const stepDelay = durationMs / steps;

  const midX = (startX + targetX) / 2 + (Math.random() * 24 - 12);
  const midY = (startY + targetY) / 2 + (Math.random() * 16 - 8);

  for (let i = 1; i <= steps; i++) {
    const t = i / steps;
    const x = Math.round((1 - t) * (1 - t) * startX + 2 * (1 - t) * t * midX + t * t * targetX);
    const y = Math.round((1 - t) * (1 - t) * startY + 2 * (1 - t) * t * midY + t * t * targetY);
    await page.mouse.move(x, y);
    currentMouse = { x, y };
    await page.waitForTimeout(stepDelay);
  }
  await page.mouse.move(targetX, targetY);
  currentMouse = { x: targetX, y: targetY };
}

async function humanClick(page, selectorOrCoords, dwellBeforeClickMs = 300) {
  await ensureVirtualCursor(page);
  let targetX = 0;
  let targetY = 0;

  if (typeof selectorOrCoords === 'string') {
    try {
      const el = await page.$(selectorOrCoords);
      if (!el) return false;
      const box = await el.boundingBox();
      if (!box) return false;
      targetX = Math.round(box.x + box.width / 2 + (Math.random() * 4 - 2));
      targetY = Math.round(box.y + box.height / 2 + (Math.random() * 4 - 2));
    } catch (e) {
      return false;
    }
  } else {
    targetX = selectorOrCoords.x;
    targetY = selectorOrCoords.y;
  }

  await humanMoveTo(page, targetX, targetY, 800);
  await page.waitForTimeout(dwellBeforeClickMs);
  await page.mouse.down();
  await page.waitForTimeout(100);
  await page.mouse.up();
  await page.waitForTimeout(250);
  return true;
}

async function humanHover(page, selector, hoverDurationMs = 2200) {
  await ensureVirtualCursor(page);
  try {
    const el = await page.$(selector);
    if (!el) return;
    const box = await el.boundingBox();
    if (!box) return;
    const targetX = Math.round(box.x + box.width / 2);
    const targetY = Math.round(box.y + box.height / 2);
    await humanMoveTo(page, targetX, targetY, 900);
    const parts = 4;
    const partTime = hoverDurationMs / parts;
    for (let i = 0; i < parts; i++) {
      await page.waitForTimeout(partTime);
      await page.mouse.move(targetX + (i % 2 === 0 ? 2 : -2), targetY + (i % 2 === 0 ? -1 : 1));
    }
  } catch (e) {}
}

async function humanScroll(page, targetScrollY, durationMs = 3000) {
  await ensureVirtualCursor(page);
  try {
    const currentY = await page.evaluate(() => window.scrollY);
    const totalDistance = targetScrollY - currentY;
    const steps = 25;
    const stepTime = durationMs / steps;

    for (let i = 1; i <= steps; i++) {
      const progress = i / steps;
      const easeProgress = progress < 0.5 
        ? 2 * progress * progress 
        : 1 - Math.pow(-2 * progress + 2, 2) / 2;
      const nextY = Math.round(currentY + (totalDistance * easeProgress));
      await page.evaluate((y) => window.scrollTo(0, y), nextY);
      await page.waitForTimeout(stepTime);
    }
    await page.evaluate((y) => window.scrollTo(0, y), targetScrollY);
  } catch (e) {}
}

async function typeHumanLike(page, selector, text) {
  try {
    await humanClick(page, selector, 200);
    for (const char of text) {
      await page.keyboard.type(char);
      const delay = Math.floor(Math.random() * 30) + 45;
      await page.waitForTimeout(delay);
    }
  } catch (e) {}
}

async function showPresenterBadge(page, sectionTitle, subtitle, narrationCue = '') {
  try {
    await ensureVirtualCursor(page);
    await page.evaluate(({ title, desc, cue }) => {
      let el = document.getElementById('admin-demo-presenter-badge');
      if (!el) {
        el = document.createElement('div');
        el.id = 'admin-demo-presenter-badge';
        el.style.cssText = `
          position: fixed;
          top: 24px;
          right: 28px;
          z-index: 9999999;
          max-width: 500px;
          padding: 16px 22px;
          border-radius: 18px;
          background: rgba(15, 23, 42, 0.94);
          backdrop-filter: blur(18px);
          -webkit-backdrop-filter: blur(18px);
          border: 1px solid rgba(245, 158, 11, 0.55);
          box-shadow: 0 20px 40px -4px rgba(0, 0, 0, 0.55);
          color: #fff;
          font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          pointer-events: none;
          transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        `;
        document.body.appendChild(el);
      }
      el.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 20px;">🛡️</span>
            <span style="font-size: 11px; font-weight: 800; color: #fbbf24; text-transform: uppercase; letter-spacing: 0.08em;">${title}</span>
          </div>
          <span style="font-size: 10px; font-weight: 700; color: #cbd5e1; background: rgba(255,255,255,0.12); padding: 3px 8px; border-radius: 6px;">ADMIN PORTAL</span>
        </div>
        <div style="font-size: 13px; font-weight: 600; color: #f8fafc; margin-top: 6px; line-height: 1.45;">${desc}</div>
        ${cue ? `<div style="font-size: 11px; font-weight: 400; color: #94a3b8; margin-top: 5px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 5px; font-style: italic;">🎙️ Presenter: ${cue}</div>` : ''}
      `;
      el.style.opacity = '1';
      el.style.transform = 'translateY(0) scale(1)';
    }, { title: sectionTitle, desc: subtitle, cue: narrationCue });
  } catch (e) {}
}

(async () => {
  const videoDir = path.resolve(__dirname, 'videos_admin');
  if (!fs.existsSync(videoDir)) fs.mkdirSync(videoDir, { recursive: true });

  console.log('🚀 Launching Visible Google Chrome for Admin Features Video...');
  const browser = await chromium.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: false,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1920,1080', '--window-position=0,0']
  });

  const context = await browser.newContext({
    recordVideo: {
      dir: videoDir,
      size: { width: 1920, height: 1080 }
    },
    viewport: { width: 1920, height: 1080 }
  });

  const page = await context.newPage();

  // =========================================================================
  // SETUP: Authenticate as Administrator
  // =========================================================================
  console.log('🔑 Authenticating as Administrator...');
  await page.goto('http://localhost:5173/login');
  await ensureVirtualCursor(page);
  await page.waitForTimeout(1500);

  try {
    await typeHumanLike(page, 'input#identifier, input[name="identifier"], input[type="text"]', 'admin');
    await page.waitForTimeout(400);
    await typeHumanLike(page, 'input#password, input[name="password"], input[type="password"]', 'leetaka!1234568');
    await page.waitForTimeout(600);
    await humanClick(page, 'button[type="submit"]');
    await page.waitForTimeout(2500);
  } catch (e) {}

  // =========================================================================
  // PART 1: Admin Overview & Interactive Recharts Analytics
  // =========================================================================
  console.log('🎬 Part 1: Admin Overview & Recharts Analytics');
  await page.goto('http://localhost:5173/admin');
  await ensureVirtualCursor(page);
  await page.waitForTimeout(3000);

  await showPresenterBadge(
    page,
    'Admin Overview & Visual Analytics',
    'Epidemiological Surveillance Dashboard powered by Recharts (30-day outbreak trends & distributions)',
    'Welcome to the Admin Portal. Here, agronomists monitor field outbreaks, confidence tiers, and system health.'
  );
  await page.waitForTimeout(3000);

  // Hover over top metric cards
  await humanHover(page, 'div:has-text("Total Diseases"), div:has-text("20")', 3000);
  await humanHover(page, 'div:has-text("Total Symptoms"), div:has-text("62")', 3000);

  // Toggle Recharts Outbreak Trend filters: 14d, then 30d
  await humanClick(page, 'button:has-text("14d")');
  await page.waitForTimeout(3000);
  await humanClick(page, 'button:has-text("30d")');
  await page.waitForTimeout(3000);

  // Hover over the trend curve to show glassmorphic tooltip
  await humanHover(page, 'div[class*="recharts"]', 4000);

  // Scroll down to Symptom Distribution Donut & Ranked Horizontal Bar charts
  await humanScroll(page, 550, 3000);
  await page.waitForTimeout(4000);
  await humanHover(page, 'div:has-text("Symptom Distribution"), div:has-text("Most Observed")', 4000);

  // Scroll down to Confidence Distribution and Health Gauges
  await humanScroll(page, 1050, 3000);
  await page.waitForTimeout(5000);
  await humanHover(page, 'div:has-text("Diagnostic Confidence"), div:has-text("Quality")', 3500);

  // Scroll smoothly back to top
  await humanScroll(page, 0, 2500);
  await page.waitForTimeout(2500);

  // =========================================================================
  // PART 2: Disease Knowledge Base Management
  // =========================================================================
  console.log('🎬 Part 2: Disease Knowledge Base Catalog');
  try {
    await humanClick(page, 'a[href="/admin/diseases"]');
    await page.waitForTimeout(1500);
  } catch (e) {}
  if (!page.url().includes('/admin/diseases')) {
    await page.goto('http://localhost:5173/admin/diseases');
    await page.waitForTimeout(3000);
  }
  await ensureVirtualCursor(page);

  await showPresenterBadge(
    page,
    'Disease Knowledge Base Catalog',
    'Master Repository of 20 Sunflower Diseases • Search, Pathogen Filters & Publish Status Toggles',
    'Admins have complete control over disease taxonomy, publication state, and clinical metadata.'
  );
  await page.waitForTimeout(3000);

  // Use search input safely
  try {
    const searchInput = await page.$('input[type="search"], input[placeholder*="Search"]');
    if (searchInput) {
      await typeHumanLike(page, 'input[type="search"], input[placeholder*="Search"]', 'Rust');
      await page.waitForTimeout(3000);
      await searchInput.fill('');
      await page.waitForTimeout(1500);
    }
  } catch (e) {}

  // Scroll down the disease table
  await humanScroll(page, 450, 3000);
  await page.waitForTimeout(4000);
  await humanScroll(page, 850, 3000);
  await page.waitForTimeout(4000);
  await humanScroll(page, 0, 2500);
  await page.waitForTimeout(2000);

  // =========================================================================
  // PART 3: Disease Creation Form Wizard
  // =========================================================================
  console.log('🎬 Part 3: Disease Creation Wizard');
  try {
    await humanClick(page, 'a[href="/admin/diseases/new"], button:has-text("New Disease")');
    await page.waitForTimeout(1500);
  } catch (e) {}
  if (!page.url().includes('/admin/diseases/new')) {
    await page.goto('http://localhost:5173/admin/diseases/new');
    await page.waitForTimeout(3000);
  }
  await ensureVirtualCursor(page);

  await showPresenterBadge(
    page,
    'Disease Creation Wizard',
    'Create New Pathology Records • Scientific Taxonomy, Pathogen Groupings & Risk Classifications',
    'New pathogens can be registered with scientific names, causal organisms, and environmental triggers.'
  );
  await page.waitForTimeout(3000);

  await humanScroll(page, 350, 2500);
  await page.waitForTimeout(3000);
  await humanScroll(page, 0, 2000);
  await page.waitForTimeout(2000);

  // =========================================================================
  // PART 4: Deep Disease Knowledge Editor (Symptoms, Weights & FRAC Codes)
  // =========================================================================
  console.log('🎬 Part 4: Deep Disease Knowledge Editor');
  await page.goto('http://localhost:5173/admin/diseases/sunflower-rust');
  await page.waitForTimeout(3500);
  await ensureVirtualCursor(page);

  await showPresenterBadge(
    page,
    'Deep Disease Knowledge Editor',
    'Sunflower Rust Clinical Configuration • Symptom Weights, Pathognomonic Markers & FRAC Protocols',
    'Here agronomists calibrate Bayesian symptom weights and designate pathognomonic hallmarks.'
  );
  await page.waitForTimeout(3000);

  // Scroll through Tab 1: Symptoms Association & Weights
  await humanScroll(page, 400, 3000);
  await page.waitForTimeout(4000);
  await humanHover(page, 'div:has-text("Pathognomonic"), span:has-text("Weight"), input[type="range"]', 3500);
  await humanScroll(page, 800, 3000);
  await page.waitForTimeout(4000);
  await humanScroll(page, 0, 2500);
  await page.waitForTimeout(2000);

  // Switch to Tab 2: Content & Biology
  const contentTab = await humanClick(page, 'button:has-text("Content"), button:has-text("Information")');
  if (contentTab) {
    await page.waitForTimeout(3000);
    await showPresenterBadge(
      page,
      'Clinical Etiology & FRAC Management',
      'Causal Biology, FRAC Chemical Mode-of-Action Rotation, Organic Biocontrols & Cultural Prevention',
      'Admins configure chemical resistance warnings, recommended spray timings, and organic alternatives.'
    );
    await humanScroll(page, 450, 3000);
    await page.waitForTimeout(4500);
    await humanScroll(page, 0, 2500);
    await page.waitForTimeout(2000);
  }

  // Switch to Tab 3: Media & Clinical Photography
  const mediaTab = await humanClick(page, 'button:has-text("Media"), button:has-text("Photos"), button:has-text("Images")');
  if (mediaTab) {
    await page.waitForTimeout(3000);
    await showPresenterBadge(
      page,
      'Clinical Photography & Media Gallery',
      'High-Resolution Leaf, Stem, and Head Lesion Photography for Farmer Diagnostic Matching',
      'Field photographs are managed here, powering both visual identification and vision AI matching.'
    );
    await humanScroll(page, 350, 2500);
    await page.waitForTimeout(3500);
    await humanScroll(page, 0, 2000);
    await page.waitForTimeout(2000);
  }

  // =========================================================================
  // PART 5: Centralized Botanical Symptom Catalog
  // =========================================================================
  console.log('🎬 Part 5: Centralized Botanical Symptom Catalog');
  try {
    await humanClick(page, 'a[href="/admin/symptoms"]');
    await page.waitForTimeout(1500);
  } catch (e) {}
  if (!page.url().includes('/admin/symptoms')) {
    await page.goto('http://localhost:5173/admin/symptoms');
    await page.waitForTimeout(3000);
  }
  await ensureVirtualCursor(page);

  await showPresenterBadge(
    page,
    'Centralized Botanical Symptom Catalog',
    '62 Standardized Indicators Categorized Across 5 Plant Zones (Leaves, Stems, Heads, Roots, Plant)',
    'Admins curate symptom codes and localized descriptions in English and native Khmer.'
  );
  await page.waitForTimeout(3000);

  // Filter by category
  await humanScroll(page, 350, 3000);
  await page.waitForTimeout(3500);
  await humanScroll(page, 750, 3000);
  await page.waitForTimeout(3500);
  await humanScroll(page, 0, 2500);
  await page.waitForTimeout(2000);

  // Open "Add Symptom" Modal
  const addSymptomBtn = await humanClick(page, 'button:has-text("Add"), button:has-text("New Symptom"), button:has(svg.lucide-plus)');
  if (addSymptomBtn) {
    await page.waitForTimeout(3000);
    await showPresenterBadge(
      page,
      'New Botanical Symptom Registration',
      'Bilingual Label Definition (English / Khmer) • Category Mapping & Standardized Symptom Code',
      'Every symptom is registered with bilingual definitions to ensure 100% field accessibility.'
    );
    await page.waitForTimeout(5000);

    // Close modal
    await humanClick(page, 'button[aria-label="Close"], button:has-text("Cancel"), button:has-text("✕")');
    await page.waitForTimeout(2000);
  }

  // =========================================================================
  // PART 6: Diagnostic Rulesets & Bayesian Tuning
  // =========================================================================
  console.log('🎬 Part 6: Diagnostic Rulesets & Bayesian Tuning');
  try {
    await humanClick(page, 'a[href="/admin/rulesets"]');
    await page.waitForTimeout(1500);
  } catch (e) {}
  if (!page.url().includes('/admin/rulesets')) {
    await page.goto('http://localhost:5173/admin/rulesets');
    await page.waitForTimeout(3000);
  }
  await ensureVirtualCursor(page);

  await showPresenterBadge(
    page,
    'Diagnostic Rulesets & Bayesian Engine',
    'Calibrate Sensitivity, Specificity, Absence Penalty Factors & Diagnostic Thresholds',
    'Fine-tune the mathematical engine that drives real-time disease probability ranking.'
  );
  await page.waitForTimeout(3000);

  await humanScroll(page, 350, 3000);
  await page.waitForTimeout(4000);
  await humanHover(page, 'div:has-text("Penalty"), div:has-text("Weight"), div:has-text("Sensitivity")', 3500);
  await humanScroll(page, 0, 2500);
  await page.waitForTimeout(2500);

  // =========================================================================
  // PART 7: Farmer Field Feedback Moderation Queue
  // =========================================================================
  console.log('🎬 Part 7: Farmer Field Feedback Queue');
  try {
    await humanClick(page, 'a[href="/admin/feedback"]');
    await page.waitForTimeout(1500);
  } catch (e) {}
  if (!page.url().includes('/admin/feedback')) {
    await page.goto('http://localhost:5173/admin/feedback');
    await page.waitForTimeout(3000);
  }
  await ensureVirtualCursor(page);

  await showPresenterBadge(
    page,
    'Farmer Feedback Moderation Queue',
    'Triage Field Outbreak Inquiries, Unclassified Symptoms & Treatment Verification Reports',
    'Review submissions from farmers, track resolution status, and identify emerging pathogen variants.'
  );
  await page.waitForTimeout(3000);

  await humanScroll(page, 350, 3000);
  await page.waitForTimeout(4000);
  await humanScroll(page, 0, 2500);
  await page.waitForTimeout(2500);

  // =========================================================================
  // PART 8: User Accounts & Role Management
  // =========================================================================
  console.log('🎬 Part 8: User Accounts & Role Management');
  try {
    await humanClick(page, 'a[href="/admin/users"]');
    await page.waitForTimeout(1500);
  } catch (e) {}
  if (!page.url().includes('/admin/users')) {
    await page.goto('http://localhost:5173/admin/users');
    await page.waitForTimeout(3000);
  }
  await ensureVirtualCursor(page);

  await showPresenterBadge(
    page,
    'User Account Administration',
    'Manage User Accounts, Account Status (Active/Suspended) & Assign System Privileges',
    'Admins manage growers, agronomists, and researchers, promoting trusted users to expert roles.'
  );
  await page.waitForTimeout(3000);

  await humanScroll(page, 350, 3000);
  await page.waitForTimeout(3500);
  await humanHover(page, 'select, button[class*="status"]', 3000);
  await humanScroll(page, 0, 2500);
  await page.waitForTimeout(2500);

  // =========================================================================
  // PART 9: Role-Based Access Control (RBAC) Matrix
  // =========================================================================
  console.log('🎬 Part 9: Role-Based Access Control (RBAC)');
  try {
    await humanClick(page, 'a[href="/admin/roles"]');
    await page.waitForTimeout(1500);
  } catch (e) {}
  if (!page.url().includes('/admin/roles')) {
    await page.goto('http://localhost:5173/admin/roles');
    await page.waitForTimeout(3000);
  }
  await ensureVirtualCursor(page);

  await showPresenterBadge(
    page,
    'Role-Based Access Control (RBAC) Matrix',
    'Enterprise Security Permissions • Administrator, Agronomist & Grower Capability Matrix',
    'Every capability—from publishing diseases to reviewing feedback—is governed by strict permissions.'
  );
  await page.waitForTimeout(3000);

  await humanScroll(page, 400, 3000);
  await page.waitForTimeout(4000);
  await humanHover(page, 'table, input[type="checkbox"]', 3500);
  await humanScroll(page, 800, 3000);
  await page.waitForTimeout(4000);
  await humanScroll(page, 0, 2500);
  await page.waitForTimeout(2500);

  // =========================================================================
  // PART 10: Admin Conversational AI Assistant & Database Commands
  // =========================================================================
  console.log('🎬 Part 10: Admin Conversational AI Assistant');
  await showPresenterBadge(
    page,
    'Admin AI Assistant Agent',
    'AI Assistant in Admin Mode • Execute Conversational Database Queries & Management Commands',
    'In Admin mode, the AI assistant gains database powers to inspect and navigate system resources.'
  );

  // Click floating AI Assistant bubble in bottom right
  try {
    const aiButton = await page.$('button[aria-label="Open AI Assistant"]');
    if (aiButton) {
      await humanClick(page, 'button[aria-label="Open AI Assistant"]');
      await page.waitForTimeout(3000);
      await ensureVirtualCursor(page);

      const chatInput = await page.$('input[placeholder*="Ask about diseases"], input[placeholder*="check symptoms"]');
      if (chatInput) {
        await typeHumanLike(page, 'input[placeholder*="Ask about diseases"], input[placeholder*="check symptoms"]', 'List all diseases in the database');
        await page.waitForTimeout(800);
        await page.keyboard.press('Enter');
        await page.waitForTimeout(12000);
      }
    }
  } catch (e) {}

  await page.waitForTimeout(3000);

  // =========================================================================
  // PART 11: Summary & Conclusion
  // =========================================================================
  console.log('🎬 Part 11: Summary & Conclusion');
  await page.goto('http://localhost:5173/admin');
  await page.waitForTimeout(3000);
  await ensureVirtualCursor(page);

  await showPresenterBadge(
    page,
    'Complete Administrative Power',
    'Sunflower Pathology Expert System • Complete Epidemiological & Agronomic Command Center',
    'Thank you for watching the Admin Demonstration of the Sunflower Pathology Expert System!'
  );
  await page.waitForTimeout(4000);

  await humanScroll(page, 350, 3000);
  await page.waitForTimeout(4000);
  await humanScroll(page, 0, 2500);
  await page.waitForTimeout(4000);

  // =========================================================================
  // FINALIZATION: Save Video & Transcode to MP4
  // =========================================================================
  console.log('💾 Finalizing video stream...');
  const recordedVideo = page.video();
  await context.close();

  if (recordedVideo) {
    try {
      if (!fs.existsSync(videoDir)) fs.mkdirSync(videoDir, { recursive: true });
      const finalWebm = path.resolve(videoDir, 'admin_features_demo.webm');
      await recordedVideo.saveAs(finalWebm);
      console.log(`✅ Saved WebM demo to: ${finalWebm}`);

      const finalMp4 = path.resolve(videoDir, 'admin_features_demo.mp4');
      console.log('🎞️ Transcoding to MP4 for maximum compatibility...');
      execSync(`/opt/homebrew/bin/ffmpeg -y -i "${finalWebm}" -c:v libx264 -crf 20 -preset fast "${finalMp4}"`, { stdio: 'inherit' });
      console.log(`🎉 MP4 Video successfully generated at: ${finalMp4}`);
    } catch (err) {
      console.log('Video post-processing note:', err.message);
    }
  }

  await browser.close();
  console.log('🎉 Admin Features Video Recording Finished Successfully!');
})();
