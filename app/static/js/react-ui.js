import React, {
  useDeferredValue,
  useEffect,
  useMemo,
  useRef,
  useState,
  startTransition,
} from 'https://esm.sh/react@18.3.1';
import { createRoot } from 'https://esm.sh/react-dom@18.3.1/client';
import htm from 'https://esm.sh/htm@3.1.1';

const html = htm.bind(React.createElement);

const COPY = {
  en: {
    home: {
      kickerAuthed: 'Crop intelligence workspace',
      kickerPublic: 'Sunflower disease intelligence',
      titleAuthed: 'Track field symptoms with a faster, clearer diagnostic dashboard.',
      titlePublic: 'A more visual sunflower diagnosis experience for growers and field teams.',
      subtitleAuthed:
        'Review recent checks, open disease reports quickly, and move from observation to action without digging through dense screens.',
      subtitlePublic:
        'Browse the disease library instantly, then sign in to run symptom checks with a cleaner and more guided flow.',
      primaryCta: 'Run symptom check',
      secondaryCta: 'Explore disease library',
      loginCta: 'Log in',
      registerCta: 'Create account',
      metrics: {
        today: 'Checks today',
        total: 'Total checks',
        library: 'Disease reports',
        pending: 'Needs review',
      },
      recentTitle: 'Recent activity',
      latestTitle: 'Latest diagnosis',
      latestEmpty: 'No diagnosis yet',
      latestEmptyBody: 'Start a symptom check to see your latest match and matched signals.',
      matchedTitle: 'Matched symptoms',
      openReport: 'Open report',
      selectedCount: 'symptoms selected',
      checkTime: 'Last updated',
      deltaUp: (value) => `+${value} vs last week`,
      deltaDown: (value) => `${value} vs last week`,
      deltaFlat: 'No change vs last week',
      recentEmpty: 'Your recent checks will appear here once you start diagnosing.',
      diseaseTitle: 'Featured disease reports',
      diseaseBody: 'Quick access to the disease references most users open after a symptom check.',
      roleLabel: 'Role',
    },
    library: {
      kicker: 'Reference library',
      title: 'Search sunflower disease reports without leaving the page.',
      subtitle:
        'Filter visually by disease name or symptom text, then jump straight into a full report.',
      searchPlaceholder: 'Search by disease name or symptom...',
      resultCount: (count) => `${count} report${count === 1 ? '' : 's'} visible`,
      diagnoseCta: 'Run symptom check',
      reportLabel: 'Report',
      openReport: 'Open report',
      emptyTitle: 'No disease reports match this search',
      emptyBody: 'Try a broader symptom keyword or clear the search field.',
    },
    diagnose: {
      kicker: 'Symptom workflow',
      title: 'Select observed symptoms with a calmer, guided interface.',
      subtitle:
        'Search, filter by plant area, and keep a live summary of everything selected before running the diagnosis.',
      searchPlaceholder: 'Search symptoms like wilting, stem lesions, root rot...',
      selectedOnly: 'Selected only',
      clearFilters: 'Clear filters',
      browseLibrary: 'Browse library',
      checkSymptoms: 'Check symptoms',
      reset: 'Reset',
      totalVisible: 'visible',
      selected: 'selected',
      allCategories: 'All categories',
      selectedSummary: 'Selected symptoms',
      selectedEmpty: 'Choose symptoms to build your diagnostic summary.',
      tipsTitle: 'How to get a stronger match',
      tipA: 'Choose only symptoms you can clearly observe.',
      tipB: 'Mix plant-part symptoms with pattern or environment clues.',
      tipC: 'If no result appears, submit feedback with a photo afterward.',
      noResults: 'No symptoms match these filters',
      noResultsBody: 'Try a broader keyword or switch off the selected-only filter.',
      progressLabel: 'Selection coverage',
      categoryLabel: 'Plant area',
      countShown: (count) => `${count} shown`,
      stickyTitle: 'Ready to diagnose',
      stickyBody:
        'Your current symptom list will be submitted to the expert system exactly as selected below.',
    },
  },
  km: {
    home: {
      kickerAuthed: 'ផ្ទាំងគ្រប់គ្រងវិភាគដំណាំ',
      kickerPublic: 'បណ្ណាល័យជំងឺផ្កាឈូករ័ត្ន',
      titleAuthed: 'តាមដានរោគសញ្ញាក្នុងចម្ការជាមួយផ្ទាំងវិនិច្ឆ័យដែលច្បាស់ និងលឿនជាងមុន។',
      titlePublic: 'បទពិសោធវិនិច្ឆ័យជំងឺផ្កាឈូករ័ត្នដែលទាន់សម័យសម្រាប់កសិករ និងក្រុមការងារវាល។',
      subtitleAuthed:
        'មើលការត្រួតពិនិត្យថ្មីៗ បើករបាយការណ៍ជំងឺបានលឿន និងបម្លែងការសង្កេតទៅជាសកម្មភាពដោយមិនចាំបាច់ស្វែងរកអេក្រង់ច្រើន។',
      subtitlePublic:
        'ស្វែងរកបណ្ណាល័យជំងឺបានភ្លាមៗ ហើយចូលប្រើគណនីដើម្បីធ្វើការពិនិត្យរោគសញ្ញាជាមួយលំហូរងាយស្រួលជាងមុន។',
      primaryCta: 'ចាប់ផ្តើមពិនិត្យរោគសញ្ញា',
      secondaryCta: 'មើលបណ្ណាល័យជំងឺ',
      loginCta: 'ចូលគណនី',
      registerCta: 'បង្កើតគណនី',
      metrics: {
        today: 'ការត្រួតពិនិត្យថ្ងៃនេះ',
        total: 'ការត្រួតពិនិត្យសរុប',
        library: 'របាយការណ៍ជំងឺ',
        pending: 'ត្រូវពិនិត្យបន្ថែម',
      },
      recentTitle: 'សកម្មភាពថ្មីៗ',
      latestTitle: 'លទ្ធផលវិនិច្ឆ័យចុងក្រោយ',
      latestEmpty: 'មិនទាន់មានលទ្ធផល',
      latestEmptyBody: 'ចាប់ផ្តើមពិនិត្យរោគសញ្ញា ដើម្បីឃើញលទ្ធផលដែលជិតស្និទ្ធបំផុត និងរោគសញ្ញាដែលត្រូវគ្នា។',
      matchedTitle: 'រោគសញ្ញាដែលត្រូវគ្នា',
      openReport: 'បើករបាយការណ៍',
      selectedCount: 'រោគសញ្ញាដែលបានជ្រើស',
      checkTime: 'ពេលធ្វើបច្ចុប្បន្នភាព',
      deltaUp: (value) => `+${value} ប្រៀបនឹងសប្ដាហ៍មុន`,
      deltaDown: (value) => `${value} ប្រៀបនឹងសប្ដាហ៍មុន`,
      deltaFlat: 'មិនមានការផ្លាស់ប្តូរប្រៀបនឹងសប្ដាហ៍មុន',
      recentEmpty: 'ប្រវត្តិការត្រួតពិនិត្យរបស់អ្នកនឹងបង្ហាញនៅទីនេះ បន្ទាប់ពីចាប់ផ្តើមវិនិច្ឆ័យ។',
      diseaseTitle: 'របាយការណ៍ជំងឺសំខាន់ៗ',
      diseaseBody: 'ចូលប្រើឯកសារជំងឺដែលអ្នកប្រើភាគច្រើនបើកបន្ទាប់ពីពិនិត្យរោគសញ្ញា។',
      roleLabel: 'តួនាទី',
    },
    library: {
      kicker: 'បណ្ណាល័យឯកសារ',
      title: 'ស្វែងរករបាយការណ៍ជំងឺផ្កាឈូករ័ត្នដោយមិនចាំបាច់ចាកចេញពីទំព័រ។',
      subtitle: 'តម្រៀបតាមឈ្មោះជំងឺ ឬអត្ថបទរោគសញ្ញា ហើយចូលទៅកាន់របាយការណ៍ពេញលេញភ្លាមៗ។',
      searchPlaceholder: 'ស្វែងរកតាមឈ្មោះជំងឺ ឬរោគសញ្ញា...',
      resultCount: (count) => `បង្ហាញ ${count} របាយការណ៍`,
      diagnoseCta: 'ពិនិត្យរោគសញ្ញា',
      reportLabel: 'របាយការណ៍',
      openReport: 'បើករបាយការណ៍',
      emptyTitle: 'មិនមានរបាយការណ៍ដែលត្រូវនឹងការស្វែងរកនេះ',
      emptyBody: 'សាកល្បងពាក្យស្វែងរកទូលំទូលាយជាងមុន ឬលុបតម្រងស្វែងរក។',
    },
    diagnose: {
      kicker: 'លំហូររោគសញ្ញា',
      title: 'ជ្រើសរោគសញ្ញាដែលបានសង្កេតឃើញជាមួយផ្ទាំងណែនាំដែលស្ងប់ស្ងាត់ និងច្បាស់។',
      subtitle:
        'ស្វែងរក តម្រៀបតាមផ្នែករុក្ខជាតិ និងមើលសេចក្តីសង្ខេបបន្តផ្ទាល់ មុនពេលដំណើរការវិនិច្ឆ័យ។',
      searchPlaceholder: 'ស្វែងរករោគសញ្ញាដូចជា wilting, stem lesions, root rot...',
      selectedOnly: 'បង្ហាញតែដែលបានជ្រើស',
      clearFilters: 'សម្អាតតម្រង',
      browseLibrary: 'មើលបណ្ណាល័យ',
      checkSymptoms: 'ពិនិត្យរោគសញ្ញា',
      reset: 'កំណត់ឡើងវិញ',
      totalVisible: 'កំពុងបង្ហាញ',
      selected: 'បានជ្រើស',
      allCategories: 'គ្រប់ផ្នែកទាំងអស់',
      selectedSummary: 'រោគសញ្ញាដែលបានជ្រើស',
      selectedEmpty: 'ជ្រើសរោគសញ្ញា ដើម្បីបង្កើតសេចក្តីសង្ខេបសម្រាប់វិនិច្ឆ័យ។',
      tipsTitle: 'របៀបទទួលបានលទ្ធផលត្រឹមត្រូវជាងមុន',
      tipA: 'ជ្រើសតែអ្វីដែលអ្នកអាចសង្កេតឃើញច្បាស់។',
      tipB: 'បញ្ចូលរោគសញ្ញាតាមផ្នែករុក្ខជាតិជាមួយសញ្ញាបរិស្ថាន ឬលំនាំបន្ថែម។',
      tipC: 'បើមិនមានលទ្ធផល សូមផ្ញើមតិយោបល់ជាមួយរូបថតក្រោយមក។',
      noResults: 'មិនមានរោគសញ្ញាដែលត្រូវនឹងតម្រងនេះ',
      noResultsBody: 'សាកល្បងពាក្យស្វែងរកទូលំទូលាយជាងមុន ឬបិទតម្រង Selected only។',
      progressLabel: 'កម្រិតគ្របដណ្តប់ការជ្រើស',
      categoryLabel: 'ផ្នែករុក្ខជាតិ',
      countShown: (count) => `បង្ហាញ ${count}`,
      stickyTitle: 'រួចរាល់សម្រាប់វិនិច្ឆ័យ',
      stickyBody: 'បញ្ជីរោគសញ្ញាបច្ចុប្បន្នរបស់អ្នក នឹងត្រូវបញ្ជូនទៅប្រព័ន្ធជំនាញតាមអ្វីដែលបានជ្រើសខាងក្រោម។',
    },
  },
};

