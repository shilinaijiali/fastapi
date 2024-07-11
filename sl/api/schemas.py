# 定义响应数据格式

from datetime import datetime
from datetime import date as date_


from pydantic import BaseModel


# 定义创建数据的格式
class CreateData(BaseModel):
    # 前端传入  创建时间
    date: date_
    # 确诊数
    confirmed: int = 0
    # 死亡数
    deaths: int = 0
    # 痊愈数
    recovered: int = 0


# 定义创建城市数据的格式
class CreateCity(BaseModel):
    # 省份
    province: str
    # 国家
    country: str
    # 国家代码
    country_code: str
    # 国家人口
    country_population: int


# 定义读取数据的格式
class ReadData(CreateData):
    # 主键id
    id: int
    # 城市代码
    city_id: int
    # 创建时间
    updated_at: datetime
    # 更新时间
    created_at: datetime

    # 定义配置: 允许使用orm语句
    class Config:
        from_attributes = True


class ReadCity(CreateCity):
    id: int
    updated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

