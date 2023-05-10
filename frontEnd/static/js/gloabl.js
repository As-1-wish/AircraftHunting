const showPanel_x = 621;   // 屏幕尺寸
const showPanel_y = 768;
const train_x = 1000;   // 训练尺寸
const train_y = 1000;
const aircraft_size = 30; // 飞行器的显示尺寸
const init_speed = 20;
const rank_x = (showPanel_x / train_x);   // 转换比例
const rank_y = (showPanel_y / train_y);

const friendly_plane_prefix = "friendly-plane-";
const enemy_plane_prefix = "enemy-plane-";
const friendly_container_prefix = "friendly-container-";
const enemy_container_prefix = "enemy-container-";

const msg = {
        '1': "超出捕获距离",
        '-1':"捕获失败",
        '0':"成功捕获"
}