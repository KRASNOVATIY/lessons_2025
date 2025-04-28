import asyncio

from aiohttp import web

routes = web.RouteTableDef()


@routes.get('/{name}')
async def default(request):
    await asyncio.sleep(1)
    return web.Response(
        text=f'{{\"data\": {int(request.match_info["name"]) * 1024}}}',
        headers={'Content-Type': 'application/json'}
    )


app = web.Application()
app.add_routes(routes)
web.run_app(app, host="0.0.0.0", port=8003)