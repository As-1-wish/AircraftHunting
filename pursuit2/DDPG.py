import gym
import random
import imageio
import datetime
import numpy as np
from collections import deque
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Lambda, Concatenate
from tensorflow.keras.optimizers import Adam
from pursuit2.env import UAV
from matplotlib import pyplot as plt
import os


from pursuit2.Prioritized_Replay import Memory

# Original paper: https://arxiv.org/pdf/1509.02971.pdf
# DDPG with PER paper: https://cardwing.github.io/files/RL_course_report.pdf

tf.keras.backend.set_floatx('float64')

EPISODE = 60000

def actor(state_shape, action_dim, action_bound,  units=(512, 256)):
    state = Input(shape=state_shape)
    x = Dense(units[0], name="L0", activation='relu')(state)
    for index in range(1, len(units)):
        x = Dense(units[index], name="L{}".format(index), activation='relu')(x)

    unscaled_output = Dense(action_dim, name="Out", activation='tanh')(x)

    output = (unscaled_output + 1) / 2

    model = Model(inputs=state, outputs=output)

    return model


def critic(state_shape, action_dim, units=(64, 32)):
    inputs = [Input(shape=state_shape), Input(shape=(action_dim,))]
    concat = Concatenate(axis=-1)(inputs)
    x = Dense(units[0], name="L0", activation='relu')(concat)
    for index in range(1, len(units)):
        x = Dense(units[index], name="L{}".format(index), activation='relu')(x)
    output = Dense(1, name="Out")(x)
    model = Model(inputs=inputs, outputs=output)

    return model


def update_target_weights(model, target_model, tau=0.005):
    weights = model.get_weights()
    target_weights = target_model.get_weights()
    for i in range(len(target_weights)):  # set tau% of target model to be new weights
        target_weights[i] = weights[i] * tau + target_weights[i] * (1 - tau)
    target_model.set_weights(target_weights)


# Taken from https://github.com/openai/baselines/blob/master/baselines/ddpg/noise.py
class OrnsteinUhlenbeckNoise:
    def __init__(self, mu, sigma=0.2, theta=.15, dt=1e-2, x0=None):
        self.theta = theta
        self.mu = mu
        self.sigma = sigma
        self.dt = dt
        self.x0 = x0
        self.reset()

    def __call__(self):
        x = self.x_prev + self.theta * (self.mu - self.x_prev) * self.dt + self.sigma * np.sqrt(self.dt) * np.random.normal(size=self.mu.shape)
        self.x_prev = x
        return x

    def reset(self):
        self.x_prev = self.x0 if self.x0 is not None else np.zeros_like(self.mu)


class NormalNoise:
    def __init__(self, mu, sigma=0.15):
        self.mu = mu
        self.sigma = sigma

    def __call__(self):
        return np.random.normal(scale=self.sigma, size=self.mu.shape)

    def reset(self):
        pass


