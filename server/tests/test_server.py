import pytest
import asyncio
from aiohttp import web
from server import init_app, VMManager, VirtualMachine

@pytest.fixture
async def client(aiohttp_client):
    app = await init_app()
    return await aiohttp_client(app)

async def test_health_check(client):
    resp = await client.get('/health')
    assert resp.status == 200
    text = await resp.text()
    assert text == "OK"

async def test_add_vm(client):
    vm_data = {
        "vm_id": "vm-test",
        "ram": 1024,
        "cpu": 2,
        "disks": [{"disk_id": "disk-1", "size": 500}]
    }
    resp = await client.post('/add_vm', json=vm_data)
    assert resp.status == 200
    text = await resp.text()
    assert text == "ВМ добавлена"

async def test_connect_vm(client):
    vm_data = {
        "vm_id": "vm-test",
        "ram": 1024,
        "cpu": 2,
        "disks": [{"disk_id": "disk-1", "size": 500}]
    }
    await client.post('/add_vm', json=vm_data)
    resp = await client.post('/connect_vm', json=vm_data)
    assert resp.status == 200
    text = await resp.text()
    assert text == "ВМ подключена"

async def test_authorize_vm(client):
    vm_data = {
        "vm_id": "vm-test",
        "ram": 1024,
        "cpu": 2,
        "disks": [{"disk_id": "disk-1", "size": 500}]
    }
    await client.post('/add_vm', json=vm_data)
    await client.post('/connect_vm', json=vm_data)
    resp = await client.post('/authorize_vm', json={"vm_id": "vm-test"})
    assert resp.status == 200
    text = await resp.text()
    assert text == "ВМ авторизована"

async def test_update_vm(client):
    vm_data = {
        "vm_id": "vm-test",
        "ram": 1024,
        "cpu": 2,
        "disks": [{"disk_id": "disk-1", "size": 500}]
    }
    await client.post('/add_vm', json=vm_data)
    await client.post('/connect_vm', json=vm_data)
    await client.post('/authorize_vm', json={"vm_id": "vm-test"})

    updated_vm_data = {
        "vm_id": "vm-test",
        "ram": 2048,
        "cpu": 4,
        "disks": [{"disk_id": "disk-1", "size": 1000}]
    }
    resp = await client.post('/update_vm', json=updated_vm_data)
    assert resp.status == 200
    text = await resp.text()
    assert text == "ВМ обновлена"

async def test_get_all_vms(client):
    vm_data = {
        "vm_id": "vm-test",
        "ram": 1024,
        "cpu": 2,
        "disks": [{"disk_id": "disk-1", "size": 500}]
    }
    await client.post('/add_vm', json=vm_data)
    resp = await client.get('/get_all_vms')
    assert resp.status == 200
    json_resp = await resp.json()
    assert len(json_resp) > 0

async def test_get_connected_vms(client):
    vm_data = {
        "vm_id": "vm-test",
        "ram": 1024,
        "cpu": 2,
        "disks": [{"disk_id": "disk-1", "size": 500}]
    }
    await client.post('/add_vm', json=vm_data)
    await client.post('/connect_vm', json=vm_data)
    resp = await client.get('/get_connected_vms')
    assert resp.status == 200
    json_resp = await resp.json()
    assert len(json_resp) > 0

async def test_get_authorized_vms(client):
    vm_data = {
        "vm_id": "vm-test",
        "ram": 1024,
        "cpu": 2,
        "disks": [{"disk_id": "disk-1", "size": 500}]
    }
    await client.post('/add_vm', json=vm_data)
    await client.post('/connect_vm', json=vm_data)
    await client.post('/authorize_vm', json={"vm_id": "vm-test"})
    resp = await client.get('/get_authorized_vms')
    assert resp.status == 200
    json_resp = await resp.json()
    assert len(json_resp) > 0

async def test_get_all_disks(client):
    vm_data = {
        "vm_id": "vm-test",
        "ram": 1024,
        "cpu": 2,
        "disks": [{"disk_id": "disk-1", "size": 500}]
    }
    await client.post('/add_vm', json=vm_data)
    resp = await client.get('/get_all_disks')
    assert resp.status == 200
    json_resp = await resp.json()
    assert len(json_resp) > 0

async def test_deauthorize_vm(client):
    vm_data = {
        "vm_id": "vm-test",
        "ram": 1024,
        "cpu": 2,
        "disks": [{"disk_id": "disk-1", "size": 500}]
    }
    await client.post('/add_vm', json=vm_data)
    await client.post('/connect_vm', json=vm_data)
    await client.post('/authorize_vm', json={"vm_id": "vm-test"})
    resp = await client.post('/deauthorize_vm', json={"vm_id": "vm-test"})
    assert resp.status == 200
    text = await resp.text()
    assert text == "ВМ деавторизована"
