var vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'], // 修改vue模板符号，防止与django冲突
    data: {
        host: host,
        username: sessionStorage.username || localStorage.username,
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,
        page: 1, // 当前页数
        page_size: 5, // 每页数量
        count: 0,  // 总数量
        orders: [], // 数据
        pay_methods: ['货到付款', '支付宝'],
        pay_statuses: ['待支付', '待发货', '待收货', '待评价', '交易完成', '交易取消'],
        // pay: ['去支付', '确认发货', '确认收货', '去评价'],
        ordering: '0',
    },
    computed: {
        total_page: function(){  // 总页数
            return Math.ceil(this.count/this.page_size);
        },
        next: function(){  // 下一页
            if (this.page >= this.total_page) {
                return 0;
            } else {
                return this.page + 1;
            }
        },
        previous: function(){  // 上一页
            if (this.page <= 0 ) {
                return 0;
            } else {
                return this.page - 1;
            }
        },
        page_nums: function(){  // 页码
            // 分页页数显示计算
            // 1.如果总页数<=5
            // 2.如果当前页是前3页
            // 3.如果当前页是后3页,
            // 4.既不是前3页，也不是后3页
            var nums = [];
            if (this.total_page <= 5) {
                for (var i=1; i<=this.total_page; i++){
                    nums.push(i);
                }
            } else if (this.page <= 3) {
                nums = [1, 2, 3, 4, 5];
            } else if (this.total_page - this.page <= 2) {
                for (var i=this.total_page; i>this.total_page-5; i--) {
                    nums.push(i);
                }
            } else {
                for (var i=this.page-2; i<this.page+3; i++){
                    nums.push(i);
                }
            }
            return nums;
        }
    },
    mounted: function(){
        this.get_orders_result('0');
        // 判断用户的登录状态
        if (this.user_id && this.token) {
            axios.get(this.host + '/user/', {
                // 向后端传递JWT token的方法
                headers: {
                    'Authorization': 'JWT ' + this.token
                },
                responseType: 'json',
            })
            .then(response => {
                // 加载用户数据
                this.user_id = response.data.id;
                this.username = response.data.username;
                this.mobile = response.data.mobile;
                this.email = response.data.email;
                this.email_active = response.data.email_active;

            })
            .catch(error => {
                if (error.response.status == 401 || error.response.status == 403) {
                    location.href = '/login.html?next=/user_center_order.html';
                }
            });
        } else {
            location.href = '/login.html?next=/user_center_order.html';
        }
    },
    methods: {
        // 点击排序
        on_sort: function(ordering){
            if (ordering != this.ordering) {
                this.page = 1;
                this.ordering = ordering;
                this.get_orders_result(this.ordering);
            }
        },
        logout(){
            sessionStorage.clear();
            localStorage.clear();
            location.href = '/login.html';
        },
        order_image_url:function (sku_id) {
            return '/goods/'+sku_id+'.html';
        },
        // 请求查询结果
        get_orders_result: function(status){
            axios.get(this.host+'/orders/list/', {
                    params: {
                        status: status,
                        page: this.page,
                        page_size: this.page_size,
                    },
                    responseType: 'json',
                    headers: {
                        'Authorization': 'JWT ' + this.token
                    },
                })
                .then(response => {
                    this.count = response.data.count;
                    this.orders = response.data.results;
                })
                .catch(error => {
                    console.log(error.response.data);
                })
        },
        // 点击页数
        on_page: function(num){
            if (num != this.page){
                this.page = num;
                this.get_orders_result(this.ordering);
            }
        },
        // 获取购物车数据
        get_cart: function(){
            axios.get(this.host+'/cart/', {
                    headers: {
                        'Authorization': 'JWT ' + this.token
                    },
                    responseType: 'json',
                    withCredentials: true
                })
                .then(response => {
                    this.cart = response.data;
                    this.cart_total_count = 0;
                    for(var i=0;i<this.cart.length;i++){
                        if (this.cart[i].name.length>25){
                            this.cart[i].name = this.cart[i].name.substring(0, 25) + '...';
                        }
                        this.cart_total_count += this.cart[i].count;

                    }
                })
                .catch(error => {
                    console.log(error.response.data);
                })
        },
        delete_order:function (index) {

            // 请求查询结果
            axios.delete(this.host+'/orders/'+ this.orders[index]['order_id'] + '/',
                {
                    responseType: 'json',
                    headers: {
                        'Authorization': 'JWT ' + this.token
                    },
                })
                .then(response => {
                    this.orders.splice(index, 1);
                })
                .catch(error => {
                    if (error.response.status == 400){
                        alert(error.response.data.message);
                    }
                    console.log(error.response.data);
                })
        },
        delete_status:function (status) {
            var sTr = '';
            if (status == 1 ){
                sTr = '取消订单'
            }else if(status == 4 || status == 5){
                sTr = '删除订单'
            }
            return sTr;
        },
        operate_status:function (status) {
            var sTr = '';
            if (status == 1){
                sTr = '去支付';
            }else if(status == 2 || status == 3){
                sTr = '确认收货';
            }else if(status == 4){
                sTr = '去评价';
            }else if(status == 5){
                sTr = '交易完成';
            }
            return sTr;

        },

         // 去支付
        next_operate: function(order_id) {

            // 发起支付
            axios.get(this.host + '/orders/' + order_id + '/payment/', {
                headers: {
                    'Authorization': 'JWT ' + this.token
                },
                responseType: 'json'
            })
                .then(response => {
                    // 跳转到支付宝支付
                    location.href = response.data.alipay_url;
                })
                .catch(error => {
                    console.log(error.response.data);
                    if (error.response.status == 400) {
                        alert(error.response.data.message);
                    }
                })
        },
        // 确认收货
        confirm_receipt: function(order_id) {

            axios.put(this.host + '/confirm/' + order_id + '/', {},{
                headers: {
                    'Authorization': 'JWT ' + this.token
                },
                responseType: 'json'
            })
                .then(response => {
                    alert(response.data.message);
                    location.reload();
                })
                .catch(error => {
                    console.log(error.response.data);
                    if (error.response.status == 400) {
                        alert(error.response.data.message);
                    }
                })
        },
        //判断当前订单是支付,确认收货,还是评价
        operate_order:function (order_id, status) {
            if (status == 1){
                this.next_operate(order_id);
            }else if(status == 2 || status == 3){
                this.confirm_receipt(order_id);
            }else if(status == 4){
                location.href = '/comment.html?order_id='+order_id;
            }
        },

    }
});