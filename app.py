import chainlit as cl
import openai
import os
import base64

open_ai_key = os.getenv("OPENAI_API_KEY")
runpod_key = os.getenv("RUNPOD_API_KEY")

api_key = open_ai_key

runpod_serverless_id = os.getenv("RUNPOD_SERVERLESS_ID")

# Can only use one endpoint at a time
openapi_endpoint = "https://api.openai.com/v1"
runpod_endpoint = f"https://api.runpod.ai/v2/{runpod_serverless_id}/openai/v1"

# Make sure endpoint and key variables match
endpoint_url = openapi_endpoint

client = openai.AsyncClient(api_key=api_key, base_url=endpoint_url)

#  GPT4o mini
# https://platform.openai.com/docs/models/gpt-4o
openai_model = {
    "model": "gpt-4o-mini",
    "temperature": 0.3,
    "max_tokens": 500
}

# Minstral 7b Instruct 0.3
minstral_model = {
    "model": "mistralai/Mistral-7B-Instruct-v0.3",
    "temperature": 0.3,
    "max_tokens": 500
}

model_kwargs = openai_model

@cl.on_message
async def on_message(message: cl.Message):
    # Maintain an array of messages in the user session
    message_history = cl.user_session.get("message_history", [])

    # Processing images if they exist
    images = [file for file in message.elements if "image" in file.mime] if message.elements else []

    if images:
        # Read the first image and encode it to base64
        with open(images[0].path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode('utf-8')
        message_history.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": message.content if message.content else "What’s in this image?"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        })
    else:
        # add in user information and current message for ease of use in API call
        message_history.append({"role": "user", "content": message.content})

    # send initial response as an empty string
    response_message = cl.Message(content="")
    await response_message.send()

    # send message history along to model and stream response
    stream = await client.chat.completions.create(messages=message_history,
                                                  stream=True, **model_kwargs)
    # send over parts of response as stream as they're ready
    async for part in stream:
        if token := part.choices[0].delta.content or "":
            await response_message.stream_token(token)
    # finish the response message; no more updates
    await response_message.update()

    # Record the AI's response in the history
    message_history.append({"role": "assistant", "content": response_message.content})
    cl.user_session.set("message_history", message_history)


