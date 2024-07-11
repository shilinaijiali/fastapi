from typing import Optional

from fastapi import APIRouter, Cookie, Header, HTTPException

app3 = APIRouter()


@app3.get('/cookie')
async def cookie(cookie_id: Optional[str] = Cookie(None)):
    return {'cookie_id': cookie_id}


@app3.get('/header')
# convert_underscores 是否转换下划线 (user_agent --> user-agent)
async def header(user_agent: Optional[str] = Header(None, convert_underscores=True),
                 x_token: Optional[str] = Header(None)):
    """
       有些HTTP代理和服务器是不允许在请求头中带有下划线的，所以Header提供convert_underscores属性让设置
       :param user_agent: convert_underscores=True 会把 user_agent 变成 user-agent
       :param x_token: x_token是包含多个值的列表
       :return:
    """
    return {"user_agent": user_agent, "x_token": x_token}


@app3.get('/http_exception')
async def http_exception(city: str):
    if city != 'chengdu':
        raise HTTPException(
            # 状态码
            status_code=404,
            # 错误的详细信息
            detail='City not found',
            # 响应的响应头
            headers={'X-Error': 'Error'}
        )
    return {'city': city}


@app3.get('/http_exception/{city_id}')
async def http_exception(city_id: int):
    if city_id != 1:
        raise HTTPException(
            status_code=418,
            detail="Nope! I don't like this city!"
        )
    return {'city_id': city_id}
