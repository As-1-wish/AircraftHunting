let friendly_coor, enemy_coor;

// 获取显示框
let showPanel = document.querySelector('#showPanel');
// 获取模态框
let modalElement = document.querySelector('#initModal');
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
        let new_coordinate_x;
        let new_coordinate_y;
        let friendly_info_table = document.querySelector('#friendly-table');
        let enemy_info_table = document.querySelector('#enemy-table')
        // 每次生成则清空表
        friendly_info_table.innerHTML = "<tr><th>序号</th><th>当前位置</th><th>当前速度</th></tr>";
        enemy_info_table.innerHTML = "<tr><th>序号</th><th>当前位置</th><th>当前速度</th></tr>";
        clearAircrafts();   // 清空界面
        let frilist = [[100., 100.], [350., 600.], [600., 100.]];
        // 生成友方飞行器
        for (let i = 0; i < friendly_aircraft_num; ++i) {
            let per = tran_coordinate(frilist[i], 1);
            // 生成随机坐标
            new_coordinate_x = getRandomNumber(0, showPanel_height);
            new_coordinate_y = getRandomNumber(0, showPanel_width);
            // // 添加至配置栏表格中
            // updateInfoTable(new_coordinate_x, new_coordinate_y, init_speed, friendly_info_table);
            // // 在页面中初始化图形
            // create_aircraft_css("friendly", i, new_coordinate_x, new_coordinate_y);
            // 添加至配置栏表格中
            updateInfoTable(per[0], per[1], init_speed, friendly_info_table);
            // 在页面中初始化图形
            create_aircraft_css("friendly", i, per[0], per[1]);
        }
        let enlist = [[350., 400.]];
        // 生成敌方飞行器
        for (let i = 0; i < enemy_aircraft_num; ++i) {
            let per = tran_coordinate(enlist[i], 1);
            new_coordinate_x = getRandomNumber(0, showPanel_height);
            new_coordinate_y = getRandomNumber(0, showPanel_width);
            // // 添加至配置栏表格中
            // updateInfoTable(new_coordinate_x, new_coordinate_y, init_speed, enemy_info_table);
            // // 在页面中初始化图形
            // create_aircraft_css("enemy", i, new_coordinate_x, new_coordinate_y);
            // 添加至配置栏表格中
            updateInfoTable(per[0], per[1], init_speed, enemy_info_table);
            // 在页面中初始化图形
            create_aircraft_css("enemy", i, per[0], per[1]);
        }
    } else {
        alert("输入为空或数据不合法！");
    }
}

/**
 * @description 更新对应信息表
 * @param coordinateX
 * @param coordinateY
 * @param speed
 * @param target_table true-我方飞行器  false-敌方飞行器
 */
function updateInfoTable(coordinateX, coordinateY, speed, target_table) {
    target_table.innerHTML += "<tr>" +
        "<td>" + target_table.rows.length + "</td>" +
        "<td>" + "(" + coordinateX.toFixed(3) + "," + coordinateY.toFixed(3) + ")" + "</td>" +
        "<td>" + speed + "</td>" +
        "</tr>";
}

/**
 * @description 生成范围内的随机数（三位小数）
 */
function getRandomNumber(minNumber, maxNumber) {
    return Math.random() * (maxNumber - minNumber);
}

/**
 * @description 针对每个随机生成的坐标，生成各自的样式并在页面显示
 * @param type
 * @param index
 * @param coordinateX
 * @param coordinateY
 */
function create_aircraft_css(type, index, coordinateX, coordinateY) {
    // 设置plane的属性
    let new_style = document.createElement('style');
    new_style.innerHTML = "." +
        (type === "friendly" ? friendly_plane_prefix : enemy_plane_prefix) + index
        + " {\n" +
        "  position: absolute;\n" +
        "  width: 50px; \n" +
        "  height: 50px; \n" +
        "  top: 0;\n" +
        "  left: 0;\n" +
        "  background-image: url(\"../static/image/" + type + "-aircraft.png\"); /* 飞机图片地址 */\n" +
        "  background-size: contain;\n" +
        "  transform-origin: 50% 50%;\n" +
        // "  animation: " + (type === "friendly" ? friendly_keyframes_prefix : enemy_keyframes_prefix)
        // + index + " 10s linear infinite; /* 控制飞机速度，10s为飞行时间 */\n" +
        "}"
    document.head.appendChild(new_style);

    // 设置 plane容器的属性
    let new_container_style = document.createElement('style');
    new_container_style.innerHTML = "." +
        (type === "friendly" ? friendly_container_prefix : enemy_container_prefix) + index + " {\n" +
        "  position: absolute;\n" +
        "  width: 50px; /* 距离顶部的距离 */\n" +
        "  height: 50px; /* 距离顶部的距离 */\n" +
        "  top: " + coordinateX + "px; /* 距离顶部的距离 */\n" +
        "  left: " + coordinateY + "px; /* 距离左侧的距离 */\n" +
        "}"
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
    let childDivs = showPanel.querySelectorAll('div');
    for (let i = 0; i < childDivs.length; ++i)
        childDivs[i].remove()
}

/**
 * @description 演示开始函数，接受坐标数据，并进行渲染
 */
function demostrating() {
    $.ajax({
        url: '/getCoorList/',
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            // 从返回的数据中获取坐标列表
            friendly_coor = data.friendly_list;
            enemy_coor = data.enemy_list;

            move();

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
        coordinates[0] = coordinates[0] * rank_height;
        coordinates[1] = coordinates[1] * rank_width;
    }
    if (tag === 2) {
        coordinates[0] = coordinates[0] / rank_height;
        coordinates[1] = coordinates[1] / rank_width;
    }
    return coordinates;
}

/**
 * @description 依据坐标列表进行移动
 */
function move() {
    let ind = 0;
    setInterval(function () {
        for (let j = 0; j < friendly_coor[ind].length; ++j) {

            let con = document.querySelector("." + friendly_container_prefix + j);
            con.style.left = friendly_coor[ind][j][1]+ 'px';
            con.style.top = friendly_coor[ind][j][0]+ 'px';
        }
        let con = document.querySelector("." + enemy_container_prefix + 0);
        con.style.left = enemy_coor[ind][1] + 'px';
        con.style.top = enemy_coor[ind][0]+ 'px';

        ind = (ind + 1) % friendly_coor.length;
    }, 200);
}