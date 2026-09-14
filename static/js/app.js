/**
 * Logic-Analisis Web Application
 * Manejo interactivo de la interfaz: tabla de verdad dinámica (2 a 5 bits),
 * selección de familias de diagramas, filtros, procesamiento asíncrono y descarga.
 */

let currentBits = 4;
const varNamesPool = ['A', 'B', 'C', 'D', 'E'];
let rowValues = {};
let currentKmapTab = 'min';
const allDiagramIds = [
  'sop_and_or_not',
  'pos_and_or_not',
  'sop_nand',
  'sop_nand_reducido',
  'pos_nand',
  'pos_nand_reducido',
  'pos_nor',
  'pos_nor_reducido',
  'sop_nor',
  'sop_nor_reducido'
];

function getSelectedDiagrams() {
  return allDiagramIds.filter(id => {
    const el = document.getElementById('chk_' + id);
    return el && el.checked;
  });
}

function updateSelectedDiagramsCount() {
  const selected = getSelectedDiagrams();
  const lbl = document.getElementById('lblDiagCount');
  if (lbl) {
    lbl.innerText = `${selected.length} de ${allDiagramIds.length}`;
  }
  
  const zipQuery = selected.length === allDiagramIds.length
    ? '/api/download_zip'
    : (selected.length === 0 ? '#' : `/api/download_zip?diagrams=${selected.join(',')}`);

  document.querySelectorAll('.zip-download-btn').forEach(btn => {
    btn.href = zipQuery;
    if (selected.length === 0) {
      btn.classList.add('opacity-50', 'pointer-events-none');
    } else {
      btn.classList.remove('opacity-50', 'pointer-events-none');
    }
  });

  applyDiagramFiltering();
}

function selectDiagramGroup(group) {
  let targetSet = new Set();
  if (group === 'all') {
    targetSet = new Set(allDiagramIds);
  } else if (group === 'reduced') {
    targetSet = new Set(['sop_nand_reducido', 'pos_nand_reducido', 'pos_nor_reducido', 'sop_nor_reducido']);
  } else if (group === 'and_or') {
    targetSet = new Set(['sop_and_or_not', 'pos_and_or_not']);
  } else if (group === 'nand') {
    targetSet = new Set(['sop_nand', 'sop_nand_reducido', 'pos_nand', 'pos_nand_reducido']);
  } else if (group === 'nor') {
    targetSet = new Set(['pos_nor', 'pos_nor_reducido', 'sop_nor', 'sop_nor_reducido']);
  } else if (group === 'none') {
    targetSet = new Set();
  }

  allDiagramIds.forEach(id => {
    const el = document.getElementById('chk_' + id);
    if (el) el.checked = targetSet.has(id);
  });

  updateSelectedDiagramsCount();
}

function applyDiagramFiltering() {
  const selected = new Set(getSelectedDiagrams());

  allDiagramIds.forEach(id => {
    const card = document.getElementById('card_' + id);
    if (card) {
      if (selected.has(id)) {
        card.classList.remove('hidden');
      } else {
        card.classList.add('hidden');
      }
    }
  });

  const andOrVisible = ['sop_and_or_not', 'pos_and_or_not'].some(id => selected.has(id));
  const emptyAndOr = document.getElementById('empty_gallery_and_or');
  if (emptyAndOr) emptyAndOr.classList.toggle('hidden', andOrVisible);

  const nandVisible = ['sop_nand', 'sop_nand_reducido', 'pos_nand', 'pos_nand_reducido'].some(id => selected.has(id));
  const emptyNand = document.getElementById('empty_gallery_nand');
  if (emptyNand) emptyNand.classList.toggle('hidden', nandVisible);

  const norVisible = ['pos_nor', 'pos_nor_reducido', 'sop_nor', 'sop_nor_reducido'].some(id => selected.has(id));
  const emptyNor = document.getElementById('empty_gallery_nor');
  if (emptyNor) emptyNor.classList.toggle('hidden', norVisible);

  allDiagramIds.forEach(id => {
    const row = document.getElementById('tbl_row_' + id);
    if (row) {
      if (selected.has(id)) {
        row.classList.remove('opacity-25', 'grayscale');
      } else {
        row.classList.add('opacity-25', 'grayscale');
      }
    }
  });
}

