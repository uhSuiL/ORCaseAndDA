import time
import numpy as np
from .util import is_land, GreatCircle, AdjacencyMat
from .tsp import tsp_branch_and_bound
from copy import deepcopy
from multiprocessing import Queue


class Particle:

	def __init__(self, particle_dim, demand_coords: np.ndarray):
		random_indices = np.random.choice(demand_coords.shape[0], int(particle_dim / 2))
		self.position = demand_coords[random_indices, :].flatten()
		self.velocity = np.random.uniform(0, 0.01, particle_dim)

		assert self.position.shape[-1] == self.velocity.shape[-1] == particle_dim, \
			(self.position.shape, self.velocity.shape)

	def fitness_value(self, start_coord: tuple | np.ndarray):
		coords = np.concatenate([start_coord, self.coords], axis=0)
		a_mat = AdjacencyMat.from_fully_connected(coords)
		node = tsp_branch_and_bound(a_mat)
		return node.path_length

	@property
	def coords(self) -> np.ndarray:
		return np.array([(self.position[i], self.position[i + 1]) for i in range(0, self.position.shape[0], 2)])

	@property
	def space_violation(self) -> float:
		violations = np.apply_along_axis(lambda array: 0 if is_land(lon=array[0], lat=array[1]) else 1, 1, self.coords)
		return np.sum(violations)

	def demand_violation(self, demand_coords: np.ndarray, distance_limit: float) -> float:
		distance_to_closest_station = np.apply_along_axis(
			lambda d_coord: np.min([
				GreatCircle.distance(lon1=coord[0], lat1=coord[1], lon2=d_coord[0], lat2=d_coord[1])
				for coord in self.coords
			]),
			axis=0,
			arr=demand_coords
		)
		violations = distance_to_closest_station - distance_limit / 2
		violations[violations > 0] = 1
		violations[violations <= 0] = 0
		return np.sum(violations)

	@staticmethod
	def better(particle1, particle2, demand_coords: np.ndarray, start_coord: np.ndarray, distance_limit: float):
		if particle2.space_violation < particle1.space_violation:
			return particle2
		elif particle2.space_violation == particle1.space_violation:
			if particle2.demand_violation(demand_coords, distance_limit) < particle1.demand_violation(demand_coords, distance_limit):
				return particle2
			elif particle2.demand_violation(demand_coords, distance_limit) == particle1.demand_violation(demand_coords, distance_limit):
				if particle2.fitness_value(start_coord) < particle1.fitness_value(start_coord):
					return particle2
		return particle1

	def update(self, g_best, p_best, omega, phi):
		r1, r2 = np.random.uniform(0, 1, 2)
		self.velocity = (
				omega * self.velocity
				+ phi * r1 * (p_best.position - self.position)
				+ phi * r2 * (g_best.position - self.position)
		)
		self.position += self.velocity


def pso(demand_coords: np.ndarray, start_coord: np.ndarray, queue: Queue, *,
		num_iter: int, num_particle: int, num_station: int, distance_limit: float, omega: float, phi: float) -> Particle:

	assert type(demand_coords) is np.ndarray, f"[Type not match] demand_coords is {type(demand_coords)}"
	assert type(start_coord) is np.ndarray, f"[Type not match] demand_coords is {type(start_coord)}"

	particle_dim = num_station * 2
	populations: list[tuple] = [(Particle(particle_dim, demand_coords), Particle(particle_dim, demand_coords))] * num_particle  # (p, p_best)
	g_best: Particle = Particle(particle_dim, demand_coords)

	for i in range(num_iter):
		for n in range(num_particle):
			start = time.time()

			particle, p_best = populations[n]
			original_p = deepcopy(particle)
			particle.update(g_best, p_best, omega, phi)
			p_best = Particle.better(particle, original_p, demand_coords, start_coord, distance_limit)
			g_best = Particle.better(p_best, g_best, demand_coords, start_coord, distance_limit)

			queue.put((
				i, n, time.time() - start,
				g_best.space_violation, g_best.demand_violation(demand_coords, distance_limit), g_best.fitness_value(start_coord), g_best.position,
				num_iter, num_particle, num_station, distance_limit
			))

	return g_best
