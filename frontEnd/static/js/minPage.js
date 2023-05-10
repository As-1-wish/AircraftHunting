let friendly_coor = [], enemy_coor = [];
let preCoors = []; // 记录当前已生成的坐标，防止生成坐标时重叠

// 获取显示框
let showPanel = document.querySelector('#showPanel');
// 获取模态框
let modalElement = document.querySelector('#initModal');
let modalRes = document.querySelector('#result-modal');
let modalSav = document.querySelector('#save-modal');
// 添加监听事件
modalElement.querySelector('#createAirs').addEventListener("click", addAircrafts);
document.querySelector('#startBtn').addEventListener("click", demostrating);

// 添加飞行器函数,
function addAircrafts() {
    let friendly_aircraft_num = modalElement.querySelector('#friendly-aircraft').value;
    let enemy_aircraft_num = modalElement.querySelector('#enemy-aircraft').value;

    // 设置匹配规则，只有符合以下数据的才是合法数据
    let regex_rule = /^\+?[1-9][0-9]*$/;

    if (regex_rule.test(friendly_aircraft_num) && regex_rule.test(enemy_aircraft_num)) {
        let friendly_info_table = document.querySelector('#friendly-table');
        let enemy_info_table = document.querySelector('#enemy-table')
        // 每次生成则清空表
        friendly_info_table.innerHTML = "<tr><th>序号</th><th>当前位置</th><th>当前速度</th></tr>";
        enemy_info_table.innerHTML = "<tr><th>序号</th><th>当前位置</th><th>当前速度</th></tr>";
        clearAircrafts();   // 清空界面
        // 生成友方飞行器
        $.ajax({
            url: '../init/', dataType: 'json', type: 'POST', data: {
                'enemyNum': enemy_aircraft_num, 'friendNum': friendly_aircraft_num
            }, success: function (res) {
                if (res.code === 0) {
                    enemy_coor = res.enemy;
                    friendly_coor = res.friend;
                    console.log(enemy_coor);
                    console.log(friendly_coor);
                    let cnt = 0;
                    for (let item in enemy_coor) {
                        // 更新配置栏表格
                        updateInfoTable(tran_coordinate(enemy_coor[item], 1), init_speed, enemy_info_table);
                        // 绘制图形
                        create_aircraft_css('enemy', cnt++, tran_coordinate(enemy_coor[item], 1));
                    }
                    cnt = 0;
                    for (let item in friendly_coor) {
                        // 更新配置栏表格
                        updateInfoTable(tran_coordinate(friendly_coor[item], 1), init_speed, friendly_info_table);
                        // 绘制图形
                        create_aircraft_css('friendly', cnt++, tran_coordinate(friendly_coor[item], 1));
                    }
                }
            }, error: function (xhr, status, error) {
                console.error('AJAX Error:', status, error);
            }
        })
    } else {
        alert("输入为空或数据不合法！");
    }
}

/**
 * @description 更新对应信息表
 * @param coordinate
 * @param speed
 * @param target_table true-我方飞行器  false-敌方飞行器
 */
function updateInfoTable(coordinate, speed, target_table) {
    target_table.innerHTML += "<tr>" +
        "<td>" + target_table.rows.length + "</td>" +
        "<td>" + "(" + coordinate[0].toFixed(1) + "," + coordinate[1].toFixed(1) + ")" + "</td>" +
        "<td>" + speed + "</td>" + "</tr>";
}

/**
 * @description 针对每个随机生成的坐标，生成各自的样式并在页面显示
 * @param type
 * @param index
 * @param coordinate
 */
