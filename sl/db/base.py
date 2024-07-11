# 数据库连接基础配置

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# engine = create_engine('sqlite:///./sl/test.sqlite', encoding='utf8', echo=True, connect_args={'check_same_thread': False})

# 定义数据库连接对象
SQLALCHEMY_DATABASE_URL = 'sqlite:///test.db'

# mysql 或者 postgresql 数据库的连接方法
# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:root@localhost:5432/test'

# 定义引擎
engine = create_engine(
    # 数据库地址
    SQLALCHEMY_DATABASE_URL,
    # 编码方式
    encoding='utf-8',
    # echo=True表示引擎将用repr()函数记录所有语句及其参数列表到日志
    echo=True,
    # 由于SQLAlchemy是多线程，指定check_same_thread=False来让建立的对象任意线程都可使用
    # 这个参数只在SQLite数据库时设置
    connect_args={"check_same_thread": False}
)

# 在SQLAlchemy中，CURD都是通过会话(session)进行的，所以我们必须要先创建会话，每一个SessionLocal实例就是一个数据库session
# flush()是指发送数据库语句到数据库，但数据库不一定执行写入磁盘
# commit()是指提交事务，将变更保存到数据库文件

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=True)

# 创建基本映射类 -- 生成数据库
Base = declarative_base(bind=engine, name='Base')
