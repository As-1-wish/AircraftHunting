import copy
from pursuit2.env import UAV
from pursuit2.DDPG import DDPG
import tensorflow as tf
import numpy as np
import random


def evaluate(xy, xy_UAV):
    global done_type
    env = UAV(V=12, xy=xy, xy_UAV=xy_UAV)
    agent = DDPG(env)
    difang = []
    wofang = []
    agent.load_actor(49500)

    s, xy, xy_UAV = env.reset()
    env.render()
    step = 0
    sum_r = 0
    difang.append(copy.deepcopy(xy))
    wofang.append(xy_UAV)
    while True:
        step += 1
        a = tf.squeeze(agent.act(s))
        s_, r, done, xy, xy_UAV = env.step_move(a)

        sum_r += sum(r)
        difang.append(copy.deepcopy(xy))
        wofang.append(xy_UAV)
        env.render()
        if done:
            done_type = env.done_type
            break
        else:
            s = s_
    # 敌方无人机坐标， 我方无人机坐标， 结束条件：0成功捕获，1超出捕获距离，-1围猎失败
    return difang, wofang, done_type


# # 敌方无人机初始位置（在中心200x200区域内随机，可以由前端传入，但取值要在400-600）
# xy = np.array([[random.randint(400, 600), random.randint(400, 600)]])
# # 我方无人机初始位置（在中心200x200区域内随机，可以由前端传入，但取值要在400-600）
# xy_UAV = np.array([[random.randint(400, 600), random.randint(400, 600)],
#                         [random.randint(400, 600), random.randint(400, 600)],
#                         [random.randint(400, 600), random.randint(400, 600)]])
# print(evaluate(xy, xy_UAV))