function setNumBits(n) {
  if (n < 2 || n > 5) return;
  currentBits = n;
  
  for (let b = 2; b <= 5; b++) {
    const btn = document.getElementById('btnBit' + b);
    if (btn) {
      if (b === n) {
        btn.className = 'bit-btn px-4 py-2 text-xs font-bold rounded-xl border bg-brand-600 border-brand-600 text-white shadow-md shadow-brand-500/20 transition';
      } else {
        btn.className = 'bit-btn px-4 py-2 text-xs font-bold rounded-xl border bg-slate-50 hover:bg-slate-100 border-slate-200 text-slate-700 transition';
      }
    }
  }

  const total = 2 ** n;
  const defaultZeros = [0, 1, 2, 5, 6, 7, 11, 15];
  rowValues = {};
  for (let i = 0; i < total; i++) {
    rowValues[i] = (n === 4 && defaultZeros.includes(i)) ? 0 : (i === 0 ? 0 : 1);
  }

  renderTruthTable();
  updateLabels();
}

function toggleRowValue(idx) {
  rowValues[idx] = rowValues[idx] === 0 ? 1 : 0;
  updateRowButton(idx);
  updateLabels();
}

function updateRowButton(idx) {
  const btn = document.getElementById('rowBtn_' + idx);
  if (!btn) return;
  const val = rowValues[idx];
  if (val === 0) {
    btn.className = 'w-full py-1.5 px-3 rounded-lg font-mono font-bold text-xs bg-rose-50 border border-rose-200 text-rose-700 hover:bg-rose-100 flex items-center justify-between shadow-xs transition';
    btn.innerHTML = `<span>0</span><span class="text-[10px] font-semibold text-rose-600 uppercase">Maxitérmino (0)</span>`;
  } else {
    btn.className = 'w-full py-1.5 px-3 rounded-lg font-mono font-bold text-xs bg-emerald-50 border border-emerald-200 text-emerald-700 hover:bg-emerald-100 flex items-center justify-between shadow-xs transition';
    btn.innerHTML = `<span>1</span><span class="text-[10px] font-semibold text-emerald-600 uppercase">Minitérmino (1)</span>`;
  }
}

function renderTruthTable() {
  const container = document.getElementById('truthTableContainer');
  container.innerHTML = '';

  const totalRows = 2 ** currentBits;
  const activeVars = varNamesPool.slice(0, currentBits);

  const half = Math.ceil(totalRows / 2);
  const parts = [
    { start: 0, end: half },
    { start: half, end: totalRows }
  ];

  parts.forEach((part) => {
    const tableCard = document.createElement('div');
    tableCard.className = 'overflow-hidden rounded-xl border border-slate-200 bg-white shadow-xs';

    let tableHtml = `
      <table class="min-w-full text-xs text-left divide-y divide-slate-200">
        <thead class="bg-slate-100 text-slate-600 font-bold uppercase tracking-wider text-[11px]">
          <tr>
            <th class="py-2.5 px-3 text-center">#</th>
            ${activeVars.map(v => `<th class="py-2.5 px-2 text-center font-mono text-slate-800">${v}</th>`).join('')}
            <th class="py-2.5 px-3 text-center font-bold text-slate-900 bg-slate-200/60">Salida f</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100 font-mono">
    `;

    for (let i = part.start; i < part.end; i++) {
      const binStr = i.toString(2).padStart(currentBits, '0');
      const bits = binStr.split('');

      tableHtml += `
        <tr class="hover:bg-slate-50 transition">
          <td class="py-1.5 px-3 text-center font-semibold text-slate-500 text-[11px]">m${i}</td>
          ${bits.map(b => `<td class="py-1.5 px-2 text-center text-slate-600">${b}</td>`).join('')}
          <td class="py-1 px-3 text-center">
            <button type="button" id="rowBtn_${i}" onclick="toggleRowValue(${i})">
            </button>
          </td>
        </tr>
      `;
    }

    tableHtml += `
        </tbody>
      </table>
    `;

    tableCard.innerHTML = tableHtml;
    container.appendChild(tableCard);

    for (let i = part.start; i < part.end; i++) {
      updateRowButton(i);
    }
  });
}

