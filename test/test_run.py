# from fastapi.testclient import TestClient
#
# from sl.run import app
#
# """测试用例"""
#
# client = TestClient(app)
#
#
# def test_send_email_route():
#     response = client.post(url="/send_email/?email=asddsaad")  # 注意这里的url包含了/app5前缀
#
#     assert response.status_code == 200
#     assert response.json() == {"status": "ok"}