function parsePayload(id) {
  const node = document.getElementById(id);
  if (!node) return null;
  try {
    return JSON.parse(node.textContent || '{}');
  } catch (error) {
    console.error(`Failed to parse payload for ${id}`, error);
    return null;
  }
}

function isKhmerLanguage(language) {
  return language === 'km';
}

function eyebrowClass(language, extra = '') {
  return [
    'text-[#55704b] dark:text-[#c7d5c2]',
    isKhmerLanguage(language)
      ? 'text-sm font-semibold tracking-normal'
      : 'text-xs font-semibold uppercase tracking-[0.28em]',
    extra,
  ]
    .filter(Boolean)
    .join(' ');
}

function heroTitleClass(language) {
  return isKhmerLanguage(language)
    ? 'font-khmer text-[2.45rem] font-bold leading-[1.34] tracking-normal text-[#163628] dark:text-[#f4f7ef] md:text-[3.7rem]'
    : 'font-display text-4xl font-black leading-tight tracking-[-0.03em] text-[#163628] dark:text-[#f4f7ef] md:text-5xl';
}

function heroBodyClass(language) {
  return [
    'max-w-2xl text-[#55704b] dark:text-[#c7d5c2]',
    isKhmerLanguage(language)
      ? 'text-lg leading-[1.95] md:text-[1.28rem]'
      : 'text-base leading-8 md:text-lg',
  ].join(' ');
}

