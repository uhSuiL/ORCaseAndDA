import numpy as np


REFER = 'https://hifld-geoplatform.opendata.arcgis.com/search?collection=Dataset&groupIds=2900322cc0b14948a74dca886b7d7cfc'

# source_dir = 'D:/DataHub/Homeland Infrastructure Foundation-Level Data/'
# source_dir_wsl = '/mnt/d/DataHub/Homeland Infrastructure Foundation-Level Data/'
source_dir = 'path/to/your/source data/'
source_dir_wsl = 'path/to/your/source data/'

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
		"omega": 0.7,  # 0.7 is best
		"phi": 2
	}
	for l in range(1, 38, 3)
]

batch_for_num_station = [
	{
		"num_iter": 3000,
		"num_particle": 30,
		"num_station": n,
		"distance_limit": 7,  # km,
		"oa": 0.7,
		"phi": 2
	}
	for n in range(4, 16)
]
