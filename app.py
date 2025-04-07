import os
from aiohttp import web
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity

# 設定 Microsoft App Id 和 App Password
APP_ID = "a9731db8-42c7-46b9-87a5-5c6231e68eca"  # 如果本地測試可以留空
APP_PASSWORD = "ff78195e-10e3-48e8-be1a-11146e8f9ec7"  # 如果本地測試可以留空

adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(adapter_settings)

class EchoBot:
    async def on_turn(self, turn_context: TurnContext):
        if turn_context.activity.type == "message":
            await turn_context.send_activity(f"你說：{turn_context.activity.text}")

bot = EchoBot()

# 處理訊息的 API 路由
async def messages(request: web.Request) -> web.Response:
    if "application/json" in request.headers.get("Content-Type", ""):
        body = await request.json()
    else:
        return web.Response(status=415)

    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")

    async def aux_func(turn_context: TurnContext):
        await bot.on_turn(turn_context)

    await adapter.process_activity(activity, auth_header, aux_func)
    return web.Response(status=201)

# 處理首頁，顯示聊天介面的 HTML 頁面
async def home(request: web.Request) -> web.Response:
    html_content = open(os.path.join(os.path.dirname(__file__), "index.html")).read()
    return web.Response(text=html_content, content_type="text/html")

# 創建應用程式
app = web.Application()

# 路由配置
app.router.add_get("/", home)  # 顯示聊天頁面
app.router.add_post("/api/messages", messages)  # 訊息處理 API

if __name__ == "__main__":
    try:
        web.run_app(app, host="0.0.0.0", port=8000)
    except Exception as error:
        raise error
