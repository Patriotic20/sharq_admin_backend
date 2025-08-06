# import httpx
# from fastapi import HTTPException , status

# ESKIZ_SMS_URL = "https://notify.eskiz.uz/api/message/sms/send"
# ESKIZ_TOKEN = "your_actual_token_here"

# async def send_sms(
#     mobile_phone: str,
#     message: str,
#     from_sender: str = "4546",
#     callback_url: str | None = None,
# ):
#     data = {
#         "mobile_phone" : mobile_phone,
#         "message" : message,
#         "from" : from_sender
#     }

#     if callback_url:
#         data["callback_url"] = callback_url

#     headers = {
#         "Authorization": f"Bearer {ESKIZ_TOKEN}"
#     }

#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.post(
#                 ESKIZ_SMS_URL,
#                 data=data,
#                 headers=headers
#             )

#         if response.status_code != 200:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=f"Eskiz error: {response.text}"
#                 )
