from os import error
import random
import pickle

from constants import *

class Learning:
    def __init__(self, default_prediction=0, learning_rate=1, behaviour=Behaviour.GREEDY, read_predictions=False):
        # dict of predicted rewards, updates as it learns
        # keys are a pair of state and action
            # self.predicted_reward[some_state, action_taken] = predicted_reward
        self.predicted_reward = dict()

        # default prediction for state, action pairs not yet explored  
            # can be changed for more optimistic / pessimistic behaviour 
        self.default_prediction = default_prediction
        self.learning_rate = learning_rate
        self.behaviour = behaviour

        # only read if there's something there
        if read_predictions:
            self.read()

    # current state is the tag it is seeing right now
    def decide(self, current_state=None):
        
        predicted_left = self.predicted_reward.get((current_state, Action.TURN_LEFT), self.default_prediction)
        predicted_right = self.predicted_reward.get((current_state, Action.TURN_RIGHT), self.default_prediction)
        
        print("Current State: %s, Predicted Left: %s, Right: %s" %\
            (current_state, predicted_left, predicted_right))
        
        if predicted_left == predicted_right:
            return random.choice([Action.TURN_LEFT, Action.TURN_RIGHT])

        if self.behaviour is Behaviour.GREEDY:
            if predicted_left > predicted_right:
                return Action.TURN_LEFT
            else:
                return Action.TURN_RIGHT

        if self.behaviour is Behaviour.WEIGHTED:
            pass

        return random.choice([Action.TURN_LEFT, Action.TURN_RIGHT])

    def learn(self, previous_state, previous_action, reward):
        if previous_state is None or previous_action is None:
            return

        print("Previous State: %s, Previous Action: %s" % (previous_state, previous_action))
        predicted_reward = self.predicted_reward.get((previous_state, previous_action), self.default_prediction)

        # if the state reached is not a reward state, calculate reward using max predicted reward of next action
        if reward is None:
            # predicted_left = self.predicted_reward.get((current_state, Action.TURN_LEFT), self.default_prediction)
            # predicted_right = self.predicted_reward.get((current_state, Action.TURN_RIGHT), self.default_prediction)
            # reward = max(predicted_left,predicted_right)
            pass

        change_in_prediction = (reward - predicted_reward) * self.learning_rate
        self.predicted_reward[(previous_state, previous_action)] = predicted_reward + change_in_prediction
       
    # if currently reached state is not an end state, predict current reward using reward of next action
    def predict_next_reward(self, current_state=None):
        predicted_left = self.predicted_reward.get((current_state, Action.TURN_LEFT), self.default_prediction)
        predicted_right = self.predicted_reward.get((current_state, Action.TURN_RIGHT), self.default_prediction)
        return max(predicted_left, predicted_right)

    def read(self):
        try:
            self.predicted_reward = pickle.load(open('learned_predictions', 'rb'))
            print("Read Success!")
            print(self.predicted_reward)
        except error:
            print(error)

    def export(self):
        pickle.dump(self.predicted_reward, open('learned_predictions','wb'))
        