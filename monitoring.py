import logging
from dataclasses import dataclass

import httpx
import telegram.ext


@dataclass
class MonitoringParams:
    host: str
    port: int
    key: str


async def do_mon_request(context: telegram.ext.CallbackContext):
    params: MonitoringParams = context.job.data
    try:
        resp = httpx.post(f'http://{params.host}:{params.port}/imalive', json={'token': params.key})
        if not 200 <= resp.status_code < 300:
            logging.warning(f'monitoring replied with non-2XX code: {resp.status_code=}')
            return

        data = resp.json()
        code = data.get('code', 200)
        if code != 200:
            logging.warning(f'response from monitoring contains and error: {data.get("message", "no error")}')

        logging.debug('monitoring request successful')
    except Exception as e:
        logging.warning('failed to make request to monitoring', exc_info=e)
