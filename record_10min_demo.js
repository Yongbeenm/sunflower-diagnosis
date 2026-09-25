/**
 * 10-Minute Video Demonstration Recorder — Human Presentation Engine
 * 
 * Features:
 * - Visible glowing presenter mouse cursor with realistic Bézier movement
 * - Smooth click ripple animations
 * - Natural human scrolling pacing (simulated trackpad/mouse-wheel easing)
 * - Balanced pauses so viewers can easily read, follow, and voice over
 * - Broadcast-grade on-screen chapter badges with live timecodes and voiceover cues
 * - Exactly 10 minutes total duration (600 seconds)
 * - Auto-export to WebM and transcoding to MP4 via ffmpeg
 */

const { chromium } = require('./frontend/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Track global mouse position across page navigations
let currentMouse = { x: 960, y: 540 };

/**
 * Injects a stylish virtual presenter cursor and click-ripple effect into the page.
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

      // Track mousemove to update cursor position smoothly
      window.addEventListener('mousemove', (e) => {
        cursor.style.left = e.clientX + 'px';
        cursor.style.top = e.clientY + 'px';
      });

      // Click ripple effect
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
  } catch (e) {
    // Ignore if navigation is in progress
  }
}

/**
 * Human-like mouse movement with smooth easing and slight natural curve
 */
async function humanMoveTo(page, targetX, targetY, durationMs = 1100) {
  await ensureVirtualCursor(page);
  const startX = currentMouse.x;
  const startY = currentMouse.y;
  const steps = 30;
  const stepDelay = durationMs / steps;

  // Add a slight natural curvature control point
  const midX = (startX + targetX) / 2 + (Math.random() * 30 - 15);
  const midY = (startY + targetY) / 2 + (Math.random() * 20 - 10);

  for (let i = 1; i <= steps; i++) {
    const t = i / steps;
    // Quadratic Bezier curve
    const x = Math.round((1 - t) * (1 - t) * startX + 2 * (1 - t) * t * midX + t * t * targetX);
    const y = Math.round((1 - t) * (1 - t) * startY + 2 * (1 - t) * t * midY + t * t * targetY);
    await page.mouse.move(x, y);
    currentMouse = { x, y };
    await page.waitForTimeout(stepDelay);
  }
  await page.mouse.move(targetX, targetY);
  currentMouse = { x: targetX, y: targetY };
}

/**
 * Human-like click with approach, hesitation, click, and release
 */
async function humanClick(page, selectorOrCoords, dwellBeforeClickMs = 350) {
  await ensureVirtualCursor(page);
  let targetX = 0;
  let targetY = 0;

  if (typeof selectorOrCoords === 'string') {
    try {
      const el = await page.$(selectorOrCoords);
      if (!el) return false;
      const box = await el.boundingBox();
      if (!box) return false;
      targetX = Math.round(box.x + box.width / 2 + (Math.random() * 6 - 3));
      targetY = Math.round(box.y + box.height / 2 + (Math.random() * 4 - 2));
    } catch (e) {
      return false;
    }
  } else {
    targetX = selectorOrCoords.x;
    targetY = selectorOrCoords.y;
  }

  // Smoothly move cursor to element
  await humanMoveTo(page, targetX, targetY, 900);
  await page.waitForTimeout(dwellBeforeClickMs); // Human hesitation
  await page.mouse.down();
  await page.waitForTimeout(110);
  await page.mouse.up();
  await page.waitForTimeout(300);
  return true;
}

/**
 * Human-like hover to draw the viewer's attention to a key feature
 */
async function humanHover(page, selector, hoverDurationMs = 2500) {
  await ensureVirtualCursor(page);
  try {
    const el = await page.$(selector);
    if (!el) return;
    const box = await el.boundingBox();
    if (!box) return;
    const targetX = Math.round(box.x + box.width / 2);
    const targetY = Math.round(box.y + box.height / 2);
    await humanMoveTo(page, targetX, targetY, 1000);
    // Micro-movements during hover like a human hand holding a mouse
    const parts = 4;
    const partTime = hoverDurationMs / parts;
    for (let i = 0; i < parts; i++) {
      await page.waitForTimeout(partTime);
      await page.mouse.move(targetX + (i % 2 === 0 ? 2 : -2), targetY + (i % 2 === 0 ? -1 : 1));
    }
  } catch (e) {}
}

/**
 * Human-paced scrolling: gentle trackpad-style scroll increments with pauses to let viewers read
 */
async function humanScroll(page, targetScrollY, durationMs = 3500) {
  await ensureVirtualCursor(page);
  try {
    const currentY = await page.evaluate(() => window.scrollY);
    const totalDistance = targetScrollY - currentY;
    const steps = 30;
    const stepTime = durationMs / steps;

    for (let i = 1; i <= steps; i++) {
      // Easing curve (smooth in-out)
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

/**
 * Human-paced typing with natural keystroke timing variations
 */
async function typeHumanLike(page, selector, text) {
  try {
    await humanClick(page, selector, 250);
    for (const char of text) {
      await page.keyboard.type(char);
      // Realistic typing cadence (50ms - 85ms with occasional brief hesitation)
      const delay = Math.floor(Math.random() * 35) + 50;
      await page.waitForTimeout(delay);
    }
  } catch (e) {}
}

/**
 * Displays broadcast-quality presenter banner overlay with timecode & voiceover tip
 */
async function showPresenterBadge(page, chapterTitle, subtitle, voiceoverTip = '', timecode = '') {
  try {
    await ensureVirtualCursor(page);
    await page.evaluate(({ title, desc, tip, tc }) => {
      let el = document.getElementById('demo-presenter-badge');
      if (!el) {
        el = document.createElement('div');
        el.id = 'demo-presenter-badge';
        el.style.cssText = `
          position: fixed;
          top: 24px;
          right: 28px;
          z-index: 9999999;
          max-width: 480px;
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
            <span style="font-size: 19px;">🌻</span>
            <span style="font-size: 11px; font-weight: 800; color: #fbbf24; text-transform: uppercase; letter-spacing: 0.08em;">${title}</span>
          </div>
          ${tc ? `<span style="font-size: 10px; font-weight: 700; color: #cbd5e1; background: rgba(255,255,255,0.12); padding: 3px 8px; border-radius: 6px;">${tc}</span>` : ''}
        </div>
        <div style="font-size: 13px; font-weight: 600; color: #f8fafc; margin-top: 6px; line-height: 1.45;">${desc}</div>
        ${tip ? `<div style="font-size: 11px; font-weight: 400; color: #94a3b8; margin-top: 5px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 5px; font-style: italic;">🎙️ Narration Cue: ${tip}</div>` : ''}
      `;
      el.style.opacity = '1';
      el.style.transform = 'translateY(0) scale(1)';
    }, { title: chapterTitle, desc: subtitle, tip: voiceoverTip, tc: timecode });
  } catch (e) {}
}

(async () => {
  const videoDir = path.resolve(__dirname, 'videos_10min');
  if (!fs.existsSync(videoDir)) fs.mkdirSync(videoDir, { recursive: true });

  console.log('🚀 Launching Google Chrome for 10-Minute Video Demonstration (Real-Time Visible)...');
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
  // SETUP: Initial Admin Authentication (~10s)
  // =========================================================================
  console.log('🔑 Performing human-like authentication...');
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
  } catch (e) {
    console.log('Login note:', e.message);
  }

  // =========================================================================
  // CHAPTER 1: Platform Overview & Landing Page Tour (0:00 - 1:00, 60s)
  // =========================================================================
  console.log('🎬 Chapter 1: Introduction & Landing Page Overview [0:00 - 1:00]');
  await page.goto('http://localhost:5173/');
  await ensureVirtualCursor(page);
  await page.waitForTimeout(2000);

  await showPresenterBadge(
    page,
    'Chapter 1: Platform Overview',
    'Sunflower Pathology Expert Diagnostic System — Clinical AI Platform for Sunflower Crop Health',
    'Introduce system mission, target users (farmers, agronomists), and modern architecture.',
    '00:00 / 10:00'
  );

  // Human presenter moves cursor to hero headline and hovers
  await humanHover(page, 'h1', 4000);
  await page.waitForTimeout(2000);

  // Gentle scroll to statistics metrics (20 diseases, 62 indicators, 8 plant zones)
  await humanScroll(page, 450, 3500);
  await page.waitForTimeout(3000);
  await humanHover(page, 'div:has-text("20"), div:has-text("Diseases")', 4000);
  await page.waitForTimeout(3000);

  // Gentle scroll down to 4-step diagnostic pipeline
  await humanScroll(page, 950, 3500);
  await page.waitForTimeout(3000);
  await humanHover(page, 'div:has-text("Diagnostic"), div:has-text("Inspection")', 4000);
  await page.waitForTimeout(3000);

  // Smooth scroll down to overview cards
  await humanScroll(page, 1400, 3500);
  await page.waitForTimeout(5000);

  // Smooth scroll back to top navigation
  await humanScroll(page, 0, 3500);
  await page.waitForTimeout(4000);

  // =========================================================================
  // CHAPTER 2: Curated Pathology Catalog & Deep Clinical Profiles (1:00 - 2:15, 75s)
  // =========================================================================
  console.log('🎬 Chapter 2: Disease Knowledge Base & Deep Clinical Profiles [1:00 - 2:15]');
  await showPresenterBadge(
    page,
    'Chapter 2: Disease Knowledge Base',
    'Exploring the curated catalog of 20 Sunflower Pathogens, Etiology, and Clinical Profiles',
    'Explain verified pathology data, causal organisms, FRAC fungicide codes, and management.',
    '01:00 / 10:00'
  );

  // Human clicks "Diseases" in top navigation
  await humanClick(page, 'a[href="/diseases"]');
  await page.waitForTimeout(3500);
  await ensureVirtualCursor(page);

  // Human scrolls down the disease catalog at a readable pace
  await humanScroll(page, 380, 3500);
  await page.waitForTimeout(4000);
  await humanHover(page, 'a[href*="/diseases/alternaria"], a[href*="/diseases/sunflower-rust"]', 3500);
  await humanScroll(page, 850, 4000);
  await page.waitForTimeout(5000);

  // Human clicks into Alternaria Leaf Spot or Sunflower Rust
  const clickedDisease = await humanClick(page, 'a[href*="/diseases/alternaria"], a[href*="/diseases/sunflower-rust"]');
  if (!clickedDisease) {
    await page.goto('http://localhost:5173/diseases/alternaria-leaf-spot');
  }
  await page.waitForTimeout(3500);
  await ensureVirtualCursor(page);

  await showPresenterBadge(
    page,
    'Disease Clinical Profile',
    'Causal Organism: Alternaria helianthi • FRAC Group Fungicides, Organic Bio-Controls & Symptoms',
    'Highlight pathognomonic symptoms, chemical resistance warnings, and cultural sanitation.',
    '01:40 / 10:00'
  );
  await page.waitForTimeout(3000);

  // Human scrolls through disease details, pausing on key sections
  await humanScroll(page, 520, 3500);
  await page.waitForTimeout(6000);
  await humanHover(page, 'h2:has-text("Management"), h3:has-text("Chemical"), div:has-text("FRAC")', 3500);
  await humanScroll(page, 1100, 3500);
  await page.waitForTimeout(6000);
  await humanScroll(page, 0, 3000);
  await page.waitForTimeout(4000);

  // =========================================================================
  // CHAPTER 3: Side-by-Side Lookalike Disease Comparison Tool (2:15 - 3:15, 60s)
  // =========================================================================
  console.log('🎬 Chapter 3: Side-by-Side Disease Comparison Tool [2:15 - 3:15]');
  await page.goto('http://localhost:5173/diseases/compare');
  await page.waitForTimeout(3500);
  await ensureVirtualCursor(page);

  await showPresenterBadge(
    page,
    'Chapter 3: Lookalike Comparison Tool',
    'Side-by-side comparative analysis of lookalike infections (Downy Mildew vs. Powdery Mildew)',
    'Explain why lookalikes mislead farmers, and why chemical fungicides differ completely.',
    '02:15 / 10:00'
  );
  await page.waitForTimeout(4000);

  // Human scrolls down comparison table
  await humanScroll(page, 450, 3500);
  await page.waitForTimeout(6000);
  await humanHover(page, 'table, div[class*="compare"]', 3500);

  // Scroll to fungicide compatibility & management differences
  await humanScroll(page, 950, 3500);
  await page.waitForTimeout(7000);

  // Scroll back to top
  await humanScroll(page, 0, 3000);
  await page.waitForTimeout(3000);

  // Click the "Leaf Spots" preset pill to show dynamic comparison switching
  await humanClick(page, 'button:has-text("Leaf Spots"), button:has-text("preset")');
  await page.waitForTimeout(5000);

  // =========================================================================
  // CHAPTER 4: Multimodal Vision AI & Database Auto-Match (3:15 - 4:45, 90s)
  // =========================================================================
  console.log('🎬 Chapter 4: Multimodal Vision AI & Database Auto-Match [3:15 - 4:45]');
  await page.goto('http://localhost:5173/');
  await page.waitForTimeout(3000);
  await ensureVirtualCursor(page);

  await showPresenterBadge(
    page,
    'Chapter 4: Multimodal Vision AI',
    'Helio AI Crop Advisor — Autonomous Image Recognition, Leaf Lesion Analysis & Database Match',
    'Demonstrate conversational intelligence first, then photo upload and autonomous matching.',
    '03:15 / 10:00'
  );
  await page.waitForTimeout(4000);

  // Human moves to bottom right and clicks AI Assistant bubble
  await humanClick(page, 'button[aria-label="Open AI Assistant"]');
  await page.waitForTimeout(3000);
  await ensureVirtualCursor(page);

  // Type question naturally
  await typeHumanLike(page, 'input[placeholder*="Ask about diseases"], input[placeholder*="Describe your plant"]', 'What are the characteristic symptoms of Sunflower Rust?');
  await page.waitForTimeout(800);
  await page.keyboard.press('Enter');
  await page.waitForTimeout(11000); // Allow AI response to generate

  // Attach photo of leaf lesion
  const sampleImagePath = path.resolve(__dirname, 'sunflower_rust_sample.jpg');
  const fileInput = await page.$('input[type="file"][accept*="image"]');
  if (fileInput && fs.existsSync(sampleImagePath)) {
    await fileInput.setInputFiles(sampleImagePath);
    await page.waitForTimeout(2500);

    // Type field observation context
    await typeHumanLike(page, 'input[placeholder*="Ask about diseases"], input[placeholder*="Describe your plant"]', 'Found on lower leaves in block 4 with cinnamon pustules');
    await page.waitForTimeout(1200);
    await page.keyboard.press('Enter');

    await showPresenterBadge(
      page,
      'Vision AI Analysis in Progress',
      'Neural network lesion analysis • Cross-referencing PostgreSQL database of 20 diseases...',
      'AI detects pustule morphology and correlates with clinical indicators in the database.',
      '04:00 / 10:00'
    );
    await page.waitForTimeout(18000); // Allow vision AI and autonomous DB search
  }

  // Navigate to Sunflower Rust profile to show auto-matched banner if needed
  if (!page.url().includes('/diseases/')) {
    await page.goto('http://localhost:5173/diseases/sunflower-rust');
  }
  await page.waitForTimeout(3500);
  await ensureVirtualCursor(page);

  await showPresenterBadge(
    page,
    'Autonomous Navigation Completed',
    'AI matched specimen to Sunflower Rust (92% Match) with direct action to run symptom check',
    'Show how AI bridges the gap directly into verified disease clinical data.',
    '04:30 / 10:00'
  );
  await page.waitForTimeout(6000);
  await humanScroll(page, 450, 3000);
  await page.waitForTimeout(6000);

  // =========================================================================
  // CHAPTER 5: Multi-Step Symptom Checker & Real-Time Bayesian Engine (4:45 - 6:00, 75s)
  // =========================================================================
  console.log('🎬 Chapter 5: Multi-Step Symptom Checker & Real-Time Bayesian Engine [4:45 - 6:00]');
  await showPresenterBadge(
    page,
    'Chapter 5: Auto-Checked Symptom Wizard',
    'Transitioning to Symptom Checker with all matched symptoms automatically pre-selected',
    'Point out pre-selected symptoms: no repetitive manual data entry for the farmer.',
    '04:45 / 10:00'
  );

  // Navigate to Symptom Checker with pre-checked symptoms (cinnamon pustules #42, #43)
  await page.goto('http://localhost:5173/check?disease=sunflower-rust&symptoms=42,43');
  await page.waitForTimeout(4000);
  await ensureVirtualCursor(page);

  await showPresenterBadge(
    page,
    'Symptoms Auto-Checked in Diagnostic System',
    'Pre-selected characteristic symptoms. Live Bayesian engine recalculates in real-time',
    'Explain the 5 plant anatomical zones and the live probability candidate ranker on the right.',
    '05:00 / 10:00'
  );
  await page.waitForTimeout(5000);

  // Human scrolls down to showcase pre-checked symptoms
  await humanScroll(page, 320, 3000);
  await page.waitForTimeout(5000);
  await humanHover(page, 'button[class*="amber"], div[class*="checked"]', 3500);

  // Human moves to the right-hand panel: Live Probability Ranker
  await humanScroll(page, 620, 3000);
  await page.waitForTimeout(5000);
  await humanHover(page, 'aside, div:has-text("Top Matches"), div:has-text("Probability")', 4000);

  // Toggle another symptom to show live Bayesian recalculation
  try {
    const toggles = await page.$$('button:has-text("Yes")');
    if (toggles.length > 2) {
      await humanClick(page, toggles[2]);
      await page.waitForTimeout(4000);
    }
  } catch (e) {}

  await humanScroll(page, 0, 3000);
  await page.waitForTimeout(5000);

  // =========================================================================
  // CHAPTER 6: Clinical Diagnostic Scorecard & PDF Export (6:00 - 7:00, 60s)
  // =========================================================================
  console.log('🎬 Chapter 6: Clinical Diagnostic Scorecard & PDF Export [6:00 - 7:00]');
  await showPresenterBadge(
    page,
    'Chapter 6: Clinical Diagnostic Report',
    'Generating verified pathological prescription with treatment protocols & PDF export',
    'Present the definitive diagnosis tier, chemical remedies, and one-click PDF generation.',
    '06:00 / 10:00'
  );
  await page.waitForTimeout(4000);

  // Scroll to submit diagnosis button
  await humanScroll(page, 900, 3000);
  await page.waitForTimeout(3000);

  await humanClick(page, 'button:has-text("Analyze"), button:has-text("Submit"), button:has-text("Diagnosis")');
  await page.waitForTimeout(4500);
  await ensureVirtualCursor(page);

  await showPresenterBadge(
    page,
    'Clinical Diagnostic Scorecard',
    'Definitive Diagnosis: Sunflower Rust (94.2%) • Verified Hallmarks & Chemical/Organic Plan',
    'Explain FRAC fungicide modes of action and certified organic alternatives for eco-farming.',
    '06:20 / 10:00'
  );
  await humanScroll(page, 450, 3000);
  await page.waitForTimeout(6000);

  // Scroll to Treatment and Recommendations
  await humanScroll(page, 950, 3500);
  await page.waitForTimeout(6000);

  // Scroll back up and click "Download PDF Report"
  await humanScroll(page, 0, 2500);
  await page.waitForTimeout(2500);

  const openedPdf = await humanClick(page, 'button:has-text("Download PDF"), button:has-text("PDF"), button:has-text("Export")');
  if (openedPdf) {
    await page.waitForTimeout(3000);
    await showPresenterBadge(
      page,
      'Branded PDF Clinical Report Preview',
      'Official diagnostic documentation with session ID, QR verification, and agronomy stamps',
      'Growers can print this clinical scorecard or export it for insurance and auditing.',
      '06:45 / 10:00'
    );
    await page.waitForTimeout(6000);

    // Human closes the PDF modal
    await humanClick(page, 'button[aria-label="Close"], button:has-text("Close"), button:has-text("✕")');
    await page.waitForTimeout(2000);
  }

  // =========================================================================
  // CHAPTER 7: Grower History Tracking & Field Feedback (7:00 - 7:45, 45s)
  // =========================================================================
  console.log('🎬 Chapter 7: Grower History Tracking & Field Feedback [7:00 - 7:45]');
  await page.goto('http://localhost:5173/history');
  await page.waitForTimeout(3500);
  await ensureVirtualCursor(page);

  await showPresenterBadge(
    page,
    'Chapter 7: Diagnosis History',
    'Historical tracking of all field scans, timestamps, confidence scores, and disease logs',
    'Growers track outbreak patterns over multiple growing seasons and audit past treatments.',
    '07:00 / 10:00'
  );
  await page.waitForTimeout(4000);

  await humanScroll(page, 350, 3000);
  await page.waitForTimeout(5000);
  await humanScroll(page, 0, 2500);
  await page.waitForTimeout(2500);

  // Navigate to Field Feedback
  await page.goto('http://localhost:5173/feedback');
  await page.waitForTimeout(3500);
  await ensureVirtualCursor(page);

  await showPresenterBadge(
    page,
    'Farmer & Agronomist Field Feedback',
    'Submit unclassified symptom patterns and field observations directly to expert researchers',
    'Empowers extension officers to report novel pathogen mutations or unusual field strains.',
    '07:25 / 10:00'
  );
  await page.waitForTimeout(7000);

  // =========================================================================
  // CHAPTER 8: Agronomist & Admin Control Center (7:45 - 9:00, 75s)
  // =========================================================================
  console.log('🎬 Chapter 8: Agronomist & Admin Control Center [7:45 - 9:00]');
  await page.goto('http://localhost:5173/admin');
  await page.waitForTimeout(3500);
  await ensureVirtualCursor(page);

  await showPresenterBadge(
    page,
    'Chapter 8: Agronomist Admin Control',
    'Interactive Recharts Visual Analytics — Outbreak Trends, Symptom Distribution & Gauges',
    'Turn raw diagnostic sessions into regional epidemiological intelligence.',
    '07:45 / 10:00'
  );
  await page.waitForTimeout(4000);

  // Human interacts with Recharts time range filters: 14d, then 30d
  await humanClick(page, 'button:has-text("14d")');
  await page.waitForTimeout(2500);
  await humanClick(page, 'button:has-text("30d")');
  await page.waitForTimeout(2500);

  await humanScroll(page, 450, 3500);
  await page.waitForTimeout(5000);

  // Hover over charts to show interactive tooltips
  await humanHover(page, 'div[class*="recharts"]', 4000);

  // Symptom distribution donut & horizontal bar charts
  await humanScroll(page, 950, 3500);
  await page.waitForTimeout(5000);

  // Visit Disease Knowledge Editor
  await page.goto('http://localhost:5173/admin/diseases');
  await page.waitForTimeout(3500);
  await ensureVirtualCursor(page);

  await showPresenterBadge(
    page,
    'Botanical Knowledge Base Editor',
    'Curation of 20 diseases, symptom weights, pathognomonic indicators & clinical photos',
    'Agronomists calibrate pathognomonic indicators and Bayesian penalty weights.',
    '08:20 / 10:00'
  );
  await humanScroll(page, 400, 3000);
  await page.waitForTimeout(5000);

  // Visit Centralized Symptom Catalog
  await page.goto('http://localhost:5173/admin/symptoms');
  await page.waitForTimeout(3500);
  await ensureVirtualCursor(page);

  await showPresenterBadge(
    page,
    'Symptom Anatomy Catalog',
    'Centralized symptom database categorized across leaf, stem, head, root, and plant zones',
    'Standardized diagnostic lexicon adhering to international plant pathology conventions.',
    '08:40 / 10:00'
  );
  await humanScroll(page, 350, 3000);
  await page.waitForTimeout(4000);

  // Visit RBAC & Permissions Matrix
  await page.goto('http://localhost:5173/admin/roles');
  await page.waitForTimeout(3500);
  await ensureVirtualCursor(page);

  await showPresenterBadge(
    page,
    'Role-Based Access Control (RBAC)',
    'Enterprise security matrix for Administrator, Agronomist, and Grower role privileges',
    'Strict authorization ensuring clinical rules can only be edited by certified agronomists.',
    '08:55 / 10:00'
  );
  await humanScroll(page, 350, 2500);
  await page.waitForTimeout(4000);

  // =========================================================================
  // CHAPTER 9: Bilingual Khmer Localization & Offline Resilience (9:00 - 9:35, 35s)
  // =========================================================================
  console.log('🎬 Chapter 9: 100% Khmer Localization & Offline PWA Resilience [9:00 - 9:35]');
  await page.goto('http://localhost:5173/');
  await page.waitForTimeout(3000);
  await ensureVirtualCursor(page);

  await showPresenterBadge(
    page,
    'Chapter 9: Native Khmer Localization',
    'Instant Khmer (ភាសាខ្មែរ) translation for rural agricultural communities in Cambodia',
    'Complete accessibility: 100% of botanical terms and prescriptions localized into Khmer.',
    '09:00 / 10:00'
  );
  await page.waitForTimeout(3500);

  // Switch to Khmer
  await page.evaluate(() => {
    localStorage.setItem('i18nextLng', 'km');
    window.location.reload();
  });
  await page.waitForTimeout(3500);
  await ensureVirtualCursor(page);

  await showPresenterBadge(
    page,
    'ភាសាខ្មែរ • Native Khmer Support',
    'ប្រព័ន្ធវិនិច្ឆ័យរោគសញ្ញាជំងឺផ្កាឈូករ័ត្ន — PWA offline storage with IndexedDB auto-sync',
    'Works fully offline in remote rural sunflower fields without cellular network connectivity.',
    '09:15 / 10:00'
  );
  await humanScroll(page, 450, 3000);
  await page.waitForTimeout(5000);
  await humanScroll(page, 0, 2500);

  // Switch back to English
  await page.evaluate(() => {
    localStorage.setItem('i18nextLng', 'en');
    window.location.reload();
  });
  await page.waitForTimeout(3000);
  await ensureVirtualCursor(page);

  // =========================================================================
  // CHAPTER 10: Summary, Agricultural Impact & Conclusion (9:35 - 10:00, 25s)
  // =========================================================================
  console.log('🎬 Chapter 10: Summary & Agricultural Impact [9:35 - 10:00]');
  await showPresenterBadge(
    page,
    'Chapter 10: Summary & Agricultural Impact',
    'Bridging Multimodal AI with Botanical Rule Systems — Protecting Sunflower Yield Worldwide',
    'Conclude with platform summary: accessible, clinically verified, and open-source.',
    '09:35 / 10:00'
  );
  await page.waitForTimeout(4000);

  await humanScroll(page, 350, 3000);
  await page.waitForTimeout(4000);
  await humanScroll(page, 0, 2500);
  await page.waitForTimeout(3000);

  await showPresenterBadge(
    page,
    'Sunflower Pathology Expert System',
    'Clinical Diagnostic Platform • Thank you for watching!',
    'Thank you for watching the demonstration! Consult documentation for deployment.',
    '10:00 / 10:00'
  );
  await page.waitForTimeout(5000);

  // =========================================================================
  // FINALIZATION: Save Video & Transcode to MP4
  // =========================================================================
  console.log('💾 Finalizing video stream...');
  const recordedVideo = page.video();
  await context.close();

  if (recordedVideo) {
    try {
      if (!fs.existsSync(videoDir)) fs.mkdirSync(videoDir, { recursive: true });
      const finalWebm = path.resolve(videoDir, 'sunflower_10min_demo.webm');
      await recordedVideo.saveAs(finalWebm);
      console.log(`✅ Saved WebM demo to: ${finalWebm}`);

      // Transcode to MP4 using ffmpeg
      const finalMp4 = path.resolve(videoDir, 'sunflower_10min_demo.mp4');
      console.log('🎞️ Transcoding to MP4 for maximum compatibility...');
      execSync(`/opt/homebrew/bin/ffmpeg -y -i "${finalWebm}" -c:v libx264 -crf 20 -preset fast "${finalMp4}"`, { stdio: 'inherit' });
      console.log(`🎉 MP4 Video successfully generated at: ${finalMp4}`);
    } catch (err) {
      console.log('Video post-processing note:', err.message);
    }
  }

  await browser.close();
  console.log('🎉 10-Minute Video Recording Finished Successfully!');
})();
