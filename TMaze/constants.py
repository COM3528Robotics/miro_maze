class Action:
    FOLLOW = 1
    TURN_LEFT = 2
    TURN_RIGHT = 3
    MAKE_DECISION = 4

class Maze:
    # Arrays of tag IDs
    END_TAGS = [3, 4, 5, 6]
    REWARDS = [3]
    PUNISHMENT = []

    JUNCTIONS = [0]
    CORNERS_LEFT = [2]
    CORNERS_RIGHT = [1]

class Behaviour:
    # always choose highest predicted reward
    GREEDY = 1
    # probability of choosing action based on difference between predicted rewards
    #NOT IMPLEMENTED, TOO LAZY, if greedy works, we can try
    WEIGHTED = 2