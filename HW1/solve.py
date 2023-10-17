import pulp as pl


def stage_1(
        L_manpower_shift:   list[int|float],    # shape: (M, 1)
        beta:               list[int],          # shape: (M, 1), binary
        e:                  int,                # shape: (1) -- same for all
        l:                  list[list],         # shape: (T, N)
        alpha:              list[int],          # shape: (S, 1), binary
        Y:                  list[list],         # shape: (S, N)
        L_dp_shift:         list[int|float],    # shape: (S, 1)
        f:                  int = None,         # shape: (1) -- only one
) -> pl.LpProblem:
    M = len(L_manpower_shift)
    T = len(l)
    N = len(l[0])
    S = len(Y)

    # check params 
    assert M == len(beta), (M, len(beta))
    assert type(e) == int, type(e)
    assert N == len(Y[0])
    assert len(alpha) == S and S == len(L_dp_shift), (len(alpha), S, len(L_dp_shift))

    # Decision Variables
    x = {m: pl.LpVariable(f"x_{m}", lowBound=0, cat="Integer") for m in range(M)}

    # Objective Function
    problem = pl.LpProblem("stage_1", pl.LpMinimize)
    problem += pl.lpSum(
        x[m] * L_manpower_shift[m] for m in range(M)
    )

    # Constraints for quantity per time-gran per day
    for t in range(T):
        for n in range(N):
            problem += (
                pl.lpSum(beta[m] * x[m] * e[t][n] * l[t][n] for m in range(M)) >= 
                sum([alpha[s] * (Y[s][n] / L_dp_shift[s]) * l[t][n] for s in range(S)])
            )

    # Constraints for manpower for a month if f is given
    if f is not None:
        problem += (
            pl.lpSum(x[m] for m in range(M)) <= f
        )

    problem.solve()
    return problem


def _stage_2_per_day(
        n:                  int,
        L_manpower_shift:   list[int|float],    # shape: (W, 1)
        beta:               list[int],          # shape: (W, 1), binary
        e:                  int,                # shape: (1) -- same for all
        l_n:                list[list],         # shape: (T, 1)
        alpha:              list[int],          # shape: (S, 1)
        Y_n:                list[list],         # shape: (S, 1)
        L_dp_shift:         list[int|float],    # shape: (S, 1)
        f_n:                int = None,         # shape: (1) -- one per day (actually for all)
) -> pl.LpProblem:
    W = len(L_manpower_shift)
    T = len(l_n)
    S = len(Y_n)

    # check params
    assert len(beta) == W, len(beta)
    assert len(alpha) == S and len(L_dp_shift) == S, (len(alpha), len(L_dp_shift))
    assert type(f_n) == int and type(e) == int , (type(f_n), type(e))

    # Decision Variables
    # a set of solution for each day
    x_n = {w: pl.LpVariable(f"x_{n}_{w}", lowBound=0, cat="Integer") for w in range(W)}

    # Objective Function
    problem = pl.LpProblem(f"stage_2_{n}", pl.LpMinimize)
    problem += (
        pl.lpSum(x_n[w] * L_manpower_shift[w] for w in range(W))
    )

    # Constraints for quantity per time-gran for day n
    for t in range(T):
        problem += (
            pl.LpSum(x_n[w] * beta[w] * e[t] * l_n[t] for w in range(W)) >=
            sum([alpha[s] * (Y_n[s] / L_dp_shift[s]) * l_n[t] for s in range(S)])
        )

    # Constraints for manpower in day n
    if f_n is not None:
        problem += (
            pl.lpSum(x_n[w] for w in range(W)) <= f_n
        )

    problem.solve()
    return problem