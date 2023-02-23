from PIL import Image, ImageDraw
import pystray
import os
import socketio
import time
import webbrowser


sio = socketio.Client()


def transmit(message):
  sio.emit('systray_controls', {'data':message})


def create_image(width, height, color1, color2):
    # Generate an image and draw a pattern
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)

    return image

def create_systray_app():   

    icon = pystray.Icon('FossBot',
                        icon=Image.open(os.path.join(os.path.dirname(__file__), "..", "app.ico")),
                        menu=pystray.Menu(
                        pystray.MenuItem("Open FossBot", after_click),
                        # pystray.MenuItem("GeeksforGeeks Youtube", after_click),
                        # pystray.MenuItem("GeeksforGeeks LinkedIn", after_click),
                        pystray.MenuItem("Exit", after_click)))

    return icon

def after_click(icon, query):
    if str(query) == "Open FossBot":
        webbrowser.open_new("http://127.0.0.1:8081")
        # icon.stop()
    # elif str(query) == "GeeksforGeeks Youtube":
    #     print("Youtube Channel of GeeksforGeeks \
    #     is -> https://www.youtube.com/@GeeksforGeeksVideos")
    #     # icon.stop()
    # elif str(query) == "GeeksforGeeks LinkedIn":
    #     print("LinkedIn of GeeksforGeeks \
    #     is -> https://www.linkedin.com/company/geeksforgeeks/")
    elif str(query) == "Exit":
        transmit('exit')
        icon.stop()


def systray_agent():
    while True:
        try:
            sio.connect('http://127.0.0.1:8081')
            break
        except Exception as e:
            print(e)
        time.sleep(1)
    icon = create_systray_app()
    icon.run()