function updateLabels() {
  const activeVars = varNamesPool.slice(0, currentBits);
  document.getElementById('lblVars').innerText = activeVars.join(', ');

  const totalRows = 2 ** currentBits;
  document.getElementById('lblTotalRows').innerText = `${totalRows} combinaciones`;

  let zeros = 0;
  let ones = 0;
  for (let i = 0; i < totalRows; i++) {
    if (rowValues[i] === 0) zeros++;
    else ones++;
  }
  document.getElementById('cntZeros').innerText = zeros;
  document.getElementById('cntOnes').innerText = ones;
}

function setAllValues(val) {
  const total = 2 ** currentBits;
  for (let i = 0; i < total; i++) {
    rowValues[i] = val;
    updateRowButton(i);
  }
  updateLabels();
}

function invertAllValues() {
  const total = 2 ** currentBits;
  for (let i = 0; i < total; i++) {
    rowValues[i] = rowValues[i] === 0 ? 1 : 0;
    updateRowButton(i);
  }
  updateLabels();
}

function loadDefaultProblem() {
  setNumBits(4);
  const defaultZeros = [0, 1, 2, 5, 6, 7, 11, 15];
  for (let i = 0; i < 16; i++) {
    rowValues[i] = defaultZeros.includes(i) ? 0 : 1;
    updateRowButton(i);
  }
  updateLabels();
  processCurrentTable();
}

