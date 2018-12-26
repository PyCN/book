from django_redis import get_redis_connection
from carts.views import get_cart_dict, get_cart_str


def merge_cart_cookie_to_redis(request, user, response):
    """合并COOKIE购物车中的商品到redis中"""

    cookie_cart_str = request.COOKIES.get('cart', None)
    # 判断cookie中是否有购物车记录
    if not cookie_cart_str:
        return response
    # 获取cookie购物车字典
    cookie_cart_dict = get_cart_dict(cookie_cart_str)

    # 获取购物车redis连接
    redis_conn = get_redis_connection('cart')
    redis_cart_bytes = redis_conn.get('cart_%s' % user.id)
    # 获取redis购物车字典
    redis_cart = {}
    if redis_cart_bytes:
        redis_cart_str = redis_cart_bytes.decode()
        redis_cart = get_cart_dict(redis_cart_str)

    # 遍历cookie购物车字典,将cookie中的数据合并到redis中,并以cookie中为准
    for sku_id, sku_state in cookie_cart_dict.items():
        redis_cart[sku_id] = sku_state
    # redis字典转换为字符串
    cart_str = get_cart_str(redis_cart)
    redis_conn.set('cart_%s' % user.id, cart_str)
    # 清空cookie中的购物车
    response.delete_cookie('cart')
    return response
