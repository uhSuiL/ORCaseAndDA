import pulp as pl


def stage_1(
        L_manpower_shift:   list[int | float],    # shape: (M, 1)
        beta:               list[list[int]],    # shape: (T, M), binary
        e:                  int,                # shape: (1) -- same for all
        l:                  list[list],         # shape: (N, T)
        alpha:              list[list[int]],    # shape: (T, S), binary
        Y:                  list[list],         # shape: (N, S)
        L_dp_shift:         list[int | float],    # shape: (S, 1)
        f:                  int = None,         # shape: (1) -- only one
) -> tuple[pl.LpProblem, dict[int: pl.LpVariable]]:
    M = len(L_manpower_shift)
    N = len(l)
    T = len(l[0])
    S = len(Y[0])

    # check params 
    assert M == len(beta[0]), (M, len(beta[0]))                                              # check M
    assert N == len(Y), len(Y)                                                               # check N
    assert len(alpha[0]) == S and S == len(L_dp_shift), (len(alpha[0]), S, len(L_dp_shift))  # check S
    assert type(e) == int and type(f) == int, (type(e), type(f))

    # Decision Variables
    x = {m: pl.LpVariable(f"x_{m}", lowBound=0, cat="Integer") for m in range(M)}

    # Objective Function
    problem = pl.LpProblem("stage_1", pl.LpMinimize)
    problem += pl.lpSum(
        x[m] * L_manpower_shift[m] for m in range(M)
    )

    # Constraints for quantity per time-gran per day
    for n in range(N):
        for t in range(T):
            problem += (
                pl.lpSum(beta[t][m] * x[m] * e * l[n][t] for m in range(M)) >=
                sum([alpha[t][s] * (Y[n][s] / L_dp_shift[s]) * l[n][t] for s in range(S)])
            )

    # Constraints for manpower for a month if f is given
    if f is not None:
        problem += (
            pl.lpSum(x[m] for m in range(M)) <= f * M
        )

    problem.solve()
    print("Stage 1: ", pl.LpStatus[problem.status], "; Objective:", problem.objective)
    return problem, x


def _stage_2_per_day(
        n:                  int,
        L_manpower_shift:   list[int | float],    # shape: (W, 1)
        beta:               list[list[int]],    # shape: (T, W), binary
        e:                  int,                # shape: (1) -- same for all
        l_n:                list[float],         # shape: (T, 1)
        alpha:              list[list[int]],    # shape: (T, S), binary
        Y_n:                list[int],         # shape: (S, 1)
        L_dp_shift:         list[int | float],    # shape: (S, 1)
        f_n:                int = None,         # shape: (1) -- one per day (actually for all)
) -> tuple[pl.LpProblem, dict[int: pl.LpVariable]]:
    W = len(L_manpower_shift)
    T = len(l_n)
    S = len(Y_n)

    # check params
    assert len(beta[0]) == W, len(beta[0])
    assert len(alpha[0]) == S and len(L_dp_shift) == S, (len(alpha[0]), len(L_dp_shift))
    assert type(f_n) == int and type(e) == int, (type(f_n), type(e))

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
            pl.lpSum(x_n[w] * beta[t][w] * e * l_n[t] for w in range(W)) >=
            sum([alpha[t][s] * (Y_n[s] / L_dp_shift[s]) * l_n[t] for s in range(S)])
        )
        print(sum([alpha[t][s] * (Y_n[s] / L_dp_shift[s]) * l_n[t] for s in range(S)]))

    # Constraints for manpower in day n
    if f_n is not None:
        problem += (
            pl.lpSum(x_n[w] for w in range(W)) <= f_n
        )

    problem.solve()
    return problem, x_n


def stage_2(
        L_manpower_shift:   list[int | float],  # shape: (W, 1)
        beta:               list[list[int]],    # shape: (T, W), binary
        e:                  int,                # shape: (1) -- same for all
        l:                  list[list],         # shape: (N, T)
        alpha:              list[list[int]],    # shape: (T, S), binary
        Y:                  list[list],         # shape: (N, S)
        L_dp_shift:         list[int | float],  # shape: (S, 1)
        f:                  int = None,         # shape: (1) -- only one
) -> list[tuple[pl.LpProblem, dict[int: pl.LpVariable]]]:
    W = len(L_manpower_shift)
    N = len(l)
    T = len(l[0])
    S = len(Y[0])

    # check params
    assert W == len(beta[0]), (W, len(beta[0]))                                              # check W
    assert N == len(Y), len(Y)                                                         # check N
    assert len(alpha[0]) == S and S == len(L_dp_shift), (len(alpha[0]), S, len(L_dp_shift))  # check S
    assert type(e) == int and type(f) == int, (type(e), type(f))

    # get solution for each day
    solutions: list[tuple[pl.LpProblem, dict[int: pl.LpVariable]]] = [
        _stage_2_per_day(n, L_manpower_shift, beta, e, l[n], alpha, Y[n], L_dp_shift, f)
        for n in range(N)
    ]

    # print result
    i = 0
    for problem, x_n in solutions:
        print("\n=================")
        print(f"Stage2 day_{i}: {pl.LpStatus[problem.status]}\n"
              f"Objective: {pl.value(problem.objective)} = {problem.objective}")
        for w in x_n.keys():
            print(f"x_{w} =  {x_n[w].value()}", end='; ')
        i += 1

    return solutions
