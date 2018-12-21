$(function () {
    //检测用户是否登录
    check_login();
    //点击退出登录
    $('.quit').click(function () {
        logout();
    });
});
function check_login() {
    // 记住登录检测

    flag = fIsLogin(localStorage);
    if (!flag){
        // 未记住登录检测
        fIsLogin(sessionStorage);
    }

}

function logout(){
    sessionStorage.clear();
    localStorage.clear();
    $('.login_info').css('display', 'none');
    $('.login_btn').css('display', 'block');

    window.location.href = '/login.html';
}

//判断用户是否登录
function fIsLogin(storage) {
    if (storage.token != null){
        $('.login_info').css('display', 'block').children('em').html(storage.username);
        $('.login_btn').css('display', 'none');
        return true;
    }else{
        $('.login_info').css('display', 'none');
        $('.login_btn').css('display', 'block');
        // next_param = get_query_prams(window.location.href);
        // if (next_param != '/' && next_param != '' && next_param != '/index.html' && next_param != '/login.html'){
        //     window.location.href = '/login.html?next='+ next_param;
        // }
    }
}
function get_query_prams(name) {
    var r = name.substring(name.lastIndexOf('/')+1, name.length);
    return r;
}