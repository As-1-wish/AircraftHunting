import sys
import numpy as np
from gym import spaces
from gym.utils import seeding
import time
import math
import copy
import random

if sys.version_info.major == 2:
    import Tkinter as tk
else:
    import tkinter as tk

WIDTH = 100  # 地图的宽度
HEIGHT = 100  # 地图的高度
UNIT = 10  # 每个方块的大小（像素值）   400m*400m的地图

ATTACK = 1
UAV_N = 3

V_X = 0
V_Y = -8
V_D = 6


class UAV(tk.Tk, object):
    def __init__(self, V=12, xy=np.array([[450., 410.]]), xy_UAV=np.array([[500., 520.], [590., 412.], [450., 550.]])):
        super(UAV, self).__init__()
        self.X_min = 0
        self.X_max = WIDTH * UNIT
        self.Y_min = 0
        self.Y_max = HEIGHT * UNIT
        # 记录无人机的位置
        self.AutoUAV = []
        self.AutoUAVOutline = []
        # 记录敌机的位置
        self.Aim = []

        self.xy = xy  # 地方无人机位置
        self.V = V
        self.V_D = V_D

        self.l_r = 1
        self.u_d = 0
        self.v_x = self.V_D * self.l_r
        self.v_y = self.V_D * self.u_d

        # 己方无人机位置
        self.xy_UAV = xy_UAV

        self.dis = np.zeros(3)
        self.state = np.zeros(11)

        self.build_maze()

        self.done_type = 0

    # 创建地图
    def build_maze(self):
        # 创建画布 Canvas.白色背景，宽高。
        self.canvas = tk.Canvas(self, bg='white', width=WIDTH * UNIT, height=HEIGHT * UNIT)

        '''
        # 标记出特殊区域
        for c in range(120, 280, UNIT * 4 - 1):
            x0, y0, x1, y1 = c, 120, c, 280
            self.canvas.create_line(x0, y0, x1, y1)
        for r in range(120, 280, UNIT * 4 - 1):
            x0, y0, x1, y1 = 120, r, 280, r
            self.canvas.create_line(x0, y0, x1, y1)
        '''
        # 创建敌机
        self.D_UAV = self.canvas.create_oval(
            self.xy[0][0] - 5, self.xy[0][1] - 5,
            self.xy[0][0] + 5, self.xy[0][1] + 5,
            fill='pink')

        # 己方无人机位置

        for i in range(UAV_N):
            L_UAV = self.canvas.create_oval(
                self.xy_UAV[i][0] - 6, self.xy_UAV[i][1] - 6,
                self.xy_UAV[i][0] + 6, self.xy_UAV[i][1] + 6,
                fill='yellow')
            self.AutoUAV.append(L_UAV)
        for i in range(UAV_N):
            L_UAV = self.canvas.create_oval(
                self.xy_UAV[i][0] - 50, self.xy_UAV[i][1] - 50,
                self.xy_UAV[i][0] + 50, self.xy_UAV[i][1] + 50,
                fill='', outline="red")
            self.AutoUAVOutline.append(L_UAV)

        self.canvas.pack()

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def reset(self):
        # self.render()
        # np.random.seed(123)
        for i in range(UAV_N):
            self.canvas.delete(self.AutoUAV[i])
            self.canvas.delete(self.AutoUAVOutline[i])
        self.canvas.delete(self.D_UAV)

        self.done_type = 0

        self.AutoUAV = []
        self.AutoUAVOutline = []

        self.Aim = []

        # self.xy = np.array([[random.randint(400, 600), random.randint(400, 600)]])  # 无人机位置
        #
        # # 己方无人机位置
        # self.xy_UAV = np.array([[random.randint(400, 600), random.randint(400, 600)],
        #                         [random.randint(400, 600), random.randint(400, 600)],
        #                         [random.randint(400, 600), random.randint(400, 600)]])

        r = l = u = d = 0
        for i in range(UAV_N):
            if self.xy_UAV[i][0] > self.xy[0][0]:
                r += self.xy_UAV[i][0] - self.xy[0][0]
            if self.xy_UAV[i][0] < self.xy[0][0]:
                l += self.xy[0][0] - self.xy_UAV[i][0]
            if self.xy_UAV[i][1] > self.xy[0][1]:
                d += self.xy_UAV[i][1] - self.xy[0][1]
            if self.xy_UAV[i][1] < self.xy[0][1]:
                u += self.xy[0][1] - self.xy_UAV[i][1]
        if r < max(l, u, d):
            self.l_r = 1
            self.u_d = 0
        if l < max(r, u, d):
            self.l_r = -1
            self.u_d = 0
        if u < max(r, l, d):
            self.l_r = 0
            self.u_d = -1
        if d < max(r, l, u):
            self.l_r = 0
            self.u_d = 1

        # if r == min(l, u, d, r):
        #     self.l_r = 1
        #     self.u_d = 0
        # if l == min(r, u, d, l):
        #     self.l_r = -1
        #     self.u_d = 0
        # if u == min(r, l, d, u):
        #     self.l_r = 0
        #     self.u_d = -1
        # if d == min(r, l, u, d):
        #     self.l_r = 0
        #     self.u_d = 1


        self.V_D = V_D
        self.v_x = self.V_D * self.l_r
        self.v_y = self.V_D * self.u_d

        self.D_UAV = self.canvas.create_oval(
            self.xy[0][0] - 5, self.xy[0][1] - 5,
            self.xy[0][0] + 5, self.xy[0][1] + 5,
            fill='pink')

        for i in range(UAV_N):
            L_UAV = self.canvas.create_oval(
                self.xy_UAV[i][0] - 6, self.xy_UAV[i][1] - 6,
                self.xy_UAV[i][0] + 6, self.xy_UAV[i][1] + 6,
                fill='yellow')
            self.AutoUAV.append(L_UAV)
        for i in range(UAV_N):
            L_UAV = self.canvas.create_oval(
                self.xy_UAV[i][0] - 50, self.xy_UAV[i][1] - 50,
                self.xy_UAV[i][0] + 50, self.xy_UAV[i][1] + 50,
                fill='', outline="red")
            self.AutoUAVOutline.append(L_UAV)

        self.flag = False

        for i in range(UAV_N):
            self.dis[i] = math.sqrt(
                pow(self.xy_UAV[i][0] - self.xy[0][0], 2) + pow(self.xy_UAV[i][1] - self.xy[0][1], 2))

        self.state = np.concatenate((self.xy.flatten() / (WIDTH * UNIT), self.xy_UAV.flatten() / (WIDTH * UNIT),
                                     self.dis.flatten() / (WIDTH * UNIT)))

        return self.state, self.xy, self.xy_UAV

    def step_move(self, action):
        done_n = []
        r_n = []
        done = False
        # 结束类型：-1敌机逃离，0成功捕获，1超出捕获距离
        done_type = 0
        r = np.zeros(3)

        xy_UAV_ = copy.deepcopy(self.xy_UAV)
        # 计算移动距离
        x_i = np.zeros(3)
        y_i = np.zeros(3)
        for i in range(UAV_N):
            theta = action[i] * 2 * math.pi
            x_i[i] = (self.V * np.cos(theta))
            y_i[i] = (self.V * np.sin(theta))

        Flag = False  # 无人机是否飞行标识
        for i in range(UAV_N):  # 无人机位置更新
            xy_UAV_[i][0] += x_i[i]
            xy_UAV_[i][1] += y_i[i]

            # 当无人机更新后的位置超出地图范围时
            # if pow((self.xy[0][0] - xy_UAV_[i][0]), 2) + \
            #         pow((self.xy[0][1] - xy_UAV_[i][1]), 2) <= 2000:
            #     if pow((self.xy[0][0] - xy_UAV_[i][0]), 2) + \
            #             pow((self.xy[0][1] - xy_UAV_[i][1]), 2) >= 1000:
            #         xy_UAV_[i][0] -= x_i[i] * 0.5
            #         xy_UAV_[i][1] -= y_i[i] * 0.5
            # 当无人机更新后的位置超出地图范围时
            # if xy_UAV_[i][0] >= self.X_min and xy_UAV_[i][0] <= self.X_max:
            #     if xy_UAV_[i][1] >= self.Y_min and xy_UAV_[i][1] <= self.Y_max:
            #         Flag = True
            #     else:
            #         xy_UAV_[i][0] -= x_i[i]
            #         xy_UAV_[i][1] -= y_i[i]
            # else:
            #     xy_UAV_[i][0] -= x_i[i]
            #     xy_UAV_[i][1] -= y_i[i]

        # 无人机位移绘图
        for i in range(UAV_N):
            self.canvas.move(self.AutoUAV[i], xy_UAV_[i][0] - self.xy_UAV[i][0],
                             xy_UAV_[i][1] - self.xy_UAV[i][1])
            self.canvas.move(self.AutoUAVOutline[i], xy_UAV_[i][0] - self.xy_UAV[i][0],
                             xy_UAV_[i][1] - self.xy_UAV[i][1])
        # self.render()

        dis_ = np.zeros(3)
        for i in range(UAV_N):
            dis_[i] = math.sqrt(pow((self.xy_UAV[i][0] - self.xy[0][0]), 2) + pow((self.xy_UAV[i][1] - self.xy[0][1]), 2))
        # wofang无人机位移完成
        self.xy_UAV = xy_UAV_

        # difang
        flag = False
        if self.l_r == 0:
            for i in range(UAV_N):
                if pow((self.xy[0][0] - self.xy_UAV[i][0]), 2) + pow((self.xy[0][1] - self.xy_UAV[i][1]), 2) <= 4900:
                    flag = True
                    if self.xy[0][0] - self.xy_UAV[i][0] > 0:
                        self.v_x = self.V_D * 1
                        self.v_y = self.V_D * self.u_d
                    else:
                        self.v_x = self.V_D * -1
                        self.v_y = self.V_D * self.u_d
        else:
            for i in range(UAV_N):
                if pow((self.xy[0][0] - self.xy_UAV[i][0]), 2) + pow((self.xy[0][1] - self.xy_UAV[i][1]), 2) <= 4900:
                    flag = True
                    if self.xy[0][1] - self.xy_UAV[i][1] > 0:
                        self.v_x = self.V_D * self.l_r
                        self.v_y = self.V_D * 1
                    else:
                        self.v_x = self.V_D * self.l_r
                        self.v_y = self.V_D * -1
        if flag:
            self.xy[0][0] += self.v_x
            self.xy[0][1] += self.v_y
        else:
            self.v_x = self.V_D * self.l_r
            self.v_y = self.V_D * self.u_d
            self.xy[0][0] += self.v_x
            self.xy[0][1] += self.v_y

        for i in range(UAV_N):
            if pow((self.xy[0][0] - self.xy_UAV[i][0]), 2) + pow((self.xy[0][1] - self.xy_UAV[i][1]), 2) <= 3600:
                r[i] += 100

        # chujie
        if self.xy[0][1] <= self.Y_min or self.xy[0][1] >= self.Y_max or self.xy[0][0] <= self.X_min or self.xy[0][
            0] >= self.X_max:
            done = True
            self.done_type = -1
            r += -10000
        self.canvas.move(self.D_UAV, self.v_x, self.v_y)

        for i in range(UAV_N):
            self.dis[i] = math.sqrt(
                pow((self.xy_UAV[i][0] - self.xy[0][0]), 2) + pow((self.xy_UAV[i][1] - self.xy[0][1]), 2))

        if self.Triangle(self.xy_UAV[0], self.xy_UAV[1], self.xy_UAV[2], self.xy[0]):
            if max(self.dis) < 70:
                print("success-----------------------------------------------------------------------")
                done = True
                self.done_type = 0
                r += 10000
            r += 200
        else:
            r += -20

        if np.nanmean(self.dis) > 300:
            done = True
            self.done_type = 1
            r += -1000

        for i in range(UAV_N):
            r[i] += (dis_[i] - self.dis[i]) * 10
            r_n.append(r[i])

        self.state = np.concatenate((self.xy.flatten() / (WIDTH * UNIT), self.xy_UAV.flatten() / (WIDTH * UNIT),
                                     self.dis.flatten() / (WIDTH * UNIT)))

        return self.state, r_n, done, self.xy, self.xy_UAV

    def Triangle(self, PointA, PointB, PointC, P):  # 找出P点是否位于以PointA，PointB，PointC三个点集的三角形中
        if P.shape != PointA.shape:  # 判断PointA中是否只有一个顶点，这种情况比较特殊，因为python矩阵只有一维那么即可以看成行向量也可以看成列向量
            Row = PointA.shape[0]
            PExtend = (np.tile(P, Row)).reshape(Row, 2)
        else:
            PExtend = P.reshape(1, 2)
            PointA = PointA.reshape(1, 2)
            PointB = PointB.reshape(1, 2)
            PointC = PointC.reshape(1, 2)
        PA = PointA - PExtend
        PB = PointB - PExtend
        PC = PointC - PExtend
        T1 = np.cross(PA, PB)
        T2 = np.cross(PB, PC)
        T3 = np.cross(PC, PA)
        flage1 = np.where(T1 * T2 >= 0, 1, 0)
        flage2 = np.where(T1 * T3 >= 0, 1, 0)
        Temp = flage1 * flage2  # 判断是否同向，如果Temp中存在True那么P点在三角形中
        Result = Temp[np.where(Temp == 1)]
        return Result.size

    def render(self, t=0.05):
        time.sleep(t)
        self.update()

    def sample_action(self):
        action = np.random.random(3)
        return action


# 这里的动画效果确实是UAV到达目标IoT位置后，满足悬停条件done = true， 然后界面开始刷新。
def update():  # 888888888888888888888888888888888888888888888888888888888888888

    for t in range(10):
        print('--------------------------------------------------------------------')
        s = env.reset()
        step = 0
        while True:
            step += 1
            env.render()
            action = env.sample_action()
            s_, r, done, x, y = env.step_move(action)
            s = s_
            if done:
                print(step)
                break


if __name__ == '__main__':
    env = UAV()
    env.after(10, update)
    env.mainloop()