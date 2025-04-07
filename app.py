import os
import logging
from aiohttp import web
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set Microsoft App Id and App Password
APP_ID = "a9731db8-42c7-46b9-87a5-5c6231e68eca"  # Leave empty for local testing
APP_PASSWORD = "ff78195e-10e3-48e8-be1a-11146e8f9ec7"  # Leave empty for local testing

adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(adapter_settings)

# Define the Echo Bot
class EchoBot:
    async def on_turn(self, turn_context: TurnContext):
        if turn_context.activity.type == "message":
            # Log received message
            logger.info(f"Received message: {turn_context.activity.text}")
            # Respond with the same message
            await turn_context.send_activity(f"You said: {turn_context.activity.text}")

bot = EchoBot()

# Define the /api/messages POST route to handle incoming messages
async def messages(request: web.Request) -> web.Response:
    if "application/json" not in request.headers.get("Content-Type", ""):
        logger.error("Invalid content type: Expected application/json")
        return web.Response(status=415)

    try:
        # Deserialize incoming activity
        body = await request.json()
        logger.info(f"Received activity: {body}")
        activity = Activity().deserialize(body)
        auth_header = request.headers.get("Authorization", "")

        # Define function to process activity and send it to bot
        async def aux_func(turn_context: TurnContext):
            try:
                await bot.on_turn(turn_context)
            except Exception as e:
                logger.error(f"Error while processing turn: {str(e)}")
                await turn_context.send_activity("An error occurred while processing your message.")

        # Process the activity
        await adapter.process_activity(activity, auth_header, aux_func)
        return web.Response(status=201)

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return web.Response(status=500, text="Internal server error")

# Define the home route to display the chat interface (HTML page)
async def home(request: web.Request) -> web.Response:
    try:
        html_content = open(os.path.join(os.path.dirname(__file__), "index.html")).read()
        return web.Response(text=html_content, content_type="text/html")
    except Exception as e:
        logger.error(f"Error loading HTML page: {str(e)}")
        return web.Response(status=500, text="Error loading page")

# Create the web application
app = web.Application()

# Add routes
app.router.add_get("/", home)  # Route to serve the HTML chat interface
app.router.add_post("/api/messages", messages)  # Route for processing bot messages

if __name__ == "__main__":
    try:
        # Run the web app
        web.run_app(app, host="0.0.0.0", port=8000)
    except Exception as error:
        logger.error(f"Error starting the server: {str(error)}")
