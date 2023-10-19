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

    solved_problem, x = solve.stage_1(
        e = e,
        f = f,

        Y = data.Y,
        L_dp_shift = data.L_dp_shift,
        l = data.l,

        L_manpower_shift=data.L_manpower_shift,
        alpha = data.alpha,
        beta = data.beta
    )

    # 打印第一阶段的解
    print('-----')
    for x_n in x.values():
        print(x_n, x_n.value())

    print(solved_problem)

    ignore = [i for i in range(len(x.values())) if list(x.values())[i].value() == 0]

    data.gen_manpower_shifts(ignore=ignore)

    solutions = solve.stage_2(
        e=e,
        f=f,

        Y=data.Y,
        L_dp_shift=data.L_dp_shift,
        l=data.l,

        L_manpower_shift=data.L_manpower_shift,
        alpha=data.alpha,
        beta=data.beta
    )

    staff_nums = []
    for n in range(len(solutions)):
        prob, x_n = solutions[n]
        staff_nums.append([x_n_t.value() for x_n_t in x_n.values()])

    data.get_manpower_shifts(staff_nums, to_csv='./output.csv')
