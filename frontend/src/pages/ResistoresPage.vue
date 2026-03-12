<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue';

defineOptions({
  name: 'ResistoresPage',
});

// --- Types & Interfaces ---

interface ResistorResult {
  r1: number;
  r2: number;
  op: string;
  total: number;
  tolerance: number;
}

interface CalculatorState {
  R: number[];
  G: number[];
  nMax: number;
}

// --- Constants ---

const COLOR_MAP: Record<number, string> = {
  0: '#1a1a1a', // Preto
  1: '#8B4513', // Marrom
  2: '#DC2626', // Vermelho
  3: '#EA580C', // Laranja
  4: '#EAB308', // Amarelo
  5: '#16A34A', // Verde
  6: '#2563EB', // Azul
  7: '#9333EA', // Roxo
  8: '#6B7280', // Cinza
  9: '#F5F5F5', // Branco
};

const COLOR_NAMES: Record<number, string> = {
  0: 'Preto',
  1: 'Marrom',
  2: 'Vermelho',
  3: 'Laranja',
  4: 'Amarelo',
  5: 'Verde',
  6: 'Azul',
  7: 'Roxo',
  8: 'Cinza',
  9: 'Branco',
};

const RBASE: readonly number[] = [1, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.1, 5.6, 6.8, 8.2];

// Valores de resistores que não temos em estoque
const UNAVAILABLE_RESISTORS: readonly number[] = [51, 510000];

// --- State ---

const resistanceInput = ref('');
const results = ref<ResistorResult[]>([]);
const selectedIndex = ref(0);
const showResults = ref(false);
const canvasRef = ref<HTMLCanvasElement | null>(null);
const resultCanvasRefs = ref<HTMLCanvasElement[]>([]);

// --- Calculator engine (converted from calculador.js) ---

function initializeSeries(): CalculatorState {
  const fullR: number[] = [];
  for (let mult = 0; mult <= 6; mult++) {
    for (let idx = 0; idx < RBASE.length; idx++) {
      fullR[idx + mult * RBASE.length] = Math.round(RBASE[idx]! * Math.pow(10, mult) * 100) / 100;
    }
  }

  const R = fullR.filter((val) => !UNAVAILABLE_RESISTORS.includes(val));
  const nMax = R.length - 1;

  const G: number[] = [];
  for (let idx = 0; idx <= nMax; idx++) {
    G[idx] = 1.0 / R[nMax - idx]!;
  }

  return { R, G, nMax };
}

function findIndex(vect: number[], value: number, nMax: number): number {
  let indexMin = 0;
  let indexMax = nMax + 1;
  let index = Math.floor((indexMin + indexMax) / 2);
  let iterations = 0;

  while (indexMax - indexMin > 1 && iterations < 500) {
    if (vect[index]! === value) break;
    else if (vect[index]! > value) indexMax = index;
    else indexMin = index;

    index = Math.floor((indexMin + indexMax) / 2);
    iterations++;
  }

  if (index < nMax) {
    const tol1 = Math.abs(vect[index]! / value - 1.0);
    const tol2 = Math.abs(vect[index + 1]! / value - 1.0);
    return tol1 < tol2 ? index : index + 1;
  }
  return index;
}

