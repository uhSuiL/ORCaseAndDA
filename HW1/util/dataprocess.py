# --------------------- ATTENTION -----------------------------
#  the implementaion depends on the order in the `python dict`,
#  while for python lower than 3.6, there is no order in dict.
# -------------------------------------------------------------

import json
import pandas as pd


with open('./cols_config.json', 'r') as f:
    cols = json.load(f)


class Data:

    def __init__(self, data: pd.DataFrame) -> None:
        self.data                  = data[list(cols.values())].sort_values(by=cols["day"])
        self.data[cols["begin_tm"]]   = pd.to_datetime(self.data[cols["begin_tm"]].astype(str), format="%H%M")
        self.data[cols["end_tm"]]     = pd.to_datetime(self.data[cols["end_tm"]].astype(str), format="%H%M")
        self.data["duration"]   = self.data[cols["end_tm"]] - self.data[cols["begin_tm"]]

        self.dp_shift_tables: dict[pd.DataFrame]  = {
            day: dp_table for day , dp_table in self.data.groupby(by='day', sort=True)
        }

        self.manpower_shift_tables: dict[str: list] = None
    
    @property
    def time_granularities(self) -> dict[str: tuple]:
        time_granularities: dict[pd.DataFrame] = dict()  #  {day: [begin_tm, end_tm, duration]}
        for day in list(self.dp_shift_tables.keys()):
            dp_table = self.dp_shift_tables[day]
            time_granularities_per_day = pd.DataFrame(columns=['begin_tm', 'end_tm'])

            time_stamps = list(set(dp_table['begin_tm'].to_list() + dp_table['end_tm'].to_list()))
            time_stamps.sort()
            for i in range(len(time_stamps) - 1):
                time_granularities_per_day = pd.concat(
                    [time_granularities_per_day, pd.Series({'begin_tm': time_stamps[i], 'end_tm': time_stamps[i+1]})], axis=0)
            
            time_granularities[str(day)] = time_granularities_per_day

            time_granularities['duration'] = time_granularities['begin_tm'] - time_granularities['end_tm']
        return time_granularities
    
    def gen_manpower_shifts(self, ignore: list[tuple] = None, lower = 4, upper = 9) -> dict[str: pd.DataFrame]:
        if ignore is None:  # suppose to be: [(begin_tm_1, end_tm_1), ......]
            ignore = []

        man_power_shifts: dict[pd.DataFrame] = dict()  # {day: [begin_tm, end_tm, staff_num, duration]}
        for day in list(self.dp_shift_tables.keys()):
            dp_table = self.dp_shift_tables[day]
            
            man_power_shifts_per_day = pd.DataFrame()
            for begin_time in dp_table['begin_tm'].values:
                for record in dp_table[
                    (dp_table['end_tm'] > begin_time + pd.Timedelta(lower, unit='hour')) & 
                    (dp_table['end_tm'] < begin_time + pd.Timedelta(upper, unit='hour'))
                ][['end_tm', 'staff_num']].values:
                    end_time, staff_num = record.tolist()
                    if (begin_time, end_time) not in ignore:
                        man_power_shifts_per_day = pd.concat([
                            man_power_shifts_per_day,
                            pd.Series({
                            'begin_tm': begin_time, 'end_tm': end_time, 
                            'staff_num': staff_num, 'duration': end_time - begin_time
                        })], axis=0)
            man_power_shifts[str(day)] = man_power_shifts_per_day

        self.manpower_shift_tables = man_power_shifts
        return man_power_shifts  # {day: [begin_tm, end_tm, staff_num, duration]}
    
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
                l_n.append(time_gran["duration"])
            l.append(l_n)
        return l

    @property
    def L_dp_shift(self) -> list[int|float]:
        # 每天的到发车班次时间结构都一样, 选一天算就行
        return get_L_xxx_shift(list(self.dp_shift_tables.values())[0])
    
    # ====== 注意：manpower_shift在stage1和stage2是不同的, 影响以下参数 ======

    @property
    def L_manpower_shift(self) -> list[int|float]:
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
    for i, time_gran in time_gran_table.iterrows():
        alpha_t = []
        for j, shift in shift_table.iterrows():
            alpha_t_s = 0
            if (time_gran[cols["begin_tm"]] <= shift[cols["begin_tm"]]) and (time_gran[cols["end_tm"]] >= shift[cols["end_tm"]]):
                alpha_t_s = 1
            alpha_t.append(alpha_t_s)
        alpha_or_beta.append(alpha_t)

    assert len(alpha_or_beta) == time_gran_table.shape[0], (len(alpha_or_beta), time_gran_table.shape, alpha_or_beta)
    assert len(alpha_or_beta[0]) == shift_table.shape[0], (len(alpha_or_beta[0]), shift_table.shape, alpha_or_beta)

    return alpha_or_beta

    
def get_L_xxx_shift(shift_table: pd.DataFrame) -> list[int|float]:
    # 获取L_manpower_shift或者L_df_shift向量的底层逻辑都一样, 所以只需一个函数
    L_xxx_shift = shift_table["duration"].to_list()
    assert len(L_xxx_shift) == shift_table.shape[0]
    return L_xxx_shift
