from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/update-coordinates")
async def update_coordinates(request: Request):
    data = await request.body()
    data = data.decode("utf-8")
    data = data.split("&")
    data = [d.split("=") for d in data]
    data = {d[0]: d[1] for d in data}
    index = data["index"]
    x = data["x"]
    y = data["y"]

    df = pd.read_csv("coordinates.csv")

    # Replace the data in the row index with the new x,y data
    df.iloc[int(index)] = [x, y]
    df.to_csv("coordinates.csv", index=False)
    return {"message": "Coordinates updated successfully"}

@app.get("/coordinates")
async def get_coordinates():
    df = pd.read_csv("coordinates.csv")
    return df.to_dict(orient="records")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='localhost', port=8000)