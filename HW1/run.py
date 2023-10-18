import pulp as pl
import pandas as pd
import util.dataprocess as dp
from util import solve

   
if __name__ == "__main__":
    excel = pd.read_excel('./effiandshifts.xlsx')

    e = excel.loc[0, 'staff_effi_standard'].item()
    f = excel.loc[0, 'staff_num'].item()

    data = dp.Data(excel)

    # stage_one
    data.gen_manpower_shifts()

    solved_problem = solve.stage_1(
        e = e,
        f = f,

        Y = data.Y,
        L_dp_shift = data.L_dp_shift,
        l = data.l,

        L_manpower_shift=data.L_manpower_shift,
        alpha = data.alpha,
        beta = data.beta
    )

    print("Stage 1: ", pl.LpStatus[solved_problem.status])
    print(solved_problem.objective)
    print(solved_problem.constraints)

    # 打印第一阶段的解
    for var in solved_problem.variables():
        print(var, var.value())
