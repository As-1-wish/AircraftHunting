from env import UAV
from DDPG import DDPG
import tensorflow as tf
import numpy as np
import copy

env = UAV(V=8, xy=np.array([[350., 400.]]), xy_UAV=np.array([[100., 100.], [350., 600.], [600., 100.]]))
agent = DDPG(env)
XY = []
XY_UAV = []


def evaluate(episode):
    agent.load_actor(1300)
    for i in range(episode):
        s, xy, xy_UAV = env.reset()
        env.render()
        step = 0
        XY.append(copy.deepcopy(xy))
        XY_UAV.append(xy_UAV)
        while True:
            step += 1
            a = tf.squeeze(agent.act(s))
            s_, r, done, xy, xy_UAV = env.step_move(a)
            XY.append(copy.deepcopy(xy))
            XY_UAV.append(xy_UAV)
            env.render()
            if done or step > 100:
                break
            else:
                s = s_
    return np.array(XY).squeeze(), np.array(XY_UAV).squeeze()


print(evaluate(1))
