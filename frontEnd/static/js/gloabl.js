const showPanel_x = 646;   // 屏幕尺寸
const showPanel_y = 1152;
const maxCoordinate = 600;  // 生成飞机区域
const minCoordinate = 400;
const train_x = 700;   // 训练尺寸
const train_y = 700;
const aircraft_size = 30; // 飞行器的显示尺寸
const init_speed = 20;
const rank_x = (showPanel_x / train_x);   // 转换比例
const rank_y = (showPanel_y / train_y);

const friendly_plane_prefix = "friendly-plane-";
const enemy_plane_prefix = "enemy-plane-";
const friendly_container_prefix = "friendly-container-";
const enemy_container_prefix = "enemy-container-";