var vm = new Vue({
    el: '#app',
    data: {
        host,
        user_id: sessionStorage.user_id || localStorage.user_id,
        username: sessionStorage.username || localStorage.username,
        token: sessionStorage.token || localStorage.token,
        password: '',
        new_password: '',
        new_password2: '',
        error_password: false,
        error_new_password: false,
        error_check_new_password: false,
        sms_code_tip: '获取短信验证码',
    },
    mounted: function () {
        // alert(this.token);
    },
    methods: {
        // 退出
        logout: function(){
            sessionStorage.clear();
            localStorage.clear();
            location.href = '/login.html';
        },
        check_pwd: function () {
            var len = this.password.length;
            if (len < 8 || len > 20) {
                this.error_password = true;
            } else {
                this.error_password = false;
            }
        },
        check_new_pwd: function () {
            var len = this.new_password.length;
            if (len < 8 || len > 20) {
                this.error_new_password = true;
            } else {
                this.error_new_password = false;
            }
        },
        check_new_cpwd: function () {
            if (this.new_password != this.new_password2) {
                this.error_check_new_password = true;
            } else {
                this.error_check_new_password = false;
            }
        },
        onSubmit: function () {
            if (this.user_id && this.token) {
                axios.put(this.host + '/user/password/',
                    {
                        password: this.password,
                        new_password: this.new_password,
                        new_password2: this.new_password2,
                    },
                    // 向后端传递JWT token的方法
                    {
                        headers: {
                        'Authorization': 'JWT ' + this.token
                    },
                    responseType: 'json',
                })
                    .then(response => {
                        user_id = response.data.id;
                        if (user_id) {
                            alert('密码修改成功');
                        }
                    })
                    .catch(error=> {
                        if (error.response.status == 400) {
                            if ('non_field_errors' in error.response.data) {
                                alert(error.response.data.non_field_errors[0]);
                            }
                        } else {
                            console.log(error.response.data);
                        }
                    })
            }
        },


    }
});