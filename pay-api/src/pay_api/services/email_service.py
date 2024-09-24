# Copyright © 2024 Province of British Columbia
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

"""This manages all of the email notification service."""
import os
from typing import Dict
from decimal import Decimal

from attr import define
from flask import current_app
from jinja2 import Environment, FileSystemLoader
from pay_api.exceptions import ServiceUnavailableException
from pay_api.services.oauth_service import OAuthService
from pay_api.utils.enums import AuthHeaderType, ContentType
from pay_api.utils.serializable import Serializable
from pay_api.utils.user_context import user_context


@user_context
def send_email(recipients: list, subject: str, body: str, **kwargs):
    """Send the email notification."""
    # Note if we send HTML in the body, we aren't sending through GCNotify, ideally we'd like to send through GCNotify.
    token = kwargs['user'].bearer_token
    current_app.logger.info(f'>send_email to recipients: {recipients}')
    notify_url = current_app.config.get('NOTIFY_API_ENDPOINT') + 'notify/'

    success = False

    for recipient in recipients:
        notify_body = {
            'recipients': recipient,
            'content': {
                'subject': subject,
                'body': body
            }
        }

        try:
            notify_response = OAuthService.post(notify_url, token=token,
                                                auth_header_type=AuthHeaderType.BEARER,
                                                content_type=ContentType.JSON, data=notify_body)
            current_app.logger.info('<send_email notify_response')
            if notify_response:
                current_app.logger.info(f'Successfully sent email to {recipient}')
                success = True
        except ServiceUnavailableException as e:
            current_app.logger.error(f'Error sending email to {recipient}: {e}')

    return success


@define
class ShortNameRefundEmailContent(Serializable):
    """Short name refund email."""

    comment: str
    decline_reason: str
    refund_amount: Decimal
    short_name_id: int
    short_name: str
    status: str
    url: str

    def render_body(self) -> str:
        """Render the email body using the provided template."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root_dir = os.path.dirname(current_dir)
        templates_dir = os.path.join(project_root_dir, 'templates')
        env = Environment(loader=FileSystemLoader(templates_dir), autoescape=True)
        template = env.get_template('eft_refund_notification.html')
        return template.render(self.to_dict())


def _render_payment_reversed_template(params: Dict) -> str:
    """Render short name statement reverse payment template."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root_dir = os.path.dirname(current_dir)
    templates_dir = os.path.join(project_root_dir, 'templates')
    env = Environment(loader=FileSystemLoader(templates_dir), autoescape=True)
    template = env.get_template('eft_reverse_payment.html')

    statement_url = f"{current_app.config.get('AUTH_WEB_URL')}/account/{params['accountId']}/settings/statements"
    params['statementUrl'] = statement_url

    return template.render(params)
