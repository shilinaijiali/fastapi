from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException

app6 = APIRouter()

"""Classes as Dependencies 类作为依赖项"""

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


class CommonQueryParams:
    def __init__(self, q: Optional[str] = None, page: int = 1, limit: int = 100):
        self.q = q
        self.page = page
        self.limit = limit


@app6.get('/classes_as_dependencies')
# 写法一
# async def classes_as_dependencies(commons: CommonQueryParams = Depends(CommonQueryParams)):
# 写法二
async def classes_as_dependencies(commons: CommonQueryParams = Depends()):
    response = {}
    if commons.q:
        response['q'] = commons.q
    # 切片
    items = fake_items_db[commons.page: commons.page + commons.limit]
    response['items'] = items
    return response


# 创建公共函数
async def common_parameters(q: Optional[str] = None, page: int = 1, limit: int = 100):
    return {"q": q, "page": page, "limit": limit}


# 定义视图
@app6.get("/dependency1")
async def dependency1(commons: dict = Depends(common_parameters)):
    return commons


# 可以在 async def 中调用 def 依赖，也可以在 def 中导入 async def 依赖
@app6.get("/dependency2")
def dependency2(commons: dict = Depends(common_parameters)):
    return commons


"""Sub-dependencies 子依赖"""


def query(q: Optional[str] = None):
    return q


def sub_query(q: str = Depends(query), last_query: Optional[str] = None):
    if not q:
        return last_query
    return q


@app6.get("/sub_dependency")
async def sub_dependency(final_query: str = Depends(sub_query, use_cache=True)):
    """use_cache默认是True, 表示当多个依赖有一个共同的子依赖时,每次request请求只会调用子依赖一次, 多次调用将从缓存中获取"""
    return {"sub_dependency": final_query}


# 执行顺序 sub_dependency --> sub_query --> query -- > sub_query


"""Dependencies in path operation decorators 路径操作装饰器中的多依赖"""


async def verify_token(x_token: str = Header(...)):
    """没有返回值的子依赖"""
    if x_token != 'fake-super-secret-token':
        raise HTTPException(status_code=400, detail='X-Token header invalid')


async def verify_key(x_key: str = Header(...)):
    """有返回值的子依赖，但是返回值不会被调用"""
    if x_key != 'fake-super-secret-key':
        raise HTTPException(status_code=400, detail='X-Key header invalid')
    return x_key


@app6.get('/dependency_in_path_operation',
          # 这时候不是在函数参数中调用依赖，而是在路径操作中
          dependencies=[Depends(verify_token), Depends(verify_key)])
async def dependency_in_path_operation():
    return [{'user': 'user1'}, {'user': 'user2'}]


"""Global Dependencies 全局依赖"""

# 单独在某个路由下的全局使用

# app6 = APIRouter(dependencies=[Depends(verify_token), Depends(verify_key)])

# 也可以房子全局的总app下


