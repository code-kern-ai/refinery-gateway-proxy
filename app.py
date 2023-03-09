import os
from fastapi import FastAPI, responses, status, Request
from typing import Optional
import requests

app = FastAPI()

BASE_URI = os.getenv("GATEWAY")
KRATOS_URI = os.getenv("KRATOS")
CONFIG_URI = os.getenv("CONFIG")


class ErrorCodes:
    UNRECOGNIZED_USER = "UNRECOGNIZED_USER"
    FORBIDDEN_USER = "FORBIDDEN_USER"
    PROJECT_NOT_FOUND = "PROJECT_NOT_FOUND"


def get_user_id_from_request(request):
    session_token = request.headers["identifier"]
    url = f"{KRATOS_URI}/sessions/whoami"
    resp = requests.get(url, headers={"Authorization": f"Bearer {session_token}"})
    whoami_dict = resp.json()
    user_id = whoami_dict["identity"]["id"]
    return user_id


def handle_response(response):
    if response.status_code == status.HTTP_200_OK:
        return responses.JSONResponse(
            status_code=status.HTTP_200_OK, content=response.json()
        )
    elif response.status_code == status.HTTP_404_NOT_FOUND:
        return responses.JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error_code": ErrorCodes.PROJECT_NOT_FOUND},
        )
    elif response.status_code == status.HTTP_403_FORBIDDEN:
        return responses.JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error_code": ErrorCodes.FORBIDDEN_USER},
        )


@app.get("/project/{project_id}/export")
def get_export(request: Request, project_id: str, num_samples: Optional[int] = None):
    try:
        user_id = get_user_id_from_request(request)
    except KeyError:
        return responses.JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error_code": ErrorCodes.UNRECOGNIZED_USER},
        )
    url = f"{BASE_URI}/project/{project_id}/export"
    resp = requests.get(url, params={"user_id": user_id, "num_samples": num_samples})
    return handle_response(resp)


@app.get("/project/{project_id}/lookup_list/{lookup_list_id}")
def get_lookup_list(request: Request, project_id: str, lookup_list_id: str):
    try:
        user_id = get_user_id_from_request(request)
    except KeyError:
        return responses.JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error_code": ErrorCodes.UNRECOGNIZED_USER},
        )
    url = f"{BASE_URI}/project/{project_id}/knowledge_base/{lookup_list_id}"
    resp = requests.get(url, params={"user_id": user_id})
    return handle_response(resp)


@app.post("/project/{project_id}/import_file")
async def post_import_file(request: Request, project_id: str):
    try:
        user_id = get_user_id_from_request(request)
    except KeyError:
        return responses.JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error_code": ErrorCodes.UNRECOGNIZED_USER},
        )
    request_body = await request.json()
    url = f"{BASE_URI}/project/{project_id}/import_file"
    resp = requests.post(
        url,
        json={
            "user_id": user_id,
            "file_name": request_body["file_name"],
            "file_type": request_body["file_type"],
            "file_import_options": request_body.get("file_import_options"),
        },
    )
    return handle_response(resp)


@app.post("/project/{project_id}/import_json")
async def post_import_json(request: Request, project_id: str):
    try:
        user_id = get_user_id_from_request(request)
    except KeyError:
        return responses.JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error_code": ErrorCodes.UNRECOGNIZED_USER},
        )
    request_body = await request.json()
    url = f"{BASE_URI}/project/{project_id}/import_json"
    resp = requests.post(
        url,
        json={
            "user_id": user_id,
            "records": request_body["records"],
            "request_uuid": request_body["request_uuid"],
            "is_last": request_body["is_last"],
        },
    )
    return responses.JSONResponse(status_code=status.HTTP_200_OK, content=resp.json())


@app.post("/project/{project_id}/associations")
async def post_associations(request: Request, project_id: str):
    try:
        user_id = get_user_id_from_request(request)
    except KeyError:
        return responses.JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error_code": ErrorCodes.UNRECOGNIZED_USER},
        )
    request_body = await request.json()
    url = f"{BASE_URI}/project/{project_id}/associations"
    resp = requests.post(
        url,
        json={
            "user_id": user_id,
            "associations": request_body["associations"],
            "indices": request_body["indices"],
            "name": request_body["name"],
            "label_task_name": request_body["label_task_name"],
            "source_type": request_body["source_type"],
        },
    )
    return handle_response(resp)


@app.get("/project/{project_id}")
def get_details(request: Request, project_id: str):
    try:
        user_id = get_user_id_from_request(request)
    except KeyError:
        return responses.JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error_code": ErrorCodes.UNRECOGNIZED_USER},
        )
    url = f"{BASE_URI}/project/{project_id}"
    resp = requests.get(url, params={"user_id": user_id})
    return handle_response(resp)


@app.get("/project/{project_id}/import/base_config")
def get_base_config(request: Request, project_id: str):
    try:
        get_user_id_from_request(request)
    except KeyError:
        return responses.JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error_code": ErrorCodes.UNRECOGNIZED_USER},
        )
    url = f"{CONFIG_URI}/base_config"
    resp = requests.get(url)
    return handle_response(resp)


@app.get("/project/{project_id}/import/task/{task_id}")
def get_details(request: Request, project_id: str, task_id: str):
    try:
        user_id = get_user_id_from_request(request)
    except KeyError:
        return responses.JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": ErrorCodes.UNRECOGNIZED_USER},
        )
    url = f"{BASE_URI}/project/{project_id}/import/task/{task_id}"
    resp = requests.get(url, params={"user_id": user_id})
    return handle_response(resp)


@app.get("/healthcheck")
def healthcheck() -> responses.PlainTextResponse:
    return responses.PlainTextResponse("OK")
