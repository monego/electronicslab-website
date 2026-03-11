// Funções retiradas de: http://www.qsl.net/in3otd/parallr.html
function select_series() { 
	Rbase = new Array(1, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.1, 5.6, 6.8, 8.2);

	R = new Array;
	for (var mult = 0; mult <= 6; mult++) {
		for (var idx = 0; idx <Rbase.length; idx++) {
			/* need to round to compensate for pow() errors; allow max two decimals, needed for E96 */
			R[idx + mult * Rbase.length] = Math.round(Rbase[idx] * Math.pow(10, mult) * 100) / 100;
		}
	}
	n_max = R.length - 1; /* maximum valid index */

	/* compute the conductances array, lowest conductance first to have an */
	/* array sorted in ascending order */
	G = new Array;
	for (idx = 0; idx <= n_max; idx++) {
		G[idx] = 1.0 / R[n_max - idx];
	}

	out_r1 = new Array;
	out_r2 = new Array;
	out_op = new Array;
	out_rres = new Array;
	out_tol = new Array;
}


function FindIndex(vect, value) {
	var index_min = 0;
	var index_max = n_max + 1;
	var index = Math.floor( (index_min + index_max) / 2);
	i = 0;

	while (((index_max - index_min) > 1) && (i < 500)) {
		if (vect[index] == value) { break; }
		else if (vect[index] > value) { index_max = index }
		else if (vect[index] < value) { index_min = index }

		index = Math.floor( (index_min + index_max) / 2);
		i++;
	} 
	if (index < n_max) {
		tol1 = Math.abs(vect[index] / value - 1.0);
		tol2 = Math.abs(vect[index + 1] / value - 1.0);
		if (tol1 < tol2)
			return index;
		else
			return (index + 1);
	} else {
		return index;
	}
}

function CalcRes(rd) {

	var retorno = "";
	var r1, r2, r1_idx, rres, rres_tol, best_tol, out_idx, op;
	var out_prres, out_vrres;
	var i, j, iter = 0; /* number of iterations */

	retorno = "";

	/* compute assuming resistors in series */
	/* locate nearest approximation with standard resistor values */
	r1_idx = FindIndex(R, rd);
	r1 = R[r1_idx];
	/* other resistor */
	/* r2 = Number.POSITIVE_INFINITY */
	r2 = 0;
	rres = r1;
	rres_tol = (rres - rd) / rd; /* relative tolerance */
	best_tol = rres_tol;

	out_idx = 0;
	out_r1[out_idx] = r1;
	out_r2[out_idx] = r2;
	out_op[out_idx] = "+";
	out_rres[out_idx] = rres;
	out_tol[out_idx++] = rres_tol;

	for (; R[r1_idx] >= rd / 2.0; r1_idx--) {
		iter++;
		r1 = R[r1_idx];

		r2d = rd - r1; // this is the value needed
		if (r2d < 0) { continue } // might happen...

		r2_idx = FindIndex(R, r2d);
		r2 = R[r2_idx];  // get the nearest standard value 
		rres = r1 + r2; // compute the resulting composition
		rres_tol = rres / rd - 1.0; // and its tolerance

		if (Math.abs(rres_tol) < Math.abs(best_tol)) {
			//best_tol = rres_tol;
			out_r1[out_idx] = r1;
			out_r2[out_idx] = r2;
			out_op[out_idx] = "+";
			out_rres[out_idx] = rres;
			out_tol[out_idx++] = rres_tol;
		}

	}

	rd = 1.0 / rd;
	/* compute assuming resistors in parallel */
	r1_idx = FindIndex(G, rd);
	for (; G[r1_idx] >= rd / 2.1; r1_idx--) {
		iter++;
		r1 = G[r1_idx];

		r2d = rd - r1; // this is the value needed
		if (r2d < 0) { continue } // might happen...

		r2_idx = FindIndex(G, r2d);
		r2 = G[r2_idx];  // get the nearest standard value 
		rres = r1 + r2; // compute the resulting composition
		rres_tol = rd / rres - 1.0; // and its tolerance

		if (Math.abs(rres_tol) < Math.abs(best_tol)) {
			//best_tol = rres_tol;
			// use values from R array to avoid rounding errors 
			//   which will lead to something like 6800.0000001...
			out_r1[out_idx] = R[n_max - r1_idx] // 1.0 / r1;
			out_r2[out_idx] = R[n_max - r2_idx] // 1.0 / r2;
			out_op[out_idx] = "||";
			out_rres[out_idx] = 1.0 / rres;
			out_tol[out_idx++] = rres_tol;
		}
	}

	// sort the results
	for (i = 1; i < out_idx; i++) {
		r1 = out_r1[i];
		r2 = out_r2[i];
		op = out_op[i];
		rres = out_rres[i];
		rres_tol = out_tol[i];
		for (j = i - 1; (j >= 0) && 
			Math.abs(out_tol[j]) > Math.abs(rres_tol); j--) {
			out_r1[j + 1] = out_r1[j];
			out_r2[j + 1] = out_r2[j];
			out_op[j + 1] = out_op[j];
			out_rres[j + 1] = out_rres[j];
			out_tol[j + 1] = out_tol[j];
		}
		out_r1[j + 1] = r1;
		out_r2[j + 1] = r2;
		out_op[j + 1] = op;
		out_rres[j + 1] = rres;
		out_tol[j + 1] = rres_tol;
	}

	for (r1_idx = 0; r1_idx < out_idx; r1_idx++) {
		out_prres = (Math.round(out_rres[r1_idx] * 1000)) / 1000 ;
		out_vrres = out_prres.toString();
		if(out_vrres.length < 8) out_vrres = out_vrres + "\t"
		retorno += 
		out_r1[r1_idx] + "\t" + 
		out_op[r1_idx] + "\t" + 
		out_r2[r1_idx] + "\t=\t" +
		/* leave three decimal digits maximum */
		out_vrres + "\n";
		// (Math.round(out_tol[r1_idx] * 100000)) / 1000 + " %)\n"
	}

	return retorno;
}