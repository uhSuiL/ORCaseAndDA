import os
import sys

if sys.platform == 'win32':
    raise RuntimeError("No Windows! Linux Please.")

import numpy as np
import pandas as pd
import data
from data import configs
from model import flp
from datetime import datetime
from multiprocessing import Process, Manager
from concurrent.futures import ProcessPoolExecutor, Future


class Logger(Process):
    def __init__(self, home: str = './log/'):
        super().__init__()

        self.manager = Manager()
        self.queue = self.manager.Queue()
        self.daemon = True
        self.home = home + datetime.now().strftime("%Y-%m-%d-%H-%M-%S/")

        if not os.path.exists(self.home):
            os.makedirs(self.home)
            print(f"Log to {self.home}")

    def run(self):
        print("Logger start")

        # header: num_iter,duration(s),num_illegal,space_violation,demand_violation,fitness,config
        while True:
            label, num_illegal, space_violation, demand_violation, fitness, pos, *config = self.queue.get()
            if label[0] == 'global best':
                i = label[1]
                duration = ""
                log_name, pos_name = 'best_log', 'best_pos'
                # print(f"""[iter {i} (config: {config})] num illegal: {num_illegal} space violation: {space_violation}, demand violation: {demand_violation}, fitness: {fitness}""")
            elif label[0] == 'track':
                n, i, duration = label[1:]
                log_name, pos_name = f'track {n} log', f'track {n} pos'
            else:
                raise ValueError(f"Undefined label: {label}")

            with open(self.home + f'{log_name}.csv', mode='a', encoding='utf-8') as f:
                f.write(f'{i},{duration},{num_illegal},{space_violation},{demand_violation},{fitness},{config}\n')
            with open(self.home + f'{pos_name}.csv', mode='a', encoding='utf-8') as f:
                f.write(str(pos.flatten().tolist()).lstrip('[').rstrip(']') + '\n')


def test_batch(demand_coords: np.ndarray, start_coord: np.ndarray, name: str, configs: list[dict]):
    pool = ProcessPoolExecutor()
    print(f"Start test_{name}")

    futures: list[Future] = [pool.submit(
        flp.pso,
        demand_coords, start_coord, logger.queue, **config, track=list(range(5))
    ) for config in configs]
    [future.result() for future in futures]

    print(f"Finish test_{name}")
    pool.shutdown()


if __name__ == '__main__':
    logger = Logger()
    logger.start()

    table = pd.read_csv(data.source_dir_wsl + data.CITY + '.csv')
    start_point = table[table['TYPE'] == 'Public_Health_Departments']

    start_coord = start_point.loc[:, ['X', 'Y']].to_numpy()
    demand_coords = table.loc[:, ['X', 'Y']].to_numpy()

    # flp.pso(demand_coords, start_coord, logger.queue, **configs['params'], track=list(range(10)))
    # test_batch(demand_coords, start_coord, 'omega', data.batch_for_omega)
    # test_batch(demand_coords, start_coord, 'distance_limit', data.batch_for_distance_limit)
    test_batch(demand_coords, start_coord, 'num_station', data.batch_for_num_station)

    logger.queue.join()
    # TODO: test the code without parallel
    # TODO: comparison among different params in parallel
