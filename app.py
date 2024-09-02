import chainlit as cl
import openai
import os

# api_key = os.getenv("OPENAI_API_KEY")
api_key = os.getenv("RUNPOD_API_KEY")
runpod_serverless_id = os.getenv("RUNPOD_SERVERLESS_ID")


# endpoint_url = "https://api.openai.com/v1"
endpoint_url = f"https://api.runpod.ai/v2/{runpod_serverless_id}/openai/v1"

client = openai.AsyncClient(api_key=api_key, base_url=endpoint_url)

#  GPT4o mini
# https://platform.openai.com/docs/models/gpt-4o
# model_kwargs = {
#     "model": "gpt-4o-mini",
#     "temperature": 0.3,
#     "max_tokens": 500
# }

# Minstral 7b Instruct 0.3
model_kwargs = {
    "model": "mistralai/Mistral-7B-Instruct-v0.3",
    "temperature": 0.3,
    "max_tokens": 500
}

@cl.on_message
async def on_message(message: cl.Message):
    # Maintain an array of messages in the user session
    message_history = cl.user_session.get("message_history", [])
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


