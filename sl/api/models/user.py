# 导入pydantic中的 BaseModel 模型类
from typing import List

from pydantic import BaseModel, constr
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# 创建表
class User(Base):
    # 表名
    __tablename__ = "users"
    # 创建字段 ID 为 Integer 类型且为逐渐，不能为空
    id = Column(Integer, primary_key=True, nullable=False)
    # 创建字段 name 为 String 类型，且指明长度为20， index建立索引， nullable不能为空，unique唯一
    name = Column(String(20), index=True, nullable=False, unique=True)
    # 创建字段 domains 为 ARRAY(数组)类型，且、数组中的元素类型为String类型，指明长度为255
    domains = Column(ARRAY(String(255)))


# 创建表 --- 定义一个表与上面的字段类型一样
class UserModel(BaseModel):
    id: int
    # constr 限制字符串
    name: constr(max_length=20)
    domains: List[constr(max_length=255)]

    # 定义配置
    class Config:
        # 'orm_mode' has been renamed to 'from_attributes'
        # orm_mode = True
        from_attributes = True


# 创建数据字典
orm_data = {
    "id": "123",
    'name': 'shilin',
    'domains': ['example.com', 'xxx.com'],
}

# 实例化表模型对象
co_orm = User(**orm_data)

# 实例化得到ORM对象
# ORM模型: 从类实例创建符合ORM对象的模型
# co_orm 是类的实例使用 UserModel.from_orm去校验他的数据类型
# pydantic定义的模型类的规范

# The `from_orm` method is deprecated; set `model_config["from_attributes"]=True` and use `model_validate` instead.
# orm_obj = UserModel.from_orm(co_orm)
orm_obj = UserModel.model_validate(co_orm, from_attributes=True)
# print(orm_obj)
