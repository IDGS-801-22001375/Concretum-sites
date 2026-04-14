class CrudManager {
  constructor(config) {
    this.id = config.id;
    this.apiEndpoint = config.apiEndpoint;
    this.columns = config.columns;
    this.formFields = config.formFields;
    this.currentPage = 1;
    this.perPage = config.perPage || 10;
    this.sortBy = config.sortBy || 'id';
    this.sortOrder = 'asc';
    this.searchTerm = '';
    this.filters = config.filters || {};
    this.onEdit = config.onEdit || null;
    this.onSubmit = config.onSubmit || null;

    this._openModal = () => {
      const fn = window[`openModal_${this.id}`];
      if (fn) fn();
      else console.warn('[CrudManager] openModal no encontrado para', this.id);
    };
    this._closeModal = () => {
      const fn = window[`closeModal_${this.id}`];
      if (fn) fn();
      else console.warn('[CrudManager] closeModal no encontrado para', this.id);
    };

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this._init());
    } else {
      this._init();
    }
  }

  _init() {
    this._setupEventListeners();
    this.cargarDatos();
  }

  async cargarDatos() {
    const params = new URLSearchParams({
      page: this.currentPage,
      per_page: this.perPage,
      sort_by: this.sortBy,
      sort_order: this.sortOrder,
      search: this.searchTerm,
      ...this.filters
    });

    const tbody = document.getElementById(`tbody-${this.id}`);
    if (tbody) {
      tbody.innerHTML = `
        <tr>
          <td colspan="99" class="px-6 py-16 text-center">
            <div class="flex flex-col items-center gap-3 text-slate-400 dark:text-slate-500">
              <svg class="w-8 h-8 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581
                     m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
              </svg>
              <span class="text-sm font-medium">Cargando datos...</span>
            </div>
          </td>
        </tr>`;
    }

    try {
      const response = await fetch(`${this.apiEndpoint}/api?${params}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      this.total = data.total;
      this.pages = data.pages;
      this.rawData = data;
      this.renderTabla(data.items);
      this._renderPaginacion(data);
    } catch (err) {
      console.error('[CrudManager] Error cargando datos:', err);
      if (tbody) {
        tbody.innerHTML = `
          <tr>
            <td colspan="99" class="px-6 py-16 text-center">
              <div class="flex flex-col items-center gap-3 text-red-500">
                <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                </svg>
                <span class="text-sm font-medium">Error al cargar datos. Intente de nuevo.</span>
              </div>
            </td>
          </tr>`;
      }
    }
  }

  renderTabla(items) {
    const tbody = document.getElementById(`tbody-${this.id}`);
    if (!tbody) return;

    if (!items || items.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="99" class="px-6 py-16 text-center">
            <div class="flex flex-col items-center gap-3 text-slate-400 dark:text-slate-500">
              <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                  d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
              </svg>
              <span class="text-sm font-medium">Sin registros encontrados</span>
            </div>
          </td>
        </tr>`;
      return;
    }

    let html = '';
    items.forEach(item => {
      const recordId = item.id ?? '';
      html += `<tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">`;

      this.columns.forEach(col => {
        let value = item[col.field];
        if (col.render) {
          value = col.render(value, item);
        } else if (value === null || value === undefined) {
          value = '<span class="text-slate-400">—</span>';
        }
        html += `<td class="px-6 py-4 text-sm text-slate-700 dark:text-slate-300 whitespace-nowrap">${value}</td>`;
      });

      const isActive = item.es_activo ?? true;
      html += `
        <td class="px-6 py-4 text-right">
          <div class="flex items-center justify-end gap-2">
            <button onclick="window.crudManagers['${this.id}'].editar(${recordId})"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-all">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
              </svg>
              Editar
            </button>
            <button onclick="window.crudManagers['${this.id}'].alternarEstado(${recordId})"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold transition-all rounded-lg
                           ${isActive
          ? 'text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20'
          : 'text-emerald-600 hover:text-emerald-700 dark:text-emerald-400 dark:hover:text-emerald-300 hover:bg-emerald-50 dark:hover:bg-emerald-900/20'}">
              ${isActive
          ? `<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"/></svg>`
          : `<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`
        }
              ${isActive ? 'Desactivar' : 'Activar'}
            </button>
          </div>
        </td>`;

      html += `</tr>`;
    });

    tbody.innerHTML = html;
  }

  _renderPaginacion(data) {
    const info = document.getElementById(`pagination-info-${this.id}`);
    const controls = document.getElementById(`pagination-controls-${this.id}`);

    if (info) {
      const from = data.total === 0 ? 0 : (data.page - 1) * data.per_page + 1;
      const to = Math.min(data.page * data.per_page, data.total);
      info.textContent = `Mostrando ${from}–${to} de ${data.total} registros`;
    }

    if (!controls) return;

    const cls = (active) =>
      active
        ? 'px-3 py-1.5 text-sm rounded-lg bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg shadow-blue-600/25'
        : 'px-3 py-1.5 text-sm rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors';

    let html = '';
    if (data.page > 1)
      html += `<button data-page="${data.page - 1}" class="${cls(false)}">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      </button>`;

    const maxBtns = 5;
    const half = Math.floor(maxBtns / 2);
    let start = Math.max(1, data.page - half);
    let end = Math.min(data.pages, start + maxBtns - 1);
    if (end - start < maxBtns - 1) start = Math.max(1, end - maxBtns + 1);

    for (let i = start; i <= end; i++)
      html += `<button data-page="${i}" class="${cls(i === data.page)}">${i}</button>`;

    if (data.page < data.pages)
      html += `<button data-page="${data.page + 1}" class="${cls(false)}">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
      </button>`;

    controls.innerHTML = html;
    controls.querySelectorAll('button[data-page]').forEach(btn => {
      btn.addEventListener('click', () => {
        this.currentPage = parseInt(btn.dataset.page);
        this.cargarDatos();
      });
    });
  }

  async editar(id) {
    try {
      const response = await fetch(`${this.apiEndpoint}/obtener/${id}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const item = await response.json();

      const titleEl = document.getElementById(`modal-title-${this.id}`);
      if (titleEl) titleEl.textContent = 'Editar registro';

      const idField = document.getElementById(`id_${this.id}`);
      if (idField) idField.value = item.id ?? id;

      this.formFields.forEach(field => {
        const el = document.getElementById(field.name);
        if (!el) return;
        el.value = (item[field.name] !== null && item[field.name] !== undefined)
          ? item[field.name] : '';
      });

      if (this.onEdit) this.onEdit(item);
      this._clearErrors();
      this._openModal();
    } catch (err) {
      console.error('[CrudManager] Error al editar:', err);
      this._showFlash('No se pudo cargar el registro.', 'error');
    }
  }

  async alternarEstado(id) {
    const csrfToken = document.querySelector('input[name="csrf_token"]')?.value ?? '';
    try {
      const response = await fetch(`${this.apiEndpoint}/alternar_estado/${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken }
      });
      const data = await response.json();
      if (data.success) {
        this.cargarDatos();
        this._showFlash(data.message, 'success');
      } else {
        this._showFlash(data.message ?? 'Error al cambiar estado.', 'error');
      }
    } catch (err) {
      console.error('[CrudManager] Error alternar estado:', err);
      this._showFlash('Error de conexión.', 'error');
    }
  }

  async guardar(event) {
    event.preventDefault();
    const form = event.target;
    let formData = new FormData(form);
    if (this.onSubmit) formData = this.onSubmit(formData) ?? formData;

    const csrfToken = document.querySelector('input[name="csrf_token"]')?.value ?? '';

    const submitBtn = form.querySelector('button[type="submit"]');
    const originalContent = submitBtn ? submitBtn.innerHTML : '';
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = `
        <svg class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
        </svg>
        Guardando...`;
    }

    try {
      const response = await fetch(`${this.apiEndpoint}/guardar`, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken },
        body: formData
      });
      const data = await response.json();

      if (data.success) {
        this._closeModal();
        this.cargarDatos();
        this._showFlash(data.message ?? 'Guardado correctamente.', 'success');
      } else {
        this._showErrors(data.errors ?? {});
        if (data.message) this._showFlash(data.message, 'error');
      }
    } catch (err) {
      console.error('[CrudManager] Error al guardar:', err);
      this._showFlash('Error de conexión al guardar.', 'error');
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalContent;
      }
    }
  }

  _showErrors(errors) {
    this._clearErrors();
    for (const [field, msg] of Object.entries(errors)) {
      const el = document.querySelector(`#form-${this.id} .error-${field}`);
      if (el) { el.textContent = msg; el.classList.remove('hidden'); }
    }
  }

  _clearErrors() {
    document.querySelectorAll(`#form-${this.id} [class*="error-"]`).forEach(el => {
      if (el.tagName === 'P') { el.classList.add('hidden'); el.textContent = ''; }
    });
  }

  _showFlash(message, category = 'info') {
    const container = document.getElementById('flash-container') || document.querySelector('.fixed.top-5.right-5');
    if (!container) return;

    const colors = {
      success: 'bg-emerald-50 border-emerald-200 text-emerald-800 dark:bg-emerald-950/50 dark:border-emerald-800 dark:text-emerald-200',
      error: 'bg-red-50 border-red-200 text-red-800 dark:bg-red-950/50 dark:border-red-800 dark:text-red-200',
      info: 'bg-sky-50 border-sky-200 text-sky-800 dark:bg-sky-950/50 dark:border-sky-800 dark:text-sky-200',
      warning: 'bg-amber-50 border-amber-200 text-amber-800 dark:bg-amber-950/50 dark:border-amber-800 dark:text-amber-200'
    };
    const icons = {
      success: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>`,
      error: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>`,
      info: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>`,
      warning: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>`
    };

    const div = document.createElement('div');
    div.className = `flex items-start gap-3 px-4 py-3 rounded-xl border shadow-lg backdrop-blur-sm pointer-events-auto max-w-sm ${colors[category] ?? colors.info}`;
    div.style.animation = 'slideIn 0.3s ease-out';
    div.innerHTML = `
      <svg class="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        ${icons[category] ?? icons.info}
      </svg>
      <span class="text-sm font-medium flex-1">${_escHtml(message)}</span>
      <button onclick="this.parentElement.remove()" class="opacity-60 hover:opacity-100 flex-shrink-0 -mr-1">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>`;

    container.prepend(div);
    setTimeout(() => {
      div.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
      div.style.opacity = '0';
      div.style.transform = 'translateX(100%)';
      setTimeout(() => div.remove(), 300);
    }, 4500);
  }

  _setupEventListeners() {
    const btnNuevo = document.getElementById(`btn-nuevo-${this.id}`);
    if (btnNuevo) {
      btnNuevo.addEventListener('click', () => {
        const titleEl = document.getElementById(`modal-title-${this.id}`);
        if (titleEl) titleEl.textContent = 'Nuevo registro';
        const form = document.getElementById(`form-${this.id}`);
        if (form) form.reset();
        const idField = document.getElementById(`id_${this.id}`);
        if (idField) idField.value = '';
        this._clearErrors();
        this._openModal();
      });
    } else {
      console.warn(`[CrudManager] btn-nuevo-${this.id} no encontrado`);
    }

    const form = document.getElementById(`form-${this.id}`);
    if (form) form.addEventListener('submit', (e) => this.guardar(e));

    const search = document.getElementById(`search-input-${this.id}`);
    if (search) {
      let debounce;
      search.addEventListener('input', () => {
        clearTimeout(debounce);
        debounce = setTimeout(() => {
          this.searchTerm = search.value.trim();
          this.currentPage = 1;
          this.cargarDatos();
        }, 350);
      });
    }

    const table = document.getElementById(`tabla-${this.id}`);
    if (table) {
      table.querySelectorAll('th[data-sort]').forEach(th => {
        th.addEventListener('click', () => {
          const sort = th.dataset.sort;
          this.sortOrder = (this.sortBy === sort && this.sortOrder === 'asc') ? 'desc' : 'asc';
          this.sortBy = sort;
          this.cargarDatos();
        });
      });
    }

    const perPage = document.getElementById(`per-page-${this.id}`);
    if (perPage) {
      perPage.addEventListener('change', () => {
        this.perPage = parseInt(perPage.value);
        this.currentPage = 1;
        this.cargarDatos();
      });
    }

    document.querySelectorAll(`[id^="filter-${this.id}-"]`).forEach(el => {
      const filterName = el.id.replace(`filter-${this.id}-`, '');
      const update = () => {
        this.filters[filterName] = el.value;
        this.currentPage = 1;
        this.cargarDatos();
      };
      el.addEventListener('change', update);
      if (el.tagName === 'INPUT') el.addEventListener('input', update);
    });
  }
}

function _escHtml(text) {
  if (!text) return '';
  const d = document.createElement('div');
  d.textContent = text;
  return d.innerHTML;
}

window.crudManagers = {};