class DDPG:
    def __init__(
            self,
            env,
            use_priority=False,
            lr_actor=1e-5,
            lr_critic=1e-3,
            actor_units=(512, 256),
            critic_units=(64, 32),
            noise='norm',
            sigma=0.15,
            tau=0.125,
            gamma=0.85,
            batch_size=64,
            memory_cap=10000,

    ):
        self.env = env
        self.state_shape = np.zeros(11).shape  # shape of observations
        self.action_dim = 3  # number of actions
        self.discrete = False
        self.action_bound = 0.5
        self.agent_num = 3
        self.one_action_dim = self.action_dim / self.agent_num
        self.tau = tau

        self.use_priority = use_priority
        self.memory = Memory(capacity=memory_cap) if use_priority else deque(maxlen=memory_cap)
        if noise == 'ou':
            self.noise = OrnsteinUhlenbeckNoise(mu=np.zeros(self.action_dim), sigma=sigma)
        else:
            self.noise = NormalNoise(mu=np.zeros(self.action_dim), sigma=sigma)

        # Define and initialize Actor network
        self.actor1 = actor(self.state_shape, self.one_action_dim, self.action_bound,  actor_units)
        self.actor_target1 = actor(self.state_shape, self.one_action_dim, self.action_bound,  actor_units)
        self.actor2 = actor(self.state_shape, self.one_action_dim, self.action_bound, actor_units)
        self.actor_target2 = actor(self.state_shape, self.one_action_dim, self.action_bound, actor_units)
        self.actor3 = actor(self.state_shape, self.one_action_dim, self.action_bound, actor_units)
        self.actor_target3 = actor(self.state_shape, self.one_action_dim, self.action_bound, actor_units)

        self.actor_optimizer = Adam(learning_rate=lr_actor)
        update_target_weights(self.actor1, self.actor_target1, tau=self.tau)
        update_target_weights(self.actor2, self.actor_target2, tau=self.tau)
        update_target_weights(self.actor3, self.actor_target3, tau=self.tau)

        # Define and initialize Critic network
        self.critic1 = critic(self.state_shape, self.action_dim, critic_units)
        self.critic_target1 = critic(self.state_shape, self.action_dim, critic_units)
        self.critic_optimizer = Adam(learning_rate=lr_critic)
        update_target_weights(self.critic1, self.critic_target1, tau=self.tau)

        self.critic2 = critic(self.state_shape, self.action_dim, critic_units)
        self.critic_target2 = critic(self.state_shape, self.action_dim, critic_units)
        update_target_weights(self.critic2, self.critic_target2, tau=self.tau)

        self.critic3 = critic(self.state_shape, self.action_dim, critic_units)
        self.critic_target3 = critic(self.state_shape, self.action_dim, critic_units)
        update_target_weights(self.critic3, self.critic_target3, tau=self.tau)

        # Set hyperparameters
        self.gamma = gamma  # discount factor
        self.tau = tau  # target model update
        self.batch_size = batch_size

        # Tensorboard
        self.summaries = {}

    def act(self, state, add_noise=True):
        state = np.expand_dims(state, axis=0).astype(np.float32)
        a = tf.concat([self.actor1.predict(state),
                     self.actor2.predict(state),
                     self.actor3.predict(state)], axis=1)
        # a += self.noise() * add_noise * self.action_bound
        a = tf.clip_by_value(a, 0, 1)

        # self.summaries['q_val'] = self.critic.predict([state, a])[0][0]

        return a

    def save_model(self, a_fn):
        self.actor1.save("pursuit2/model/ddpg_actor{}_episode{}.h5".format(1, a_fn))
        self.actor2.save("pursuit2/model/ddpg_actor{}_episode{}.h5".format(2, a_fn))
        self.actor3.save("pursuit2/model/ddpg_actor{}_episode{}.h5".format(3, a_fn))
        self.critic1.save("pursuit2/model/ddpg_critic{}_episode{}.h5".format(1, a_fn))
        self.critic2.save("pursuit2/model/ddpg_critic{}_episode{}.h5".format(2, a_fn))
        self.critic3.save("pursuit2/model/ddpg_critic{}_episode{}.h5".format(3, a_fn))

    def load_actor(self, a_fn):
        self.actor1.load_weights("pursuit2/model/ddpg_actor{}_episode{}.h5".format(1, a_fn))
        self.actor_target1.load_weights("pursuit2/model/ddpg_actor{}_episode{}.h5".format(1, a_fn))
        self.actor2.load_weights("pursuit2/model/ddpg_actor{}_episode{}.h5".format(2, a_fn))
        self.actor_target2.load_weights("pursuit2/model/ddpg_actor{}_episode{}.h5".format(2, a_fn))
        self.actor3.load_weights("pursuit2/model/ddpg_actor{}_episode{}.h5".format(3, a_fn))
        self.actor_target3.load_weights("pursuit2/model/ddpg_actor{}_episode{}.h5".format(3, a_fn))
        print(self.actor1.summary())
        print(self.actor2.summary())
        print(self.actor3.summary())

    def load_critic(self, a_fn):
        self.critic1.load_weights("pursuit2/model/ddpg_critic{}_episode{}.h5".format(1, a_fn))
        self.critic_target1.load_weights("pursuit2/model/ddpg_critic{}_episode{}.h5".format(1, a_fn))
        self.critic2.load_weights("pursuit2/model/ddpg_critic{}_episode{}.h5".format(2, a_fn))
        self.critic_target2.load_weights("pursuit2/model/ddpg_critic{}_episode{}.h5".format(2, a_fn))
        self.critic3.load_weights("pursuit2/model/ddpg_critic{}_episode{}.h5".format(3, a_fn))
        self.critic_target3.load_weights("pursuit2/model/ddpg_critic{}_episode{}.h5".format(3, a_fn))


    def remember(self, state, action, reward, next_state, done):
        if self.use_priority:
            action = np.squeeze(action)
            transition = np.hstack([state, action, reward, next_state, done])
            self.memory.store(transition)
        else:
            state = np.expand_dims(state, axis=0)
            next_state = np.expand_dims(next_state, axis=0)
            self.memory.append([state, action, reward, next_state, done])

    def replay(self):
        if len(self.memory) < self.batch_size:
            return

        if self.use_priority:
            tree_idx, samples, ISWeights = self.memory.sample(self.batch_size)
            split_shape = np.cumsum([self.state_shape[0], self.action_dim, 1, self.state_shape[0]])
            states, actions, rewards, next_states, dones = np.hsplit(samples, split_shape)

        else:
            ISWeights = 1.0
            samples = random.sample(self.memory, self.batch_size)
            s = np.array(samples).T
            states, actions, rewards, next_states, dones = [np.vstack(s[i, :]).astype(np.float) for i in range(5)]




        next_actions = tf.concat([self.actor_target1.predict(next_states),
                                  self.actor_target2.predict(next_states),
                                  self.actor_target3.predict(next_states)], axis=1)

        q_future1 = self.critic_target1.predict([next_states, next_actions])
        q_future2 = self.critic_target2.predict([next_states, next_actions])
        q_future3 = self.critic_target3.predict([next_states, next_actions])

        target_qs1 = tf.expand_dims(rewards[:, 0], axis=1) + q_future1 * self.gamma * (1. - dones)
        target_qs2 = tf.expand_dims(rewards[:, 1], axis=1) + q_future2 * self.gamma * (1. - dones)
        target_qs3 = tf.expand_dims(rewards[:, 2], axis=1) + q_future3 * self.gamma * (1. - dones)

        # train critic
        with tf.GradientTape() as tape:
            q_values = self.critic1([states, actions])
            td_error = q_values - target_qs1
            critic_loss = tf.reduce_mean(ISWeights * tf.math.square(td_error))
        critic_grad = tape.gradient(critic_loss, self.critic1.trainable_variables)  # compute critic gradient
        self.critic_optimizer.apply_gradients(zip(critic_grad, self.critic1.trainable_variables))

        with tf.GradientTape() as tape:
            q_values = self.critic2([states, actions])
            td_error = q_values - target_qs2
            critic_loss = tf.reduce_mean(ISWeights * tf.math.square(td_error))
        critic_grad = tape.gradient(critic_loss, self.critic2.trainable_variables)  # compute critic gradient
        self.critic_optimizer.apply_gradients(zip(critic_grad, self.critic2.trainable_variables))

        with tf.GradientTape() as tape:
            q_values = self.critic3([states, actions])
            td_error = q_values - target_qs3
            critic_loss = tf.reduce_mean(ISWeights * tf.math.square(td_error))
        critic_grad = tape.gradient(critic_loss, self.critic3.trainable_variables)  # compute critic gradient
        self.critic_optimizer.apply_gradients(zip(critic_grad, self.critic3.trainable_variables))


        # update priority
        if self.use_priority:
            abs_errors = tf.reduce_sum(tf.abs(td_error), axis=1)
            self.memory.batch_update(tree_idx, abs_errors)

        # train actor
        with tf.GradientTape() as tape:
            actions = tf.concat([self.actor1(states),
                                 self.actor2(states),
                                 self.actor3(states)], axis=1)
            actor_loss = -tf.reduce_mean(self.critic1([states, actions]))
        actor_grad1 = tape.gradient(actor_loss, self.actor1.trainable_variables)  # compute actor gradient
        self.actor_optimizer.apply_gradients(zip(actor_grad1, self.actor1.trainable_variables))

        with tf.GradientTape() as tape:
            actions = tf.concat([self.actor1(states),
                                 self.actor2(states),
                                 self.actor3(states)], axis=1)
            actor_loss = -tf.reduce_mean(self.critic2([states, actions]))
        actor_grad2 = tape.gradient(actor_loss, self.actor2.trainable_variables)  # compute actor gradient
        self.actor_optimizer.apply_gradients(zip(actor_grad2, self.actor2.trainable_variables))

        with tf.GradientTape() as tape:
            actions = tf.concat([self.actor1(states),
                                 self.actor2(states),
                                 self.actor3(states)], axis=1)
            actor_loss = -tf.reduce_mean(self.critic3([states, actions]))
        actor_grad3 = tape.gradient(actor_loss, self.actor3.trainable_variables)  # compute actor gradient
        self.actor_optimizer.apply_gradients(zip(actor_grad3, self.actor3.trainable_variables))

        # tensorboard info
        self.summaries['critic_loss'] = critic_loss
        self.summaries['actor_loss'] = actor_loss

    def train(self, max_episodes=EPISODE, max_epochs=8000, max_steps=500, save_freq=50):
        current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        train_log_dir = 'logs/DDPG_basic_' + current_time
        summary_writer = tf.summary.create_file_writer(train_log_dir)

        done, episode, steps, epoch, total_reward = False, 50001, 0, 0, 0
        cur_state, xy, xy_UAV = self.env.reset()
        running_reward = 0
        ren = False
        max_reward = 0
        while episode < max_episodes:
            if done:
                if episode % 5 == 0:
                    update_target_weights(self.actor1, self.actor_target1, tau=self.tau)  # iterates target model
                    update_target_weights(self.actor2, self.actor_target2, tau=self.tau)
                    update_target_weights(self.actor3, self.actor_target3, tau=self.tau)
                    update_target_weights(self.critic1, self.critic_target1, tau=self.tau)
                    update_target_weights(self.critic2, self.critic_target2, tau=self.tau)
                    update_target_weights(self.critic3, self.critic_target3, tau=self.tau)
                if total_reward > 500:
                    ren = True
                if running_reward == 0:
                    running_reward = total_reward
                else:
                    running_reward = running_reward * 0.99 + total_reward * 0.1
                plot_r.append(running_reward)
                plot_r2.append(total_reward)

                episode += 1
                write_str = "episode {}: {} total reward, {} steps, {} epochs \n".format(
                    episode, total_reward, steps, epoch)
                print(write_str)
                file.write(write_str)
                file.flush()

                with summary_writer.as_default():
                    tf.summary.scalar('Main/episode_reward', total_reward, step=episode)
                    tf.summary.scalar('Main/episode_steps', steps, step=episode)

                summary_writer.flush()
                self.noise.reset()

                if total_reward > 500 and total_reward > max_reward:
                    max_reward = total_reward
                    print("episode {}, save best model".format(episode))

                    self.save_model(episode)

                done = False
                cur_state, xy, xy_UAV = self.env.reset()
                steps = 0
                total_reward = 0
                if episode % save_freq == 0:
                    self.save_model(episode)

            a = tf.squeeze(self.act(cur_state))  # model determine action given state

            # print(a)
            next_state, reward, done, xy, xy_UAV = self.env.step_move(a)  # perform action on env

            # if ren:
            #     env.render()

            self.remember(cur_state, a, reward, next_state, done)  # add to memory
            self.replay()  # train models through memory replay



            cur_state = next_state
            total_reward += sum(reward)
            steps += 1
            epoch += 1

            # Tensorboard update
            with summary_writer.as_default():
                if len(self.memory) > self.batch_size:
                    tf.summary.scalar('Loss/actor_loss', self.summaries['actor_loss'], step=epoch)
                    tf.summary.scalar('Loss/critic_loss', self.summaries['critic_loss'], step=epoch)
                tf.summary.scalar('Main/step_reward', sum(reward), step=epoch)
                # tf.summary.scalar('Stats/q_val', self.summaries['q_val'], step=epoch)

            summary_writer.flush()

        self.save_model(episode)



if __name__ == "__main__":

    env = UAV()
    ddpg = DDPG(env)
    ddpg.load_critic(50000)
    ddpg.load_actor(50000)
    plot_r = []
    plot_r2 = []

    file = open(os.path.join('{}{}'.format('./', 'log.txt')), 'w+')

    ddpg.train(max_episodes=EPISODE)

    file.close()
    # rewards = ddpg.test()
    # print("Total rewards: ", rewards)

    plt.figure()
    plt.plot([i for i in range(EPISODE)], plot_r)
    plt.xlabel('episode')
    plt.ylabel('reward')
    plt.savefig('./img/reward.jpg')
    plt.close()

    plt.figure()
    plt.plot([i for i in range(EPISODE)], plot_r2)
    plt.xlabel('episode')
    plt.ylabel('reward')
    plt.savefig('./img/reward2.jpg')
    plt.close()