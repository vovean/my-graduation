import asyncio
import logging
from dataclasses import dataclass

import httpx


@dataclass
class MonitoringParams:
    host: str
    port: int
    key: str


def run_monitoring(params: MonitoringParams):
    async def run_periodically():
        while True:
            do_mon_request(params)
            await asyncio.sleep(1)

    asyncio.create_task(run_periodically())


def do_mon_request(params: MonitoringParams):
    resp = httpx.post(f'http://{params.host}:{params.port}/imalive', json={'token': params.key})
    if not 200 <= resp.status_code < 300:
        logging.warning(f'failed to make request to monitoring: {resp.status_code=}')
        return

    data = resp.json()
    code = data.get('code', 200)
    if code != 200:
        logging.warning(f'response from monitoring contains and error: {data.get("message", "no error")}')

    logging.debug('monitoring request successful')
