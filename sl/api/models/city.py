from sqlalchemy import Column, Integer, String, BigInteger, DateTime, func, ForeignKey, Date
from sqlalchemy.orm import relationship

from sl.db.base import Base


class City(Base):
    # 数据库表名
    __tablename__ = 'city'
    # 定义主键ID: 数字类型 主键 索引 自增
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    # 定义省份字段:字符串类型(长度) 唯一 是否可为空 注释
    province = Column(String(100), unique=True, nullable=False, comment="省/直辖市")
    # 定义国家字段:字符串类型(长度) 是否可为空 注释
    country = Column(String(100), nullable=False, comment='国家')
    # 定义国家代码字段: 字符串类型(长度) 是否可为空 注释
    country_code = Column(String(100), nullable=False, comment='国家代码')
    # 定义国家人口字段 ： 大整数类型 是否可为空 注释
    country_population = Column(BigInteger, nullable=False, comment='国家人口')
    # 'CityData'是关联的类名；back_populates来指定反向访问的属性名称
    data = relationship('Data', back_populates='city')

    # 定义字段创建时间: 时间类型 当数据创建或者更新时自动更新时间 注释
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    # 根据 country_code 排序   默认是正序   倒序加上.desc()方法 (country_code.desc())
    # __mapper_args__ = {'oreder_by': country_code}

    # 显示类对象的信息
    def __repr__(self):
        return '{}_{}'.format(self.country, self.province)


class Data(Base):
    __tablename__ = 'data'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    # 定义外键字段 关联国家ID: 数字类型 外键关联(表.字段) 注释
    # ForeignKey里的字符串格式不是类名.属性名，而是表名.字段名
    city_id = Column(Integer, ForeignKey('city.id'), comment='所属省/直辖市')
    date = Column(Date, nullable=False, comment='数据日期')
    confirmed = Column(BigInteger, default=0, nullable=False, comment='确诊数量')
    deaths = Column(BigInteger, default=0, nullable=False, comment='死亡数量')
    recovered = Column(BigInteger, default=0, nullable=False, comment='痊愈数量')
    # 'City'是关联的类名；back_populates来指定反向访问的属性名称
    city = relationship('City', back_populates='data')

    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    # 显示类对象的信息
    def __repr__(self):
        return f'{repr(self.date)}：确诊{self.confirmed}例'
