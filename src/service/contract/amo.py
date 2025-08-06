import http
import requests
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum

from sharq_models import PassportData #type: ignore


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



PIPELINE_TYPES = {
    "FIRST_CREATE": "first_create",
    "LEAD_ACCEPTED": "lead_accepted",
    "LEAD_REJECTED": "lead_rejected",
    "GET_CONTRACT": "get_contract",
}





class AmoCRMConfig:
    def __init__(self, config_data: Dict[str, Any]):
        self.base_api = config_data.get("base_url")
        self.token = config_data.get("token")

        self.pipelines = {
            PIPELINE_TYPES["GET_CONTRACT"]: {
                "pipeline_id": config_data.get("get_contract_pipline_id"),
                "status_id": config_data.get("get_contract_status_id"),
            },
        }

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }


class AmoCRMException(Exception):
    pass



class AmoCRMService:
    def __init__(self, config: AmoCRMConfig):
        self.config = config
        self._contact_fields_cache: Optional[Dict[str, int]] = None
        self._lead_fields_cache: Optional[Dict[str, int]] = None

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Union[Dict, List]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.config.base_api}/{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.config.headers,
                params=params,
                json=json_data,
            )
            response.raise_for_status()

            if response.status_code == http.HTTPStatus.NO_CONTENT:
                return {}

            return response.json()

        except requests.exceptions.RequestException as e:
            self._handle_request_error(e, method, endpoint)

    def _handle_request_error(
        self, error: Exception, method: str, endpoint: str
    ) -> None:
        error_msg = f"API request failed for {method} {endpoint}: {error}"
        if hasattr(error, "response") and error.response is not None:
            error_msg += f" | Status: {error.response.status_code} | Response: {error.response.text}"

        logger.error(error_msg)
        raise AmoCRMException(error_msg)


    def update_lead_status(
        self, pipeline_id: int, status_id: int, lead_id: int
    ) -> Optional[Dict[str, Any]]:
        try:
            data = self._make_request(
                "PATCH",
                f"leads/{lead_id}",
                json_data={
                    "pipeline_id": int(pipeline_id),
                    "status_id": int(status_id),
                },
            )

            logger.info(f"Lead {lead_id} status updated successfully")
            return data

        except AmoCRMException as e:
            logger.error(f"Failed to update lead status: {e}")
            return None

    


def create_amocrm_service(config_data: Dict[str, Any]) -> AmoCRMService:
    config = AmoCRMConfig(config_data)
    return AmoCRMService(config)


def move_lead_to_get_contract_pipeline(
    lead_id: int, config_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    try:
        amo_service = create_amocrm_service(config_data)
        return amo_service.update_lead_status(
            pipeline_id=config_data.get("get_contract_pipline_id"),
            status_id=config_data.get("get_contract_status_id"),
            lead_id=lead_id,
        )
    except Exception as e:
        logger.error(f"Failed to move lead to get contract pipeline: {e}")
        return None
