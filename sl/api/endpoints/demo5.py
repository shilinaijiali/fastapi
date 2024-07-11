import time
from typing import List, Optional

from fastapi import APIRouter, File, UploadFile, BackgroundTasks, Depends

app5 = APIRouter()

"""Request Files 单文件多文件上次及参数详解"""


@app5.post('/file')
async def file_(file: bytes = File(...)):  # 如果要上传多个文件 files: List[bytes] = File(...)
    """使用File类 文件内容会以bytes的形式读入内存，适合于上次小文件"""
    return {"file_size": len(file)}


@app5.post('/upload_files')
async def upload_files(files: List[UploadFile] = File(...)):  # 如果要上传单个文件 files: UploadFile = file(...)
    """
    使用UploadFile类的优势:
    1.文件存储在内存中，使用的内存达到阈值后，将被保存在磁盘中
    2.适合于图片、视频大文件
    3.可以获取上传的文件的元数据，如文件名，创建时间等
    4.有文件对象的异步接口
    5.上次的文件是Python文件对象，可以使用write(), read(), seek(), close()操作
    """
    for file in files:
        contents = await file.read()
        print(contents)
    return {"filename": files[0].filename, "content_type": files[0].content_type}


def bg_task(framework: str):
    with open("README.md", mode="a") as f:
        f.write(f"## {framework} 框架精讲")


@app5.post("/background_tasks")
async def run_bg_task(framework: str, background_tasks: BackgroundTasks):
    """
    :param framework: 被调用的后台任务函数的参数
    :param background_tasks: FastAPI.BackgroundTasks
    :return:
    """
    # 模拟执行耗时任务
    background_tasks.add_task(bg_task, framework)
    return {"message": "任务已在后台运行"}


def continue_write_readme(background_tasks: BackgroundTasks, q: Optional[str] = None):
    if q:
        background_tasks.add_task(bg_task,
                                  "\n> 整体的介绍 FastAPI，快速上手开发，结合 API 交互文档逐个讲解核心模块的使用\n")
    return q


@app5.post("/dependency/background_tasks")
async def dependency_run_bg_task(q: str = Depends(continue_write_readme)):
    if q:
        return {"message": "README.md更新成功"}

