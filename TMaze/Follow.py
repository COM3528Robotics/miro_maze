from math import dist

from utils import Utils


class Follow:
    def rule_linear(dist_l, dist_r, scale=1, cap=1):
        dist_l = dist_l * scale
        dist_r = dist_r * scale

        spd_l = dist_l
        spd_r = dist_r

        return min(spd_l, cap), min(spd_r, cap)

    def rule_delta_linear(dist_l, dist_r, scale=1, cap=1):
        delta = (dist_l - dist_r) * scale
        delta = Utils.bound(delta, cap)
        return delta, -delta 


    def rule_ratio(dist_l, dist_r, scale=1, cap=1):
        dist_l = dist_l * scale
        dist_r = dist_r * scale

        total = (dist_l + dist_r)

        spd_l = dist_l / total
        spd_r = dist_r / total

        return spd_l *cap, spd_r * cap
