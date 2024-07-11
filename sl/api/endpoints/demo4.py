from datetime import timedelta, datetime
from typing import Optional, Union, List

from jose import JWTError, jwt
from fastapi import APIRouter, Form, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from starlette import status
from passlib.context import CryptContext

app4 = APIRouter()


# 响应模型

# 定义基本类
class User(BaseModel):
    username: str
    # 定义字段 email: 邮箱 类型为 EmailStr: 自动校验邮箱
    email: Optional[EmailStr] = None
    # mobile: str = '123456'
    # 定义字段 full_name: 类型为 Optional[str]: 可选填参数 ，字符串类型
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


# 定义用户登录类
class UserIn(User):
    # 登陆需要校验密码
    # 定义字段 password ： 密码 类型为 str ： 字符串
    password: str


# 定义用户响应信息类
class UserOut(User):
    # 返回信息 不需要将用户的密码作为响应数据返回
    ...


# 新建两个用户
users = {
    "user01": {"username": "user01", "password": "123123", "email": "user01@example.com"},
    "user02": {"username": "user02", "password": "123456", "email": "user02@example.com", "mobile": "110"}
}


# response_model: 默认响应数据模型
# response_model_exclude_unset: 只使用前端传过来的值，而不使用默认值(mobile: str = '123456' --> 不使用123456而是使用前端传入的数据/函数中赋值)
@app4.post('/response_model', response_model=UserOut, response_model_exclude_unset=True)
async def response_model(user: UserIn):
    """response_model_exclude_unset=True表示默认值不包含在响应中，仅包含实际给的值，如果实际给的值与默认值相同也会包含在响应中"""
    # password不会被返回
    print(user.password)
    return users['user01']


# 响应字段取两个模型类的并集
@app4.post('/response_model/attributes', response_model=Union[UserIn, UserOut])
async def response_model_attributes(user: UserIn):
    return user


# 响应字段取两个模型类的并集
@app4.post('/response_model/v1/attributes', response_model=List[UserOut])
async def response_model_attributes(user: UserIn):
    # 在返回时，需要返回多个用户信息
    return [user, user]


@app4.post(
    '/response_model/v2/attributes',
    # 只使用固定的响应模型类
    response_model=UserOut,
    # 返回的响应数据中必须包含的字段
    response_model_include={'username', 'email'},
    # 返回的响应数据中必须排除的字段
    response_model_exclude={'mobile'}
)
async def response_model_attributes(user: UserIn):
    return user


# 响应状态码
@app4.get('/status_code', status_code=status.HTTP_200_OK)
async def status_attributes():
    return {"status_code": 200, "status_type": str(type(status.HTTP_200_OK))}


@app4.post('/login')
async def login(
        # username 用户名 str 字符串类型 必填 通过表单验证 下同
        username: str = Form(...), password: str = Form(...)
):  # 定义表单参数
    """
    用Form类需要 pip install python-multipart；
    Form类的元数据和校验方法类似Body/Query/Path/Cookie
    """
    return {"username": username}


@app4.post(
    '/path_operation_configuration',
    response_model=UserOut,
    # tags=["path", "Operation", "Configuration"],
    summary='This is summary',
    description='This is description',
    deprecated=True,
    status_code=status.HTTP_200_OK
)
async def path_operation_configuration(user: UserIn):
    """
    Path Operation Configuration 路径操作配置
    :param user: 用户信息
    :return: 返回结果
    """
    return user.model_dump()


"""OAuth2 密码模式和 FastAPI 的 OAuth2PasswordBearer"""

"""
OAuth2PasswordBearer是接收URL作为参数的一个类：客户端会向该URL发送username和password参数，然后得到一个Token值
OAuth2PasswordBearer并不会创建相应的URL路径操作，只是指明客户端用来请求Token的URL地址
当请求到来的时候，FastAPI会检查请求的Authorization头信息，如果没有找到Authorization头信息，或者头信息的内容不是Bearer token，它会返回401状态码(UNAUTHORIZED)
"""

# 1、定义Token请求地址
# 请求Token的URL地址 http://127.0.0.1:8000/app4/token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/app4/token")


# 2、定义获取token视图
@app4.get('/oauth2_paassword_bearer')
async def oauth2_password_bearer(token: str = Depends(oauth2_scheme)):
    return {"token": token}


# 3、定义登录视图

"""基于Password 和 Bearer token 的 OAuth2 认证"""
# 模拟数据库
fake_users_db = {
    'jiali': {
        'username': 'jiali',
        'full_name': 'jiali',
        'email': '313092582@qq.com',
        'hashed_password': 'fakehashed19980705',
        # 模拟权限: 未激活用户 无权限
        'disabled': False,
    },
    'shilin': {
        'username': 'shilin',
        'full_name': 'shilin',
        'email': '1164426001@qq.com',
        'hashed_password': 'fakehashedsecret',
        # 模拟权限: 激活用户 有权限
        'disabled': True,
    }
}


# 模拟加密密码操作
def fake_hash_password(password: str):
    return 'fakehashed' + password


# 创建用户模型类  上面已创建

# 创建用户登入传入的数据类
class UserInDB(User):
    hashed_password: str


