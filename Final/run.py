import os
import pandas as pd
import data
from data import configs
from model import flp
from datetime import datetime
from multiprocessing import Queue, Process


class Logger(Process):
    def __init__(self, home: str = './log/'):
        super().__init__()

        self.queue = Queue()
        self.daemon = True
        self.home = home + datetime.now().strftime("%Y-%m-%d-%H-%M-%S/")

        if not os.path.exists(self.home):
            os.makedirs(self.home)
            print(f"Log to {self.home}")

    def run(self):
        print("Logger start")
        with open(self.home + 'log.csv', mode='a', encoding='utf-8') as f:
            f.write('num_iter,num_particle,duration(s),space_violation,demand_violation,fitness,config,best_coord\n')

        while True:
            i, n, duration, space_violation, demand_violation, fitness, best_pos, *config = self.queue.get()
            print(f"""[iter {i} particle {n} ({duration: .3f}s) (config: {config})] space violation: {space_violation}, demand violation: {demand_violation}, fitness: {fitness}""")
            with open(self.home + 'log.csv', mode='a', encoding='utf-8') as f:
                f.write(f'{i},{n},{duration},{space_violation},{demand_violation},{fitness},{config}\n')
            with open(self.home + 'best_pos.csv', mode='a', encoding='utf-8') as f:
                f.write(str(best_pos.flatten().tolist()).lstrip('[').rstrip(']') + '\n')


if __name__ == '__main__':
    logger = Logger()
    logger.start()

    table = pd.read_csv(data.source_dir + data.CITY + '.csv')
    start_point = table[table['TYPE'] == 'Public_Health_Departments']

    start_coord = start_point.loc[:, ['X', 'Y']].to_numpy()
    demand_coords = table.loc[:, ['X', 'Y']].to_numpy()

    flp.pso(demand_coords, start_coord, logger.queue, **configs.params1)
    # TODO: test the code without parallel
    # TODO: comparison among different params in parallel
