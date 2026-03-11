document.addEventListener('DOMContentLoaded', () => {
	const resistanceInput = document.getElementById('resistance-input');
	const resultsList = document.getElementById('results-list');
	const canvas = document.getElementById('resistor-canvas');
	const ctx = canvas.getContext('2d');
	const resultsContainer = document.getElementById('results-container');
	const canvasContainer = document.getElementById('canvas-container');

	// Código de cores dos resistores
	const colorMap = {
		0: '#000000', // Preto
		1: '#A52A2A', // Marrom
		2: '#FF0000', // Vermelho
		3: '#FFA500', // Laranja
		4: '#FFFF00', // Amarelo
		5: '#008000', // Verde
		6: '#0000FF', // Azul
		7: '#EE82EE', // Roxo
		8: '#808080', // Cinza
		9: '#FFFFFF', // branco
	};

	// Função para normalizar o valor da resistência
	function parseResistance(value) {
		if (!value) return 0;
		let str = value.toLowerCase().replace(',', '.');
		let multiplier = 1;

		if (str.includes('k')) {
			multiplier = 1000;
			str = str.replace('k', '.');
		} else if (str.includes('m')) {
			multiplier = 1000000;
			str = str.replace('m', '.');
		}

		const num = parseFloat(str);
		if (isNaN(num)) return 0;

		return num * multiplier;
	}

	// Função para obter as cores das faixas do resistor (3 faixas só)
	function getBandColors(value) {
		if (value <= 0) return [];
		const strValue = String(value);
		let significantDigits = '';
		let multiplier = 0;

		for(let i = 0; i < strValue.length; i++){
			if(!isNaN(parseInt(strValue[i])) && strValue[i] !== '.'){
				significantDigits += strValue[i];
			}
		}

		if (significantDigits.length === 1) {
			multiplier = Math.floor(Math.log10(value));
		} else {
			multiplier = Math.pow(10, String(Math.round(value)).length - 2);
		}

		const firstDigit = parseInt(significantDigits[0]);
		const secondDigit = parseInt(significantDigits[1] || '0');
		const exponent = Math.floor(Math.log10(value / (firstDigit * 10 + secondDigit)));
		
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

		return [colorMap[d1], colorMap[d2], colorMap[exp]];
	}

	// Funções de desenho no Canvas
	function drawResistor(x, y, value) {
		const width = 120;
		const height = 40;
		const wireLength = 40;

		// Terminais
		ctx.strokeStyle = '#333';
		ctx.lineWidth = 2;
		ctx.beginPath();
		ctx.moveTo(x - wireLength, y + height / 2);
		ctx.lineTo(x, y + height / 2);
		ctx.moveTo(x + width, y + height / 2);
		ctx.lineTo(x + width + wireLength, y + height / 2);
		ctx.stroke();

		// Corpo do resistor
		ctx.fillStyle = '#f0d9b5';
		ctx.fillRect(x, y, width, height);
		ctx.strokeRect(x, y, width, height);

		// Faixas de cor
		const colors = getBandColors(value);
		if (!colors || colors.length < 3) return;

		const bandWidth = 10;
		const spacing = 15;
		for (let i = 0; i < 3; i++) {
			ctx.fillStyle = colors[i];
			ctx.fillRect(x + 25 + i * spacing, y, bandWidth, height);
			if(colors[i] === '#000000') { // Adiciona borda branca em faixa preta
				ctx.strokeStyle = '#FFFFFF';
				ctx.strokeRect(x + 25 + i * spacing, y, bandWidth, height);
			}
		}
	}

	function drawAssociation(r1, r2, op) {
		ctx.clearRect(0, 0, canvas.width, canvas.height);

		if (op === '+') { // Série
			const resistorBodyWidth = 120;
			const wireLength = 40;
			const internalWireGap = 40; // Espaço entre os terminais dos resistores

			const totalOccupiedWidth = (resistorBodyWidth + wireLength) * 2 + internalWireGap;
			const startX = (canvas.width - totalOccupiedWidth) / 2;

			const x1_body = startX + wireLength; // X for R1 body
			const x2_body = x1_body + resistorBodyWidth + internalWireGap + wireLength; // Onde inicia o segundo resistor

			const y = (canvas.height - 40) / 2;

			drawResistor(x1_body, y, r1);
			drawResistor(x2_body, y, r2);

			// Desenhar os terminais
			ctx.strokeStyle = '#333';
			ctx.lineWidth = 2;
			ctx.beginPath();
			ctx.moveTo(x1_body + resistorBodyWidth + wireLength, y + 20); // Final do terminal do R1
			ctx.lineTo(x2_body - wireLength, y + 20); // Final do terminal do R2
			ctx.stroke();

		} else { // Paralelo
			const y1 = (canvas.height / 2) - 50;
			const y2 = (canvas.height / 2) + 10;
			const x = (canvas.width - 120) / 2;
			drawResistor(x, y1, r1);
			drawResistor(x, y2, r2);

			// Conexões verticais e horizontais
			ctx.strokeStyle = '#333';
			ctx.lineWidth = 2;
			ctx.beginPath();

			// Terminal esquerdo
			ctx.moveTo(x - 40, y1 + 20);
			ctx.lineTo(x - 20, y1 + 20);
			ctx.lineTo(x - 20, y2 + 20);
			ctx.lineTo(x - 40, y2 + 20);
			ctx.moveTo(x - 20, (y1 + 20 + y2 + 20)/2);
			ctx.lineTo(x - 60, (y1 + 20 + y2 + 20)/2);
			// Terminal direito
			ctx.moveTo(x + 120 + 40, y1 + 20);
			ctx.lineTo(x + 120 + 20, y1 + 20);
			ctx.lineTo(x + 120 + 20, y2 + 20);
			ctx.lineTo(x + 120 + 40, y2 + 20);
			ctx.moveTo(x + 120 + 20, (y1 + 20 + y2 + 20)/2);
			ctx.lineTo(x + 120 + 60, (y1 + 20 + y2 + 20)/2);
			ctx.stroke();
		}
	}

	function formatValue(value) {
		if (value >= 1000000) return (value / 1000000).toPrecision(3) + ' MΩ';
		if (value >= 1000) return (value / 1000).toPrecision(3) + ' kΩ';
		return value.toPrecision(3) + ' Ω';
	}

	function updateResults() {
		const targetResistance = parseResistance(resistanceInput.value);
		resultsList.innerHTML = '';

		// Esconde os contêineres por padrão
		resultsContainer.style.display = 'none';
		canvasContainer.style.display = 'none';

		if (targetResistance <= 0) {
			ctx.clearRect(0, 0, canvas.width, canvas.height);
			ctx.fillStyle = '#888';
			return;
		}

		const resultString = CalcRes(targetResistance);
		const lines = resultString.trim().split('\n');
		const top3 = lines.slice(0, 3);

		if (top3.length === 0 || (top3.length === 1 && top3[0].trim() === '')) {
			ctx.clearRect(0, 0, canvas.width, canvas.height);
			ctx.fillStyle = '#888';
			ctx.textAlign = 'center';
			ctx.font = '16px Roboto';
			ctx.fillText('Nenhuma associação encontrada.', canvas.width / 2, canvas.height / 2);
			return;
		}

		resultsContainer.style.display = 'block';
		canvasContainer.style.display = 'block';

		top3.forEach((line, index) => {
			const parts = line.split(/\t+/);
			if (parts.length < 5) return;

			const r1 = parseFloat(parts[0]);
			const op = parts[1];
			const r2 = parseFloat(parts[2]);
			const total = parseFloat(parts[4]);

			const li = document.createElement('li');
			li.dataset.r1 = r1;
			li.dataset.r2 = r2;
			li.dataset.op = op;

			const formula = `<span>${formatValue(r1)} ${op} ${formatValue(r2)}</span>`;
			const result = `<span>= ${formatValue(total)}</span>`;
			li.innerHTML = `${formula}${result}`;

			li.addEventListener('click', () => {
				document.querySelectorAll('#results-list li').forEach(item => item.classList.remove('selected'));
				li.classList.add('selected');
				drawAssociation(r1, r2, op);
			});

			resultsList.appendChild(li);

			if (index === 0) {
				li.classList.add('selected');
				drawAssociation(r1, r2, op);
			}
		});
	}

	// Inicialização
	select_series();

	// Valores de resistores que não devem ser sugeridos (não temos em estoque)
	const unavailableResistors = [51, 510000];

	// Filtra o array global R (definido em calculador.js)
	// Esta modificação afeta diretamente os dados que CalcRes utiliza.
	if (typeof R !== 'undefined' && Array.isArray(R)) {
		R = R.filter(resistorValue => !unavailableResistors.includes(resistorValue));
		// Atualiza n_max, pois o tamanho do array R pode ter mudado
		n_max = R.length - 1;

		// Regenera o array global G (definido em calculador.js) com base no novo R
		G = new Array;
		for (let idx = 0; idx <= n_max; idx++) {
			G[idx] = 1.0 / R[n_max - idx];
		}
	}

	resistanceInput.addEventListener('input', updateResults);
	updateResults();
});
