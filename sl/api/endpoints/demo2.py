from datetime import date
from typing import List

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

app2 = APIRouter()


class CityInfo(BaseModel):
    # 给name字段添加注解
    # ...: 表示必填字段
    # example: 表示示例，只是注解，不会被验证
    name: str = Field(..., example='chengdu')
    country: str
    country_code: str = None
    # 给country_population字段进行校验
    # default: 默认值
    # title: 字段标题
    # description: 字段描述
    # ge: 大于等于
    country_population: int = Field(default=800, title="人口数量", description="国家人口数量", ge=800)

    # 指定配置
    class Config:
        json_schema_extra = {
            # 置顶默认示例
            "example": {
                "name": "shanghai",
                "country": "China",
                "country_code": "CN",
                "country_population": 1400000000
            }
        }


@app2.post('/request_body/city')
async def city_info(city: CityInfo):
    return city.model_dump()


@app2.put('/request_body/city/{name}')
async def mix_city_info(
        # 路径参数
        name: str,
        # 请求体 Body 可以定义多个
        city01: CityInfo,
        city02: CityInfo,
        # 对请求参数进行校验码，所以使用Query
        confirmed: int = Query(ge=0, description="确诊数", default=0),
        death: int = Query(ge=0, description="死亡数", default=0)
):
    if name == "Shanghai":
        return {"Shanghai": {"confirmed": confirmed, "death": death}}
    return city01.model_dump(), city02.model_dump()


class Data(BaseModel):
    # 定义数据格式嵌套的请求体
    city: List[CityInfo] = None
    # 额外的数据类型，还有uuid datetime bytes frozenset等
    # 参考: https://fastapi.tiangolo.com/tutorial/extra-data-types/
    date: date
    confirmed: int = Field(ge=0, description="确诊数", default=0)
    death: int = Field(ge=0, description="死亡数", default=0)
    recovered: int = Field(ge=0, description="痊愈数", default=0)


@app2.put('/request_body/nested')
async def nested_models(data: Data):
    return data.model_dump()
