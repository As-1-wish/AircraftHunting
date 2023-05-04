// 登录按钮绑定事件
document.querySelector('#loginBtn').addEventListener('click', login);


/**
 * @description 用户登录
 */
function login() {
    let username = document.querySelector('#username').value;
    let password = document.querySelector('#password').value;
    $.ajax({
        url: '/login/',
        dataType: 'json',
        data: {
            'username': username,
            'password': password
        },
        success: function (res) {
            if (res.code === 0)
                location.href = '/main/'
            else {
                location.reload()
                alert(res.msg)
            }
        },
        error: function (xhr, status, error) {
            console.error('AJAX Error:', status, error);
        }
    });
}