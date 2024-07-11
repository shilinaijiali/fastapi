from typing import List

from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import crud
from starlette import status
from starlette.templating import Jinja2Templates

from sl.api import schemas, curd
from sl.db.base import Base, engine, SessionLocal

# 创建子路由
application = APIRouter()

# 创建前端页面配置
templates = Jinja2Templates(directory="./sl/templates")

# 初始化数据库引擎对象
Base.metadata.create_all(bind=engine)


# 创建子依赖对象
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 创建城市
@application.post("/create_city", response_model=schemas.ReadCity)
async def create_city(citys: schemas.CreateCity, db: Session = Depends(get_db)):
    """

    :param citys: 前端传入的符合 CreateCity 格式的城市数据
    :param db: 数据库操作对象，基于子依赖的数据库操作
    :return:
    """
    # 判断是否存在当前城市 --- 根据前端传入的城市名字进行过滤
    db_city = curd.get_city_by_name(db=db, city_name=citys.province)
    # 存在则主动抛出异常
    if db_city:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='City already exists',
        )
    # 不存在则创建
    return curd.create_city(db=db, citys=citys)


# 查询多个城市的数据
@application.get('/get_cities', response_model=List[schemas.ReadCity])
async def get_cities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """

    :param skip: 起始位置
    :param limit: 结束位置
    :param db: 数据库对象，依赖子依赖
    :return:
    """
    cities = curd.get_cities(db=db, skip=skip, limit=limit)

    return cities


# 创建数据
@application.post('/create_data', response_model=schemas.ReadData)
async def create_data_for_city(city: str, data: schemas.CreateData, db: Session = Depends(get_db)):
    """

    :param city: 给那个城市创建数据
    :param data: 城市的详细数据
    :param db: 数据库对象，依赖子依赖
    :return:
    """
    # 查询当前城市是否存在
    db_city = curd.get_city_by_name(db=db, city_name=city)
    # 创建数据
    data = curd.create_city_data(db=db, data=data, city_id=db_city.id)
    return data


# 获取数据
@application.get('/get_data')
async def get_data(city: str = None, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """

    :param city: 城市名字
    :param skip: 起始位置
    :param limit: 截止位置
    :param db: 数据库对象，依赖子依赖
    :return:
    """
    data = curd.get_data(city_name=city, skip=skip, limit=limit, db=db)
    return data
