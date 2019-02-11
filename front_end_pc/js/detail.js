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
        page: 1, // 当前页数
        page_size: 5, // 每页数量
        count: 0,  // 总数量
        sku_id: '',
        sku_count: 1,
        sku_price: price,
        cart_total_count: 0, // 购物车总数量
        cart: [], // 购物车数据
        hots: [], // 热销商品
        cat: cat, // 商品类别
        comments: [], // 评论信息
        score_classes: {
            1: 'stars_one',
            2: 'stars_two',
            3: 'stars_three',
            4: 'stars_four',
            5: 'stars_five',
        },
        keywords:[],
    },
    computed: {
        sku_amount: function(){
            return (this.sku_price * this.sku_count).toFixed(2);
        },
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
    created: function(){
        // 添加用户浏览历史记录
        this.get_sku_id();
        //用户登录后,访问商品商品详情,添加浏览记录
        if (this.user_id) {
            axios.post(this.host+'/browse_histories/', {
                sku_id: this.sku_id
            }, {
                headers: {
                    'Authorization': 'JWT ' + this.token
                }
            })
        }
        this.get_cart();
        this.get_hot_goods();
        this.get_comments();
        this.get_keyword();
    },
    methods: {
        get_keyword_url:function (name) {
          return "/search.html?q="+name;
        },
        // 请求查询结果
        get_keyword: function () {
            axios.get(this.host+'/keyword/', {
                responseType:'json'
            })
            .then(response => {
                this.keywords = response.data;
            })
            .catch(error => {
                console.log(error.response.data)
            });
        },
        user_anonymous:function (name, is_anonymous) {
            if (is_anonymous){
                name = name.substring(0,1) + '***' + name.substring(name.length-1) + '(匿名)';
                return name;
            }else {
                return name;
            }
        },
        // 退出
        logout: function(){
            sessionStorage.clear();
            localStorage.clear();
            location.href = '/login.html';
        },
        // 控制页面标签页展示
        on_tab_content: function(name){
            this.tab_content = {
                detail: false,
                pack: false,
                comment: false,
                service: false
            };
            this.tab_content[name] = true;
        },
        // 从路径中提取sku_id
        get_sku_id: function(){
            var re = /^\/goods\/(\d+).html$/;
            this.sku_id = document.location.pathname.match(re)[1];
        },
        // 减小数值
        on_minus: function(){
            if (this.sku_count > 1) {
                this.sku_count--;
            }
        },
        // 添加购物车
        add_cart: function(){
            axios.post(this.host+'/cart/', {
                    sku_id: parseInt(this.sku_id),
                    count: this.sku_count
                }, {
                    headers: {
                        'Authorization': 'JWT ' + this.token
                    },
                    responseType: 'json',
                    withCredentials: true
                })
                .then(response => {
                    alert('添加购物车成功');
                    this.cart_total_count += response.data.count;
                    this.get_cart();
                })
                .catch(error => {
                    if ('non_field_errors' in error.response.data) {
                        alert(error.response.data.non_field_errors[0]);
                    } else {
                        alert('添加购物车失败');
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
        // 获取热销商品数据
        get_hot_goods: function(){
            axios.get(this.host+'/categories/'+this.cat+'/hotskus/', {
                    responseType: 'json'
                })
                .then(response => {
                    this.hots = response.data;
                    for(var i=0; i<this.hots.length; i++){
                        this.hots[i].url = '/goods/' + this.hots[i].id + '.html';
                    }
                })
                .catch(error => {
                    console.log(error.response.data);
                })
        },
        // 点击页数
        on_page: function(num){
            if (num != this.page){
                this.page = num;
                this.get_comments();
            }
        },
        // 获取商品评价信息
        get_comments: function(){
            axios.get(this.host+'/comments/' + this.sku_id + '/', {
                    params: {
                        page: this.page,
                        page_size: this.page_size,
                    },
                    responseType: 'json',
                })
                .then(response => {
                    this.count = response.data.count;
                    this.comments = response.data.results;
                })
                .catch(error => {
                    console.log(error.response.data);
                })
        },

    }
});