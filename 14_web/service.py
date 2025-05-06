import asyncio
import concurrent.futures
import multiprocessing
import uuid
from time import sleep
from multiprocessing import Process
from threading import Thread

from aiohttp import web
from hident import identify_hashes, long_solve_hash

routes = web.RouteTableDef()

RESULTS = {}


@routes.get('/define/{hash}')  # ручка '/', метод - GET
async def get_algs(request):
    return web.Response(text=f'{{\"variants\": {[]}}}', headers={'Content-Type': 'application/json'})


@routes.get('/solve')  # ручка '/', метод - GET
async def solve(request):
    ...


def main():
    app = web.Application()
    app.add_routes(routes)  # регистрируем обработчики (ручки)
    web.run_app(app, host="0.0.0.0", port=8003)  # localhost:8003


if __name__ == '__main__':
    main()