# 定义登录视图
@app4.post('/token')
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # 根据输入的用户名 从数据库中获取到用户数据
    user_dict = fake_users_db.get(form_data.username)
    # 用户不存在
    if not user_dict:
        # 抛出异常, 用户不存在
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect username or password')
    # 用户存在，将查询到的用户数据进行校验
    user = UserInDB(**user_dict)
    # 校验输入的密码是否争取 (先对密码进行加密, 再对比)
    hashed_password = fake_hash_password(form_data.password)
    # 如果加密后的密码 不等于 数据库查询到的用户对应的密码
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect username or password')
    # 用户登录成功 返回用户名和token等信息
    return {'access_token': user.username, 'token_type': 'bearer'}


# 模拟校验用户信息视图
def get_user(db, username: str):
    """

    :param db: 数据库对象
    :param username: token字符串
    :return:
    """
    # 怕那段当前token字符串是否存在于数据库当中
    if username in db:
        # 存在数据库当中，取出详细的用户信息返回
        user_dict = db[username]
        return UserInDB(**user_dict)


# 验证token
def fake_decode_token(token: str):
    # 传入token字符串
    # 从数据库中查询当前登陆对象
    user = get_user(fake_users_db, token)
    # 返回校验通过后的用户对象
    return user


# 获取当前用户
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # 根据当前用户传入的用户名和密码 自动签发token
    # 校验签发的token是否正确
    user = fake_decode_token(token)
    # token不正确
    if not user:
        # 抛出异常
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication credentials',
            # OAuth2的规范，如果验证失败，请求头中返回'WWW-Authenticate'
            headers={'WWW-Authenticate': 'Bearer'}
        )
    # token正确,返回用户信息
    return user


# 获取激活用户信息
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    # 依赖于上一步  用户已经登录，并且已经是当前登录的用户对象
    # 校验disable字段，校验是否处于激活状态
    if current_user.disabled:
        # 未激活抛出异常
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Inactive user')
    # 激活返回用户对象
    return current_user


# 定义视图
@app4.get('/users/me')
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    # 只有当前用户是登录且激活的用户才能被返回
    return current_user


"""OAuth2 with Password (and hashing), Bearer with JWT tokens 开发预计JSON Web Tokens的认证"""
# 模拟数据库
fake_users_db.update({
    'shilin': {
        'username': 'shilin',
        'full_name': 'shilin',
        'email': '1164426001@qq.com',
        'hashed_password': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
        'disabled': False,
    }
})

# 配置

# 生成密钥
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # 生成密钥 openssl rand -hex 32
ALGORITHM = 'HS256'  # 算法
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 访问令牌过期分钟


# 模拟Token库
class Token(BaseModel):
    """返回给用户的Token"""
    access_token: str
    token_type: str


# 加密密码的方法
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# 签发token的方法
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/app4/jwt/token")


# 校验密码
def verify_password(plain_password: str, hashed_password: str):
    """对密码进行校验"""
    return pwd_context.verify(plain_password, hashed_password)


# 获取签发认证后的用户
def jwt_get_user(db, username: str):
    # 判断用户是否存在数据库中
    if username in db:
        # 存在数据库中则返回用户信息
        user_dict = db[username]
        # 返回用户对象
        return UserInDB(**user_dict)


# JWT认证用户
def jwt_authenticate_user(db, username: str, password: str):
    # 首先获取到签发认证的用户
    user = jwt_get_user(db=db, username=username)
    if not user:
        # 签发不成功，返回失败
        return False
    # 签发成功则校验密码
    if not verify_password(plain_password=password, hashed_password=user.hashed_password):
        return False
    # 密码正确返回用户对象
    return user


# 签发token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    # 先将数据 copy 一份
    to_encode = data.copy()
    # 过期时间存在则取出
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # 默认时间15分钟
        expire = datetime.utcnow() + timedelta(minutes=15)
    # 更新过期时间
    to_encode.update({'exp': expire})
    # 加密签发token
    # claims 原始数据
    # key 密钥
    # algorithm 算法
    encoded_jwt = jwt.encode(claims=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    # 返回签发好的token
    return encoded_jwt


# 定义视图，登录签发token，定义响应数据体Token
@app4.post('/jwt/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # 认证用户
    user = jwt_authenticate_user(db=fake_users_db, username=form_data.username, password=form_data.password)
    if not user:
        # 认证不通过抛出异常
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    # 认证过期时间
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # 签发token
    access_token = create_access_token(
        # 默认的参数是sub
        data={'sub': user.username}, expires_delta=access_token_expires
    )
    # 返回签发成功的token
    return {'access_token': access_token, 'token_type': 'bearer'}


# 创建依赖 --- 获取当前登录的用户
async def jwt_get_current_user(token: str = Depends(oauth2_scheme)):
    # 定义一个异常对象， 方便下面多次调用
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    try:
        # 对token进行解码
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # 获取到解码后的数据中的用户名
        username = payload.get('sub')
        if username is None:
            # 用户名不存在则抛出异常
            raise credentials_exception
    except JWTError:
        # JWT认证失败 抛出异常
        raise credentials_exception

    # 获取到签发认证成功后的用户对象
    user = jwt_get_user(db=fake_users_db, username=username)
    if not user:
        raise credentials_exception
    return user


# 创建依赖 --- 获取当前登录的激活后的用户
async def jwt_get_current_active_user(current_user: User = Depends(jwt_get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Inactive user')
    return current_user


# 定义登录视图
@app4.post('/jwt/users/me')
async def jwt_read_users_me(current_user: User = Depends(jwt_get_current_active_user)):
    return current_user
