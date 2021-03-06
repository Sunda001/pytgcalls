import json
from aiohttp.web_request import BaseRequest
from aiohttp import web
from pyrogram.raw.functions.phone import JoinGroupCall
from pyrogram.raw.types import Updates, DataJSON
from pyrogram.errors import ChannelPrivate


class JoinVoiceCall:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    async def _join_voice_call(self, request: BaseRequest):
        params = await request.json()
        if isinstance(params, str):
            params = json.loads(params)
        request_call = {
            'ufrag': params['ufrag'],
            'pwd': params['pwd'],
            'fingerprints': [{
                'hash': params['hash'],
                'setup': params['setup'],
                'fingerprint': params['fingerprint']
            }],
            'ssrc': params['source']
        }
        chat_call = None
        # noinspection PyBroadException
        try:
            chat_call = (await self.pytgcalls._load_full_chat(params['chat_id'])).full_chat.call
        except Exception:
            pass
        if chat_call is not None:
            try:
                result: Updates = await self.pytgcalls._app.send(
                    JoinGroupCall(
                        call=chat_call,
                        params=DataJSON(data=json.dumps(request_call)),
                        muted=False
                    )
                )
                transport = json.loads(result.updates[0].call.params.data)['transport']
                result_json = {
                    'transport': {
                        'ufrag': transport['ufrag'],
                        'pwd': transport['pwd'],
                        'fingerprints': transport['fingerprints'],
                        'candidates': transport['candidates'],
                    }
                }
            except Exception as e:
                if 'GROUPCALL_FORBIDDEN' not in str(e):
                    print(e)
                result_json = {
                    'transport': None
                }
        else:
            result_json = {
                'transport': None
            }
        return web.json_response(result_json)
