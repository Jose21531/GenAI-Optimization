"""Live Colab demo: direct baseline and final QLoRA on the frozen Entrega 1 case.

Run only after the benchmark judge is complete, with Drive mounted and a T4.
This performs fresh inference; it never overwrites the historical baseline CSV.
"""
from pathlib import Path
import hashlib
import json
import time

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed

PACKAGE = Path('/content/drive/MyDrive/IA/entrega2_qlora')
PROJECT = Path('/content/drive/MyDrive/IA/qwen25_qlora_or_v2')
FINAL = PROJECT / 'final/user_only_run01'
assert torch.cuda.is_available(), 'La demostración requiere GPU'
assert json.loads((PROJECT / 'worker_judge.json').read_text())['status'] == 'completed', (
    'Esperar a que el juez libere la GPU antes de grabar la demostración.')
manifest = json.loads((FINAL / 'manifest.json').read_text())
completed = json.loads((FINAL / 'completed.json').read_text())
assert completed['manifest_sha256'] == hashlib.sha256((FINAL / 'manifest.json').read_bytes()).hexdigest()
assert manifest['training_messages'] == 'user_only' and len(manifest['train_ids']) == 1050
item = json.loads((PACKAGE / 'results/baseline/caso_entrega1_generation_only.jsonl')
                  .read_text(encoding='utf-8').strip())
assert item['id'] == 'diagnostic_oftalmo'
set_seed(42)

print('ENTRADA FIJADA EN ENTREGA 1', flush=True)
print(item['problem'], flush=True)
print('Cargando Qwen2.5-1.5B-Instruct FP16 y el adapter final...', flush=True)
tokenizer = AutoTokenizer.from_pretrained(manifest['model_id'], revision=manifest['revision'])
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
base = AutoModelForCausalLM.from_pretrained(
    manifest['model_id'], revision=manifest['revision'], torch_dtype=torch.float16,
    device_map={'': 0})
model = PeftModel.from_pretrained(base, FINAL / 'final_adapter', is_trainable=False)
model.eval()
messages = [{'role': 'user', 'content': item['problem']}]
prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(prompt, return_tensors='pt').to(model.device)


def generate():
    started = time.perf_counter()
    with torch.inference_mode():
        output = model.generate(**inputs, max_new_tokens=1200, do_sample=False,
                                pad_token_id=tokenizer.eos_token_id)
    new = output[0][inputs['input_ids'].shape[1]:]
    return {'candidate': tokenizer.decode(new, skip_special_tokens=True).strip(),
            'output_tokens': int(new.shape[0]),
            'latency_sec': time.perf_counter() - started}


print('\nBASELINE DIRECTO: ejecutando ahora...', flush=True)
with model.disable_adapter():
    direct = generate()
print(f"BASELINE: {direct['output_tokens']} tokens en {direct['latency_sec']:.1f} s", flush=True)
print(direct['candidate'], flush=True)

print('\nQLoRA FINAL: ejecutando ahora sobre la misma entrada...', flush=True)
adapted = generate()
print(f"QLoRA: {adapted['output_tokens']} tokens en {adapted['latency_sec']:.1f} s", flush=True)
print(adapted['candidate'], flush=True)

destination = FINAL / 'benchmark/live_demo.json'
payload = {'id': item['id'], 'problem_sha256': hashlib.sha256(item['problem'].encode()).hexdigest(),
           'model_revision': manifest['revision'], 'prompt': 'user_only',
           'max_new_tokens': 1200, 'do_sample': False, 'baseline_new_run': direct,
           'qlora_final_new_run': adapted}
destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
print('\nEvidencia guardada:', destination, flush=True)
