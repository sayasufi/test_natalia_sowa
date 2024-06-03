import json
import logging
import os
from typing import List, Dict, Any

import asyncpg
from aiohttp import web

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/yourdatabase")


class VirtualMachine:
    def __init__(self, vm_id: str, ram: int, cpu: int, disks: List[Dict[str, Any]]):
        self.vm_id = vm_id
        self.ram = ram
        self.cpu = cpu
        self.disks = disks


class VMManager:
    def __init__(self):
        self.connected_vms: Dict[str, VirtualMachine] = {}
        self.authorized_vms: set = set()
        self.all_vms: set = set()

    async def init_db(self):
        """Инициализация базы данных"""
        logger.info("Подключение к базе данных")
        try:
            self.conn = await asyncpg.connect(DATABASE_URL)
            await self.conn.execute("""
                CREATE TABLE IF NOT EXISTS virtual_machines (
                    id SERIAL PRIMARY KEY,
                    vm_id VARCHAR(50) UNIQUE,
                    ram INTEGER,
                    cpu INTEGER
                );
                CREATE TABLE IF NOT EXISTS disks (
                    id SERIAL PRIMARY KEY,
                    disk_id VARCHAR(50) UNIQUE,
                    size INTEGER,
                    vm_id INTEGER REFERENCES virtual_machines(id)
                );
            """)
            logger.info("База данных успешно инициализирована")
        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")

    async def add_vm(self, vm: VirtualMachine):
        """Добавление виртуальной машины в базу данных"""
        try:
            await self.conn.execute('''
                INSERT INTO virtual_machines (vm_id, ram, cpu) VALUES ($1, $2, $3)
                ON CONFLICT (vm_id) DO NOTHING;
            ''', vm.vm_id, vm.ram, vm.cpu)
            for disk in vm.disks:
                await self.conn.execute('''
                    INSERT INTO disks (disk_id, size, vm_id) VALUES ($1, $2, (SELECT id FROM virtual_machines WHERE vm_id=$3))
                    ON CONFLICT (disk_id) DO NOTHING;
                ''', disk['disk_id'], disk['size'], vm.vm_id)
            logger.info(f"Добавлена ВМ {vm.vm_id} с RAM: {vm.ram}, CPU: {vm.cpu}, дисками: {vm.disks}")
        except Exception as e:
            logger.error(f"Ошибка добавления ВМ: {e}")

    async def update_vm(self, vm: VirtualMachine):
        """Обновление данных авторизованной виртуальной машины"""
        try:
            if vm.vm_id not in self.authorized_vms:
                raise Exception("ВМ не авторизована")

            await self.conn.execute('''
                UPDATE virtual_machines SET ram = $1, cpu = $2 WHERE vm_id = $3;
            ''', vm.ram, vm.cpu, vm.vm_id)

            for disk in vm.disks:
                await self.conn.execute('''
                    INSERT INTO disks (disk_id, size, vm_id) VALUES ($1, $2, (SELECT id FROM virtual_machines WHERE vm_id=$3))
                    ON CONFLICT (disk_id) DO UPDATE SET size = $2;
                ''', disk['disk_id'], disk['size'], vm.vm_id)

            logger.info(f"Обновлена ВМ {vm.vm_id} с RAM: {vm.ram}, CPU: {vm.cpu}, дисками: {vm.disks}")
        except Exception as e:
            logger.error(f"Ошибка обновления ВМ: {e}")

    async def get_all_vms(self) -> List[Dict[str, Any]]:
        """Получение списка всех виртуальных машин"""
        try:
            vms = await self.conn.fetch('''
                SELECT vm.*, COALESCE(json_agg(disk.*) FILTER (WHERE disk.id IS NOT NULL), '[]') AS disks
                FROM virtual_machines vm
                LEFT JOIN disks disk ON vm.id = disk.vm_id
                GROUP BY vm.id
            ''')
            logger.info("Получен список всех ВМ")
            return [dict(vm) for vm in vms]
        except Exception as e:
            logger.error(f"Ошибка получения списка всех ВМ: {e}")
            return []

    async def get_connected_vms(self) -> List[Dict[str, Any]]:
        """Получение списка подключенных виртуальных машин"""
        try:
            vms = []
            for vm in self.connected_vms.values():
                disks = await self.conn.fetch('''
                    SELECT * FROM disks WHERE vm_id = (SELECT id FROM virtual_machines WHERE vm_id = $1)
                ''', vm.vm_id)
                vm_info = {
                    'vm_id': vm.vm_id,
                    'ram': vm.ram,
                    'cpu': vm.cpu,
                    'disks': [dict(disk) for disk in disks]
                }
                vms.append(vm_info)
            logger.info("Получен список подключенных ВМ")
            return vms
        except Exception as e:
            logger.error(f"Ошибка получения списка подключенных ВМ: {e}")
            return []

    async def get_authorized_vms(self) -> List[Dict[str, Any]]:
        """Получение списка авторизованных виртуальных машин"""
        try:
            vms = []
            for vm in self.connected_vms.values():
                if vm.vm_id in self.authorized_vms:
                    disks = await self.conn.fetch('''
                        SELECT * FROM disks WHERE vm_id = (SELECT id FROM virtual_machines WHERE vm_id = $1)
                    ''', vm.vm_id)
                    vm_info = {
                        'vm_id': vm.vm_id,
                        'ram': vm.ram,
                        'cpu': vm.cpu,
                        'disks': [dict(disk) for disk in disks]
                    }
                    vms.append(vm_info)
            logger.info("Получен список авторизованных ВМ")
            return vms
        except Exception as e:
            logger.error(f"Ошибка получения списка авторизованных ВМ: {e}")
            return []

    async def get_all_disks(self) -> List[asyncpg.Record]:
        """Получение списка всех жестких дисков"""
        try:
            disks = await self.conn.fetch('''
                SELECT disks.*, virtual_machines.vm_id FROM disks
                JOIN virtual_machines ON disks.vm_id = virtual_machines.id
            ''')
            logger.info("Получен список всех дисков")
            return disks
        except Exception as e:
            logger.error(f"Ошибка получения списка всех дисков: {e}")
            return []

    async def connect_vm(self, vm: VirtualMachine):
        """Подключение виртуальной машины"""
        self.connected_vms[vm.vm_id] = vm
        self.all_vms.add(vm.vm_id)
        logger.info(f"ВМ {vm.vm_id} подключена")

    async def authorize_vm(self, vm_id: str):
        """Авторизация виртуальной машины"""
        if vm_id in self.connected_vms:
            self.authorized_vms.add(vm_id)
            logger.info(f"ВМ {vm_id} авторизована")
        else:
            logger.error(f"ВМ {vm_id} не найдена среди подключенных")

    async def deauthorize_vm(self, vm_id: str):
        """Деавторизация виртуальной машины"""
        self.authorized_vms.discard(vm_id)
        logger.info(f"ВМ {vm_id} деавторизована")