function calcRes(rd: number, state: CalculatorState): ResistorResult[] {
  const { R, G, nMax } = state;
  const outR1: number[] = [];
  const outR2: number[] = [];
  const outOp: string[] = [];
  const outRres: number[] = [];
  const outTol: number[] = [];
  let outIdx = 0;

  // Série: valor único mais próximo
  let r1Idx = findIndex(R, rd, nMax);
  const r1Single = R[r1Idx]!;
  const rresSingle = r1Single;
  const rresTolSingle = (rresSingle - rd) / rd;
  const bestTol = rresTolSingle;

  outR1[outIdx] = r1Single;
  outR2[outIdx] = 0;
  outOp[outIdx] = '+';
  outRres[outIdx] = rresSingle;
  outTol[outIdx] = rresTolSingle;
  outIdx++;

  // Série: dois resistores
  for (; (R[r1Idx] ?? 0) >= rd / 2.0; r1Idx--) {
    const r1 = R[r1Idx]!;
    const r2d = rd - r1;
    if (r2d < 0) continue;

    const r2Idx = findIndex(R, r2d, nMax);
    const r2 = R[r2Idx]!;
    const rres = r1 + r2;
    const rresTol = rres / rd - 1.0;

    if (Math.abs(rresTol) < Math.abs(bestTol)) {
      outR1[outIdx] = r1;
      outR2[outIdx] = r2;
      outOp[outIdx] = '+';
      outRres[outIdx] = rres;
      outTol[outIdx] = rresTol;
      outIdx++;
    }
  }

  // Paralelo
  const rdCond = 1.0 / rd;
  r1Idx = findIndex(G, rdCond, nMax);
  for (; (G[r1Idx] ?? 0) >= rdCond / 2.1; r1Idx--) {
    const r1 = G[r1Idx]!;
    const r2d = rdCond - r1;
    if (r2d < 0) continue;

    const r2Idx = findIndex(G, r2d, nMax);
    const r2 = G[r2Idx]!;
    const rres = r1 + r2;
    const rresTol = rdCond / rres - 1.0;

    if (Math.abs(rresTol) < Math.abs(bestTol)) {
      outR1[outIdx] = R[nMax - r1Idx]!;
      outR2[outIdx] = R[nMax - r2Idx]!;
      outOp[outIdx] = '||';
      outRres[outIdx] = 1.0 / rres;
      outTol[outIdx] = rresTol;
      outIdx++;
    }
  }

  // Ordena por tolerância (menor desvio primeiro) - insertion sort
  for (let i = 1; i < outIdx; i++) {
    const tmpR1 = outR1[i]!;
    const tmpR2 = outR2[i]!;
    const tmpOp = outOp[i]!;
    const tmpRres = outRres[i]!;
    const tmpTol = outTol[i]!;
    let j = i - 1;
    for (; j >= 0 && Math.abs(outTol[j]!) > Math.abs(tmpTol); j--) {
      outR1[j + 1] = outR1[j]!;
      outR2[j + 1] = outR2[j]!;
      outOp[j + 1] = outOp[j]!;
      outRres[j + 1] = outRres[j]!;
      outTol[j + 1] = outTol[j]!;
    }
    outR1[j + 1] = tmpR1;
    outR2[j + 1] = tmpR2;
    outOp[j + 1] = tmpOp;
    outRres[j + 1] = tmpRres;
    outTol[j + 1] = tmpTol;
  }

  // Retorna os top 3
  const mapped: ResistorResult[] = [];
  const limit = Math.min(outIdx, 3);
  for (let i = 0; i < limit; i++) {
    mapped.push({
      r1: outR1[i]!,
      r2: outR2[i]!,
      op: outOp[i]!,
      total: Math.round(outRres[i]! * 1000) / 1000,
      tolerance: outTol[i]!,
    });
  }
  return mapped;
}

// --- Formatting ---

