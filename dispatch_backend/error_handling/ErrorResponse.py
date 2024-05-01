from rest_framework.response import Response
from rest_framework import status
from .error_type import *


class ErrorResponse(Response):

    def __init__(
            self,
            http_status: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_type: str = UNKNOWN_ERROR,
            message: str = "Unexpected error occurred"
    ):
        super().__init__(
            data={"error_type": error_type, "message": message},
            status=http_status
        )

    @staticmethod
    def from_exception(exception):
        return ErrorResponse(
            http_status=exception.status,
            error_type=exception.error_type,
            message=exception.message
        )
