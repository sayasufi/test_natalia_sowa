import asyncio
import aiohttp
import logging
from typing import List, Dict, Any

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Список виртуальных машин для тестирования
VIRTUAL_MACHINES = [
    {"vm_id": "vm-1", "ram": 1024, "cpu": 2, "disks": [{"disk_id": "disk-1", "size": 500}]},
    {"vm_id": "vm-2", "ram": 2048, "cpu": 4, "disks": [{"disk_id": "disk-2", "size": 1000}]},
    {"vm_id": "vm-3", "ram": 4096, "cpu": 4, "disks": [{"disk_id": "disk-3", "size": 2000}]},
    {"vm_id": "vm-4", "ram": 8192, "cpu": 8, "disks": [{"disk_id": "disk-4", "size": 4000}]},
    {"vm_id": "vm-5", "ram": 1024, "cpu": 1, "disks": [{"disk_id": "disk-5", "size": 250}]},
    {"vm_id": "vm-6", "ram": 512, "cpu": 1, "disks": [{"disk_id": "disk-6", "size": 100}]},
    {"vm_id": "vm-7", "ram": 16384, "cpu": 16, "disks": [{"disk_id": "disk-7", "size": 8000}]},
    {"vm_id": "vm-8", "ram": 32768, "cpu": 32, "disks": [{"disk_id": "disk-8", "size": 16000}]},
    {"vm_id": "vm-9", "ram": 4096, "cpu": 2, "disks": [{"disk_id": "disk-9", "size": 500}]},
    {"vm_id": "vm-10", "ram": 8192, "cpu": 4, "disks": [{"disk_id": "disk-10", "size": 1000}]}
]

async def add_vm(session: aiohttp.ClientSession, vm: Dict[str, Any]):
    """Добавление виртуальной машины"""
    try:
        async with session.post('http://server:8080/add_vm', json=vm) as response:
            response_text = await response.text()
            logger.info(f"Ответ на добавление ВМ {vm['vm_id']}: {response_text}")
    except Exception as e:
        logger.error(f"Ошибка при добавлении ВМ {vm['vm_id']}: {e}")

async def connect_vm(session: aiohttp.ClientSession, vm: Dict[str, Any]):
    """Подключение виртуальной машины"""
    try:
        async with session.post('http://server:8080/connect_vm', json=vm) as response:
            response_text = await response.text()
            logger.info(f"Ответ на подключение ВМ {vm['vm_id']}: {response_text}")
    except Exception as e:
        logger.error(f"Ошибка при подключении ВМ {vm['vm_id']}: {e}")

async def authorize_vm(session: aiohttp.ClientSession, vm_id: str):
    """Авторизация виртуальной машины"""
    try:
        async with session.post('http://server:8080/authorize_vm', json={"vm_id": vm_id}) as response:
            response_text = await response.text()
            logger.info(f"Ответ на авторизацию ВМ {vm_id}: {response_text}")
    except Exception as e:
        logger.error(f"Ошибка при авторизации ВМ {vm_id}: {e}")

async def deauthorize_vm(session: aiohttp.ClientSession, vm_id: str):
    """Деавторизация виртуальной машины"""
    try:
        async with session.post('http://server:8080/deauthorize_vm', json={"vm_id": vm_id}) as response:
            response_text = await response.text()
            logger.info(f"Ответ на деавторизацию ВМ {vm_id}: {response_text}")
    except Exception as e:
        logger.error(f"Ошибка при деавторизации ВМ {vm_id}: {e}")

async def update_vm(session: aiohttp.ClientSession, vm: Dict[str, Any]):
    """Обновление данных виртуальной машины"""
    try:
        async with session.post('http://server:8080/update_vm', json=vm) as response:
            response_text = await response.text()
            logger.info(f"Ответ на обновление ВМ {vm['vm_id']}: {response_text}")
    except Exception as e:
        logger.error(f"Ошибка при обновлении ВМ {vm['vm_id']}: {e}")

async def get_all_vms(session: aiohttp.ClientSession):
    """Получение списка всех виртуальных машин"""
    try:
        async with session.get('http://server:8080/get_all_vms') as response:
            json_resp = await response.json()
            logger.info(f"Список всех ВМ: {json_resp}")
    except Exception as e:
        logger.error(f"Ошибка при получении списка всех ВМ: {e}")

async def get_connected_vms(session: aiohttp.ClientSession):
    """Получение списка подключенных виртуальных машин"""
    try:
        async with session.get('http://server:8080/get_connected_vms') as response:
            json_resp = await response.json()
            logger.info(f"Список подключенных ВМ: {json_resp}")
    except Exception as e:
        logger.error(f"Ошибка при получении списка подключенных ВМ: {e}")

async def get_authorized_vms(session: aiohttp.ClientSession):
    """Получение списка авторизованных виртуальных машин"""
    try:
        async with session.get('http://server:8080/get_authorized_vms') as response:
            json_resp = await response.json()
            logger.info(f"Список авторизованных ВМ: {json_resp}")
    except Exception as e:
        logger.error(f"Ошибка при получении списка авторизованных ВМ: {e}")

async def get_all_disks(session: aiohttp.ClientSession):
    """Получение списка всех жестких дисков"""
    try:
        async with session.get('http://server:8080/get_all_disks') as response:
            json_resp = await response.json()
            logger.info(f"Список всех дисков: {json_resp}")
    except Exception as e:
        logger.error(f"Ошибка при получении списка всех дисков: {e}")

async def main():
    """Основная функция для запуска клиентских задач"""
    async with aiohttp.ClientSession() as session:
        for vm in VIRTUAL_MACHINES:
            await add_vm(session, vm)
            await connect_vm(session, vm)
            await authorize_vm(session, vm['vm_id'])
            await update_vm(session, {**vm, "ram": vm["ram"] * 2, "cpu": vm["cpu"] * 2, "disks": [{"disk_id": vm["disks"][0]["disk_id"], "size": vm["disks"][0]["size"] * 2}]})
            await deauthorize_vm(session, vm['vm_id'])

        await get_all_vms(session)
        await get_connected_vms(session)
        await get_authorized_vms(session)
        await get_all_disks(session)

if __name__ == '__main__':
    logger.info("Запуск клиента")
    asyncio.run(main())
