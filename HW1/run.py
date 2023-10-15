import pandas as pd


# 班次生成约束：
#   - 人力班次以月为单位
#   - 每班人力班次时长4~9小时
#   - 一个仓管班次的开始时间为至少一个到发车班次的开始时间
#   - 一个仓管班次的结束时间为至少一个到发车班次的结束时间
class WMSP:

    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data

        self.data['begin_tm']   = pd.to_datetime(self.data['begin_tm'].astype(str), format="%H%M")
        self.data['end_tm']     = pd.to_datetime(self.data['end_tm'].astype(str), format="%H%M")
        self.data['duration']   = self.data['end_tm'] - self.data['begin_tm']

        self.dp_tables:             dict[pd.DataFrame]  = {day: dp_table for day , dp_table in self.data.groupby(by='day', sort=True)}
        self.time_granularities:    dict[pd.DataFrame]  = dict()  #  {day: [begin_tm, end_tm, duration]}
        self.man_power_shifts:      dict[pd.DataFrame]  = dict()  # {day: [begin_tm, end_tm, staff_num]}

        self.alpha: list[list] = [[]]  # shape: (num_day, num_manpower_shift)
        self.beta:  list[list] = [[]]  # shape: (num_day, num_dp_shift)
    
    def get_time_granularities(self):
        for day in self.dp_tables.keys():
            dp_table = self.dp_tables[day]
            time_granularities = pd.DataFrame(columns=['begin_tm', 'end_tm'])

            time_stamps = set(dp_table['begin_tm'].to_list() + dp_table['end_tm'].to_list())
            for i in range(len(time_stamps) - 1):
                time_granularities.append({'begin_tm': time_stamps[i], 'end_tm': time_stamps[i+1]})
            
            self.time_granularities[str(day)] = time_granularities
        return self
    
    def get_manpower_shifts(self, upper = 9, lower = 4):
        for day, dp_table in self.dp_tables:
            man_power_shifts = pd.DataFrame()
            for begin_time in dp_table['begin_tm'].values:
                for record in dp_table[
                    (dp_table['end_tm'] > begin_time + pd.Timedelta(lower, unit='hour')) & 
                    (dp_table['end_tm'] < begin_time + pd.Timedelta(upper, unit='hour'))
                ][['end_tm', 'staff_num']].values:
                    end_time, staff_num = record.tolist()
                    man_power_shifts.append(
                        {'begin_tm': begin_time, 'end_tm': end_time, 'staff_num': staff_num, 'duration': end_time - begin_time}
                    )
            self.man_power_shifts[str(day)] = man_power_shifts
        return self
    
    def compute_alpha_and_beta(self):
        for day_t in self.time_granularities.keys():
            time_granularities: pd.DataFrame = self.time_granularities[day_t]
            man_power_shifts:   pd.DataFrame = self.man_power_shifts[day_t]
            dp_tables:          pd.DataFrame = self.dp_tables[day_t]
                            
        

if __name__ == '__main__':
    data = pd.read_excel(
        io='./effiandshifts.xlsx', 
        usecols=[
            'dp_schedule', 'dp_period', 
            'staff_effi_standard', 'staff_effi_full', 'staff_num', 
            'day', 'begin_tm', 'end_tm', 'y']
    )

    WMSP(data)
    
