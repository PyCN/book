var vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        host,
        username: sessionStorage.username || localStorage.username,
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,
        tab_content: {
            detail: true,
            pack: false,
            comment: false,
            service: false
        },
        cart: [], // 购物车数据
        cat: cat, // 商品类别
        categories: [],
        cat1: {url: '', category:{name:'', id:''}},  // 一级类别
        cat2: {name:''},  // 二级类别
        cat3: {name:''},  // 三级类别,
        cart_total_count: 0, // 购物车总数量
        order_id: '',
        order: '',
        score: 5, //商品评分
        is_anonymous: true, //用户匿名
        comment:'', //用户评价
    },
    mounted: function(){
        this.get_categories();
        this.order_id = this.get_query_string('order_id');
        this.get_cart();
        this.get_order();
    },
    methods: {

        // 获取url路径参数
        get_query_string: function(name){
            var reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)', 'i');
            var r = window.location.search.substr(1).match(reg);
            if (r != null) {
                return decodeURI(r[2]);
            }
            return null;
        },
        get_order:function(){
            axios.get(this.host+'/orders/'+ this.order_id + '/', {
                    responseType: 'json',
                    headers: {
                        'Authorization': 'JWT ' + this.token
                    },
            })
            .then(response => {
                this.order = response.data;
            })
            .catch(error => {
                console.log(error.response.data);
            })
        },
        cat3_url: function (cat_id) {
          return '/list.html?cat=' + cat_id;
        },
        get_categories:function(){
            axios.get(this.host+'/categories/', {
                    responseType: 'json'
            })
            .then(response => {
                this.categories = response.data;
            })
            .catch(error => {
                console.log(error.response.data);
            })
        },

        // 退出
        logout: function(){
            sessionStorage.clear();
            localStorage.clear();
            location.href = '/login.html';
        },

        // 添加购物车
        add_comment: function(goods_id, sku_id){
            axios.put(this.host+'/comment/', {
                    id: parseInt(goods_id),
                    sku_id: parseInt(sku_id),
                    order_id: this.order_id,
                    score: this.score,
                    is_anonymous: this.is_anonymous,
                    comment: this.comment,
                }, {
                    headers: {
                        'Authorization': 'JWT ' + this.token
                    },
                    responseType: 'json',
                    withCredentials: true
                })
                .then(response => {
                    alert(response.data.message);
                    this.cart_total_count += response.data.count;
                    this.get_cart();
                })
                .catch(error => {
                    if (error.response.status == 400){
                        alert(error.response.data.message);
                    }
                    console.log(error.response.data);
                })
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

    }
});