function create_aircraft_css(type, index, coordinate) {
    // 设置plane的属性
    let new_style = document.createElement('style');
    new_style.innerHTML = "." + (type === "friendly" ? friendly_plane_prefix : enemy_plane_prefix) +
        index + " {\n" +
        "  position: absolute;\n" +
        "  width: " + aircraft_size + "px; \n" +
        "  height: " + aircraft_size + "px; \n" +
        "  top: 0;\n" + "  left: 0;\n" +
        "  background-image: url(\"../static/image/" + type + "-aircraft.png\"); /* 飞机图片地址 */\n" +
        "  background-size: contain;\n" +
        "  transform-origin: 50% 50%;\n" +
        "}"
    document.head.appendChild(new_style);

    // 设置 plane容器的属性
    let new_container_style = document.createElement('style');
    new_container_style.innerHTML = "." + (type === "friendly" ?
            friendly_container_prefix : enemy_container_prefix) + index + " {\n" +
        "  position: absolute;\n" +
        "  width: " + aircraft_size + "px; \n" +
        "  height: " + aircraft_size + "px; \n" +
        "  top: " + coordinate[1].toFixed(1) + "px; /* 距离顶部的距离 */\n" +
        "  left: " + coordinate[0].toFixed(1) + "px; /* 距离左侧的距离 */\n" + "}"
    document.head.appendChild(new_container_style);

    let new_plane = document.createElement("div");
    let new_container = document.createElement('div');

    new_plane.classList.add((type === "friendly" ? friendly_plane_prefix : enemy_plane_prefix) + index);
    new_container.classList.add((type === "friendly" ? friendly_container_prefix : enemy_container_prefix) + index);
    new_container.appendChild(new_plane);

    showPanel.appendChild(new_container);
}

/**
 * @description 每次生成都清空显示界面
 */
function clearAircrafts() {
    preCoors = []
    friendly_coor = []
    enemy_coor = []
    let childDivs = showPanel.querySelectorAll('div');
    for (let i = 0; i < childDivs.length; ++i)
        childDivs[i].remove()
}

/**
 * @description 演示开始函数，接受坐标数据，并进行渲染
 */
function demostrating() {
    let enemyPush = enemy_coor;
    for (let i = 0; i < enemyPush.length; ++i)
        enemyPush[i] = tran_coordinate(enemyPush[i], 2);
    let friendPush = friendly_coor;
    for (let i = 0; i < friendPush.length; ++i)
        friendPush[i] = tran_coordinate(friendPush[i], 2);
    $.ajax({
        url: '../pursuit/evaluate/',
        type: 'POST',
        dataType: 'json',
        data: {
            'enemy': JSON.stringify(enemyPush),
            'friend': JSON.stringify(friendPush)
        },
        success: function (data) {
            // 从返回的数据中获取坐标列表
            friendly_coor = data.friend;
            enemy_coor = data.enemy;
            let tag = data.result;
            move(tag);
        },
        error: function (xhr, status, error) {
            console.error('AJAX Error:', status, error);
        }
    });

}


/**
 * @description 负责训练模型坐标与显示区域坐标间的转化
 * @param coordinates
 * @param tag 1-训练转显示 2-显示转训练
 */
function tran_coordinate(coordinates, tag) {
    if (tag === 1) {
        coordinates[0] = (coordinates[0] * rank_x);
        coordinates[1] = (coordinates[1] * rank_y);
    }
    if (tag === 2) {
        coordinates[0] = (coordinates[0] / rank_x);
        coordinates[1] = (coordinates[1] / rank_y);
    }
    return coordinates;
}

/**
 * @description 依据坐标列表进行移动
 */
function move(tag) {
    let ind = 0;
    let moveTimer = setInterval(function () {
        for (let j = 0; j < friendly_coor[ind].length; ++j) {
            let con = document.querySelector("." + friendly_container_prefix + j);
            let pre = tran_coordinate(friendly_coor[ind][j], 1);
            con.style.left = pre[1] + 'px';
            con.style.top = pre[0] + 'px';
        }
        for (let j = 0; j < enemy_coor[ind].length; ++j) {
            let con = document.querySelector("." + enemy_container_prefix + j);
            let pre = tran_coordinate(enemy_coor[ind][j], 1);
            con.style.left = pre[1] + 'px';
            con.style.top = pre[0] + 'px';
        }

        ind = (ind + 1) % friendly_coor.length;
        if (ind + 1 === friendly_coor.length) {
            clearInterval(moveTimer);
            confirm(msg[tag])
            $('#result-modal').modal('show');
        }
    }, 200);
}
