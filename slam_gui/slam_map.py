# Create a sample FastAPI web application

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from fastapi.responses import FileResponse
from fastapi import HTTPException

import uvicorn
import subprocess
import threading
import time
from PIL import Image
import glob
import os

def run_script(path):
    subprocess.check_output(["bash", path])

app = FastAPI()
# Add the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Get route for the index page
@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return FileResponse("index.html")

@app.get("/update_map")
async def update():
    print("Update")
    update_script = os.path.abspath('./save_map.sh')
    os.chdir('/home/projects/ros1_ws')
    subprocess.call(['bash', update_script])

    os.chdir('/home/projects/ECE_MAE_148_Final_Project/slam_gui')

    tif_file = glob.glob('./static/*.tif')[0]

    with Image.open(tif_file) as img:
        # Convert the image to PNG and save it
        img.save('map.png', 'PNG')


    return {"message": "Update"}

if __name__ == "__main__":
    print('Starting server and initializing SLAM with ROS1')
    t1 = threading.Thread(target=run_script, args=('init_terminal1.sh',))
    t1.setDaemon(True)
    t1.start()
    time.sleep(5)
    print('Starting ROS Bridge')
    t2 = threading.Thread(target=run_script, args=('init_terminal2.sh',))
    t2.setDaemon(True)
    t2.start()
    time.sleep(5)
    print('Starting ROS2')
    t3 = threading.Thread(target=run_script, args=('init_terminal3.sh',))
    t3.setDaemon(True)
    t3.start()
    
    try:
        uvicorn.run(app, host='localhost', port=8000)
    except KeyboardInterrupt:
        print('Stopping server')
        # Join threads
        t1.join()
        t2.join()
        t3.join()