async function processCurrentTable() {
  const btn = document.getElementById('btnProcess');
  const origHtml = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i><span>Procesando función...</span>';

  const total = 2 ** currentBits;
  const zeros = [];
  const ones = [];
  for (let i = 0; i < total; i++) {
    if (rowValues[i] === 0) zeros.push(i);
    else ones.push(i);
  }

  const activeVars = varNamesPool.slice(0, currentBits);

  try {
    const response = await fetch('/api/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        num_bits: currentBits,
        variables: activeVars,
        zeros: zeros,
        ones: ones
      })
    });

    const json = await response.json();
    if (!json.success) {
      alert('Error al procesar: ' + json.error);
      return;
    }

    const d = json.data;
    const timestamp = Date.now();

    document.getElementById('resultsSection').classList.remove('hidden');

    document.getElementById('unreducedSop').innerText = d.unreduced_sop || '0';
    document.getElementById('unreducedPos').innerText = d.unreduced_pos || '1';
    document.getElementById('reducedSop').innerText = d.reduced_sop || '0';
    document.getElementById('reducedPos').innerText = d.reduced_pos || '1';

    switchKmapTab(currentKmapTab);

    // Actualizar dinámicamente las 10 tarjetas de diagramas y las etiquetas del Paso 3
    d.tabla_conteo.forEach(r => {
      const card = document.getElementById('card_' + r.id);
      if (card) {
        const img = card.querySelector('img');
        if (img) {
          img.src = '/static/generated/' + r.archivo + '?t=' + timestamp;
        }
        const dl = card.querySelector('a[download]');
        if (dl) {
          dl.href = '/static/generated/' + r.archivo + '?t=' + timestamp;
        }
        const p = card.querySelector('p');
        if (p) {
          if (r.tipo === 'AND / OR / NOT') {
            p.innerText = `${r.not} NOT + ${r.and} AND + ${r.or} OR = ${r.total} compuertas (2 entradas)`;
          } else if (r.nand > 0) {
            p.innerText = `${r.nand} compuertas NAND de 2 entradas`;
          } else if (r.nor > 0) {
            p.innerText = `${r.nor} compuertas NOR de 2 entradas`;
          }
        }
        resetZoomDiagram('img_' + r.id);
      }

      // Actualizar subtítulo en el checkbox del Paso 3
      const chk = document.getElementById('chk_' + r.id);
      if (chk) {
        const lbl = chk.closest('label');
        const lblP = lbl ? lbl.querySelector('p') : null;
        if (lblP) {
          if (r.tipo === 'AND / OR / NOT') {
            lblP.innerText = `${r.not} NOT + ${r.and} AND + ${r.or} OR = ${r.total} compuertas`;
          } else if (r.nand > 0) {
            lblP.innerText = `${r.nand} compuertas NAND de 2 entradas`;
          } else if (r.nor > 0) {
            lblP.innerText = `${r.nor} compuertas NOR de 2 entradas`;
          }
        }
      }
    });

    // Actualizar badges de ahorro en compuertas de los diagramas reducidos
    const sopNandDir = d.tabla_conteo.find(x => x.id === 'sop_nand')?.total || 0;
    const sopNandRed = d.tabla_conteo.find(x => x.id === 'sop_nand_reducido')?.total || 0;
    const bSopNand = document.querySelector('#card_sop_nand_reducido .bg-brand-100');
    if (bSopNand) bSopNand.innerText = `${Math.max(0, sopNandDir - sopNandRed)} compuertas ahorradas`;

    const posNandDir = d.tabla_conteo.find(x => x.id === 'pos_nand')?.total || 0;
    const posNandRed = d.tabla_conteo.find(x => x.id === 'pos_nand_reducido')?.total || 0;
    const bPosNand = document.querySelector('#card_pos_nand_reducido .bg-brand-100');
    if (bPosNand) bPosNand.innerText = `${Math.max(0, posNandDir - posNandRed)} compuertas ahorradas`;

    const posNorDir = d.tabla_conteo.find(x => x.id === 'pos_nor')?.total || 0;
    const posNorRed = d.tabla_conteo.find(x => x.id === 'pos_nor_reducido')?.total || 0;
    const bPosNor = document.querySelector('#card_pos_nor_reducido .bg-brand-100');
    if (bPosNor) bPosNor.innerText = `${Math.max(0, posNorDir - posNorRed)} compuertas ahorradas`;

    const sopNorDir = d.tabla_conteo.find(x => x.id === 'sop_nor')?.total || 0;
    const sopNorRed = d.tabla_conteo.find(x => x.id === 'sop_nor_reducido')?.total || 0;
    const bSopNor = document.querySelector('#card_sop_nor_reducido .bg-brand-100');
    if (bSopNor) bSopNor.innerText = `${Math.max(0, sopNorDir - sopNorRed)} compuertas ahorradas`;

    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';
    d.tabla_conteo.forEach(r => {
      const tr = document.createElement('tr');
      tr.id = 'tbl_row_' + r.id;
      tr.className = 'hover:bg-slate-50 transition';
      tr.innerHTML = `
        <td class="px-4 py-2.5 font-bold text-slate-700">${r.num}</td>
        <td class="px-4 py-2.5 font-semibold text-slate-900">${r.nombre}</td>
        <td class="px-4 py-2.5 text-xs text-slate-500">${r.tipo}</td>
        <td class="px-3 py-2.5 text-center">${r.not}</td>
        <td class="px-3 py-2.5 text-center">${r.and}</td>
        <td class="px-3 py-2.5 text-center">${r.or}</td>
        <td class="px-3 py-2.5 text-center">${r.nand}</td>
        <td class="px-3 py-2.5 text-center">${r.nor}</td>
        <td class="px-4 py-2.5 text-center font-bold text-slate-900 bg-slate-50">${r.total}</td>
      `;
      tbody.appendChild(tr);
    });

    applyDiagramFiltering();

  } catch (err) {
    alert('Error de conexión: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = origHtml;
  }
}

async function downloadConfigFile() {
  const total = 2 ** currentBits;
  const zeros = [];
  for (let i = 0; i < total; i++) {
    if (rowValues[i] === 0) zeros.push(i);
  }
  const activeVars = varNamesPool.slice(0, currentBits);

  const res = await fetch('/api/download_config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ variables: activeVars, zeros: zeros })
  });
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'funcion.txt';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function handleFileSelected(e) {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = function(evt) {
    const text = evt.target.result;
    parseAndApplyFileContent(text);
  };
  reader.readAsText(file);
}

