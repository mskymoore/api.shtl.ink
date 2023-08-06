
from starlette.responses import JSONResponse
from fastapi import status

def json_response_not_found(short_code):
    return JSONResponse(
        {"message": f"{short_code} not found"}, status_code=status.HTTP_404_NOT_FOUND
    )


def json_response_in_use(short_code):
    return JSONResponse(
        {"message": f"{short_code} already in use"},
        status_code=status.HTTP_409_CONFLICT,
    )


def json_response_not_owned(short_code):
    return JSONResponse(
        {"message": f"{short_code} not owned by you"},
        status_code=status.HTTP_403_FORBIDDEN,
    )


def json_response_created(url_record):
    return JSONResponse(url_record.to_dict(), status_code=status.HTTP_201_CREATED)


def json_response_already_reported(url_record):
    return JSONResponse(
        url_record.to_dict(), status_code=status.HTTP_208_ALREADY_REPORTED
    )


def json_response_deleted(short_code, url):
    return JSONResponse(
        {"message": f"deleted record {short_code} -> {url}"},
        status_code=status.HTTP_200_OK,
    )


def json_response_record(url_record):
    return JSONResponse(url_record.to_dict(), status_code=status.HTTP_200_OK)


def json_response_missing(something):
    return JSONResponse(
        {"message": f"you must supply {something}"},
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
    )


def json_response_failure():
    return JSONResponse(
        {"message": "something went wrong..."},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )