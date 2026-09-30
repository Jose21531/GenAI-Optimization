"""Submit one request to the already connected local MCP SDK session."""
from pathlib import Path
import argparse, json, time, uuid
ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'tmp/colab_mcp'
parser=argparse.ArgumentParser()
parser.add_argument('name')
parser.add_argument('--args-file',type=Path)
parser.add_argument('--wait',type=float,default=8)
parser.add_argument('--compact',action='store_true')
args=parser.parse_args()
ident=str(time.time_ns())+'_'+uuid.uuid4().hex[:6]
req=STATE/f'request_{ident}.json'
payload={'name':args.name,'arguments':json.loads(args.args_file.read_text(encoding='utf-8-sig')) if args.args_file else {}}
tmp=req.with_suffix('.tmp');tmp.write_text(json.dumps(payload,ensure_ascii=False),encoding='utf-8');tmp.replace(req)
result=STATE/f'result_{ident}.json'
start=time.monotonic()
while time.monotonic()-start<args.wait:
    if result.exists():
        value=json.loads(result.read_text(encoding='utf-8'))
        if args.compact:
            value=value.get('structuredContent',value)
            if 'outputs' in value:
                for output in value['outputs']:
                    if output.get('output_type')=='stream':
                        print(''.join(output.get('text',[])))
                    else:
                        print(json.dumps(output,ensure_ascii=False))
            else:
                print(json.dumps(value,ensure_ascii=False))
        else:
            print(json.dumps(value,ensure_ascii=False,indent=2))
        break
    time.sleep(0.2)
else:
    print(json.dumps({'pending_result':str(result)}))
