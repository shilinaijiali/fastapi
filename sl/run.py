import logging
import time

from fastapi import FastAPI, Depends
import uvicorn
from fastapi.exceptions import RequestValidationError
from starlette.background import BackgroundTasks
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse
from starlette.staticfiles import StaticFiles

from sl import application
from sl.api.endpoints import app1, app2, app3, app4, app5, app6
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(
    # dependencies=[Depends()],
    title='FastAPI Study and API Docs',
    openapi_version='3.0.2',
    description='FastAPI学习',
    docs_url='/docs',
    redoc_url='/redoc',
)

# 允许所有来源访问，允许所有方法、所有头
"""
allow_origins: 允许访问的来源，可以是字符串或列表。------------->在生产环境中，避免使用 allow_origins=["*"]，而是明确指定允许的来源
allow_credentials: 是否允许携带身份验证信息，如 cookies。
allow_methods: 允许的 HTTP 方法，可以是字符串或列表。
allow_headers: 允许的 HTTP 头，可以是字符串或列表。
expose_headers: 暴露给浏览器的头，可以是字符串或列表。
max_age: 指定预检请求的缓存时间（以秒为单位）。

==================通过配置 CORS 中间件，FastAPI 应用就可以与不同域的前端应用进行跨域通信===========================
"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1",
        "http://127.0.0.1:8000"
    ],
    # allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# mount表示将某个目录下一个完全独立的应用挂载过来，这个不会在API交互文档中显示
# .mount()不要在分路由APIRouter().mount()调用，模板会报错
# path 访问路由
# directory 指定具体的文件目录
# name 别名
app.mount(path='/static', app=StaticFiles(directory='sl/static'), name='static')


@app.middleware('http')
async def my_middleware(request, call_next):
    response = await call_next(request)
    return response


# 重写HTTPException异常处理器
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """
    :param request: 这个参数不能省
    :param exc:
    :return:
    """
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


# 重写请求验证异常处理器
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """
    :param request: 这个参数不能省
    :param exc:
    :return:
    """
    return PlainTextResponse(str(exc.args), status_code=400)


# 定义中间件 ： 拦截请求并计算处理请求的时间
@app.middleware('http')
async def add_process_time_header(request, call_next):
    """

    :param request: 拦截到请求对象
    :param call_next:   call_next将接收request请求做为参数
    :return:
    """
    # 请求开始进入计时
    start_time = time.time()
    # 处理请求
    response = await call_next(request)
    # 请求结束计时
    process_time = time.time() - start_time
    # 将程序耗时 放到 响应头中
    # 添加自定义的以“X-”开头的响应头
    response.headers['X-Process-Time'] = str(process_time)

    return response


# 假设send_email函数实际发送电子邮件，这里简化为打印信息
def send_email(email: str, message: str):
    print(f"Sending email to {email} with message: {message}")
    # 实际发送电子邮件的代码应该在这里


@app.post('/send_email/{email}')
async def send_email_route(email: str, background_tasks: BackgroundTasks):
    message = 'Hello'  # 定义要发送的消息内容
    background_tasks.add_task(send_email, email, message)  # 将任务添加到后台任务队列
    background_tasks.add_task(send_email, email, '这是第二条短信, 我将按照添加的顺序异步执行发送')
    return {'message': 'Email sent!'}

# 将其他app添加到主路由下
# app03 ： app名字
# prefix ：自定义路由地址
# tags ：自定义路由标题 （默认是default）

app.include_router(app1, prefix='/app1', tags=['demo1'])
app.include_router(app2, prefix='/app2', tags=['demo2'])
app.include_router(app3, prefix='/app3', tags=['demo3'])
app.include_router(app4, prefix='/app4', tags=['demo4'])
app.include_router(app5, prefix='/app5', tags=['demo5'])
app.include_router(app6, prefix='/app6', tags=['demo6'])
app.include_router(application, prefix='/application', tags=['application'])


def main():
    """
    run:sl : 启动文件：app名字
    host : IP
    port : 端口
    reload : 自动重启
    debug : debug模式
    workers : 开启的进程数
    """

    uvicorn.run(app, host='127.0.0.1', port=8000, reload=True, workers=1)
    # uvicorn.run(app, host='127.0.0.1', port=8000, reload=True, workers=1, log_level=logging.DEBUG)


if __name__ == '__main__':
    main()
