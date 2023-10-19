# --------------------- ATTENTION -----------------------------
#  the implementation depends on the order in the `python dict`,
#  while for python lower than 3.6, there is no order in dict.
# -------------------------------------------------------------

# 计算时间间隔精确到分钟(in L_xxx_shift, l)


import json
import pandas as pd


with open('./cols_config.json', 'r') as f:
    cols = json.load(f)


class Data:

    def __init__(self, data: pd.DataFrame) -> None:
        self.data                     = data[list(cols.values())].sort_values(by=cols["day"])
        self.data[cols["begin_tm"]]   = pd.to_datetime(self.data[cols["begin_tm"]].astype(str), format="%H%M")
        self.data[cols["end_tm"]]     = pd.to_datetime(self.data[cols["end_tm"]].astype(str), format="%H%M")
        self.data["duration"]         = self.data[cols["end_tm"]] - self.data[cols["begin_tm"]]

        # 每天的表都必须按照begin_tm从小到大排好序
        self.dp_shift_tables: dict[str: pd.DataFrame] = {
            day.strftime('%Y-%m-%d'): dp_table.sort_values(by=cols['begin_tm']).reset_index(drop=True) for day, dp_table in self.data.groupby(by='day', sort=True)
        }

        self.manpower_shift_tables: dict[str: list] = None

    @property
    def time_granularities(self) -> dict[str: tuple]:
        time_granularities: dict[str: pd.DataFrame] = dict()  # {day: [begin_tm, end_tm, duration]}
        for day in list(self.dp_shift_tables.keys()):
            dp_table = self.dp_shift_tables[day]
            time_granularities_per_day = pd.DataFrame(columns=['begin_tm', 'end_tm'])

            time_stamps = list(set(dp_table['begin_tm'].to_list() + dp_table['end_tm'].to_list()))
            time_stamps.sort()  # TODO: 检查是否按顺序从小到大排列
            for i in range(len(time_stamps) - 1):
                new_df = pd.DataFrame({'begin_tm': [time_stamps[i]], 'end_tm': [time_stamps[i+1]]})
                if time_granularities_per_day.empty:
                    time_granularities_per_day = new_df
                else:
                    time_granularities_per_day = pd.concat([time_granularities_per_day, new_df], axis=0)

            time_granularities_per_day['duration'] = time_granularities_per_day['end_tm'] - time_granularities_per_day['begin_tm']
            time_granularities[day] = time_granularities_per_day

        return time_granularities

    def gen_manpower_shifts(self, ignore: list[int] = None, lower=4, upper=9) -> dict[str: pd.DataFrame]:
        # TODO: 改ignore, ignore实际上为要删除的人力班次的index
        if ignore is None:  # suppose to be: [(begin_tm_1, end_tm_1), ......]
            ignore = []

        manpower_shifts: dict[str: pd.DataFrame] = dict()  # {day: [begin_tm, end_tm, staff_num, duration]}
        for day in list(self.dp_shift_tables.keys()):
            dp_table = self.dp_shift_tables[day]

            manpower_shifts_per_day = pd.DataFrame()
            for begin_time in dp_table['begin_tm'].values:
                for record in dp_table[
                    (dp_table['end_tm'] >= begin_time + pd.Timedelta(lower, unit='hour')) &
                    (dp_table['end_tm'] <= begin_time + pd.Timedelta(upper, unit='hour'))
                ][['end_tm', 'staff_num']].values:
                    end_time, staff_num = record.tolist()
                    new_df = pd.DataFrame({'begin_tm': [begin_time], 'end_tm': [end_time], 'staff_num': [staff_num], 'duration': [end_time - begin_time]})
                    if manpower_shifts_per_day.empty:
                        manpower_shifts_per_day = new_df
                    else:
                        manpower_shifts_per_day = pd.concat([manpower_shifts_per_day, new_df], axis=0)

            # 要保证人力表的index表示的是真实的序, 然后再用ignore删除指定的行
            # 还要保证drop后人力表的index表示真实序, 然后才能通过解的序号索引出具体的班次
            manpower_shifts[day] = manpower_shifts_per_day.\
                reset_index(drop=True).\
                drop(ignore, axis=0).\
                reset_index(drop=True)

        self.manpower_shift_tables = manpower_shifts
        return manpower_shifts  # {day: [begin_tm, end_tm, staff_num, duration]}

    def get_manpower_shifts(self, staff_nums: list[list[int]], to_csv: str = None) -> dict[str: pd.DataFrame]:
        manpower_shifts = dict()
        days = list(self.manpower_shift_tables.keys())
        for i in range(len(days)):
            day = days[i]
            manpower_shift = self.manpower_shift_tables[day]
            manpower_shift['date'] = day
            manpower_shift['begin_tm'] = manpower_shift['begin_tm'].dt.strftime('%H:%M')
            manpower_shift['end_tm'] = manpower_shift['end_tm'].dt.strftime('%H:%M')
            manpower_shift['staff_num'] = staff_nums[i]
            manpower_shifts[day] = manpower_shift

        if type(to_csv) == str:
            pd.concat(manpower_shifts.values(), keys=manpower_shifts.keys()).to_csv(to_csv, index=False)
        return manpower_shifts

    @property
    def Y(self) -> list[list]:
        Y = []
        for day in list(self.dp_shift_tables.keys()):
            Y_n = self.dp_shift_tables[day][cols["y"]].to_list()
            Y.append(Y_n)
        return Y

    @property
    def l(self) -> list[list]:
        l = []
        for day in list(self.time_granularities.keys()):
            l_n = []
            for t, time_gran in self.time_granularities[day].iterrows():
                l_n.append(float((time_gran["duration"] / pd.Timedelta(minutes=1))) / 60)  # 分钟转小时
            l.append(l_n)
        return l

    @property
    def L_dp_shift(self) -> list[int | float]:
        # 每天的到发车班次时间结构都一样, 选一天算就行
        return get_L_xxx_shift(list(self.dp_shift_tables.values())[0])

    # ====== 注意：manpower_shift在stage1和stage2是不同的, 影响以下参数 ======

    @property
    def L_manpower_shift(self) -> list[int | float]:
        # 每天的人力班次时间结构都一样, 选一天算就行
        return get_L_xxx_shift(list(self.manpower_shift_tables.values())[0])

    @property
    def alpha(self) -> list[list[int]]:
        day = list(self.dp_shift_tables.keys())[0]
        return get_alpha_or_beta(self.dp_shift_tables[day], self.time_granularities[day])

    @property
    def beta(self) -> list[list[int]]:
        day = list(self.manpower_shift_tables.keys())[0]
        return get_alpha_or_beta(self.manpower_shift_tables[day], self.time_granularities[day])