function parseAndApplyFileContent(text) {
  let variables = null;
  let zeros = null;
  let ones = null;
  let nBits = null;

  text.split('\n').forEach(line => {
    line = line.trim();
    if (line.includes('#')) line = line.split('#')[0].trim();
    if (line.includes('//')) line = line.split('//')[0].trim();
    if (!line) return;

    if (line.includes('=') || line.includes(':')) {
      const sep = line.includes('=') ? '=' : ':';
      const parts = line.split(sep);
      const k = parts[0].trim().toLowerCase();
      const v = parts.slice(1).join(sep).trim();

      if (['variables', 'vars', 'var'].includes(k)) {
        variables = v.split(/[,; ]+/).map(x => x.trim().toUpperCase()).filter(x => x.length > 0);
      } else if (['bits', 'num_bits'].includes(k)) {
        nBits = parseInt(v);
      } else if (['f', 'salidas_en_0', 'ceros', 'maxiterminos'].includes(k)) {
        const matches = v.match(/\b\d+\b/g);
        if (matches) zeros = matches.map(Number);
      } else if (["f'", 'salidas_en_1', 'unos', 'miniterminos'].includes(k)) {
        const matches = v.match(/\b\d+\b/g);
        if (matches) ones = matches.map(Number);
      }
    }
  });

  let detectedBits = nBits || (variables ? variables.length : 4);
  if (zeros && zeros.length > 0) {
    const maxZ = Math.max(...zeros);
    detectedBits = Math.max(detectedBits, maxZ.toString(2).length);
  }
  if (ones && ones.length > 0) {
    const maxO = Math.max(...ones);
    detectedBits = Math.max(detectedBits, maxO.toString(2).length);
  }
  detectedBits = Math.min(5, Math.max(2, detectedBits));

  setNumBits(detectedBits);
  const total = 2 ** detectedBits;

  if (zeros) {
    for (let i = 0; i < total; i++) {
      rowValues[i] = zeros.includes(i) ? 0 : 1;
      updateRowButton(i);
    }
  } else if (ones) {
    for (let i = 0; i < total; i++) {
      rowValues[i] = ones.includes(i) ? 1 : 0;
      updateRowButton(i);
    }
  }

  updateLabels();
  processCurrentTable();
}

function switchKmapTab(tab) {
  currentKmapTab = tab;
  const img = document.getElementById('kmapImage');
  const btnMin = document.getElementById('btnKmapMin');
  const btnMax = document.getElementById('btnKmapMax');
  const dlBtn = document.getElementById('kmapDownloadBtn');
  const t = Date.now();

  if (tab === 'min') {
    img.src = '/static/generated/kmap_miniterminos.png?t=' + t;
    dlBtn.href = '/static/generated/kmap_miniterminos.png?t=' + t;
    btnMin.className = 'px-3 py-1.5 text-xs font-semibold rounded-lg bg-brand-600 text-white shadow-sm transition';
    btnMax.className = 'px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 transition';
  } else {
    img.src = '/static/generated/kmap_maxiterminos.png?t=' + t;
    dlBtn.href = '/static/generated/kmap_maxiterminos.png?t=' + t;
    btnMax.className = 'px-3 py-1.5 text-xs font-semibold rounded-lg bg-brand-600 text-white shadow-sm transition';
    btnMin.className = 'px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 transition';
  }
}

