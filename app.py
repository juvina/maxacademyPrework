import chainlit as cl
import openai
import os

api_key = os.getenv("OPENAI_API_KEY")

endpoint_url = "https://api.openai.com/v1"
client = openai.AsyncClient(api_key=api_key, base_url=endpoint_url)

# https://platform.openai.com/docs/models/gpt-4o
model_kwargs = {
    "model": "gpt-4o-mini",
    "temperature": 0.3,
    "max_tokens": 500
}

@cl.on_message
async def on_message(message: cl.Message):
    # send initial response as an empty string
    response_message = cl.Message(content="")
    await response_message.send()

    # set up model to stream response based on message
    stream = await client.chat.completions.create(messages=[{"role": "user", "content": message.content}],
                                                  stream=True, **model_kwargs)
    # send over parts of response as stream as they're ready
    async for part in stream:
        if token := part.choices[0].delta.content or "":
            await response_message.stream_token(token)
    # finish the response message; no more updates
    await response_message.update()


