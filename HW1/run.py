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

    staff_nums = [x_n[w].value() for problem, x_n in solutions for w in x_n.keys()]

    data.get_manpower_shifts(staff_nums, to_csv='./output.csv')