function switchCircuitFamily(fam) {
  const gAndOr = document.getElementById('gallery_and_or');
  const gNand = document.getElementById('gallery_nand');
  const gNor = document.getElementById('gallery_nor');

  const tAndOr = document.getElementById('tab_and_or');
  const tNand = document.getElementById('tab_nand');
  const tNor = document.getElementById('tab_nor');

  [gAndOr, gNand, gNor].forEach(g => g.classList.add('hidden'));
  [tAndOr, tNand, tNor].forEach(t => {
    t.className = 'px-3 py-1.5 font-semibold rounded-lg text-slate-600 hover:text-slate-900 transition';
  });

  if (fam === 'and_or') {
    gAndOr.classList.remove('hidden');
    tAndOr.className = 'px-3 py-1.5 font-semibold rounded-lg bg-white shadow-sm text-slate-900 transition';
  } else if (fam === 'nand') {
    gNand.classList.remove('hidden');
    tNand.className = 'px-3 py-1.5 font-semibold rounded-lg bg-white shadow-sm text-slate-900 transition';
  } else {
    gNor.classList.remove('hidden');
    tNor.className = 'px-3 py-1.5 font-semibold rounded-lg bg-white shadow-sm text-slate-900 transition';
  }
}

// =============================================================================
// ZOOM Y PAN INTERACTIVO PARA DIAGRAMAS
// =============================================================================
const zoomLevels = {};

function getZoomLevel(imgId) {
  if (zoomLevels[imgId] === undefined) zoomLevels[imgId] = 1.0;
  return zoomLevels[imgId];
}

function updateZoomLabel(imgId, val) {
  const lbl = document.getElementById('zoom_label_' + imgId);
  if (lbl) {
    lbl.innerText = Math.round(val * 100) + '%';
  }
}

function zoomDiagram(imgId, delta) {
  const img = document.getElementById(imgId);
  if (!img) return;
  let cur = getZoomLevel(imgId);
  cur = Math.min(4.0, Math.max(0.3, cur + delta));
  zoomLevels[imgId] = cur;
  applyDiagramZoom(imgId);
}

function resetZoomDiagram(imgId) {
  zoomLevels[imgId] = 1.0;
  applyDiagramZoom(imgId, true);
}

function fitZoomDiagram(imgId) {
  const img = document.getElementById(imgId);
  if (!img) return;
  zoomLevels[imgId] = 1.0;
  img.style.transform = 'scale(1)';
  img.style.maxWidth = '100%';
  img.style.width = 'auto';
  updateZoomLabel(imgId, 1.0);
}

function applyDiagramZoom(imgId, isReset = false) {
  const img = document.getElementById(imgId);
  if (!img) return;
  const zoom = getZoomLevel(imgId);
  img.style.maxWidth = (zoom > 1.0 || isReset) ? 'none' : '100%';
  img.style.transform = `scale(${zoom})`;
  img.style.transformOrigin = 'center center';
  updateZoomLabel(imgId, zoom);
}

// Paneo por arrastre del mouse (Drag to Pan)
function initDiagramViewports() {
  document.querySelectorAll('.diagram-viewport').forEach(vp => {
    let isDown = false;
    let startX, startY, scrollLeft, scrollTop;

    vp.addEventListener('mousedown', (e) => {
      if (e.target.closest('button') || e.target.closest('a')) return;
      isDown = true;
      vp.classList.add('cursor-grabbing');
      startX = e.pageX - vp.offsetLeft;
      startY = e.pageY - vp.offsetTop;
      scrollLeft = vp.scrollLeft;
      scrollTop = vp.scrollTop;
    });

    vp.addEventListener('mouseleave', () => {
      isDown = false;
      vp.classList.remove('cursor-grabbing');
    });

    vp.addEventListener('mouseup', () => {
      isDown = false;
      vp.classList.remove('cursor-grabbing');
    });

    vp.addEventListener('mousemove', (e) => {
      if (!isDown) return;
      e.preventDefault();
      const x = e.pageX - vp.offsetLeft;
      const y = e.pageY - vp.offsetTop;
      const walkX = (x - startX) * 1.5;
      const walkY = (y - startY) * 1.5;
      vp.scrollLeft = scrollLeft - walkX;
      vp.scrollTop = scrollTop - walkY;
    });

    // Zoom con Ctrl + Rueda de ratón en el viewport
    vp.addEventListener('wheel', (e) => {
      if (e.ctrlKey) {
        e.preventDefault();
        const img = vp.querySelector('.diagram-img');
        if (img) {
          const delta = e.deltaY < 0 ? 0.15 : -0.15;
          zoomDiagram(img.id, delta);
        }
      }
    }, { passive: false });
  });
}