function panelLabelClass(language) {
  return isKhmerLanguage(language)
    ? 'block font-khmer text-sm font-semibold leading-6 tracking-normal text-white/70'
    : 'block text-xs font-semibold uppercase tracking-[0.28em] text-white/55';
}

function searchInputClass(language, tone = 'light') {
  const palette =
    tone === 'dark'
      ? 'text-white placeholder:text-white/45'
      : 'text-[#17311d] placeholder:text-[#7d9273] dark:text-[#f4f7ef] dark:placeholder:text-[#8ea188]';
  return [
    'w-full border-0 bg-transparent p-0 focus:ring-0',
    palette,
    isKhmerLanguage(language)
      ? 'font-khmer text-[1rem] leading-7 tracking-normal [word-spacing:normal]'
      : 'text-sm',
  ].join(' ');
}

function cardBadgeClass(language) {
  return [
    'rounded-full bg-[#eaf4df] dark:bg-white/10 dark:text-[#c7d5c2]',
    isKhmerLanguage(language)
      ? 'font-khmer px-3 py-1.5 text-sm font-semibold leading-none tracking-normal text-[#55704b]'
      : 'px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-[#55704b]',
  ].join(' ');
}

function diseaseTitleClass(language) {
  return isKhmerLanguage(language)
    ? 'font-khmer text-[1.45rem] font-bold leading-[1.55] tracking-normal text-[#19331f] dark:text-[#f4f7ef]'
    : 'text-lg font-bold leading-7 text-[#19331f] dark:text-[#f4f7ef]';
}

function diseaseExcerptClass(language) {
  return isKhmerLanguage(language)
    ? 'font-khmer min-h-[7.75rem] flex-1 text-[1rem] leading-[1.9] tracking-normal text-[#5b715a] dark:text-[#c7d5c2]'
    : 'min-h-[6.75rem] flex-1 text-sm leading-7 text-[#5b715a] dark:text-[#c7d5c2]';
}

function diseaseActionClass(language) {
  return [
    'mt-auto inline-flex items-center gap-2 self-start rounded-full bg-[#17311d] text-white transition hover:bg-[#0f2314] dark:bg-[#f2bf4c] dark:text-[#1c1f12] dark:hover:bg-[#f6cf72]',
    isKhmerLanguage(language)
      ? 'font-khmer px-5 py-2.5 text-[1rem] font-semibold leading-none tracking-normal'
      : 'px-4 py-2.5 text-sm font-semibold',
  ].join(' ');
}

function getLanguageValue(language, value) {
  if (!value || typeof value !== 'object') return value || '';
  return (language === 'km' ? value.km : value.en) || value.en || value.km || '';
}

function translatePhrase(language, text) {
  const source = String(text || '');
  if (!source || language !== 'km') return source;

  const phrases = window.SF_I18N_STORE?.km?.phrases || {};
  if (phrases[source]) return phrases[source];

  let translated = source;
  Object.entries(phrases)
    .filter(([key]) => key && key.length >= 3)
    .sort((a, b) => b[0].length - a[0].length)
    .forEach(([key, value]) => {
      if (translated.includes(key)) {
        translated = translated.split(key).join(value);
      }
    });
  return translated;
}

function useLanguage() {
  const [language, setLanguage] = useState(
    window.SF_GET_LANGUAGE?.() || document.documentElement.lang || 'en'
  );

  useEffect(() => {
    const handler = (event) => {
      const next = event?.detail?.language || window.SF_GET_LANGUAGE?.() || 'en';
      setLanguage(next === 'km' ? 'km' : 'en');
    };

    window.addEventListener('sf:languagechange', handler);
    return () => window.removeEventListener('sf:languagechange', handler);
  }, []);

  return language === 'km' ? 'km' : 'en';
}

function useKhmerLooseTranslation(language, deps) {
  useEffect(() => {
    if (language !== 'km') return undefined;
    const frame = window.requestAnimationFrame(() => {
      window.SF_TRANSLATE_LOOSE_CONTENT?.();
    });
    return () => window.cancelAnimationFrame(frame);
  }, deps);
}

