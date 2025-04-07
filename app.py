import asyncio
from aiohttp import web
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity

# 如果你有設定 Microsoft App Id 及 Microsoft App Password，請填入以下變數
APP_ID = "a9731db8-42c7-46b9-87a5-5c6231e68eca"  # 如果本地測試可以留空
APP_PASSWORD = "ff78195e-10e3-48e8-be1a-11146e8f9ec7"  # 如果本地測試可以留空

adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(adapter_settings)

# 定義一個簡單的 Echo Bot
class EchoBot:
    async def on_turn(self, turn_context: TurnContext):
        if turn_context.activity.type == "message":
            # 回覆使用者所傳的訊息
            await turn_context.send_activity(f"你說：{turn_context.activity.text}")

bot = EchoBot()

# 定義 HTTP POST /api/messages 的處理函式
async def messages(request: web.Request) -> web.Response:
    # 檢查是否為 JSON 格式
    if "application/json" in request.headers.get("Content-Type", ""):
        body = await request.json()
    else:
        return web.Response(status=415)

    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")

    async def aux_func(turn_context: TurnContext):
        await bot.on_turn(turn_context)

    # 處理傳入的活動
    await adapter.process_activity(activity, auth_header, aux_func)
    return web.Response(status=201)

app = web.Application()
app.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    try:
        #web.run_app(app, host="localhost", port=3978)
        web.run_app(app, host="0.0.0.0", port=8000)
    except Exception as error:
        raise error
