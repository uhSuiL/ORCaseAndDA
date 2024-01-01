import os
import pandas as pd
import data
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
            f.writelines('num_iter,num_particle,duration(s),space_violation,demand_violation,fitness')

        while True:
            i, n, duration, g_best, *config = self.queue.get()
            print(f"[iter {i} particle {n} ({duration: .3f}s) (config: {config})]\
                 space violation: {g_best.space_violation}, \
                 demand violation: {g_best.demand_violation}, \
                 fitness: {g_best.fitness}")
            with open(self.home + 'log.csv', mode='a', encoding='utf-8') as f:
                f.writelines(
                    f'{i},{n},{duration},{g_best.space_violation},{g_best.demand_violation},{g_best.fitness},{config}'
                )


if __name__ == '__main__':
    logger = Logger()
    logger.start()

    table = pd.read_csv(data.source_dir + data.CITY + '.csv')
    demand_coords = table.loc[:, ['X', 'Y']]

    flp.pso()
