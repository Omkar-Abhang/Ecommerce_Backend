# orders/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

# without authentication 
class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # For testing: connect to a common group (like \"broadcast\") instead of user-specific group
        self.group_name = 'broadcast'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def order_status_update(self, event):
        await self.send(text_data=json.dumps({
            'order_id': event['order_id'],
            'status': event['status'],
        }))










# with authentication 

# class OrderConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user = self.scope["user"]
#         if self.user.is_authenticated:
#             self.group_name = f"user_{self.user.id}"
#             await self.channel_layer.group_add(
#                 self.group_name,
#                 self.channel_name
#             )
#             await self.accept()
#         else:
#             await self.close()

#     async def disconnect(self, close_code):
#         if self.user.is_authenticated:
#             await self.channel_layer.group_discard(
#                 self.group_name,
#                 self.channel_name
#             )

#     async def order_status_update(self, event):
#         await self.send(text_data=json.dumps({
#             'order_id': event['order_id'],
#             'status': event['status'],
#         }))



