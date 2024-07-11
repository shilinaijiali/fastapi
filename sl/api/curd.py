from sqlalchemy.orm import Session

from sl.api import schemas
from sl.api.models import city, user


# 查询城市的数据
def get_city(db: Session, city_id: int):
    # 通过数据库对象 查询模型表中的City模型， 过滤出City.id == 输入的城市id的数据取出来
    return db.query(city.City).filter(city.City.id == city_id).first()


# 通过省份查询城市数据
def get_city_by_name(db: Session, city_name: str):
    return db.query(city.City).filter(city.City.province == city_name).first()


# 获取到指定范围内的城市数据  -- 分页操作
def get_cities(db: Session, skip: int = 0, limit: int = 10):
    return db.query(city.City).offset(skip).limit(limit).all()


# 创建城市数据
def create_city(db: Session, citys: schemas.CreateCity):
    # 初始化城市数据对象
    db_city = city.City(**citys.model_dump())
    # 提交数据库
    db.add(db_city)
    # 执行事务
    db.commit()
    # 刷新数据
    db.refresh(db_city)
    # 将创建好的城市对象返回
    return db_city


# 获取到指定城市的指定范围内的数据
def get_data(db: Session, city_name: str = None, skip: int = 0, limit: int = 10):
    # 是否根据城市进行数据查询
    if city_name:
        return db.query(city.Data).join(city.City, city.Data.city_id == city.City.id).filter(city.City.province == city_name).all()
    # 不按城市查询则根据模型类中的数据格式进行数据查询切片并返回
    return db.query(city.Data).offset(skip).limit(limit).all()


# 创建城市详细数据
def create_city_data(db: Session, data: schemas.CreateData, city_id: int):
    # 初始化城市详细数据对象
    db_data = city.Data(**data.model_dump(), city_id=city_id)
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data





