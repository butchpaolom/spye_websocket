import asyncio
import websockets
from PIL import Image, ImageGrab
import io
import cv2
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import d3dshot

class Server:
    d = d3dshot.create()
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    async def main(self, websocket, path):
        await SendReceive(websocket, self.d).run()

    def start_server(self):
        start_server = websockets.serve(self.main, self.ip, self.port)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_server)
        loop.run_forever()


class SendReceive:
    send_frames = True

    def __init__(self, websocket, d):
        self.websocket = websocket
        self.d = d

    async def display_msg(self):
        try:
            async for msg in self.websocket:
                print(msg)
                if msg[:3] == 'cmd':
                    action = msg[4:]
                    if action == 'SendFramesToggle':
                        self.send_frames = not self.send_frames
                        await self.websocket.send(f'sendFrames{self.send_frames*1}')
                        print(f'sendFrames{self.send_frames*1}')
                    elif action == 'ShutDown':
                        print('shuting downzz')

                await asyncio.sleep(0)
        except:
            await self.websocket.close()

    def create_frame(self, frame):
        frame_bytes = io.BytesIO()
        frame.save(frame_bytes, format='JPEG',
                    quality=40, optimize=True)
        frame_bytes = frame_bytes.getvalue()
        return frame_bytes

    async def auto_send(self):
        try:
            await self.websocket.send(f'sendFrames{self.send_frames*1}')
            connected = True
            while connected:
                t = time.time()
                frame = self.d.screenshot()
                if self.send_frames:
                    new_frame = self.create_frame(frame)
                    await self.websocket.send(new_frame)
                    print(f'time: {round((time.time()-t)*1000)}ms')
                await asyncio.sleep(0)
        except Exception as e:
            print(e)
            await self.websocket.close()

    async def run(self):
        await asyncio.gather(
            self.display_msg(),
            self.auto_send()
        )


Server(ip='192.168.0.14', port=1234).start_server()