async def handle_add_vm(request: web.Request) -> web.Response:
    """Обработчик для добавления виртуальной машины"""
    data = await request.json()
    vm = VirtualMachine(data['vm_id'], data['ram'], data['cpu'], data['disks'])
    await request.app['manager'].add_vm(vm)
    return web.Response(text="ВМ добавлена")


async def handle_update_vm(request: web.Request) -> web.Response:
    """Обработчик для обновления данных виртуальной машины"""
    data = await request.json()
    vm = VirtualMachine(data['vm_id'], data['ram'], data['cpu'], data['disks'])
    await request.app['manager'].update_vm(vm)
    return web.Response(text="ВМ обновлена")


async def handle_get_all_vms(request: web.Request) -> web.Response:
    """Обработчик для получения списка всех виртуальных машин"""
    vms = await request.app['manager'].get_all_vms()
    # Преобразование строковых представлений дисков в JSON объекты
    for vm in vms:
        if isinstance(vm['disks'], str):
            vm['disks'] = json.loads(vm['disks'])
    return web.json_response(vms)


async def handle_get_connected_vms(request: web.Request) -> web.Response:
    """Обработчик для получения списка подключенных виртуальных машин"""
    vms = await request.app['manager'].get_connected_vms()
    return web.json_response(vms)


async def handle_get_authorized_vms(request: web.Request) -> web.Response:
    """Обработчик для получения списка авторизованных виртуальных машин"""
    vms = await request.app['manager'].get_authorized_vms()
    return web.json_response(vms)


async def handle_get_all_disks(request: web.Request) -> web.Response:
    """Обработчик для получения списка всех дисков"""
    disks = await request.app['manager'].get_all_disks()
    return web.json_response([dict(disk) for disk in disks])


async def handle_connect_vm(request: web.Request) -> web.Response:
    """Обработчик для подключения виртуальной машины"""
    data = await request.json()
    vm = VirtualMachine(data['vm_id'], data['ram'], data['cpu'], data['disks'])
    await request.app['manager'].connect_vm(vm)
    return web.Response(text="ВМ подключена")


async def handle_authorize_vm(request: web.Request) -> web.Response:
    """Обработчик для авторизации виртуальной машины"""
    data = await request.json()
    vm_id = data['vm_id']
    await request.app['manager'].authorize_vm(vm_id)
    return web.Response(text="ВМ авторизована")


async def handle_deauthorize_vm(request: web.Request) -> web.Response:
    """Обработчик для деавторизации виртуальной машины"""
    data = await request.json()
    vm_id = data['vm_id']
    await request.app['manager'].deauthorize_vm(vm_id)
    return web.Response(text="ВМ деавторизована")


async def handle_health_check(request: web.Request) -> web.Response:
    """Обработчик для проверки состояния сервера"""
    return web.Response(text="OK")


async def init_app() -> web.Application:
    """Инициализация приложения"""
    app = web.Application()
    manager = VMManager()
    await manager.init_db()
    app['manager'] = manager

    app.add_routes([
        web.post('/add_vm', handle_add_vm),
        web.post('/update_vm', handle_update_vm),
        web.post('/connect_vm', handle_connect_vm),
        web.post('/authorize_vm', handle_authorize_vm),
        web.post('/deauthorize_vm', handle_deauthorize_vm),
        web.get('/get_all_vms', handle_get_all_vms),
        web.get('/get_connected_vms', handle_get_connected_vms),
        web.get('/get_authorized_vms', handle_get_authorized_vms),
        web.get('/get_all_disks', handle_get_all_disks),
        web.get('/health', handle_health_check)
    ])

    return app


if __name__ == '__main__':
    logger.info("Запуск сервера")
    web.run_app(init_app(), port=8080)
