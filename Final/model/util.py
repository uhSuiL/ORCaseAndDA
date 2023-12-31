import math
import numpy as np
from global_land_mask import globe


def is_land(lat, lon):
	"""Check if a point is on land"""
	return globe.is_land(lon=lon, lat=lat)


class GreatCircle:
	def __init__(self, earth_radius = 6371):
		self.earth_radius = earth_radius  # km

	def __call__(self, lat1, lon1, lat2, lon2):
		lat1_rad = math.radians(lat1)
		lon1_rad = math.radians(lon1)
		lat2_rad = math.radians(lat2)
		lon2_rad = math.radians(lon2)

		delta_lon = lon2_rad - lon1_rad
		_ = math.sin(lat1_rad) * math.sin(lat2_rad) + math.cos(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)
		try:
			# to avoid numeric problem like: 1.0000000000000002
			if 0 < _ - 1 < 1e-5:
				_ = 1
			elif 0 < -1 - _ < 1e-5:
				_ = -1
			central_angle = math.acos(_)
		except ValueError as ve:
			print(lat1, lon1, lat2, lon2, _)
			raise ve
		distance = central_angle * self.earth_radius
		return distance

	@staticmethod
	def distance(lat1, lon1, lat2, lon2):
		great_circle_dis = GreatCircle()
		return great_circle_dis(lat1, lon1, lat2, lon2)


class AdjacencyMat:
	@staticmethod
	def from_fully_connected(coords, distance_fn = GreatCircle(), diagonal = float('inf')) -> np.ndarray:
		num_point = len(coords)
		a_mat = np.ones((num_point, num_point)) * diagonal
		for i in range(num_point):
			for j in range(num_point):
				if i != j:
					a_mat[i, j] = distance_fn(lon1=coords[i][0], lat1=coords[i][1], lon2=coords[j][0], lat2=coords[j][1])
		return a_mat
