"""Local MCP SDK client for the official Google Colab server.

Keeps one stdio session alive. Requests/results use a private local directory;
the relay exposes no HTTP service and uses only tools advertised by the server.
"""
from pathlib import Path
import asyncio
from datetime import timedelta
import json
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'tmp/colab_mcp'
STATE.mkdir(parents=True,exist_ok=True)

def write(name,obj):
    path=STATE/name
    temp=path.with_suffix('.tmp')
    temp.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
    temp.replace(path)

async def run():
    server=ROOT/'.tools/colab-mcp/.venv/Scripts/python.exe'
    params=StdioServerParameters(command=str(server),args=['-X','utf8',str(ROOT/'scripts/start_colab_mcp.py')])
    write('state.json',{'status':'starting','pid':os.getpid()})
    with (STATE/'server_stderr.log').open('a',encoding='utf-8') as log:
        async with stdio_client(params,errlog=log) as (read,send):
            async with ClientSession(read,send,read_timeout_seconds=timedelta(seconds=180)) as session:
                await session.initialize()
                tools=await session.list_tools()
                write('tools.json',tools.model_dump(mode='json'))
                print('Official MCP initialized:',[t.name for t in tools.tools],flush=True)
                write('state.json',{'status':'awaiting_browser_connection','pid':os.getpid()})
                # Official server tool opens the Colab connection page.
                result=await session.call_tool('open_colab_browser_connection',{})
                write('connection.json',result.model_dump(mode='json'))
                tools=await session.list_tools()
                write('tools.json',tools.model_dump(mode='json'))
                write('state.json',{'status':'ready','pid':os.getpid(),'tools':[t.name for t in tools.tools]})
                print('Connection result:',result.model_dump(mode='json'),flush=True)
                print('Available tools:',[t.name for t in tools.tools],flush=True)
                while not (STATE/'stop').exists():
                    for req in sorted(STATE.glob('request_*.json')):
                        out=STATE/req.name.replace('request_','result_')
                        if out.exists(): continue
                        payload=json.loads(req.read_text(encoding='utf-8'))
                        try:
                            if payload['name']=='list_tools':
                                result=await session.list_tools()
                                write('tools.json',result.model_dump(mode='json'))
                            else:
                                available=await session.list_tools()
                                assert payload['name'] in {t.name for t in available.tools}
                                result=await session.call_tool(payload['name'],payload.get('arguments',{}))
                            write(out.name,result.model_dump(mode='json'))
                        except Exception as e:
                            write(out.name,{'isError':True,'error':repr(e)})
                    await asyncio.sleep(0.25)
    write('state.json',{'status':'stopped','pid':os.getpid()})

if __name__=='__main__':
    try:
        asyncio.run(run())
    except Exception as error:
        write('state.json',{'status':'failed','error':repr(error)})
        raise
