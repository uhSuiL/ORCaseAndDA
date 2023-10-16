import pulp as pl


def stage_1(
        L_manpower_shift:   list[int],    # shape: (M, 1)
        beta:               list[int],    # shape: (M, 1), binary
        e:                  int,          # shape: (1) -- same for all
        l:                  list[list],   # shape: (T, N)
        alpha:              list[int],    # shape: (S, 1)
        Y:                  list[list],   # shape: (S, N)
        L_dp_shift:         list[int],    # shape: (S, 1)
        f:                  int = None,   # shape: (1) -- only one
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
        L_manpower_shift:   list[int],  # shape: (W, 1)
        beta:               list[int],  # shape: (W, 1), binary
        e:                  int,        # shape: (1) -- same for all
        l:                  list[list], # shape: (T, N)
        alpha:              list[int],  # shape: (S)
        Y:                  list[list], # shape: (S, N)
        L_dp_shift:         list[int],  # shape: (S, 1)
        f_n:                int,        # shape: (1) -- one per day (actually for all)
) -> pl.LpProblem:
    W = len(L_manpower_shift)
    T = len(l)
    N = len(l[0])
    S = len(Y)

    # Decision Variable
    x = {w: pl.LpVariable(f"x_{w}", lowBound=0, cat="Integer") for w in range(W)}

    # Objective Function
    problem = pl.LpProblem(f"stage_2_{n}", pl.LpMinimize)
    problem += (
        
    )