function formatValue(value: number): string {
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1).replace(/\.0$/, '')}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1).replace(/\.0$/, '')}k`;
  return `${value.toFixed(1).replace(/\.0$/, '')}`;
}

function formatValueWithUnit(value: number): string {
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1).replace(/\.0$/, '')}MΩ`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1).replace(/\.0$/, '')}kΩ`;
  return `${value.toFixed(1).replace(/\.0$/, '')}Ω`;
}

function parseResistance(value: string): number {
  if (!value) return 0;
  let str = value.toLowerCase().replace(',', '.');
  let multiplier = 1;

  if (str.includes('k')) {
    multiplier = 1_000;
    str = str.replace('k', '.');
  } else if (str.includes('m')) {
    multiplier = 1_000_000;
    str = str.replace('m', '.');
  }

  const num = parseFloat(str);
  if (isNaN(num)) return 0;
  return num * multiplier;
}

// --- Canvas Drawing: Realistic Resistor ---

function getBandColors(value: number): [string, string, string] | null {
  if (value <= 0) return null;

  let val = value;
  let exp = 0;
  while (val >= 100) {
    val /= 10;
    exp++;
  }
  while (val < 10 && val !== 0) {
    val *= 10;
    exp--;
  }
  val = Math.round(val);
  const d1 = Math.floor(val / 10);
  const d2 = val % 10;

  return [COLOR_MAP[d1]!, COLOR_MAP[d2]!, COLOR_MAP[exp]!];
}

function getBandDigits(value: number): [number, number, number] | null {
  if (value <= 0) return null;

  let val = value;
  let exp = 0;
  while (val >= 100) {
    val /= 10;
    exp++;
  }
  while (val < 10 && val !== 0) {
    val *= 10;
    exp--;
  }
  val = Math.round(val);
  const d1 = Math.floor(val / 10);
  const d2 = val % 10;
  return [d1, d2, exp];
}

/** Desenha um resistor realista com corpo cilíndrico, terminais verdes e faixas de cores */
function drawRealisticResistor(
  ctx: CanvasRenderingContext2D,
  cx: number,
  cy: number,
  value: number,
  scale: number = 1.0,
): void {
  const bodyW = 80 * scale;
  const bodyH = 28 * scale;
  const wireLen = 36 * scale;
  const capW = 6 * scale;
  const bodyR = 6 * scale;

  const x = cx - bodyW / 2;
  const y = cy - bodyH / 2;

  // Terminais (fios verdes)
  ctx.strokeStyle = '#4CAF50';
  ctx.lineWidth = 3 * scale;
  ctx.lineCap = 'round';

  // Fio esquerdo
  ctx.beginPath();
  ctx.moveTo(x - wireLen, cy);
  ctx.lineTo(x - capW, cy);
  ctx.stroke();

  // Fio direito
  ctx.beginPath();
  ctx.moveTo(x + bodyW + capW, cy);
  ctx.lineTo(x + bodyW + wireLen, cy);
  ctx.stroke();

  // Caps metálicas nas pontas (cilindros menores)
  ctx.fillStyle = '#A0A0A0';
  ctx.strokeStyle = '#888';
  ctx.lineWidth = 1 * scale;

  // Cap esquerda
  roundRect(ctx, x - capW, y + 2 * scale, capW, bodyH - 4 * scale, 2 * scale);
  ctx.fill();
  ctx.stroke();

  // Cap direita
  roundRect(ctx, x + bodyW, y + 2 * scale, capW, bodyH - 4 * scale, 2 * scale);
  ctx.fill();
  ctx.stroke();

  // Corpo principal - gradiente para efeito cilíndrico
  const bodyGrad = ctx.createLinearGradient(x, y, x, y + bodyH);
  bodyGrad.addColorStop(0, '#E8D5B7');
  bodyGrad.addColorStop(0.15, '#F5E6CE');
  bodyGrad.addColorStop(0.5, '#F0D9B5');
  bodyGrad.addColorStop(0.85, '#D4BC96');
  bodyGrad.addColorStop(1, '#C4AC86');

  ctx.fillStyle = bodyGrad;
  ctx.strokeStyle = '#B0986E';
  ctx.lineWidth = 1.2 * scale;
  roundRect(ctx, x, y, bodyW, bodyH, bodyR);
  ctx.fill();
  ctx.stroke();

  // Faixas de cor
  const colors = getBandColors(value);
  if (!colors) return;

  const bandW = 7 * scale;
  const bandSpacing = 14 * scale;
  const bandStartX = x + bodyW * 0.22;
  const bandY = y + 1 * scale;
  const bandH = bodyH - 2 * scale;

  for (let i = 0; i < 3; i++) {
    const bx = bandStartX + i * bandSpacing;
    const bandColor = colors[i]!;

    // Gradiente na faixa para efeito 3D
    const bandGrad = ctx.createLinearGradient(bx, bandY, bx, bandY + bandH);
    bandGrad.addColorStop(0, lightenColor(bandColor, 30));
    bandGrad.addColorStop(0.5, bandColor);
    bandGrad.addColorStop(1, darkenColor(bandColor, 20));

    ctx.fillStyle = bandGrad;
    roundRect(ctx, bx, bandY, bandW, bandH, 1.5 * scale);
    ctx.fill();

    // Borda na faixa
    if (bandColor === '#1a1a1a' || bandColor === '#F5F5F5') {
      ctx.strokeStyle = bandColor === '#F5F5F5' ? '#ccc' : '#444';
      ctx.lineWidth = 0.8 * scale;
      roundRect(ctx, bx, bandY, bandW, bandH, 1.5 * scale);
      ctx.stroke();
    }
  }
}

/** Nó de conexão (ponto preto) nos terminais */
function drawConnectionNode(ctx: CanvasRenderingContext2D, x: number, y: number, scale: number = 1.0): void {
  ctx.fillStyle = '#333';
  ctx.beginPath();
  ctx.arc(x, y, 4 * scale, 0, Math.PI * 2);
  ctx.fill();
}

/** Desenha um rect com bordas arredondadas */
function roundRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  r: number,
): void {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r);
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}

function lightenColor(hex: string, percent: number): string {
  const num = parseInt(hex.replace('#', ''), 16);
  const r = Math.min(255, ((num >> 16) & 0xff) + Math.round(255 * percent / 100));
  const g = Math.min(255, ((num >> 8) & 0xff) + Math.round(255 * percent / 100));
  const b = Math.min(255, (num & 0xff) + Math.round(255 * percent / 100));
  return `rgb(${r},${g},${b})`;
}

function darkenColor(hex: string, percent: number): string {
  const num = parseInt(hex.replace('#', ''), 16);
  const r = Math.max(0, ((num >> 16) & 0xff) - Math.round(255 * percent / 100));
  const g = Math.max(0, ((num >> 8) & 0xff) - Math.round(255 * percent / 100));
  const b = Math.max(0, (num & 0xff) - Math.round(255 * percent / 100));
  return `rgb(${r},${g},${b})`;
}

/** Desenha o diagrama de associação no canvas principal */
function drawAssociation(r1: number, r2: number, op: string): void {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  // HiDPI support
  const dpr = window.devicePixelRatio || 1;
  const displayW = canvas.clientWidth;
  const displayH = canvas.clientHeight;
  canvas.width = displayW * dpr;
  canvas.height = displayH * dpr;
  ctx.scale(dpr, dpr);

  // Background color based on association
  ctx.fillStyle = op === '+' ? '#EBF5FF' : '#FFF4E6'; // Levemente azulado ou laranjado
  ctx.fillRect(0, 0, displayW, displayH);

  const cw = displayW;
  const ch = displayH;
  const scale = Math.min(cw / 360, 1.2);

  if (op === '+') {
    if (r2 === 0) {
      // Resistor único
      drawRealisticResistor(ctx, cw / 2, ch / 2, r1, scale);
      ctx.fillStyle = '#555';
      ctx.font = `bold ${12 * scale}px Inter, sans-serif`;
      ctx.textAlign = 'center';
      ctx.fillText(formatValue(r1), cw / 2, ch / 2 - 22 * scale);
    } else {
      // Série: dois resistores lado a lado
      const gap = 50 * scale;
      const totalW = 80 * scale * 2 + gap + 36 * scale * 2;
      const startX = (cw - totalW) / 2 + 36 * scale + 40 * scale;

      const cx1 = startX;
      const cx2 = startX + 80 * scale + gap;
      const cy = ch / 2;

      drawRealisticResistor(ctx, cx1, cy, r1, scale);
      drawRealisticResistor(ctx, cx2, cy, r2, scale);

      // Fio de conexão entre R1 e R2
      const r1RightX = cx1 + 40 * scale + 6 * scale + 36 * scale;
      const r2LeftX = cx2 - 40 * scale - 6 * scale - 36 * scale;

      ctx.strokeStyle = '#4CAF50';
      ctx.lineWidth = 3 * scale;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.moveTo(r1RightX, cy);
      ctx.lineTo(r2LeftX, cy);
      ctx.stroke();

      // Label values
      ctx.fillStyle = '#555';
      ctx.font = `bold ${12 * scale}px Inter, sans-serif`;
      ctx.textAlign = 'center';
      ctx.fillText(formatValue(r1), cx1, cy - 22 * scale);
      ctx.fillText(formatValue(r2), cx2, cy - 22 * scale);
    }
  } else {
    // Paralelo: dois resistores empilhados com conexões
    const vGap = 46 * scale;
    const cy1 = ch / 2 - vGap / 2;
    const cy2 = ch / 2 + vGap / 2;
    const cx = cw / 2;

    drawRealisticResistor(ctx, cx, cy1, r1, scale);
    drawRealisticResistor(ctx, cx, cy2, r2, scale);

    const leftWireEnd = cx - (40 + 36) * scale;
    const rightWireEnd = cx + (40 + 36) * scale;
    const extLen = 20 * scale;

    ctx.strokeStyle = '#4CAF50';
    ctx.lineWidth = 3 * scale;
    ctx.lineCap = 'round';

    // Barras verticais esquerdas
    ctx.beginPath();
    ctx.moveTo(leftWireEnd, cy1);
    ctx.lineTo(leftWireEnd, cy2);
    ctx.stroke();

    // Barras verticais direitas
    ctx.beginPath();
    ctx.moveTo(rightWireEnd, cy1);
    ctx.lineTo(rightWireEnd, cy2);
    ctx.stroke();

    // Terminal esquerdo externo
    const termY = (cy1 + cy2) / 2;
    ctx.beginPath();
    ctx.moveTo(leftWireEnd, termY);
    ctx.lineTo(leftWireEnd - extLen, termY);
    ctx.stroke();

    // Terminal direito externo
    ctx.beginPath();
    ctx.moveTo(rightWireEnd, termY);
    ctx.lineTo(rightWireEnd + extLen, termY);
    ctx.stroke();

    // Nós de conexão
    drawConnectionNode(ctx, leftWireEnd, cy1, scale);
    drawConnectionNode(ctx, leftWireEnd, cy2, scale);
    drawConnectionNode(ctx, rightWireEnd, cy1, scale);
    drawConnectionNode(ctx, rightWireEnd, cy2, scale);
    drawConnectionNode(ctx, leftWireEnd - extLen, termY, scale);
    drawConnectionNode(ctx, rightWireEnd + extLen, termY, scale);

    // Labels
    ctx.fillStyle = '#555';
    ctx.font = `bold ${12 * scale}px Inter, sans-serif`;
    
    // R1: label value on the left
    ctx.textAlign = 'right';
    ctx.fillText(formatValue(r1), cx - (40 + 36 + 10) * scale, cy1 + 5 * scale);
    
    // R2: label value on the right
    ctx.textAlign = 'left';
    ctx.fillText(formatValue(r2), cx + (40 + 36 + 10) * scale, cy2 + 5 * scale);
  }
}

/** Desenha resistor(es) num canvas de resultado */
function drawResultMiniCanvas(canvas: HTMLCanvasElement, result: ResistorResult): void {
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const dpr = window.devicePixelRatio || 1;
  const displayW = canvas.clientWidth;
  const displayH = canvas.clientHeight;
  canvas.width = displayW * dpr;
  canvas.height = displayH * dpr;
  ctx.scale(dpr, dpr);

  // Background color based on association
  ctx.fillStyle = result.op === '+' ? '#EBF5FF' : '#FFF4E6';
  
  // Draw rounded background
  const r = 10;
  roundRect(ctx, 0, 0, displayW, displayH, r);
  ctx.fill();

  const scale = Math.min(displayW / 240, 0.8);
  const textScale = Math.min(displayW / 240, 1.0);

  if (result.r2 === 0) {
    // Resistor único
    drawRealisticResistor(ctx, displayW / 2, displayH / 2, result.r1, scale);
    ctx.fillStyle = '#555';
    ctx.font = `bold ${11 * textScale}px Inter, sans-serif`;
    ctx.textAlign = 'center';
    ctx.fillText(formatValue(result.r1), displayW / 2, displayH / 2 - 20 * scale);
  } else if (result.op === '+') {
    // Série: dois lado a lado, menor
    const gap = 30 * scale;
    const cx1 = displayW / 2 - 40 * scale - gap / 2;
    const cx2 = displayW / 2 + 40 * scale + gap / 2;
    drawRealisticResistor(ctx, cx1, displayH / 2, result.r1, scale * 0.85);
    drawRealisticResistor(ctx, cx2, displayH / 2, result.r2, scale * 0.85);

    ctx.fillStyle = '#555';
    ctx.font = `bold ${10 * textScale}px Inter, sans-serif`;
    ctx.textAlign = 'center';
    ctx.fillText(formatValue(result.r1), cx1, displayH / 2 - 18 * scale);
    ctx.fillText(formatValue(result.r2), cx2, displayH / 2 - 18 * scale);
  } else {
    // Paralelo: empilhados com conexões
    const vGap = 28 * scale;
    const cy1 = displayH / 2 - vGap / 2;
    const cy2 = displayH / 2 + vGap / 2;
    const cx = displayW / 2;
    
    drawRealisticResistor(ctx, cx, cy1, result.r1, scale * 0.75);
    drawRealisticResistor(ctx, cx, cy2, result.r2, scale * 0.75);

    // Conexões paralelas
    const leftWireEnd = cx - (40 + 36) * scale * 0.75;
    const rightWireEnd = cx + (40 + 36) * scale * 0.75;

    ctx.strokeStyle = '#4CAF50';
    ctx.lineWidth = 2 * scale;
    ctx.beginPath();
    ctx.moveTo(leftWireEnd, cy1);
    ctx.lineTo(leftWireEnd, cy2);
    ctx.moveTo(rightWireEnd, cy1);
    ctx.lineTo(rightWireEnd, cy2);
    ctx.stroke();

    ctx.fillStyle = '#555';
    ctx.font = `bold ${9 * textScale}px Inter, sans-serif`;
    
    // Label value on the left
    ctx.textAlign = 'right';
    ctx.fillText(formatValue(result.r1), leftWireEnd - 5 * scale, cy1 + 3 * scale);
    
    // Label value on the right
    ctx.textAlign = 'left';
    ctx.fillText(formatValue(result.r2), rightWireEnd + 5 * scale, cy2 + 3 * scale);
  }
}

// --- Event Handlers ---

const calculatorState = initializeSeries();

function drawAllResultCanvases(): void {
  void nextTick(() => {
    resultCanvasRefs.value.forEach((canvas, i) => {
      const result = results.value[i];
      if (canvas && result) {
        drawResultMiniCanvas(canvas, result);
      }
    });
  });
}

function updateResults(): void {
  const targetResistance = parseResistance(resistanceInput.value);

  if (targetResistance <= 0) {
    results.value = [];
    showResults.value = false;
    return;
  }

  const computed = calcRes(targetResistance, calculatorState);

  if (computed.length === 0) {
    results.value = [];
    showResults.value = false;
    return;
  }

  results.value = computed;
  showResults.value = true;
  selectedIndex.value = 0;

  const first = computed[0];
  if (first) {
    void nextTick(() => {
      drawAssociation(first.r1, first.r2, first.op);
      drawAllResultCanvases();
    });
  }
}

function selectResult(index: number): void {
  selectedIndex.value = index;
  const result = results.value[index];
  if (result) {
    drawAssociation(result.r1, result.r2, result.op);
  }
}

function getOperationLabel(op: string): string {
  return op === '+' ? 'Série' : 'Paralelo';
}

function getBandLabel(value: number): string {
  const digits = getBandDigits(value);
  if (!digits) return '';
  return digits.map((d) => COLOR_NAMES[d] ?? '').join(' - ');
}

function setResultCanvasRef(el: HTMLCanvasElement | null, index: number): void {
  if (el) {
    resultCanvasRefs.value[index] = el;
  }
}

// Redraw on resize
function handleResize(): void {
  if (!showResults.value) return;
  const result = results.value[selectedIndex.value];
  if (result) {
    drawAssociation(result.r1, result.r2, result.op);
  }
  drawAllResultCanvases();
}

watch(selectedIndex, () => {
  const result = results.value[selectedIndex.value];
  if (result) {
    void nextTick(() => drawAssociation(result.r1, result.r2, result.op));
  }
});

onMounted(() => {
  updateResults();
  window.addEventListener('resize', handleResize);
});
</script>

<template>
  <q-page class="page-container">
    <div class="content-wrapper">
      <!-- Header -->
      <div class="header-section">
        <div class="header-icon-row">
          <q-icon name="mdi-resistor" color="primary" size="32px" />
          <h1 class="page-title">Calculador de Resistores</h1>
        </div>
        <p class="page-subtitle">
          Encontre a melhor associação de resistores da série E12
        </p>
      </div>

      <!-- Input -->
      <div class="input-section">
        <label class="input-label" for="resistance-input">
          Resistência desejada (Ω):
        </label>
        <q-input
          id="resistance-input"
          v-model="resistanceInput"
          placeholder="ex: 4k7 ou 100"
          outlined
          class="resistance-input"
          input-class="text-center text-weight-bold resistance-input-text"
          @update:model-value="updateResults"
          :debounce="150"
        >
          <template v-slot:prepend>
            <div style="width: 28px"></div>
          </template>
          <template v-slot:append>
            <q-icon name="mdi-omega" color="primary" size="28px" />
          </template>
        </q-input>
      </div>

      <!-- Results -->
      <div v-if="showResults && results.length > 0" class="results-section">
        <!-- Legend removed -->

        <!-- Result Cards with inline resistor drawings -->
        <div
          v-for="(result, index) in results"
          :key="index"
          class="result-card"
          :class="{ 'result-selected': selectedIndex === index }"
          @click="selectResult(index)"
        >
          <!-- Mini resistor canvas -->
          <div class="mini-canvas-wrapper">
            <canvas
              :ref="(el) => setResultCanvasRef(el as HTMLCanvasElement, index)"
              class="mini-canvas"
            ></canvas>
          </div>

          <!-- Info -->
          <div class="result-info">
            <div class="result-row">
              <div class="formula-group">
                <span class="op-tag" :class="result.op === '+' ? 'op-serie' : 'op-paralelo'">
                  {{ getOperationLabel(result.op) }}
                </span>
                <span class="formula-text">
                  {{ formatValue(result.r1) }}
                  <span class="op-symbol">{{ result.op }}</span>
                  <template v-if="result.r2 > 0">
                    {{ formatValue(result.r2) }}
                  </template>
                </span>
              </div>
              <span class="result-value" :class="result.op === '+' ? 'text-serie' : 'text-paralelo'">
                = {{ formatValueWithUnit(result.total) }}
              </span>
            </div>
            <div class="band-labels">
              <span class="band-label-item">R1: {{ getBandLabel(result.r1) }}</span>
              <span v-if="result.r2 > 0" class="band-label-item">R2: {{ getBandLabel(result.r2) }}</span>
            </div>
          </div>
        </div>

        <!-- Main association canvas (HIDDEN) -->
        <div v-if="false" class="association-section">
          <h3 class="section-subtitle">Diagrama da Associação</h3>
          <div class="main-canvas-wrapper">
            <canvas ref="canvasRef" class="main-canvas"></canvas>
          </div>
        </div>
      </div>
    </div>
  </q-page>
</template>

<style lang="scss" scoped>
.page-container {
  background-color: #f5f7fa;
  min-height: 100vh;
  padding: 16px;
}

.content-wrapper {
  max-width: 600px;
  margin: 0 auto;
}

// --- Header ---

.header-section {
  text-align: center;
  margin-bottom: 12px;
}

.header-icon-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: -2px;
}

.page-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--q-primary);
  margin: 0;
  text-transform: uppercase;
  letter-spacing: -0.02em;
  line-height: 1;
}

.page-subtitle {
  font-size: 0.8rem;
  color: #94a3b8;
  margin: 0;
  line-height: 1.2;
}

// --- Input ---

.input-section {
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.input-label {
  display: block;
  margin-bottom: 8px;
  color: #64748b;
  font-weight: 700;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.resistance-input {
  :deep(.q-field__control) {
    border-radius: 12px;
    background-color: #f8fafc;
    min-height: 50px;
  }
  :deep(.q-field__control:focus-within) {
    background-color: #fff;
    box-shadow: 0 0 0 3px rgba(25, 118, 210, 0.15);
  }
}

:deep(.resistance-input-text) {
  font-size: 1.8rem !important;
  color: var(--q-primary);
}

// --- Results ---

.results-section {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.section-subtitle {
  font-size: 1rem;
  font-weight: 700;
  color: #475569;
  margin: 24px 0 12px 0;
  text-align: center;
}

// --- Result cards ---

.result-card {
  background: #fff;
  border-radius: 14px;
  padding: 14px;
  margin-bottom: 12px;
  border: 2px solid transparent;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  gap: 8px;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    transform: translateY(-1px);
  }

  &:active {
    transform: scale(0.99);
  }
}

.result-selected {
  border-color: var(--q-primary);
  background: rgba(25, 118, 210, 0.04);
  box-shadow: 0 2px 8px rgba(25, 118, 210, 0.15);
}

.mini-canvas-wrapper {
  width: 100%;
  height: 60px;
  border-radius: 10px;
  background: #fafbfc;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.mini-canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.result-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.result-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  width: 100%;
}

.formula-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: nowrap;
  overflow: hidden;
}

.op-tag {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.02em;
  flex-shrink: 0;
}

.op-serie {
  background: #dbeafe;
  color: #1d4ed8;
}

.op-paralelo {
  background: #ffedd5;
  color: #c2410c;
}

.formula-text {
  font-size: 1.1rem;
  font-weight: 700;
  color: #334155;
  white-space: nowrap;
}

.op-symbol {
  color: #94a3b8;
  margin: 0 4px;
}

.result-value {
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--q-primary);
  white-space: nowrap;
}

.text-serie {
  color: #2563eb !important;
}

.text-paralelo {
  color: #ea580c !important;
}

.legend-row {
  display: flex;
  gap: 16px;
  align-items: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  color: #64748b;
  font-weight: 500;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.legend-serie {
  background: #2563eb;
}

.legend-paralelo {
  background: #ea580c;
}

.band-labels {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: 0;
}

.band-label-item {
  font-size: 0.85rem;
  color: #78909c;
  font-weight: 500;
}

// --- Association canvas ---

.association-section {
  margin-top: 8px;
}

.main-canvas-wrapper {
  background: #fff;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  padding: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.main-canvas {
  width: 100%;
  height: 180px;
  display: block;
}

// --- Responsive ---

@media (min-width: 480px) {
  .page-container {
    padding: 24px;
  }

  .page-title {
    font-size: 1.6rem;
  }

  :deep(.resistance-input-text) {
    font-size: 2.2rem !important;
  }

  .mini-canvas-wrapper {
    height: 70px;
  }

  .main-canvas {
    height: 220px;
  }
}

@media (min-width: 768px) {
  .page-container {
    padding: 32px;
  }

  .content-wrapper {
    max-width: 650px;
  }

  .input-section {
    padding: 28px;
  }

  .main-canvas {
    height: 250px;
  }
}
</style>
