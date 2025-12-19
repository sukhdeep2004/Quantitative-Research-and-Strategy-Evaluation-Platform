from fastapi import FastAPI
from api.routes import router

app = FastAPI(title="Quant Research Platform")
@app.get("/")
def health_check():
    return {"status": "Quant platform running"}
app.include_router(router)

