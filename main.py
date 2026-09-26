# Resume Parser API using FastAPI and SpaCy


from http import HTTPStatus
from fastapi import FastAPI
from api.routes.parser import router as parser_router

app = FastAPI()



@app.get("/health")
# status as HTTPStatus 200 as well use try and exception block
def health_check():
    try:
        return {
            "status": "Healthy",
            "status_code": HTTPStatus.OK
        }
    except Exception as e:
        return {
            "status": "Unhealthy",
            "status_code": HTTPStatus.SERVICE_UNAVAILABLE
        }

#include router
app.include_router(parser_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)