function MetricCard({ label, value, detail, accent, delay = 0, language = 'en' }) {
  const accentClass =
    accent === 'sun'
      ? 'from-sunflower-300/70 via-white/85 to-white/60 dark:from-sunflower-500/20'
      : accent === 'soil'
        ? 'from-soil-100 via-white/85 to-white/60 dark:from-soil-400/15'
        : 'from-leaf-100 via-white/85 to-white/60 dark:from-leaf-500/15';

  return html`
    <article
      data-reveal
      data-reveal-delay=${delay}
      className=${`group relative overflow-hidden rounded-[28px] border border-white/70 bg-gradient-to-br ${accentClass} p-5 shadow-soft backdrop-blur transition duration-300 hover:-translate-y-1 hover:shadow-glow dark:border-white/10 dark:bg-[#17261b]/90`}
    >
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/80 to-transparent dark:via-white/20"></div>
      <div className=${eyebrowClass(language, 'dark:text-[#b7d0a9]')}>${label}</div>
      <div className="mt-4 text-4xl font-black tracking-tight text-[#17311d] dark:text-[#f4f7ef]">${value}</div>
      <div className="mt-2 text-sm leading-6 text-[#54705d] dark:text-[#c7d5c2]">${detail}</div>
    </article>
  `;
}

function DiseaseCard({ disease, language, openLabel, reportLabel, delay = 0 }) {
  return html`
    <article
      data-reveal
      data-reveal-delay=${delay}
      className="group relative flex h-full flex-col overflow-hidden rounded-[30px] border border-white/70 bg-white/75 shadow-soft backdrop-blur transition duration-300 hover:-translate-y-1 hover:shadow-glow dark:border-white/10 dark:bg-[#142117]/90"
    >
      <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-leaf-500 via-sunflower-300 to-soil-400 opacity-80"></div>
      <div className="aspect-[4/3] overflow-hidden">
        <img
          src=${disease.imageUrl}
          alt=${getLanguageValue(language, disease.name)}
          className="h-full w-full object-cover transition duration-500 group-hover:scale-105"
        />
      </div>
      <div className="flex flex-1 flex-col space-y-4 p-5">
        <div className="flex items-start justify-between gap-3">
          <div className=${diseaseTitleClass(language)}>
            ${getLanguageValue(language, disease.name)}
          </div>
          <span className=${cardBadgeClass(language)}>
            ${reportLabel}
          </span>
        </div>
        <p className=${diseaseExcerptClass(language)}>
          ${getLanguageValue(language, disease.excerpt)}
        </p>
        <a
          href=${disease.detailUrl}
          className=${diseaseActionClass(language)}
        >
          <span>${openLabel}</span>
          <i className="bi bi-arrow-up-right" aria-hidden="true"></i>
        </a>
      </div>
    </article>
  `;
}

function HomeApp({ data }) {
  const language = useLanguage();
  const copy = COPY[language].home;
  const metrics = data.metrics || {};
  const latestDiagnosis = data.latestDiagnosis || {};
  const featuredDiseases = (data.featuredDiseases || []).slice(0, 3);
  const recentChecks = data.recentChecks || [];
  const isAuthenticated = !!data.authenticated;

  useKhmerLooseTranslation(language, [language, featuredDiseases.length, recentChecks.length]);

  const deltaText = (() => {
    if ((metrics.weeklyDiff || 0) > 0) return copy.deltaUp(metrics.weeklyDiff);
    if ((metrics.weeklyDiff || 0) < 0) return copy.deltaDown(metrics.weeklyDiff);
    return copy.deltaFlat;
  })();

  const heroTitle = isAuthenticated ? copy.titleAuthed : copy.titlePublic;
  const heroSubtitle = isAuthenticated ? copy.subtitleAuthed : copy.subtitlePublic;
  const heroKicker = isAuthenticated ? copy.kickerAuthed : copy.kickerPublic;
  const latestTitle = getLanguageValue(language, latestDiagnosis.title) || copy.latestEmpty;

  return html`
    <div className="space-y-8 font-body">
      <section
        data-reveal
        className="relative overflow-hidden rounded-[34px] border border-white/70 bg-white/70 px-6 py-7 shadow-soft backdrop-blur dark:border-white/10 dark:bg-[#132017]/85 lg:px-10 lg:py-10"
      >
        <div className="pointer-events-none absolute -right-20 top-8 h-48 w-48 rounded-full bg-sunflower-300/40 blur-3xl dark:bg-sunflower-500/15"></div>
        <div className="pointer-events-none absolute -left-16 bottom-0 h-44 w-44 rounded-full bg-leaf-300/40 blur-3xl dark:bg-leaf-500/20"></div>
        <div className="pointer-events-none absolute right-10 top-14 hidden h-24 w-24 rounded-full border border-white/60 bg-white/30 md:block"></div>
        <div className="relative max-w-4xl space-y-6">
          <div className="space-y-6">
            <div className=${`inline-flex items-center gap-2 rounded-full border border-white/70 bg-white/70 px-4 py-2 shadow-sm dark:border-white/10 dark:bg-white/5 ${eyebrowClass(language)}`}>
              <span className="h-2.5 w-2.5 rounded-full bg-leaf-500 animate-pulse-slow"></span>
              <span>${heroKicker}</span>
            </div>

            <div className="max-w-3xl space-y-4">
              <h1 className=${heroTitleClass(language)}>
                ${heroTitle}
              </h1>
              <p className=${heroBodyClass(language)}>
                ${heroSubtitle}
              </p>
            </div>

            <div className="flex flex-wrap gap-3">
              ${isAuthenticated
                ? html`
                    <a
                      href=${data.links?.diagnose}
                      className="inline-flex items-center gap-2 rounded-full bg-[#17311d] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#0f2314] dark:bg-[#f2bf4c] dark:text-[#1c1f12] dark:hover:bg-[#f6cf72]"
                    >
                      <i className="bi bi-clipboard2-pulse" aria-hidden="true"></i>
                      <span>${copy.primaryCta}</span>
                    </a>
                    <a
                      href=${data.links?.library}
                      className="inline-flex items-center gap-2 rounded-full border border-[#cadabf] bg-white/70 px-5 py-3 text-sm font-semibold text-[#17311d] transition hover:border-[#9ab789] hover:bg-white dark:border-white/15 dark:bg-white/5 dark:text-[#f4f7ef] dark:hover:bg-white/10"
                    >
                      <i className="bi bi-journal-medical" aria-hidden="true"></i>
                      <span>${copy.secondaryCta}</span>
                    </a>
                  `
                : html`
                    <a
                      href=${data.links?.login}
                      className="inline-flex items-center gap-2 rounded-full bg-[#17311d] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#0f2314] dark:bg-[#f2bf4c] dark:text-[#1c1f12] dark:hover:bg-[#f6cf72]"
                    >
                      <i className="bi bi-box-arrow-in-right" aria-hidden="true"></i>
                      <span>${copy.loginCta}</span>
                    </a>
                    <a
                      href=${data.links?.register}
                      className="inline-flex items-center gap-2 rounded-full border border-[#cadabf] bg-white/70 px-5 py-3 text-sm font-semibold text-[#17311d] transition hover:border-[#9ab789] hover:bg-white dark:border-white/15 dark:bg-white/5 dark:text-[#f4f7ef] dark:hover:bg-white/10"
                    >
                      <i className="bi bi-person-plus" aria-hidden="true"></i>
                      <span>${copy.registerCta}</span>
                    </a>
                  `}
            </div>
          </div>
        </div>
      </section>

      ${isAuthenticated
        ? html`
            <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              ${[
                {
                  label: copy.metrics.today,
                  value: metrics.todayChecks ?? 0,
                  detail: deltaText,
                  accent: 'leaf',
                },
                {
                  label: copy.metrics.total,
                  value: metrics.totalChecks ?? 0,
                  detail: copy.recentTitle,
                  accent: 'sun',
                },
                {
                  label: copy.metrics.library,
                  value: metrics.diseaseCount ?? 0,
                  detail: copy.diseaseBody,
                  accent: 'soil',
                },
                {
                  label: copy.metrics.pending,
                  value: metrics.pendingReports ?? 0,
                  detail: copy.latestTitle,
                  accent: 'leaf',
                },
              ].map(
                (card, index) => html`
                  <${MetricCard}
                    key=${card.label}
                    label=${card.label}
                    value=${card.value}
                    detail=${card.detail}
                    accent=${card.accent}
                    language=${language}
                    delay=${index * 70}
                  />
                `
              )}
            </section>

            <section className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
              <article
                data-reveal
                className="relative overflow-hidden rounded-[30px] border border-white/70 bg-white/75 p-6 shadow-soft backdrop-blur dark:border-white/10 dark:bg-[#142117]/90"
              >
                <div className="absolute right-0 top-0 h-28 w-28 rounded-full bg-sunflower-300/30 blur-3xl dark:bg-sunflower-500/10"></div>
                <div className="relative space-y-5">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <div className=${eyebrowClass(language)}>${copy.latestTitle}</div>
                      <h2 className="mt-3 text-3xl font-black tracking-tight text-[#17311d] dark:text-[#f4f7ef]">
                        ${latestTitle}
                      </h2>
                    </div>
                    <div className="rounded-full bg-[#e8f4db] px-4 py-2 text-sm font-semibold text-[#17311d] dark:bg-white/10 dark:text-[#f2f5ee]">
                      ${latestDiagnosis.percent != null ? `${latestDiagnosis.percent}%` : '--'}
                    </div>
                  </div>

                  ${latestDiagnosis.reportUrl
                    ? html`
                        <p className="text-sm leading-7 text-[#5b715a] dark:text-[#c7d5c2]">
                          ${latestDiagnosis.checkedOn} • ${latestDiagnosis.selectedCount || 0}
                          ${copy.selectedCount}
                        </p>
                        <div className="grid gap-3 sm:grid-cols-2">
                          ${(latestDiagnosis.matched || []).map(
                            (item, index) => html`
                              <div
                                key=${`${item}-${index}`}
                                className="rounded-[22px] border border-[#d9e7cf] bg-[#f6fbf1] px-4 py-3 text-sm font-medium text-[#2e4e2f] dark:border-white/10 dark:bg-white/5 dark:text-[#dbe6d5]"
                              >
                                <i className="bi bi-check2-circle mr-2 text-leaf-500" aria-hidden="true"></i>
                                ${item}
                              </div>
                            `
                          )}
                        </div>
                      `
                    : html`
                        <div className="rounded-[24px] border border-dashed border-[#cadabf] bg-[#f8fbf4] px-5 py-8 text-center dark:border-white/10 dark:bg-white/5">
                          <div className="text-lg font-semibold text-[#17311d] dark:text-[#f4f7ef]">${copy.latestEmpty}</div>
                          <p className="mt-2 text-sm leading-7 text-[#5b715a] dark:text-[#c7d5c2]">${copy.latestEmptyBody}</p>
                        </div>
                      `}

                  ${latestDiagnosis.reportUrl
                    ? html`
                        <div className="pt-2">
                          <a
                            href=${latestDiagnosis.reportUrl}
                            className="inline-flex items-center gap-2 rounded-full bg-[#17311d] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#0f2314] dark:bg-[#f2bf4c] dark:text-[#1c1f12] dark:hover:bg-[#f6cf72]"
                          >
                            <span>${copy.openReport}</span>
                            <i className="bi bi-arrow-up-right" aria-hidden="true"></i>
                          </a>
                        </div>
                      `
                    : null}
                </div>
              </article>

              <article
                data-reveal
                data-reveal-delay="80"
                className="rounded-[30px] border border-white/70 bg-white/75 p-6 shadow-soft backdrop-blur dark:border-white/10 dark:bg-[#142117]/90"
              >
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className=${eyebrowClass(language)}>${copy.recentTitle}</div>
                    <h2 className="mt-3 text-2xl font-black tracking-tight text-[#17311d] dark:text-[#f4f7ef]">${copy.recentTitle}</h2>
                  </div>
                  <div className="rounded-full bg-[#edf5e5] px-4 py-2 text-sm font-semibold text-[#305331] dark:bg-white/10 dark:text-[#dbe6d5]">
                    ${recentChecks.length}
                  </div>
                </div>

                <div className="mt-5 space-y-3">
                  ${recentChecks.length
                    ? recentChecks.map(
                        (check, index) => html`
                          <a
                            key=${check.id}
                            href=${check.detailUrl || data.links?.diagnose}
                            className="flex items-center justify-between gap-4 rounded-[24px] border border-[#dbe8d1] bg-[#f8fbf4] px-4 py-4 transition hover:border-[#a9c397] hover:bg-white dark:border-white/10 dark:bg-white/5 dark:hover:bg-white/10"
                          >
                            <div className="min-w-0">
                              <div className="truncate text-base font-semibold text-[#17311d] dark:text-[#f4f7ef]">
                                ${getLanguageValue(language, check.title)}
                              </div>
                              <div className="mt-1 text-sm text-[#5b715a] dark:text-[#c7d5c2]">
                                ${check.createdAt} • ${check.selectedCount} ${copy.selectedCount}
                              </div>
                            </div>
                            <div className="shrink-0 rounded-full bg-[#e8f4db] px-3 py-2 text-sm font-semibold text-[#204327] dark:bg-white/10 dark:text-[#f4f7ef]">
                              ${check.percent != null ? `${check.percent}%` : '--'}
                            </div>
                          </a>
                        `
                      )
                    : html`
                        <div className="rounded-[24px] border border-dashed border-[#cadabf] bg-[#f8fbf4] px-5 py-8 text-center text-sm leading-7 text-[#5b715a] dark:border-white/10 dark:bg-white/5 dark:text-[#c7d5c2]">
                          ${copy.recentEmpty}
                        </div>
                      `}
                </div>
              </article>
            </section>
          `
        : null}

      <section className="space-y-4">
        <div data-reveal className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <div className=${eyebrowClass(language)}>${copy.diseaseTitle}</div>
            <h2 className="mt-3 text-3xl font-black tracking-tight text-[#17311d] dark:text-[#f4f7ef]">${copy.diseaseTitle}</h2>
            <p className="mt-2 max-w-2xl text-sm leading-7 text-[#5b715a] dark:text-[#c7d5c2]">${copy.diseaseBody}</p>
          </div>
          <a
            href=${data.links?.library}
            className="inline-flex items-center gap-2 rounded-full border border-[#cadabf] bg-white/70 px-5 py-3 text-sm font-semibold text-[#17311d] transition hover:border-[#9ab789] hover:bg-white dark:border-white/15 dark:bg-white/5 dark:text-[#f4f7ef] dark:hover:bg-white/10"
          >
            <span>${copy.secondaryCta}</span>
            <i className="bi bi-arrow-right" aria-hidden="true"></i>
          </a>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          ${featuredDiseases.map(
            (disease, index) => html`
              <${DiseaseCard}
                key=${disease.slug}
                disease=${disease}
                language=${language}
                openLabel=${copy.openReport}
                reportLabel=${COPY[language].library.reportLabel}
                delay=${index * 70}
              />
            `
          )}
        </div>
      </section>
    </div>
  `;
}

function LibraryApp({ data }) {
  const language = useLanguage();
  const copy = COPY[language].library;
  const [query, setQuery] = useState('');
  const deferredQuery = useDeferredValue(query);
  const diseases = data.diseases || [];

  const filteredDiseases = useMemo(() => {
    const term = deferredQuery.trim().toLowerCase();
    if (!term) return diseases;
    return diseases.filter((disease) => {
      const haystack = [
        disease.name?.en,
        disease.name?.km,
        disease.excerpt?.en,
        disease.excerpt?.km,
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();
      return haystack.includes(term);
    });
  }, [deferredQuery, diseases]);

  useKhmerLooseTranslation(language, [language, filteredDiseases.length]);

  return html`
    <div className="space-y-8 font-body">
      <section
        data-reveal
        className="relative overflow-hidden rounded-[34px] border border-white/70 bg-white/70 px-6 py-7 shadow-soft backdrop-blur dark:border-white/10 dark:bg-[#132017]/85 lg:px-10 lg:py-10"
      >
        <div className="pointer-events-none absolute -right-20 top-8 h-48 w-48 rounded-full bg-sunflower-300/40 blur-3xl dark:bg-sunflower-500/15"></div>
        <div className="pointer-events-none absolute -left-12 bottom-0 h-40 w-40 rounded-full bg-leaf-300/30 blur-3xl dark:bg-leaf-500/20"></div>
        <div className="relative grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <div className="space-y-5">
            <div className=${`inline-flex items-center gap-2 rounded-full border border-white/70 bg-white/70 px-4 py-2 shadow-sm dark:border-white/10 dark:bg-white/5 ${eyebrowClass(language)}`}>
              <i className="bi bi-journal-richtext text-leaf-500" aria-hidden="true"></i>
              <span>${copy.kicker}</span>
            </div>
            <div className="space-y-4">
              <h1 className=${heroTitleClass(language)}>
                ${copy.title}
              </h1>
              <p className=${heroBodyClass(language)}>
                ${copy.subtitle}
              </p>
            </div>
          </div>

          <div
            data-reveal
            data-reveal-delay="90"
            className="rounded-[30px] border border-white/70 bg-[#17311d] p-5 text-white shadow-glow dark:border-white/10"
          >
            <label className=${panelLabelClass(language)}>
              ${copy.searchPlaceholder}
            </label>
            <div className="mt-4 flex items-center gap-3 rounded-[24px] border border-white/15 bg-white/10 px-4 py-3 backdrop-blur">
              <i className="bi bi-search text-white/70" aria-hidden="true"></i>
              <input
                type="search"
                value=${query}
                onInput=${(event) => {
                  const nextValue = event.currentTarget.value;
                  startTransition(() => setQuery(nextValue));
                }}
                placeholder=${copy.searchPlaceholder}
                className=${searchInputClass(language, 'dark')}
              />
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              <span className="rounded-full bg-white/12 px-3 py-2 text-sm text-white/80">
                ${copy.resultCount(filteredDiseases.length)}
              </span>
              ${data.authenticated
                ? html`
                    <a
                      href=${data.links?.diagnose}
                      className="rounded-full bg-white px-4 py-2 text-sm font-semibold text-[#17311d] transition hover:bg-[#f3f5f0]"
                    >
                      ${copy.diagnoseCta}
                    </a>
                  `
                : null}
            </div>
          </div>
        </div>
      </section>

      ${filteredDiseases.length
        ? html`
            <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              ${filteredDiseases.map(
                (disease, index) => html`
                  <${DiseaseCard}
                    key=${disease.slug}
                    disease=${disease}
                    language=${language}
                    openLabel=${copy.openReport}
                    reportLabel=${copy.reportLabel}
                    delay=${index * 60}
                  />
                `
              )}
            </section>
          `
        : html`
            <section
              data-reveal
              className="rounded-[30px] border border-dashed border-[#cadabf] bg-white/75 px-6 py-16 text-center shadow-soft backdrop-blur dark:border-white/10 dark:bg-[#142117]/90"
            >
              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-[#edf5e5] text-2xl text-[#305331] dark:bg-white/10 dark:text-[#f4f7ef]">
                <i className="bi bi-search" aria-hidden="true"></i>
              </div>
              <h2 className="mt-5 text-2xl font-black tracking-tight text-[#17311d] dark:text-[#f4f7ef]">${copy.emptyTitle}</h2>
              <p className="mx-auto mt-3 max-w-2xl text-sm leading-7 text-[#5b715a] dark:text-[#c7d5c2]">${copy.emptyBody}</p>
            </section>
          `}
    </div>
  `;
}

function DiagnoseApp({ data }) {
  const language = useLanguage();
  const copy = COPY[language].diagnose;
  const categories = data.categories || [];
  const [selected, setSelected] = useState(() => new Set(data.selected || []));
  const [query, setQuery] = useState('');
  const searchRef = useRef(null);
  const deferredQuery = useDeferredValue(query);

  useEffect(() => {
    const onKeyDown = (event) => {
      if (event.key !== '/') return;
      const target = event.target;
      if (
        target instanceof HTMLElement &&
        (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable)
      ) {
        return;
      }
      event.preventDefault();
      searchRef.current?.focus();
    };

    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, []);

  const visibleItems = useMemo(() => {
    const term = deferredQuery.trim().toLowerCase();
    return categories
      .flatMap((category) =>
        (category.items || []).map((item) => ({
          ...item,
          categoryName: category.name,
        }))
      )
      .filter((item) => {
        const currentLabel = getLanguageValue(language, item.label);
        const translatedLabel = translatePhrase(language, currentLabel).toLowerCase();
        const englishLabel = getLanguageValue('en', item.label).toLowerCase();
        const khmerLabel = getLanguageValue('km', item.label).toLowerCase();
        return (
          !term ||
          englishLabel.includes(term) ||
          khmerLabel.includes(term) ||
          translatedLabel.includes(term)
        );
      });
  }, [categories, deferredQuery, language]);

  const totalVisible = visibleItems.length;
  const visibleCategories = useMemo(() => {
    const grouped = new Map();
    visibleItems.forEach((item) => {
      const key = item.categoryName || 'General';
      if (!grouped.has(key)) {
        grouped.set(key, []);
      }
      grouped.get(key).push(item);
    });
    return Array.from(grouped.entries()).map(([name, items]) => ({ name, items }));
  }, [visibleItems]);

  const selectedItems = useMemo(() => {
    const itemMap = new Map();
    categories.forEach((category) => {
      (category.items || []).forEach((item) => {
        itemMap.set(item.key, translatePhrase(language, getLanguageValue(language, item.label)));
      });
    });
    return Array.from(selected).map((key) => ({
      key,
      label: itemMap.get(key) || key,
    }));
  }, [categories, language, selected]);

  const progressValue = data.totalSymptoms
    ? Math.min(100, Math.round((selected.size / data.totalSymptoms) * 100))
    : 0;

  useKhmerLooseTranslation(language, [
    language,
    selected.size,
    totalVisible,
    visibleCategories.length,
  ]);

  return html`
    <div className="space-y-6 font-body">
      <section
        data-reveal
        className="relative overflow-hidden rounded-[34px] border border-white/70 bg-white/70 px-6 py-7 shadow-soft backdrop-blur dark:border-white/10 dark:bg-[#132017]/85 lg:px-10 lg:py-10"
      >
        <div className="pointer-events-none absolute -right-20 top-8 h-48 w-48 rounded-full bg-sunflower-300/40 blur-3xl dark:bg-sunflower-500/15"></div>
        <div className="pointer-events-none absolute -left-16 bottom-0 h-44 w-44 rounded-full bg-leaf-300/30 blur-3xl dark:bg-leaf-500/20"></div>
        <div className="relative grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
          <div className="space-y-5">
            <div className=${`inline-flex items-center gap-2 rounded-full border border-white/70 bg-white/70 px-4 py-2 shadow-sm dark:border-white/10 dark:bg-white/5 ${eyebrowClass(language)}`}>
              <i className="bi bi-sliders2-vertical text-leaf-500" aria-hidden="true"></i>
              <span>${copy.kicker}</span>
            </div>
            <div className="space-y-4">
              <h1 className=${heroTitleClass(language)}>
                ${copy.title}
              </h1>
              <p className=${heroBodyClass(language)}>
                ${copy.subtitle}
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <div className="rounded-full bg-[#edf5e5] px-4 py-2 text-sm font-semibold text-[#305331] dark:bg-white/10 dark:text-[#f4f7ef]">
                ${selected.size} ${copy.selected}
              </div>
              <div className="rounded-full bg-[#edf5e5] px-4 py-2 text-sm font-semibold text-[#305331] dark:bg-white/10 dark:text-[#f4f7ef]">
                ${totalVisible} ${copy.totalVisible}
              </div>
            </div>
          </div>

          <div
            data-reveal
            data-reveal-delay="90"
            className="rounded-[30px] border border-white/70 bg-[#17311d] p-5 text-white shadow-glow dark:border-white/10"
          >
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className=${isKhmerLanguage(language) ? 'text-sm font-semibold tracking-normal text-white/70' : 'text-xs font-semibold uppercase tracking-[0.28em] text-white/55'}>${copy.progressLabel}</div>
                <div className="mt-3 text-4xl font-black">${progressValue}%</div>
              </div>
              <div className="flex h-20 w-20 items-center justify-center rounded-full border border-white/15 bg-white/10 text-xl font-bold">
                ${selected.size}
              </div>
            </div>
            <div className="mt-5 h-3 overflow-hidden rounded-full bg-white/10">
              <div
                className="h-full rounded-full bg-gradient-to-r from-leaf-500 via-sunflower-300 to-soil-400 transition-[width] duration-300"
                style=${{ width: `${progressValue}%` }}
              ></div>
            </div>
            <p className="mt-4 text-sm leading-7 text-white/75">${copy.stickyBody}</p>
          </div>
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_340px]">
        <section className="space-y-5">
          <div
            data-reveal
            className="rounded-[30px] border border-white/70 bg-white/75 p-5 shadow-soft backdrop-blur dark:border-white/10 dark:bg-[#142117]/90"
          >
            <div className="max-w-xl">
              <label className="flex items-center gap-3 rounded-[22px] border border-[#d9e7cf] bg-[#f7fbf2] px-4 py-3 dark:border-white/10 dark:bg-white/5">
                <i className="bi bi-search text-[#55704b] dark:text-[#dbe6d5]" aria-hidden="true"></i>
                <input
                  ref=${searchRef}
                  type="search"
                  value=${query}
                  onInput=${(event) => {
                    const nextValue = event.currentTarget.value;
                    startTransition(() => setQuery(nextValue));
                  }}
                  placeholder=${copy.searchPlaceholder}
                  className=${searchInputClass(language)}
                />
              </label>
            </div>
          </div>

          ${visibleCategories.length
            ? visibleCategories.map(
                (category, categoryIndex) => html`
                  <section
                    key=${category.name}
                    data-reveal
                    data-reveal-delay=${categoryIndex * 40}
                    className="rounded-[30px] border border-white/70 bg-white/75 p-5 shadow-soft backdrop-blur dark:border-white/10 dark:bg-[#142117]/90"
                  >
                    <div className="mb-4 flex items-center justify-between gap-3">
                      <div>
                        <div className=${eyebrowClass(language)}>${copy.categoryLabel}</div>
                        <h2 className="mt-2 text-2xl font-black tracking-tight text-[#17311d] dark:text-[#f4f7ef]">
                          ${translatePhrase(language, category.name)}
                        </h2>
                      </div>
                      <div className="rounded-full bg-[#edf5e5] px-4 py-2 text-sm font-semibold text-[#305331] dark:bg-white/10 dark:text-[#f4f7ef]">
                        ${copy.countShown(category.items.length)}
                      </div>
                    </div>

                    <div className="grid gap-3 md:grid-cols-2 2xl:grid-cols-3">
                      ${category.items.map((item, itemIndex) => {
                        const checked = selected.has(item.key);
                        return html`
                          <label
                            key=${item.key}
                            data-reveal-delay=${Math.min(itemIndex * 20, 240)}
                            className=${`group flex cursor-pointer items-start gap-3 rounded-[24px] border px-4 py-4 transition ${
                              checked
                                ? 'border-[#8ebb79] bg-[#eef8e5] shadow-[0_16px_35px_rgba(79,169,95,0.14)] dark:border-[#5f8a50] dark:bg-[#1c311f]'
                                : 'border-[#d9e7cf] bg-[#f8fbf4] hover:border-[#a8c495] hover:bg-white dark:border-white/10 dark:bg-white/5 dark:hover:bg-white/10'
                            }`}
                          >
                            <input
                              type="checkbox"
                              name="symptoms"
                              value=${item.key}
                              checked=${checked}
                              onChange=${() => {
                                setSelected((previous) => {
                                  const next = new Set(previous);
                                  if (next.has(item.key)) {
                                    next.delete(item.key);
                                  } else {
                                    next.add(item.key);
                                  }
                                  return next;
                                });
                              }}
                              className="mt-1 rounded border-[#9eb48d] text-[#255a31] focus:ring-[#255a31]"
                            />
                            <span className="text-sm font-semibold leading-7 text-[#17311d] dark:text-[#f4f7ef]">
                              ${translatePhrase(language, getLanguageValue(language, item.label))}
                            </span>
                          </label>
                        `;
                      })}
                    </div>
                  </section>
                `
              )
            : html`
                <section
                  data-reveal
                  className="rounded-[30px] border border-dashed border-[#cadabf] bg-white/75 px-6 py-16 text-center shadow-soft backdrop-blur dark:border-white/10 dark:bg-[#142117]/90"
                >
                  <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-[#edf5e5] text-2xl text-[#305331] dark:bg-white/10 dark:text-[#f4f7ef]">
                    <i className="bi bi-search" aria-hidden="true"></i>
                  </div>
                  <h2 className="mt-5 text-2xl font-black tracking-tight text-[#17311d] dark:text-[#f4f7ef]">${copy.noResults}</h2>
                  <p className="mx-auto mt-3 max-w-2xl text-sm leading-7 text-[#5b715a] dark:text-[#c7d5c2]">${copy.noResultsBody}</p>
                </section>
              `}
        </section>

        <aside className="space-y-5 xl:sticky xl:top-24">
          <section
            data-reveal
            data-reveal-delay="80"
            className="rounded-[30px] border border-white/70 bg-white/75 p-5 shadow-soft backdrop-blur dark:border-white/10 dark:bg-[#142117]/90"
          >
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className=${eyebrowClass(language)}>${copy.stickyTitle}</div>
                <h2 className="mt-2 text-2xl font-black tracking-tight text-[#17311d] dark:text-[#f4f7ef]">${copy.selectedSummary}</h2>
              </div>
              <div className="rounded-full bg-[#edf5e5] px-4 py-2 text-sm font-semibold text-[#305331] dark:bg-white/10 dark:text-[#f4f7ef]">
                ${selected.size}
              </div>
            </div>

            <div className="mt-5 flex flex-wrap gap-2">
              ${selectedItems.length
                ? selectedItems.map(
                    (item) => html`
                      <button
                        key=${item.key}
                        type="button"
                        onClick=${() => {
                          setSelected((previous) => {
                            const next = new Set(previous);
                            next.delete(item.key);
                            return next;
                          });
                        }}
                        className="inline-flex items-center gap-2 rounded-full bg-[#edf5e5] px-3 py-2 text-sm font-medium text-[#305331] transition hover:bg-[#dcefd0] dark:bg-white/10 dark:text-[#f4f7ef] dark:hover:bg-white/15"
                      >
                        <span>${item.label}</span>
                        <i className="bi bi-x-lg text-xs" aria-hidden="true"></i>
                      </button>
                    `
                  )
                : html`
                    <p className="text-sm leading-7 text-[#5b715a] dark:text-[#c7d5c2]">${copy.selectedEmpty}</p>
                  `}
            </div>

            <div className="mt-6 flex flex-wrap gap-3">
              <button
                type="submit"
                className="inline-flex items-center gap-2 rounded-full bg-[#17311d] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#0f2314] dark:bg-[#f2bf4c] dark:text-[#1c1f12] dark:hover:bg-[#f6cf72]"
              >
                <i className="bi bi-clipboard2-pulse" aria-hidden="true"></i>
                <span>${copy.checkSymptoms}</span>
              </button>
              <a
                href=${data.resetUrl}
                className="inline-flex items-center gap-2 rounded-full border border-[#cadabf] bg-white px-5 py-3 text-sm font-semibold text-[#17311d] transition hover:border-[#9ab789] dark:border-white/10 dark:bg-white/5 dark:text-[#f4f7ef]"
              >
                <i className="bi bi-arrow-counterclockwise" aria-hidden="true"></i>
                <span>${copy.reset}</span>
              </a>
            </div>
          </section>

          <section
            data-reveal
            data-reveal-delay="120"
            className="rounded-[30px] border border-white/70 bg-white/75 p-5 shadow-soft backdrop-blur dark:border-white/10 dark:bg-[#142117]/90"
          >
            <div className=${eyebrowClass(language)}>${copy.tipsTitle}</div>
            <ul className="mt-4 space-y-3 text-sm leading-7 text-[#5b715a] dark:text-[#c7d5c2]">
              <li className="rounded-[22px] bg-[#f8fbf4] px-4 py-3 dark:bg-white/5">${copy.tipA}</li>
              <li className="rounded-[22px] bg-[#f8fbf4] px-4 py-3 dark:bg-white/5">${copy.tipB}</li>
              <li className="rounded-[22px] bg-[#f8fbf4] px-4 py-3 dark:bg-white/5">${copy.tipC}</li>
            </ul>
          </section>
        </aside>
      </div>
    </div>
  `;
}

function mount(id, payloadId, Component) {
  const node = document.getElementById(id);
  const payload = parsePayload(payloadId);
  if (!node || !payload) return;
  createRoot(node).render(html`<${Component} data=${payload} />`);
  window.requestAnimationFrame(() => {
    const revealNodes = Array.from(node.querySelectorAll('[data-reveal]'));
    revealNodes.forEach((element, index) => {
      if (!(element instanceof HTMLElement)) return;
      element.classList.add('sf-scroll-reveal');
      if (!element.style.getPropertyValue('--sf-reveal-delay')) {
        const explicitDelay = Number(element.getAttribute('data-reveal-delay'));
        const delay = Number.isFinite(explicitDelay) ? explicitDelay : Math.min(index * 60, 360);
        element.style.setProperty('--sf-reveal-delay', `${delay}ms`);
      }
      window.requestAnimationFrame(() => {
        element.classList.add('is-inview');
      });
    });
    window.SF_TRANSLATE_LOOSE_CONTENT?.();
  });
}

mount('sf-home-react-root', 'sf-home-data', HomeApp);
mount('sf-library-react-root', 'sf-library-data', LibraryApp);
mount('sf-diagnose-react-root', 'sf-diagnose-data', DiagnoseApp);
