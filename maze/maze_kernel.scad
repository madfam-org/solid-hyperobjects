// ─────────────────────────────────────────────────────────────────────────────
// Shared deterministic maze kernel — OpenSCAD side.
//
// This file is the OpenSCAD half of a kernel that MUST produce bit-identical
// mazes to maze_kernel.py for the same (rows, cols, seed, x_wrapping). Both
// sides implement the same 32-bit LCG and the same iterative recursive
// backtracker, in the same cell order and the same neighbour order.
//
// Double-arithmetic contract (OpenSCAD has no integers — every number is an
// IEEE-754 double, exact only below 2^53):
//   * the LCG multiply-add peaks at 1664525*(2^32-1)+1013904223 = 7.149e15,
//     which is 0.79 * 2^53 — exact, with headroom.
//   * the pick `floor(s*n/2^32)` peaks at 4*(2^32-1) = 1.718e10 — exact.
//   * every reduction is an explicit `%` or `floor`; nothing relies on
//     truncation, bit ops (OpenSCAD has none) or integer division.
// ─────────────────────────────────────────────────────────────────────────────

MZ_M = 4294967296;   // 2^32
MZ_A = 1664525;      // Numerical Recipes multiplier
MZ_C = 1013904223;   // Numerical Recipes increment

function mz_next(s) = (MZ_A * s + MZ_C) % MZ_M;

// Fold the user seed twice so adjacent small seeds (1, 2, 3 ...) do not start
// out correlated in the low bits, which a bare LCG state would.
function mz_seed(seed) = mz_next(mz_next(((floor(seed) % MZ_M) + MZ_M) % MZ_M));

// Neighbour order, fixed and shared: 0=N(r-1) 1=S(r+1) 2=W(c-1) 3=E(c+1).
MZ_DR = [-1, 1, 0, 0];
MZ_DC = [0, 0, -1, 1];

// Passage bit flags, shared: 1=N 2=S 4=W 8=E.
function mz_bit(d) = d == 0 ? 1 : d == 1 ? 2 : d == 2 ? 4 : 8;
function mz_opp(d) = d == 0 ? 2 : d == 1 ? 1 : d == 2 ? 8 : 4;

function _upd(v, i, x) = [for (j = [0 : len(v) - 1]) j == i ? x : v[j]];

// Candidate neighbour direction indices at (r, c), in N,S,W,E order.
function _cands(r, c, rows, cols, vis, wrap) = [
    for (d = [0 : 3])
        let(nr = r + MZ_DR[d],
            nc0 = c + MZ_DC[d],
            nc = wrap ? ((nc0 % cols) + cols) % cols : nc0)
        if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && vis[nr * cols + nc] == 0)
            d
];

function _nr(r, d) = r + MZ_DR[d];
function _nc(c, d, cols, wrap) =
    let(nc0 = c + MZ_DC[d]) wrap ? ((nc0 % cols) + cols) % cols : nc0;

// One step of the backtracker. State is [grid, vis, stack, s].
// Carrying the stack as a plain vector (push = concat, pop = slice) keeps the
// cell order identical to the Python side's list-as-stack.
function _step(st, rows, cols, wrap) =
    let(
        grid  = st[0], vis = st[1], stk = st[2], s = st[3],
        n     = len(stk),
        top   = stk[n - 1],
        r     = floor(top / cols),
        c     = top % cols,
        cd    = _cands(r, c, rows, cols, vis, wrap),
        k     = len(cd)
    )
    k == 0
      ? [grid, vis, [for (i = [0 : n - 2]) stk[i]], s]
      : let(
            s2  = mz_next(s),
            idx = min(k - 1, floor(s2 * k / MZ_M)),
            d   = cd[idx],
            nr  = _nr(r, d),
            nc  = _nc(c, d, cols, wrap),
            here = r * cols + c,
            there = nr * cols + nc
        )
        [
            _upd(_upd(grid, here, grid[here] + mz_bit(d)), there, grid[there] + mz_opp(d)),
            _upd(vis, there, 1),
            concat(stk, [there]),
            s2
        ];

function _run(st, rows, cols, wrap) =
    len(st[2]) == 0 ? st : _run(_step(st, rows, cols, wrap), rows, cols, wrap);

// The shared entry point: a flat rows*cols vector of passage bitmasks.
function mz_grid(rows, cols, seed, x_wrapping = false) =
    _run([
        [for (i = [0 : rows * cols - 1]) 0],
        [for (i = [0 : rows * cols - 1]) i == 0 ? 1 : 0],
        [0],
        mz_seed(seed)
    ], rows, cols, x_wrapping)[0];

// Turn a passage grid into wall segments, in a fixed, shared order.
//
// A wall stands on a cell's south and east side wherever that cell has no
// passage that way, and on the field's outer boundary. With x_wrapping the
// east and west edges are omitted — the field closes on itself, so there is no
// outside there. The emission order is part of the contract both engines
// honour: cells row-major, and within a cell south, east, north, west.
function mz_walls(grid, rows, cols, cell_size, x_wrapping = false) = [
    for (r = [0 : rows - 1], c = [0 : cols - 1])
        let(x = c * cell_size, y = r * cell_size, mask = grid[r * cols + c])
        each concat(
            // South side of this cell (its +y edge), and the field's south rim.
            (mask % 4 < 2 || r == rows - 1)
                ? [[[x, y + cell_size], [x + cell_size, y + cell_size]]] : [],
            // East side (its +x edge), and the field's east rim — neither
            // exists on a wrapping field, where column cols-1 abuts column 0.
            (!x_wrapping && (floor(mask / 8) % 2 == 0 || c == cols - 1))
                ? [[[x + cell_size, y], [x + cell_size, y + cell_size]]] : [],
            // North rim of the field.
            (r == 0) ? [[[x, y], [x + cell_size, y]]] : [],
            // West rim of the field (absent when wrapping).
            (c == 0 && !x_wrapping) ? [[[x, y], [x, y + cell_size]]] : []
        )
];
