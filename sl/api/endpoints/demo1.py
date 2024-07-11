from typing import Optional, List

from fastapi import APIRouter, Path, Query

app1 = APIRouter()


# 不带参数的验证
# @app1.get('/path/parameters')
# def path_params01():
#     return {"message": 'This is a message!'}


# 路径参数和数字验证

# 函数的顺序就是路由访问的顺序
@app1.get('/path/parameters')
def path_params01(parameters: str):
    dic = {1: 2, 2: 3, 3: 4}
    # a = {k: v for k, v in dic.items()}
    a = [{k: v} for k, v in dic.items()]
    return {"message": parameters, "A": a}


# # 按照键排序
# sorted_by_key = {k: dic[k] for k in sorted(dic.keys())}
# print("按键排序:", sorted_by_key)
#
# # 按照值排序
# sorted_by_value = {k: v for k, v in sorted(dic.items(), key=lambda item: item[1])}


@app1.get('/files/{file_path: path}')
async def file_path(file_path: str):
    return {'File': file_path}


@app1.get('/path_num/{num}')
async def path_params_validate(
        # num 必须是 int类型，且使用Path校验，必须大于1小于10
        # title给参数添加标题
        # description: 给参数添加描述
        # None: 可以使用...代替
        num: int = Path(..., title='Your number', description='校验的数字类型', ge=1, le=10)
):
    return num


@app1.get('/query')
async def page_limit(page: int = 1, limit: Optional[int] = None):
    if limit:
        return {"page": page, 'limit': limit}
    else:
        return {'page': page}


@app1.get('/query/bool/conversion')
async def type_conversion(param: bool = False):
    return param


@app1.get('query/validations')
async def query_validations(
        # str 字符串类型
        # ... 必填参数
        # min_length 最小长度
        # max_length 最大长度
        # regex 正则表达式匹配 -- 必须以a开头
        value: str = Query(..., min_length=3, max_length=16, regex="^a"),
        # List 列表类型
        # default 默认值
        # alias 参数别名
        values: List[str] = Query(default=['v1', 'v2'], alias="alias_name")
):
    return value, values