def get_alpha_or_beta(shift_table: pd.DataFrame, time_gran_table: pd.DataFrame) -> list[list[int]]:
    # 获取alpha或者beta矩阵的底层逻辑都一样, 所以只需一个函数
    # 每天的结构一样, 取一天的算即可
    alpha_or_beta = []
    for t, time_gran in time_gran_table.iterrows():
        alpha_or_beta_t = []
        for s, shift in shift_table.iterrows():
            alpha_or_beta_t_s = 0
            if (time_gran[cols["begin_tm"]] >= shift[cols["begin_tm"]]) and (time_gran[cols["end_tm"]] <= shift[cols["end_tm"]]):
                alpha_or_beta_t_s = 1
            alpha_or_beta_t.append(alpha_or_beta_t_s)
        alpha_or_beta.append(alpha_or_beta_t)

    assert len(alpha_or_beta) == time_gran_table.shape[0], (len(alpha_or_beta), time_gran_table.shape, alpha_or_beta)
    assert len(alpha_or_beta[0]) == shift_table.shape[0], (len(alpha_or_beta[0]), shift_table.shape, alpha_or_beta)

    return alpha_or_beta


def get_L_xxx_shift(shift_table: pd.DataFrame) -> list[int | float]:
    # 获取L_manpower_shift或者L_df_shift向量的底层逻辑都一样, 所以只需一个函数
    L_xxx_shift = (shift_table["duration"] / pd.Timedelta(minutes=1)).astype(float) / 60
    L_xxx_shift = L_xxx_shift.to_list()
    assert len(L_xxx_shift) == shift_table.shape[0]
    return L_xxx_shift
