
import numpy as np
from enum import Enum, unique

import time


def timeit(func):
    def wrapper(*args, **wargs):
        start = time.time()
        res = func(*args, **wargs)
        end = time.time()
        print(f'{func.__name__}: {(end-start)*1000}')
        return res
    return wrapper


# Status
UNKNOWN = -1
NOISE = -2


class DBSCAN(object):
    """
    Base Class of DBSCAN, please do NOT instantiate this Class
    """

    def __init__(self, path):
        """
        DBSCAN Classes should be instantiate with data file path
        """
        self.m, _ = self._load_data(path)
        self.num_p = self.m.shape[0]
        self.tags = [UNKNOWN] * self.num_p

    def _load_data(self, path: str):
        with open(path, 'r') as f:
            data = []
            label = []
            for l in f.readlines():
                source = l.strip().split()
                data.append([float(val) for val in source[:2]])
                label.append(int(source[-1]))
            return np.array(data), np.array(label)

    def _get_dist(self, a, b, fast_mode: bool = False) -> float:
        """
        for float comparison, set all distance value precision to 5
        :param: a: int; index of given point in data matrix
        :param: b: same as a
        :param: fast_mode: bool -> if True, ignore sqrt() opration for distance
        """
        if fast_mode:
            result = np.power(self.m[b] - self.m[a], 2).sum()
        else:
            result = np.sqrt(np.power(self.m[b] - self.m[a], 2).sum())
        return round(result, 5)

    def _get_neighbours(self, p: int, eps: float, fast_mode=False) -> list:
        """
        return neighbours index of given point p in source data matrix
        :param: p: int; index of given point in data matrix
        :param: eps: float; the value of radius of density area
        """
        pass

    def _clustering(self, p, eps, min_pts, cluster_id, fast_mode=False):
        """
        tag given point p and all of its neighbours and sub-neighbours with the same cluster id
        :param: m: np.matrix; N * 2 matrix recoding all nodes' coordinates
        :param: eps: float; the value of radius of density area
        :param: min_pts: int; least neighbours should be in a density area
        :param: cluster_id: int; current id of cluster
        """
        pass

    @timeit
    def predict(self, eps, min_pts, fast_mode=False) -> list:
        """
        return list of labels as the sequence in data matrix
        :param: m: np.matrix; N * 2 matrix recoding all nodes' coordinates
        :param: eps: float; the value of radius of density area
        :param: min_pts: int; least neighbours should be in a density area
        """

        cluster_id = 1
        for p_id in range(self.num_p):
            if self.tags[p_id] != UNKNOWN:
                continue
            if self._clustering(p_id, eps, min_pts, cluster_id, fast_mode):
                cluster_id += 1
        return np.array(self.tags)


class NaiveDBSCAN(DBSCAN):

    def __init__(self, path):
        super(NaiveDBSCAN, self).__init__(path)

    def _get_neighbours(self, p: int, eps: float, fast_mode=False) -> list:

        ngbs = []
        for idx in range(len(self.m)):
            if self._get_dist(p, idx, fast_mode) < eps:
                ngbs.append(idx)
        return ngbs

    def _clustering(self, p, eps, min_pts, cluster_id, fast_mode=False) -> bool:

        neighbours = self._get_neighbours(p, eps, fast_mode)
        if len(neighbours) < min_pts:
            self.tags[p] = NOISE
            return False
        else:
            self.tags[p] = cluster_id
            for idx in neighbours:
                self.tags[idx] = cluster_id
            while len(neighbours) > 0:
                sub_neighbours = self._get_neighbours(neighbours[0], eps, fast_mode)
                if len(sub_neighbours) >= min_pts:
                    for sub_n in sub_neighbours:
                        if self.tags[sub_n] < 0:
                            self.tags[sub_n] = cluster_id
                            if self.tags[sub_n] == UNKNOWN:
                                neighbours.append(sub_n)
                neighbours = neighbours[1:]
        return True


class MatrixDBSCAN(DBSCAN):

    def __init__(self, path):
        super(MatrixDBSCAN, self).__init__(path)
        self._get_distance_matrix()     # self.dist_m will be created
        del self.m

    def _get_distance_matrix(self):
        """
        Only once calculation will be on each point-pairs
        results will be stored in self.dist_m
        """

        self.dist_m = np.zeros((self.num_p, self.num_p))
        for p_id in range(self.num_p):
            for q_id in range(p_id, self.num_p):
                dist = self._get_dist(p_id, q_id)
                self.dist_m[q_id, p_id] = dist
                self.dist_m[p_id, q_id] = dist

    def _get_neighbours(self, p: int, eps: float, fast_mode=False) -> list:
        return list(np.nonzero(self.dist_m[p] < eps))

    def _clustering(self, p, eps, min_pts, cluster_id, fast_mode=False) -> bool:
        """
        TODO: There should be some optimizations for this part, current code is too ugly
        """

        neighbours = self._get_neighbours(p, eps, fast_mode)
        if len(neighbours) < min_pts:
            self.tags[p] = NOISE
            return False
        else:
            self.tags[p] = cluster_id
            for idx in neighbours:
                self.tags[idx] = cluster_id
            while len(neighbours) > 0:
                sub_neighbours = self._get_neighbours(neighbours[0], eps, fast_mode)
                if len(sub_neighbours) >= min_pts:
                    for sub_n in sub_neighbours:
                        if self.tags[sub_n] < 0:
                            self.tags[sub_n] = cluster_id
                            if self.tags[sub_n] == UNKNOWN:
                                neighbours.append(sub_n)
                neighbours = neighbours[1:]
        return True

if __name__ == '__main__':

    pass
            