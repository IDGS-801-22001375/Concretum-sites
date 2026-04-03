/* ============================================================
   crud.js — CRM CONCRETUM v2
   ============================================================ */

class CrudManager {
  constructor(config) {
    this.id          = config.id;
    this.apiEndpoint = config.apiEndpoint;
    this.columns     = config.columns;
    this.formFields  = config.formFields;
    this.currentPage = 1;
    this.perPage     = config.perPage || 10;
    this.sortBy      = config.sortBy  || 'id';
    this.sortOrder   = 'asc';
    this.searchTerm  = '';
    this.filters     = config.filters || {};
    this.onEdit      = config.onEdit  || null;
    this.onSubmit    = config.onSubmit|| null;

    this._openModal  = () => {
      const fn = window[`openModal_${this.id}`];
      if (fn) fn();
      else console.warn('[CrudManager] openModal no encontrado para', this.id);
    };
    this._closeModal = () => {
      const fn = window[`closeModal_${this.id}`];
      if (fn) fn();
      else console.warn('[CrudManager] closeModal no encontrado para', this.id);
    };

    /* El script va al final del body, el DOM ya está listo.
       Pero si por alguna razón no, esperamos. */
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

  /* ── cargar datos ────────────────────────────────────────── */
  async cargarDatos() {
    const params = new URLSearchParams({
      page:       this.currentPage,
      per_page:   this.perPage,
      sort_by:    this.sortBy,
      sort_order: this.sortOrder,
      search:     this.searchTerm,
      ...this.filters
    });

    const tbody = document.getElementById(`tbody-${this.id}`);
    if (tbody) {
      tbody.innerHTML = `
        <tr>
          <td colspan="99" class="px-5 py-8 text-center text-gray-400 dark:text-gray-500">
            <div class="flex flex-col items-center gap-2">
              <svg class="w-6 h-6 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581
                     m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
              </svg>
              <span class="text-sm">Cargando...</span>
            </div>
          </td>
        </tr>`;
    }

    try {
      const response = await fetch(`${this.apiEndpoint}/api?${params}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      this.renderTabla(data.items);
      this._renderPaginacion(data);
    } catch (err) {
      console.error('[CrudManager] Error cargando datos:', err);
      if (tbody) {
        tbody.innerHTML = `
          <tr>
            <td colspan="99" class="px-5 py-8 text-center text-sm text-red-500">
              Error al cargar datos. Intente de nuevo.
            </td>
          </tr>`;
      }
    }
  }

  /* ── render tabla ────────────────────────────────────────── */
  renderTabla(items) {
    const tbody = document.getElementById(`tbody-${this.id}`);
    if (!tbody) return;

    if (!items || items.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="99" class="px-5 py-6 text-center">
            <div class="flex flex-col items-center gap-2 text-gray-400 dark:text-gray-500">
              <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                  d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01
                     M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <span class="text-sm">Sin registros encontrados</span>
            </div>
          </td>
        </tr>`;
      return;
    }

    let html = '';
    items.forEach(item => {
      const recordId = item.id ?? '';
      html += `<tr class="hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">`;

      this.columns.forEach(col => {
        let value = item[col.field];
        if (col.render) {
          value = col.render(value, item);
        } else if (value === null || value === undefined) {
          value = '—';
        }
        html += `<td class="px-5 py-3.5 text-sm text-gray-700 dark:text-gray-300 whitespace-nowrap">${value}</td>`;
      });

      const isActive = item.es_activo ?? true;
      html += `
        <td class="px-5 py-3.5 text-right">
          <div class="flex items-center justify-end gap-3">
            <button onclick="window.crudManagers['${this.id}'].editar(${recordId})"
                    class="text-xs font-bold text-blue-600 hover:text-blue-800
       dark:text-blue-300 dark:hover:text-blue-100 transition-colors">
              Editar
            </button>
            <button onclick="window.crudManagers['${this.id}'].alternarEstado(${recordId})"
                    class="text-xs font-medium transition-colors
                           ${isActive
                             ? 'text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300'
                             : 'text-green-600 hover:text-green-800 dark:text-green-400 dark:hover:text-green-300'}">
              ${isActive ? 'Desactivar' : 'Activar'}
            </button>
          </div>
        </td>`;

      html += `</tr>`;
    });

    tbody.innerHTML = html;
  }

  /* ── paginación ──────────────────────────────────────────── */
  _renderPaginacion(data) {
    const info     = document.getElementById(`pagination-info-${this.id}`);
    const controls = document.getElementById(`pagination-controls-${this.id}`);

    if (info) {
      const from = data.total === 0 ? 0 : (data.page - 1) * data.per_page + 1;
      const to   = Math.min(data.page * data.per_page, data.total);
      info.textContent = `Mostrando ${from}–${to} de ${data.total} registros`;
    }

    if (!controls) return;

    const cls = (active) =>
      `px-3 py-1.5 text-xs rounded-lg border transition-colors ` +
      (active
        ? 'bg-blue-600 text-white border-blue-600'
        : 'border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700');

    let html = '';
    if (data.page > 1)
      html += `<button data-page="${data.page - 1}" class="${cls(false)}">‹</button>`;

    const maxBtns = 5;
    const half    = Math.floor(maxBtns / 2);
    let start     = Math.max(1, data.page - half);
    let end       = Math.min(data.pages, start + maxBtns - 1);
    if (end - start < maxBtns - 1) start = Math.max(1, end - maxBtns + 1);

    for (let i = start; i <= end; i++)
      html += `<button data-page="${i}" class="${cls(i === data.page)}">${i}</button>`;

    if (data.page < data.pages)
      html += `<button data-page="${data.page + 1}" class="${cls(false)}">›</button>`;

    controls.innerHTML = html;
    controls.querySelectorAll('button[data-page]').forEach(btn => {
      btn.addEventListener('click', () => {
        this.currentPage = parseInt(btn.dataset.page);
        this.cargarDatos();
      });
    });
  }

  /* ── editar ──────────────────────────────────────────────── */
  async editar(id) {
    try {
      const response = await fetch(`${this.apiEndpoint}/obtener/${id}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const item = await response.json();

      const titleEl = document.getElementById(`modal-title-${this.id}`);
      if (titleEl) titleEl.textContent = 'Editar registro';

      /* El hidden del ID puede tener distintos nombres según id_field del macro.
         Intentamos con id_{id_modal} que es lo que genera el macro. */
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

  /* ── alternar estado ─────────────────────────────────────── */
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

  /* ── guardar ─────────────────────────────────────────────── */
  async guardar(event) {
    event.preventDefault();
    const form = event.target;
    let formData = new FormData(form);
    if (this.onSubmit) formData = this.onSubmit(formData) ?? formData;

    const csrfToken = document.querySelector('input[name="csrf_token"]')?.value ?? '';

    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Guardando...';
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
        submitBtn.innerHTML = `
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
          Guardar`;
      }
    }
  }

  /* ── errores ─────────────────────────────────────────────── */
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

  /* ── flash ───────────────────────────────────────────────── */
  _showFlash(message, category = 'info') {
    const container = document.querySelector('.fixed.top-5.right-5');
    if (!container) return;

    const colors = {
      success: 'bg-green-50 border-green-200 text-green-800 dark:bg-green-900/40 dark:text-green-300',
      error:   'bg-red-50 border-red-200 text-red-800 dark:bg-red-900/40 dark:text-red-300',
      info:    'bg-blue-50 border-blue-200 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300'
    };
    const icons = {
      success: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>`,
      error:   `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>`,
      info:    `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>`
    };

    const div = document.createElement('div');
    div.className = `flex items-start gap-3 p-4 rounded-xl border shadow-lg max-w-sm ${colors[category] ?? colors.info}`;
    div.innerHTML = `
      <svg class="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        ${icons[category] ?? icons.info}
      </svg>
      <span class="text-sm font-medium flex-1">${_escHtml(message)}</span>
      <button onclick="this.parentElement.remove()" class="opacity-60 hover:opacity-100 flex-shrink-0">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>`;

    container.prepend(div);
    setTimeout(() => {
      div.style.transition = 'opacity 0.4s ease';
      div.style.opacity    = '0';
      setTimeout(() => div.remove(), 400);
    }, 4500);
  }

  /* ── event listeners ─────────────────────────────────────── */
  _setupEventListeners() {
    /* Botón "+ Nuevo" */
    const btnNuevo = document.getElementById(`btn-nuevo-${this.id}`);
    if (btnNuevo) {
      btnNuevo.addEventListener('click', () => {
        const titleEl = document.getElementById(`modal-title-${this.id}`);
        if (titleEl) titleEl.textContent = 'Registrar nuevo';
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

    /* Submit */
    const form = document.getElementById(`form-${this.id}`);
    if (form) form.addEventListener('submit', (e) => this.guardar(e));

    /* Búsqueda con debounce */
    const search = document.getElementById(`search-input-${this.id}`);
    if (search) {
      let debounce;
      search.addEventListener('input', () => {
        clearTimeout(debounce);
        debounce = setTimeout(() => {
          this.searchTerm  = search.value.trim();
          this.currentPage = 1;
          this.cargarDatos();
        }, 350);
      });
    }

    /* Ordenamiento */
    const table = document.getElementById(`tabla-${this.id}`);
    if (table) {
      table.querySelectorAll('th[data-sort]').forEach(th => {
        th.addEventListener('click', () => {
          const sort = th.dataset.sort;
          this.sortOrder = (this.sortBy === sort && this.sortOrder === 'asc') ? 'desc' : 'asc';
          this.sortBy    = sort;
          this.cargarDatos();
        });
      });
    }

    /* Registros por página */
    const perPage = document.getElementById(`per-page-${this.id}`);
    if (perPage) {
      perPage.addEventListener('change', () => {
        this.perPage     = parseInt(perPage.value);
        this.currentPage = 1;
        this.cargarDatos();
      });
    }

    /* Filtros: id="filter-{id_table}-{nombre_filtro}" */
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

/* helper global */
function _escHtml(text) {
  if (!text) return '';
  const d = document.createElement('div');
  d.textContent = text;
  return d.innerHTML;
}

window.crudManagers = {};