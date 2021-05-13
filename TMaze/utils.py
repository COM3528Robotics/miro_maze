class Utils:
    def bound(value, limit):
        return min(max(value, -limit), limit)
