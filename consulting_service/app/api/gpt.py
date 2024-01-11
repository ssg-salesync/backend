import aiohttp
import asyncio


async def send_prompt_to_gpt_async(req_id, prompt, engine='davinci'):
    req_id = req_id
    url = f"https://api.openai.com/v1/engines/{engine}/completions"

    headers = {
        "Authorization": f"Bearer YOUR_OPENAI_API_KEY{}",
        "Content-Type": "application/json"
    }

    data = {
        "prompt": prompt,
        "max_tokens": 500
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                return {
                    "response": await response.json()
                }
            else:
                return {
                    "error": await response.text()
                }


async def main():
    prompt = "Translate the following English text to French: 'Hello, how are you?'"
    result = await send_prompt_to_gpt_async(prompt)
    print(result)


asyncio.run(main())