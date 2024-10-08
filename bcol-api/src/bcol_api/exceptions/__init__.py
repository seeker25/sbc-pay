# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Application Specific Exceptions, to manage the business errors.

@log_error - a decorator to automatically log the exception to the logger provided

BusinessException - error, status_code - Business rules error
error - a description of the error {code / description: classname / full text}
status_code - where possible use HTTP Error Codes
"""
import json
from http import HTTPStatus
from typing import Dict

from flask import Response

from bcol_api.utils.errors import Error


def convert_to_response(body: Dict, status: int = HTTPStatus.BAD_REQUEST):
    """Convert json error to problem response."""
    return Response(response=json.dumps(body), mimetype="application/problem+json", status=status)


def error_to_response(error: Error, invalid_params=None):
    """Convert Error enum to response."""
    return convert_to_response(
        body={
            "type": error.name,
            "title": error.title,
            "detail": error.details,
            "invalidParams": invalid_params,
        },
        status=error.status,
    )


class BusinessException(Exception):  # noqa
    """Exception that adds error code and error name, that can be used for i18n support."""

    def __init__(self, error: Error, *args, **kwargs):
        """Return a valid BusinessException."""
        super().__init__(*args, **kwargs)
        self.message = error.title
        self.details = error.details
        self.code = error.name
        self.status = error.status

    def as_problem_json(self):
        """Return problem+json of error message."""
        return {"type": self.code, "title": self.message, "detail": self.details}

    def response(self):
        """Response attributes."""
        return convert_to_response(body=self.as_problem_json(), status=self.status)


class PaymentException(Exception):  # noqa
    """Exception that adds error code and error name, that can be used for i18n support."""

    def __init__(self, code: str, message: str, *args, **kwargs):
        """Return a valid BusinessException."""
        super().__init__(*args, **kwargs)
        self.status = HTTPStatus.BAD_REQUEST
        self.message = message
        self.details = message
        self.code = str(code)

    def as_problem_json(self):
        """Return problem+json of error message."""
        return {"type": self.code, "title": self.message, "detail": self.details}

    def response(self):
        """Response attributes."""
        return convert_to_response(body=self.as_problem_json(), status=self.status)