// =============================================================================
// MODAL LIGHTBOX DE ALTA RESOLUCIÓN
// =============================================================================
let lightboxZoomLevel = 1.0;
let lbIsDown = false;
let lbStartX, lbStartY, lbTranslateX = 0, lbTranslateY = 0;

function openDiagramLightbox(imgId, title, subtitle) {
  const sourceImg = document.getElementById(imgId);
  if (!sourceImg) return;

  const modal = document.getElementById('diagramLightbox');
  const lbImg = document.getElementById('lightboxImg');
  const lbTitle = document.getElementById('lightboxTitle');
  const lbSub = document.getElementById('lightboxSubtitle');
  const lbDl = document.getElementById('lightboxDownloadBtn');

  lbImg.src = sourceImg.src;
  lbTitle.innerText = title || 'Diagrama Lógico';
  lbSub.innerText = subtitle || 'Visualización de alta resolución con compuertas de 2 entradas';
  if (lbDl) lbDl.href = sourceImg.src;

  lightboxZoomLevel = 1.0;
  lbTranslateX = 0;
  lbTranslateY = 0;
  updateLightboxTransform();

  modal.classList.remove('hidden');
  document.body.classList.add('overflow-hidden');
}

function closeDiagramLightbox() {
  const modal = document.getElementById('diagramLightbox');
  if (modal) modal.classList.add('hidden');
  document.body.classList.remove('overflow-hidden');
}

function lightboxZoom(delta) {
  lightboxZoomLevel = Math.min(5.0, Math.max(0.2, lightboxZoomLevel + delta));
  updateLightboxTransform();
}

function lightboxResetZoom() {
  lightboxZoomLevel = 1.0;
  lbTranslateX = 0;
  lbTranslateY = 0;
  updateLightboxTransform();
}

function lightboxFitZoom() {
  const vp = document.getElementById('lightboxViewport');
  const img = document.getElementById('lightboxImg');
  if (vp && img && img.naturalWidth && img.naturalHeight) {
    const scaleX = (vp.clientWidth - 60) / img.naturalWidth;
    const scaleY = (vp.clientHeight - 60) / img.naturalHeight;
    lightboxZoomLevel = Math.min(scaleX, scaleY, 1.0);
    lbTranslateX = 0;
    lbTranslateY = 0;
    updateLightboxTransform();
  }
}

function updateLightboxTransform() {
  const wrapper = document.getElementById('lightboxWrapper');
  const label = document.getElementById('lightboxZoomLabel');
  if (wrapper) {
    wrapper.style.transform = `translate(${lbTranslateX}px, ${lbTranslateY}px) scale(${lightboxZoomLevel})`;
  }
  if (label) {
    label.innerText = Math.round(lightboxZoomLevel * 100) + '%';
  }
}

function initLightboxEvents() {
  const vp = document.getElementById('lightboxViewport');
  if (!vp) return;

  vp.addEventListener('wheel', (e) => {
    e.preventDefault();
    const delta = e.deltaY < 0 ? 0.2 : -0.2;
    lightboxZoom(delta);
  }, { passive: false });

  vp.addEventListener('mousedown', (e) => {
    lbIsDown = true;
    vp.classList.add('cursor-grabbing');
    lbStartX = e.clientX - lbTranslateX;
    lbStartY = e.clientY - lbTranslateY;
  });

  window.addEventListener('mouseup', () => {
    lbIsDown = false;
    if (vp) vp.classList.remove('cursor-grabbing');
  });

  window.addEventListener('mousemove', (e) => {
    if (!lbIsDown) return;
    lbTranslateX = e.clientX - lbStartX;
    lbTranslateY = e.clientY - lbStartY;
    updateLightboxTransform();
  });

  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeDiagramLightbox();
    }
  });
}

window.addEventListener('DOMContentLoaded', () => {
  setNumBits(4);
  updateSelectedDiagramsCount();
  initDiagramViewports();
  initLightboxEvents();
});
