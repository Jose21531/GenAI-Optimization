"""Verify every target remains intact under user-only Qwen chat formatting."""
from pathlib import Path
import json
import zipfile
from transformers import AutoTokenizer

root=Path(__file__).resolve().parents[1]
tok=AutoTokenizer.from_pretrained('Qwen/Qwen2.5-1.5B-Instruct',revision='989aa7980e4cf806f80c7fef2b1adb7bc71aa306')
with zipfile.ZipFile(root/'or_sft_dataset_v1_2_final.zip') as archive:
    rows=[json.loads(x) for x in archive.read('or_sft_1050_messages_v1_2.jsonl').decode().splitlines()]
lengths=[]
for row in rows:
    messages=row['messages'][1:]
    prefix=tok.apply_chat_template(messages[:1],tokenize=True,add_generation_prompt=True)
    full=tok.apply_chat_template(messages,tokenize=True)
    assert full[:len(prefix)]==prefix,row['id']
    assert full[-2:]==[tok.eos_token_id,198],row['id']
    target=tok.decode(full[len(prefix):-2])
    assert target==messages[-1]['content'],row['id']
    lengths.append(len(full))
print(json.dumps({'n':len(rows),'max_tokens':max(lengths),'truncated_1024':sum(x>1024 for x in lengths),
                  'strict_prefix_ok':True,'exact_target_and_eos_ok':True}))
