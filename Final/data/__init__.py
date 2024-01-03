import numpy as np


REFER = 'https://hifld-geoplatform.opendata.arcgis.com/search?collection=Dataset&groupIds=2900322cc0b14948a74dca886b7d7cfc'

source_dir = 'D:/DataHub/Homeland Infrastructure Foundation-Level Data/'
source_dir_wsl = '/mnt/d/DataHub/Homeland Infrastructure Foundation-Level Data/'

CITY = 'SAN FRANCISCO'


configs = {
	'params': {
		"num_iter": 10000,
		"num_particle": 30,
		"num_station": 5,
		"distance_limit": 6,  # km,
		"omega": 0.6,  # 0.6 is good
		"phi": 2
	},
}

batch_for_omega = [
	{
		"num_iter": 10000,
		"num_particle": 30,
		"num_station": 5,
		"distance_limit": 40,  # km,
		"omega": omega,
		"phi": 2
	}
	for omega in np.arange(0.4, 1, 0.1)
]

batch_for_distance_limit = [
	{
		"num_iter": 10000,
		"num_particle": 30,
		"num_station": 5,
		"distance_limit": l,  # km,
		"omega": None,  # TODO: fill
		"phi": 2
	}
	for l in range(10, 55, 5)
]

batch_for_num_station = [
	{
		"num_iter": 10000,
		"num_particle": 30,
		"num_station": n,
		"distance_limit": None,  # km,  TODO: fill
		"omega": None,  # TODO: fill
		"phi": 2
	}
	for n in range(3, 8)
]
