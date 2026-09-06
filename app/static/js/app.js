(() => {
  const root = document.documentElement;
  const body = document.body;

  // ----- Language (EN/KM) -----
  const STORE_I18N = window.SF_I18N_STORE || {};
  const I18N = {
    en: (STORE_I18N.en && STORE_I18N.en.ui) || {},
    km: (STORE_I18N.km && STORE_I18N.km.ui) || {},
  };
  const LOOSE_I18N = {
    km: (STORE_I18N.km && STORE_I18N.km.phrases) || {},
  };

  const KM_FRAGMENT_ENTRIES = Object.entries(LOOSE_I18N.km || {})
    .filter(([source]) => source && source.length >= 3)
    .sort((a, b) => b[0].length - a[0].length);
  const looseTextOriginals = new WeakMap();

  let currentLanguage = 'en';
  const originalDocumentTitle = document.title;

  function translateLooseText(lang, text) {
    if (!text) return text;
    if (lang !== 'km') return text;

    const exact = LOOSE_I18N.km[text];
    if (exact) return exact;
    let translated = text;

    KM_FRAGMENT_ENTRIES.forEach(([source, target]) => {
      if (!source || source === translated) return;
      if (translated.includes(source)) {
        translated = translated.split(source).join(target);
      }
    });

    return translated;
  }

  function translateLooseString(lang, text) {
    return translateLooseText(lang, text);
  }

  function translateLooseContent(lang) {
    const isKhmer = lang === 'km';

    const textWalker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const textNodes = [];
    while (textWalker.nextNode()) {
      textNodes.push(textWalker.currentNode);
    }

    textNodes.forEach((node) => {
      if (!(node instanceof Text)) return;
      const parent = node.parentElement;
      if (!parent) return;
      if (parent.closest('script,style,noscript,textarea,code,pre')) return;
      if (parent.closest('[data-i18n], [data-i18n-placeholder], [data-i18n-title]')) return;
      if (parent.closest('[data-no-translate]')) return;

      const raw = node.nodeValue || '';
      if (!raw.trim()) return;

      if (isKhmer) {
        const source = looseTextOriginals.get(node) || raw;
        const translated = translateLooseText(lang, source);
        if (!looseTextOriginals.has(node)) {
          looseTextOriginals.set(node, source);
        }
        if (translated !== source) {
          node.nodeValue = translated;
        }
        return;
      }

      if (looseTextOriginals.has(node)) {
        node.nodeValue = looseTextOriginals.get(node);
      }
    });

    document.querySelectorAll('[placeholder]').forEach((node) => {
      if (!(node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement)) return;
      if (node.hasAttribute('data-i18n-placeholder')) return;
      if (node.closest('[data-no-translate]')) return;
      const original = node.dataset.i18nLoosePlaceholder || node.getAttribute('placeholder') || '';
      if (!original) return;
      if (!node.dataset.i18nLoosePlaceholder) {
        node.dataset.i18nLoosePlaceholder = original;
      }
      if (isKhmer) {
        const translated = translateLooseText(lang, original);
        node.setAttribute('placeholder', translated);
        return;
      }
      node.setAttribute('placeholder', original);
    });

    document.querySelectorAll('[title]').forEach((node) => {
      if (!(node instanceof HTMLElement)) return;
      if (node.hasAttribute('data-i18n-title')) return;
      if (node.closest('[data-no-translate]')) return;
      const original = node.dataset.i18nLooseTitle || node.getAttribute('title') || '';
      if (!original) return;
      if (!node.dataset.i18nLooseTitle) {
        node.dataset.i18nLooseTitle = original;
      }
      if (isKhmer) {
        const translated = translateLooseText(lang, original);
        node.setAttribute('title', translated);
        return;
      }
      node.setAttribute('title', original);
    });

    document.querySelectorAll('input[type="submit"], input[type="button"], input[type="reset"]').forEach((node) => {
      if (!(node instanceof HTMLInputElement)) return;
      if (node.closest('[data-no-translate]')) return;
      const original = node.dataset.i18nLooseValue || node.value || '';
      if (!original) return;
      if (!node.dataset.i18nLooseValue) {
        node.dataset.i18nLooseValue = original;
      }
      if (isKhmer) {
        const translated = translateLooseText(lang, original);
        node.value = translated;
        return;
      }
      node.value = original;
    });

    document.querySelectorAll('[onsubmit]').forEach((node) => {
      if (!(node instanceof HTMLElement)) return;
      if (node.closest('[data-no-translate]')) return;
      const original = node.dataset.i18nLooseOnsubmit || node.getAttribute('onsubmit') || '';
      if (!original) return;
      if (!node.dataset.i18nLooseOnsubmit) {
        node.dataset.i18nLooseOnsubmit = original;
      }
      if (isKhmer) {
        const translated = translateLooseText(lang, original);
        node.setAttribute('onsubmit', translated);
        return;
      }
      node.setAttribute('onsubmit', original);
    });

    if (isKhmer) {
      const translatedTitle = translateLooseText(lang, originalDocumentTitle);
      document.title = translatedTitle;
    } else {
      document.title = originalDocumentTitle;
    }
  }

  function safeLanguage(lang) {
    return lang === 'km' ? 'km' : 'en';
  }

  function applyLanguage(lang) {
    const nextLang = safeLanguage(lang);
    currentLanguage = nextLang;
    root.setAttribute('lang', nextLang);

    try {
      localStorage.setItem('sf-language', nextLang);
    } catch (_) {}
    document.cookie = `sf-language=${nextLang}; path=/; max-age=31536000; samesite=lax`;

    const dict = I18N[nextLang] || I18N.en;
    const fallback = I18N.en;

    document.querySelectorAll('[data-i18n]').forEach((node) => {
      const key = node.getAttribute('data-i18n');
      if (!key) return;
      const value = dict[key] || fallback[key];
      if (value) node.textContent = value;
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach((node) => {
      const key = node.getAttribute('data-i18n-placeholder');
      if (!key || !(node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement)) return;
      const value = dict[key] || fallback[key];
      if (value) node.setAttribute('placeholder', value);
    });

    document.querySelectorAll('[data-i18n-title]').forEach((node) => {
      const key = node.getAttribute('data-i18n-title');
      if (!key) return;
      const value = dict[key] || fallback[key];
      if (!value) return;
      node.setAttribute('title', value);
      node.setAttribute('aria-label', value);
    });

    document.querySelectorAll('[data-language-select]').forEach((node) => {
      if (node instanceof HTMLSelectElement) {
        node.value = nextLang;
      }
    });

    translateLooseContent(nextLang);
    window.dispatchEvent(new CustomEvent('sf:languagechange', { detail: { language: nextLang } }));
  }

  const savedLanguage = (() => {
    try {
      return localStorage.getItem('sf-language');
    } catch (_) {
      return null;
    }
  })();
  applyLanguage(savedLanguage || 'en');

  document.addEventListener('change', (e) => {
    const target = e.target;
    if (!(target instanceof HTMLSelectElement)) return;
    if (!target.matches('[data-language-select]')) return;
    applyLanguage(target.value);
  });

  // ----- Theme -----
  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    root.setAttribute('data-bs-theme', theme);
    root.classList.toggle('dark', theme === 'dark');
    try {
      localStorage.setItem('sf-theme', theme);
    } catch (_) {}
  }

  const savedTheme = (() => {
    try {
      return localStorage.getItem('sf-theme');
    } catch (_) {
      return null;
    }
  })();

  if (savedTheme === 'dark' || savedTheme === 'light') {
    applyTheme(savedTheme);
  }

  window.SF_GET_LANGUAGE = () => currentLanguage;
  window.SF_TRANSLATE_LOOSE_CONTENT = () => translateLooseContent(currentLanguage);

  // ----- Sidebar -----
  function openSidebar() {
    body.classList.add('sf-sidebar-open');
  }
  function closeSidebar() {
    body.classList.remove('sf-sidebar-open');
  }
  function toggleSidebar() {
    body.classList.toggle('sf-sidebar-open');
  }

  // ----- Events -----
  document.addEventListener('click', (e) => {
    const t = e.target;
    if (!(t instanceof Element)) return;

    const action = t.closest('[data-action]')?.getAttribute('data-action');

    if (action === 'toggleTheme') {
      const current = root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
      applyTheme(current === 'dark' ? 'light' : 'dark');
      return;
    }

    if (action === 'toggleSidebar') toggleSidebar();
    if (action === 'openSidebar') openSidebar();
  });

  // Close sidebar on ESC
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeSidebar();
    }
  });

  // ----- Search suggestions -----
  const searchForm = document.querySelector('.sf-search');
  const searchInput = searchForm?.querySelector('.sf-search-input');
  const suggestBox = searchForm?.querySelector('[data-search-suggest]');
  let searchTimer = null;
  function clearSuggestions() {
    if (!suggestBox) return;
    suggestBox.innerHTML = '';
    suggestBox.setAttribute('aria-hidden', 'true');
  }

  function renderSuggestions(items) {
    if (!suggestBox) return;
    if (!items.length) {
      suggestBox.innerHTML = `<div class="sf-suggest-empty">${translateLooseString(currentLanguage, 'No suggestions')}</div>`;
      suggestBox.setAttribute('aria-hidden', 'false');
      return;
    }
    suggestBox.innerHTML = items
      .map(
        (item) => `
        <a class="sf-suggest-item" href="${item.url}">
          <span class="sf-suggest-type">${translateLooseString(currentLanguage, item.type)}</span>
          <span class="sf-suggest-label">${item.label}</span>
        </a>
      `
      )
      .join('');
    suggestBox.setAttribute('aria-hidden', 'false');
    if (currentLanguage === 'km') {
      translateLooseContent('km');
    }
  }

  function fetchSuggestions(query) {
    if (!suggestBox) return;
    clearSuggestions();
  }

  if (searchInput && suggestBox) {
    searchInput.addEventListener('input', () => {
      const value = searchInput.value.trim();
      clearTimeout(searchTimer);
      if (value.length < 2) {
        clearSuggestions();
        return;
      }
      searchTimer = setTimeout(() => fetchSuggestions(value), 180);
    });

    searchInput.addEventListener('focus', () => {
      const value = searchInput.value.trim();
      if (value.length >= 2) {
        fetchSuggestions(value);
      }
    });

    searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        clearSuggestions();
      }
    });

    searchInput.addEventListener('blur', () => {
      setTimeout(clearSuggestions, 120);
    });

  }

  // ----- Hash tabs (home dashboard sections) -----
  function initHashTabs() {
    const tabGroups = Array.from(document.querySelectorAll('.sf-tabs'));
    if (!tabGroups.length) return;

    function parseHashFromHref(href) {
      if (!href || !href.startsWith('#')) return null;
      return href;
    }

    function setActiveTab(tabs, activeHash) {
      let hasMatch = false;
      tabs.forEach((tab) => {
        const tabHash = parseHashFromHref(tab.getAttribute('href'));
        const isActive = tabHash === activeHash;
        if (isActive) hasMatch = true;
        tab.classList.toggle('is-active', isActive);
        if (isActive) {
          tab.setAttribute('aria-current', 'page');
        } else {
          tab.removeAttribute('aria-current');
        }
      });

      if (!hasMatch && tabs.length) {
        tabs[0].classList.add('is-active');
        tabs[0].setAttribute('aria-current', 'page');
      }
    }

    tabGroups.forEach((group) => {
      const tabs = Array.from(group.querySelectorAll('.sf-tab[href^="#"]'));
      if (!tabs.length) return;

      const tabByHash = new Map();
      tabs.forEach((tab) => {
        const hash = parseHashFromHref(tab.getAttribute('href'));
        if (!hash) return;
        tabByHash.set(hash, tab);
      });

      function syncFromHash() {
        const hash = window.location.hash || '';
        if (hash && tabByHash.has(hash)) {
          setActiveTab(tabs, hash);
        } else {
          setActiveTab(tabs, parseHashFromHref(tabs[0].getAttribute('href')));
        }
      }

      tabs.forEach((tab) => {
        tab.addEventListener('click', (e) => {
          const hash = parseHashFromHref(tab.getAttribute('href'));
          if (!hash) return;

          const target = document.querySelector(hash);
          if (!target) return;

          e.preventDefault();
          setActiveTab(tabs, hash);
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          history.replaceState(null, '', hash);
        });
      });

      syncFromHash();
      window.addEventListener('hashchange', syncFromHash);
    });
  }

  // ----- Diagnose page symptom filters -----
  function initDiagnoseFilters() {
    const diagnoseRoot = document.querySelector('[data-diagnose-root]');
    if (!diagnoseRoot) return;

    const searchField = diagnoseRoot.querySelector('[data-symptom-search]');
    const selectedOnly = diagnoseRoot.querySelector('[data-symptom-selected-only]');
    const clearBtn = diagnoseRoot.querySelector('[data-symptom-clear]');
    const filterButtons = Array.from(diagnoseRoot.querySelectorAll('[data-symptom-filter]'));
    const symptomItems = Array.from(diagnoseRoot.querySelectorAll('[data-symptom-item]'));
    const sections = Array.from(diagnoseRoot.querySelectorAll('[data-symptom-section]'));
    const selectedCountEl = diagnoseRoot.querySelector('[data-symptom-selected-count]');
    const visibleCountEl = diagnoseRoot.querySelector('[data-symptom-visible-count]');
    const emptyState = diagnoseRoot.querySelector('[data-symptom-empty]');

    let activeCategory = 'all';

    function getCheckboxes() {
      return Array.from(diagnoseRoot.querySelectorAll('[data-symptom-checkbox]'));
    }

    function setActiveFilterButton() {
      filterButtons.forEach((btn) => {
        const isActive = btn.getAttribute('data-symptom-filter') === activeCategory;
        btn.classList.toggle('is-active', isActive);
      });
    }

    function applyFilters() {
      const keyword = (searchField?.value || '').trim().toLowerCase();
      const selectedOnlyEnabled = !!selectedOnly?.checked;
      let visibleTotal = 0;

      symptomItems.forEach((item) => {
        const label = (item.getAttribute('data-symptom-label') || '').toLowerCase();
        const category = item.getAttribute('data-symptom-category') || '';
        const checkbox = item.querySelector('[data-symptom-checkbox]');
        const isChecked = !!checkbox?.checked;
        const checkItem = item.querySelector('.sf-check-item');
        if (checkItem) checkItem.classList.toggle('is-checked', isChecked);

        const matchesText = !keyword || label.includes(keyword);
        const matchesCategory = activeCategory === 'all' || category === activeCategory;
        const matchesSelected = !selectedOnlyEnabled || isChecked;
        const shouldShow = matchesText && matchesCategory && matchesSelected;

        item.style.display = shouldShow ? '' : 'none';
        if (shouldShow) visibleTotal += 1;
      });

      sections.forEach((section) => {
        const sectionItems = Array.from(section.querySelectorAll('[data-symptom-item]'));
        const visibleInSection = sectionItems.filter((item) => item.style.display !== 'none').length;
        section.style.display = visibleInSection > 0 ? '' : 'none';

        const counter = section.querySelector('[data-symptom-section-count]');
        if (counter) counter.textContent = translateLooseString(currentLanguage, `${visibleInSection} shown`);
      });

      if (emptyState) emptyState.classList.toggle('d-none', visibleTotal > 0);
      if (visibleCountEl) visibleCountEl.textContent = String(visibleTotal);
      if (selectedCountEl) {
        selectedCountEl.textContent = String(getCheckboxes().filter((cb) => cb.checked).length);
      }
    }

    filterButtons.forEach((btn) => {
      btn.addEventListener('click', () => {
        activeCategory = btn.getAttribute('data-symptom-filter') || 'all';
        setActiveFilterButton();
        applyFilters();
      });
    });

    if (searchField) {
      searchField.addEventListener('input', applyFilters);
    }
    if (selectedOnly) {
      selectedOnly.addEventListener('change', applyFilters);
    }
    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        activeCategory = 'all';
        if (searchField) searchField.value = '';
        if (selectedOnly) selectedOnly.checked = false;
        setActiveFilterButton();
        applyFilters();
      });
    }

    getCheckboxes().forEach((cb) => cb.addEventListener('change', applyFilters));

    // Quick keyboard focus: "/" jumps to symptom search field.
    document.addEventListener('keydown', (e) => {
      if (e.key !== '/' || !searchField) return;
      const target = e.target;
      if (
        target instanceof HTMLElement &&
        (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable)
      ) {
        return;
      }
      e.preventDefault();
      searchField.focus();
    });

    setActiveFilterButton();
    applyFilters();
  }

  // ----- Bilingual form language switcher -----
  function initBilingualFormSwitcher() {
    const forms = Array.from(document.querySelectorAll('[data-bilingual-form]'));
    if (!forms.length) return;

    forms.forEach((form) => {
      const buttons = Array.from(form.querySelectorAll('[data-lang-switch]'));
      const panels = Array.from(form.querySelectorAll('[data-lang-panel]'));
      if (!buttons.length || !panels.length) return;

      const available = new Set(
        panels
          .map((panel) => panel.getAttribute('data-lang-panel'))
          .filter(Boolean)
      );

      let active = form.getAttribute('data-default-lang') || 'en';
      if (!available.has(active)) {
        active = panels[0].getAttribute('data-lang-panel') || 'en';
      }

      function setActiveLanguage(lang) {
        if (!available.has(lang)) return;
        active = lang;

        buttons.forEach((btn) => {
          const btnLang = btn.getAttribute('data-lang-switch');
          const isActive = btnLang === active;
          btn.classList.toggle('btn-dark', isActive);
          btn.classList.toggle('btn-outline-dark', !isActive);
          btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
        });

        panels.forEach((panel) => {
          const panelLang = panel.getAttribute('data-lang-panel');
          panel.classList.toggle('d-none', panelLang !== active);
        });
      }

      buttons.forEach((btn) => {
        btn.addEventListener('click', () => {
          const lang = btn.getAttribute('data-lang-switch') || '';
          setActiveLanguage(lang);
        });
      });

      setActiveLanguage(active);
    });
  }

  // ----- Add disease form: quick symptom appender -----
  function initSymptomsBuilder() {
    const forms = Array.from(document.querySelectorAll('form[data-symptoms-builder]'));
    if (!forms.length) return;

    function normalize(value) {
      return String(value || '')
        .replace(/^[-*•\s]+/, '')
        .trim()
        .replace(/\s+/g, ' ');
    }

    function parseTokens(raw) {
      return String(raw || '')
        .split(/[\n,;]+/)
        .map(normalize)
        .filter(Boolean);
    }

    function dedupeTokens(tokens) {
      const out = [];
      const seen = new Set();
      tokens.forEach((token) => {
        const key = token.toLowerCase();
        if (!key || seen.has(key)) return;
        seen.add(key);
        out.push(token);
      });
      return out;
    }

    forms.forEach((form) => {
      const builders = Array.from(form.querySelectorAll('[data-symptom-builder]'));
      if (!builders.length) return;

      builders.forEach((builder) => {
        const targetName = (builder.getAttribute('data-symptom-target') || '').trim();
        const textarea = targetName
          ? form.querySelector(`textarea[name="${targetName}"]`)
          : form.querySelector('textarea[name="symptoms_en"], textarea[name="symptoms"]');
        const input = builder.querySelector('[data-symptom-builder-input]');
        const categorySelect = builder.querySelector('[data-symptom-builder-category]');
        const addBtn = builder.querySelector('[data-symptom-builder-add]');
        if (!textarea || !input || !addBtn) return;

        let items = dedupeTokens(parseTokens(textarea.value));

        const listWrap = document.createElement('div');
        listWrap.className = 'mt-2';
        const listBody = document.createElement('div');
        listBody.className = 'd-flex flex-column gap-2';
        listWrap.appendChild(listBody);
        builder.insertAdjacentElement('afterend', listWrap);

        function setTextareaLockState() {
          textarea.readOnly = true;
          textarea.classList.add('bg-light');
        }

        function syncTextareaValue() {
          textarea.value = items.join('\n');
          textarea.dispatchEvent(new Event('input', { bubbles: true }));
        }

        function renderItems() {
          listBody.innerHTML = '';
          listWrap.classList.toggle('d-none', !items.length);
          setTextareaLockState();

          items.forEach((item, idx) => {
            const row = document.createElement('div');
            row.className = 'd-flex align-items-center justify-content-between gap-2 border rounded px-2 py-1';

            const label = document.createElement('div');
            label.className = 'small flex-grow-1 text-break';
            label.textContent = item;

            const deleteBtn = document.createElement('button');
            deleteBtn.type = 'button';
            deleteBtn.className = 'btn btn-sm btn-outline-danger';
            deleteBtn.setAttribute('data-symptom-builder-delete', String(idx));
            deleteBtn.textContent = translateLooseString(currentLanguage, 'Delete');

            row.append(label, deleteBtn);
            listBody.appendChild(row);
          });
        }

        function addFromInput() {
          const incoming = parseTokens(input.value);
          if (!incoming.length) return;
          const category = normalize(categorySelect?.value || '');

          const existingSet = new Set(items.map((item) => item.toLowerCase()));
          const withCategory = incoming.map((item) =>
            category ? `${category}: ${item}` : item
          );

          const toAppend = withCategory.filter((item) => !existingSet.has(item.toLowerCase()));
          if (!toAppend.length) {
            input.value = '';
            return;
          }

          items = dedupeTokens(items.concat(toAppend));
          syncTextareaValue();
          renderItems();
          input.value = '';
        }

        addBtn.addEventListener('click', addFromInput);

        input.addEventListener('keydown', (e) => {
          if (e.key !== 'Enter') return;
          e.preventDefault();
          addFromInput();
        });

        listBody.addEventListener('click', (e) => {
          const target = e.target;
          if (!(target instanceof Element)) return;

          const deleteBtn = target.closest('[data-symptom-builder-delete]');
          if (!deleteBtn) return;

          const idx = Number(deleteBtn.getAttribute('data-symptom-builder-delete'));
          if (!Number.isInteger(idx) || idx < 0 || idx >= items.length) return;

          items.splice(idx, 1);
          syncTextareaValue();
          renderItems();
        });

        // Normalize pre-filled values (for example after validation errors) and lock editing.
        if (items.length) {
          syncTextareaValue();
        }
        renderItems();
      });
    });
  }

  function initBulletTextareas() {
    const textareas = Array.from(document.querySelectorAll('textarea[data-bullet-textarea]'));
    if (!textareas.length) return;

    function normalizeBullets(value) {
      const rows = String(value || '').split('\n');
      return rows
        .map((row) => {
          const trimmed = row.trim();
          if (!trimmed) return '';
          return `• ${trimmed.replace(/^[•*\-\u2022]+\s*/, '')}`;
        })
        .join('\n');
    }

    textareas.forEach((textarea) => {
      if (!(textarea instanceof HTMLTextAreaElement)) return;

      textarea.addEventListener('keydown', (e) => {
        if (e.key !== 'Enter') return;
        e.preventDefault();

        const start = textarea.selectionStart ?? textarea.value.length;
        const end = textarea.selectionEnd ?? textarea.value.length;
        const currentValue = textarea.value || '';
        const before = currentValue.slice(0, start);
        const after = currentValue.slice(end);
        const currentLine = before.split('\n').pop() || '';
        const lineHasContent = currentLine.trim().length > 0;
        const insert = lineHasContent ? '\n• ' : '\n';

        textarea.value = `${before}${insert}${after}`;
        const nextPos = before.length + insert.length;
        textarea.setSelectionRange(nextPos, nextPos);
        textarea.dispatchEvent(new Event('input', { bubbles: true }));
      });

      textarea.addEventListener('blur', () => {
        const normalized = normalizeBullets(textarea.value);
        if (normalized === textarea.value) return;
        textarea.value = normalized;
        textarea.dispatchEvent(new Event('input', { bubbles: true }));
      });
    });
  }

  // ----- Disease form symptom manager -----
  function initSymptomChecklistManager() {
    const form = document.querySelector('form[data-symptom-manager]');
    if (!form) return;

    const typeButtons = Array.from(form.querySelectorAll('[data-symptom-type]'));
    const sourceFields = Array.from(form.querySelectorAll('[data-symptom-source-key]'));
    const itemInput = form.querySelector('[data-symptom-item-input]');
    const saveBtn = form.querySelector('[data-symptom-save]');
    const cancelEditBtn = form.querySelector('[data-symptom-cancel-edit]');
    const activeTypeLabel = form.querySelector('[data-symptom-active-label]');
    const masterList = form.querySelector('[data-symptom-master-list]');
    const emptyState = form.querySelector('[data-symptom-empty]');
    const totalCountEl = form.querySelector('[data-symptom-total-count]');

    if (!typeButtons.length || !sourceFields.length || !itemInput || !saveBtn || !masterList) return;

    const sourceByKey = new Map();
    const typeMeta = new Map();
    const typeOrder = [];
    let selectedType = null;
    let editingId = null;
    let nextId = 1;
    let items = [];

    function splitTokens(raw) {
      return String(raw || '')
        .split(/[\n,;]+/)
        .map((v) => v.trim().replace(/\s+/g, ' '))
        .filter(Boolean);
    }

    function normalized(value) {
      return String(value || '').trim().replace(/\s+/g, ' ').toLowerCase();
    }

    sourceFields.forEach((field) => {
      const key = field.getAttribute('data-symptom-source-key');
      if (!key) return;
      sourceByKey.set(key, field);
      typeOrder.push(key);
    });

    typeButtons.forEach((btn) => {
      const key = btn.getAttribute('data-symptom-type');
      if (!key) return;
      typeMeta.set(key, {
        title: btn.getAttribute('data-symptom-title') || key,
        placeholder: btn.getAttribute('data-symptom-placeholder') || 'Add symptom',
      });
      if (!selectedType || btn.classList.contains('is-active')) {
        selectedType = key;
      }
    });

    if (!selectedType && typeOrder.length) {
      selectedType = typeOrder[0];
    }

    function itemExists(typeKey, label, ignoreId = null) {
      const needle = normalized(label);
      return items.some(
        (item) =>
          item.typeKey === typeKey &&
          normalized(item.label) === needle &&
          (ignoreId === null || item.id !== ignoreId)
      );
    }

    function setSelectedType(typeKey) {
      if (!typeKey) return;
      selectedType = typeKey;
      typeButtons.forEach((btn) => {
        const key = btn.getAttribute('data-symptom-type');
        btn.classList.toggle('is-active', key === selectedType);
      });

      const meta = typeMeta.get(selectedType);
      if (activeTypeLabel) {
        activeTypeLabel.textContent = translateLooseString(currentLanguage, meta?.title || selectedType);
      }
      if (editingId === null) {
        itemInput.placeholder = translateLooseString(currentLanguage, meta?.placeholder || 'Add symptom');
      }
    }

    function resetEditor() {
      editingId = null;
      itemInput.value = '';
      const meta = typeMeta.get(selectedType);
      itemInput.placeholder = translateLooseString(currentLanguage, meta?.placeholder || 'Add symptom');
      saveBtn.textContent = translateLooseString(currentLanguage, 'Add');
      if (cancelEditBtn) cancelEditBtn.classList.add('d-none');
    }

    function syncSourcesAndCounts() {
      sourceByKey.forEach((field, key) => {
        const labels = items
          .filter((item) => item.typeKey === key)
          .map((item) => item.label);
        field.value = labels.join('\n');

        const countBadge = form.querySelector(`[data-symptom-tab-count="${key}"]`);
        if (countBadge) countBadge.textContent = String(labels.length);
      });

      if (totalCountEl) totalCountEl.textContent = String(items.length);
    }

    function renderList() {
      masterList.innerHTML = '';

      typeOrder.forEach((typeKey) => {
        const meta = typeMeta.get(typeKey);
        const groupItems = items
          .filter((item) => item.typeKey === typeKey)
          .sort((a, b) => a.label.localeCompare(b.label));

        const group = document.createElement('div');
        group.className = 'sf-symptom-group';

        const header = document.createElement('div');
        header.className = 'sf-symptom-group-head';
        const title = document.createElement('span');
        title.className = 'sf-symptom-group-title';
        title.textContent = meta?.title || typeKey;
        const count = document.createElement('span');
        count.className = 'sf-symptom-group-count';
        count.textContent = `${groupItems.length}`;
        header.append(title, count);
        group.appendChild(header);

        if (!groupItems.length) {
          const empty = document.createElement('div');
          empty.className = 'small text-muted';
          empty.textContent = translateLooseString(currentLanguage, 'No items in this type.');
          group.appendChild(empty);
        } else {
          const list = document.createElement('div');
          list.className = 'sf-symptom-rows';

          groupItems.forEach((item) => {
            const row = document.createElement('div');
            row.className = 'sf-symptom-row';

            const label = document.createElement('div');
            label.className = 'sf-symptom-row-label';
            label.textContent = item.label;

            const actions = document.createElement('div');
            actions.className = 'd-flex gap-2';

            const editBtn = document.createElement('button');
            editBtn.type = 'button';
            editBtn.className = 'btn btn-sm btn-outline-dark';
            editBtn.setAttribute('data-symptom-edit-id', String(item.id));
            editBtn.textContent = translateLooseString(currentLanguage, 'Edit');

            const deleteBtn = document.createElement('button');
            deleteBtn.type = 'button';
            deleteBtn.className = 'btn btn-sm btn-outline-danger';
            deleteBtn.setAttribute('data-symptom-delete-id', String(item.id));
            deleteBtn.textContent = translateLooseString(currentLanguage, 'Delete');

            actions.append(editBtn, deleteBtn);
            row.append(label, actions);
            list.appendChild(row);
          });

          group.appendChild(list);
        }

        masterList.appendChild(group);
      });

      if (emptyState) {
        emptyState.classList.toggle('d-none', items.length > 0);
      }
    }

    function startEdit(id) {
      const item = items.find((it) => it.id === id);
      if (!item) return;

      editingId = id;
      setSelectedType(item.typeKey);
      itemInput.value = item.label;
      itemInput.placeholder = translateLooseString(currentLanguage, 'Update symptom item');
      saveBtn.textContent = translateLooseString(currentLanguage, 'Update');
      if (cancelEditBtn) cancelEditBtn.classList.remove('d-none');
      itemInput.focus();
    }

    function saveItem() {
      const tokens = splitTokens(itemInput.value);
      if (!tokens.length || !selectedType) return;

      if (editingId !== null) {
        const updatedLabel = tokens[0];
        const row = items.find((it) => it.id === editingId);
        if (!row) {
          resetEditor();
          return;
        }
        if (!itemExists(selectedType, updatedLabel, editingId)) {
          row.label = updatedLabel;
          row.typeKey = selectedType;
        }
        resetEditor();
      } else {
        tokens.forEach((label) => {
          if (!itemExists(selectedType, label)) {
            items.push({ id: nextId++, typeKey: selectedType, label });
          }
        });
        itemInput.value = '';
      }

      syncSourcesAndCounts();
      renderList();
    }

    function deleteItem(id) {
      items = items.filter((item) => item.id !== id);
      if (editingId === id) {
        resetEditor();
      }
      syncSourcesAndCounts();
      renderList();
    }

    // Load existing values from hidden source fields.
    sourceByKey.forEach((field, typeKey) => {
      const seen = new Set();
      splitTokens(field.value).forEach((label) => {
        const key = normalized(label);
        if (!key || seen.has(key)) return;
        seen.add(key);
        items.push({ id: nextId++, typeKey, label });
      });
    });

    typeButtons.forEach((btn) => {
      btn.addEventListener('click', () => {
        const typeKey = btn.getAttribute('data-symptom-type');
        if (typeKey) setSelectedType(typeKey);
      });
    });

    saveBtn.addEventListener('click', saveItem);

    if (cancelEditBtn) {
      cancelEditBtn.addEventListener('click', resetEditor);
    }

    itemInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        saveItem();
      }
    });

    masterList.addEventListener('click', (e) => {
      const target = e.target;
      if (!(target instanceof Element)) return;

      const editBtn = target.closest('[data-symptom-edit-id]');
      if (editBtn) {
        const id = Number(editBtn.getAttribute('data-symptom-edit-id'));
        if (Number.isInteger(id)) startEdit(id);
        return;
      }

      const deleteBtn = target.closest('[data-symptom-delete-id]');
      if (deleteBtn) {
        const id = Number(deleteBtn.getAttribute('data-symptom-delete-id'));
        if (Number.isInteger(id)) deleteItem(id);
      }
    });

    form.addEventListener('submit', () => {
      if (itemInput.value.trim()) {
        saveItem();
      } else {
        syncSourcesAndCounts();
      }
    });

    setSelectedType(selectedType);
    resetEditor();
    syncSourcesAndCounts();
    renderList();
  }

  // ----- Global scroll interactions (reveal + parallax) -----
  function initScrollEffects() {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const revealSelectors = [
      '[data-reveal]',
      '.sf-page-head',
      '.sf-public-hero',
      '.sf-hero-card',
      '.sf-section-bar',
      '.sf-panel',
      '.sf-card',
      '.sf-action',
      '.sf-section',
      '.sf-disease',
      '.sf-stat-card',
      '.sf-kpi-card',
      '.sf-plot-card',
      '.alert',
    ];

    const revealCandidates = [];
    const revealSeen = new Set();

    revealSelectors.forEach((selector) => {
      document.querySelectorAll(selector).forEach((node) => {
        if (!(node instanceof HTMLElement)) return;
        if (revealSeen.has(node)) return;
        if (node.closest('.sf-sidebar, .sf-topbar, .sf-search-suggest')) return;
        revealSeen.add(node);
        revealCandidates.push(node);
      });
    });

    revealCandidates.forEach((el, idx) => {
      el.classList.add('sf-scroll-reveal');
      const explicitDelay = Number(el.getAttribute('data-reveal-delay'));
      const delay = Number.isFinite(explicitDelay)
        ? explicitDelay
        : Math.min((idx % 6) * 40, 200);
      el.style.setProperty('--sf-reveal-delay', `${delay}ms`);
    });

    if (!prefersReducedMotion) {
      if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(
          (entries) => {
            entries.forEach((entry) => {
              if (!entry.isIntersecting) return;
              entry.target.classList.add('is-inview');
              observer.unobserve(entry.target);
            });
          },
          {
            root: null,
            rootMargin: '0px 0px -12% 0px',
            threshold: 0.14,
          }
        );

        revealCandidates.forEach((el) => observer.observe(el));
      } else {
        revealCandidates.forEach((el) => el.classList.add('is-inview'));
      }
    } else {
      revealCandidates.forEach((el) => el.classList.add('is-inview'));
    }

    const parallaxTargets = [];
    const parallaxSeen = new Set();
    const enableParallax = !prefersReducedMotion && !window.matchMedia('(max-width: 767.98px)').matches;

    function registerParallax(selector, strength) {
      document.querySelectorAll(selector).forEach((node) => {
        if (!(node instanceof HTMLElement)) return;
        if (parallaxSeen.has(node)) return;
        if (node.closest('.sf-sidebar, .sf-topbar, .sf-search-suggest')) return;
        parallaxSeen.add(node);
        node.classList.add('sf-parallax-layer');
        node.style.setProperty('--sf-parallax-shift', '0px');
        parallaxTargets.push({ el: node, strength });
      });
    }

    if (enableParallax) {
      registerParallax('.sf-page-head', 14);
      registerParallax('.sf-public-hero', 10);
      registerParallax('.sf-hero-card', 8);
      registerParallax('.sf-plot-image img', 14);
      registerParallax('.sf-disease-img', 10);
      registerParallax('.sf-img-lg', 12);
      registerParallax('.sf-img', 8);
    }

    let rafPending = false;
    function updateScrollEffects() {
      rafPending = false;

      const scrollY = window.scrollY || window.pageYOffset || 0;
      root.style.setProperty('--sf-scroll-y', `${scrollY}px`);

      const doc = document.documentElement;
      const maxScroll = Math.max(1, doc.scrollHeight - window.innerHeight);
      const ratio = Math.min(1, scrollY / maxScroll);
      root.style.setProperty('--sf-scroll-ratio', ratio.toFixed(4));

      if (!enableParallax || !parallaxTargets.length) return;

      const viewportH = window.innerHeight || 1;
      parallaxTargets.forEach(({ el, strength }) => {
        const rect = el.getBoundingClientRect();
        if (rect.bottom < -120 || rect.top > viewportH + 120) return;
        const centerDelta = (rect.top + rect.height * 0.5 - viewportH * 0.5) / viewportH;
        const shift = Math.max(-30, Math.min(30, -centerDelta * strength));
        el.style.setProperty('--sf-parallax-shift', `${shift.toFixed(2)}px`);
      });
    }

    function queueScrollEffectsUpdate() {
      if (rafPending) return;
      rafPending = true;
      window.requestAnimationFrame(updateScrollEffects);
    }

    queueScrollEffectsUpdate();
    window.addEventListener('scroll', queueScrollEffectsUpdate, { passive: true });
    window.addEventListener('resize', queueScrollEffectsUpdate);
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) queueScrollEffectsUpdate();
    });
  }

  initBilingualFormSwitcher();
  initSymptomsBuilder();
  initBulletTextareas();
  initSymptomChecklistManager();
  initHashTabs();
  initDiagnoseFilters();
  initScrollEffects();
  translateLooseContent(currentLanguage);
})();
