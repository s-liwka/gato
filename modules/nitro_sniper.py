import aiohttp
import asyncio
import modules.token_tools

async def redeem_nitro(token, gift_id, channel_id):

    headers = {
    'Authorization': modules.token_tools.decrypt_token(token),
    'Content-Type': 'application/json',
    'payment_source_id': 'null',
    }

    json = {'channel_id': channel_id}

    async with aiohttp.ClientSession() as session:
        request = await session.post(
            url=f"https://discord.com/api/v9/entitlements/gift-codes/{gift_id}/redeem",
            headers=headers,
            json=json,
        )

        return await request.json()