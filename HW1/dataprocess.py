import pandas as pd


class UsefulCols(dict):
    def __init__(self):
        super.__init__(    
            dp_schedule         = 'dp_schedule',
            dp_period           = 'dp_period',
            staff_effi_standard = 'staff_effi_standard',
            staff_effi_full     = 'staff_effi_full',
            staff_num           = 'staff_num',
            day                 = 'day',
            begin_tm            = 'begin_tm',
            end_tm              = 'end_tm',
            y                   = 'y',
            duration            = 'duration',
        )

    def __call__(self) -> tuple:
        return tuple(self.values())

cols = UsefulCols()


class Data:

    def __init__(self, data: pd.DataFrame, manpower_shift_lower = 4, manpower_shift_upper = 9) -> None:
        self.manpower_shift_lower = manpower_shift_lower
        self.manpower_shift_upper = manpower_shift_upper

        self.data = data[cols()].sort_values(by=cols.day)
        self.data[cols.begin_tm]   = pd.to_datetime(self.data[cols.begin_tm].astype(str), format="%H%M")
        self.data[cols.end_tm]     = pd.to_datetime(self.data[cols.end_tm].astype(str), format="%H%M")
        self.data[cols.duration]   = self.data[cols.end_tm] - self.data[cols.begin_tm]

        self.dp_tables: dict[pd.DataFrame]  = {
            day: dp_table for day , dp_table in self.data.groupby(by='day', sort=True)
        }

        self.alpha: list[list] = [[]]  # shape: (num_day, num_manpower_shift)
        self.beta:  list[list] = [[]]  # shape: (num_day, num_dp_shift)
    
    @property
    def time_granularities(self) -> dict[str: tuple]:
        time_granularities: dict[pd.DataFrame] = dict()  #  {day: [begin_tm, end_tm, duration]}
        for day in self.dp_tables.keys():
            dp_table = self.dp_tables[day]
            time_granularities_per_day = pd.DataFrame(columns=['begin_tm', 'end_tm'])

            time_stamps = set(dp_table['begin_tm'].to_list() + dp_table['end_tm'].to_list())
            for i in range(len(time_stamps) - 1):
                time_granularities_per_day.append({'begin_tm': time_stamps[i], 'end_tm': time_stamps[i+1]})
            
            time_granularities[str(day)] = time_granularities_per_day
        return time_granularities
    
    @property
    def manpower_shifts(self) -> dict[str: list]:
        man_power_shifts: dict[pd.DataFrame] = dict()  # {day: [begin_tm, end_tm, staff_num]}
        for day, dp_table in self.dp_tables:
            man_power_shifts_per_day = pd.DataFrame()
            for begin_time in dp_table['begin_tm'].values:
                for record in dp_table[
                    (dp_table['end_tm'] > begin_time + pd.Timedelta(self.manpower_shift_lower, unit='hour')) & 
                    (dp_table['end_tm'] < begin_time + pd.Timedelta(self.manpower_shift_upper, unit='hour'))
                ][['end_tm', 'staff_num']].values:
                    end_time, staff_num = record.tolist()
                    man_power_shifts_per_day.append({
                        'begin_tm': begin_time, 'end_tm': end_time, 
                        'staff_num': staff_num, 'duration': end_time - begin_time
                    })
            man_power_shifts[str(day)] = man_power_shifts_per_day
        return man_power_shifts

    