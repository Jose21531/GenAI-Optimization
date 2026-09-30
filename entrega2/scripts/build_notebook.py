"""Build a self-contained Colab notebook, preserving the supplied notebook."""
from pathlib import Path
import ast
import json
import textwrap

ROOT = Path(__file__).resolve().parents[1]
original = json.loads((ROOT/'qlora_qwen25_or_sft_v1_2_fixed.ipynb').read_text(encoding='utf-8'))
cells = []

def add(source, kind='code'):
    source = textwrap.dedent(source).strip()+'\n'
    if kind == 'code' and not source.startswith('%pip'):
        ast.parse(source)
    cell = {'cell_type':kind,'metadata':{},'source':source.splitlines(keepends=True)}
    if kind == 'code':
        cell.update(execution_count=None,outputs=[])
    cells.append(cell)

def old(index):
    return ''.join(original['cells'][index]['source'])

add('''
# Qwen2.5-1.5B + QLoRA: experimento controlado

Versión revisada para Entrega 2. **No contiene resultados de GPU preejecutados.**
Ejecutar en Colab con T4 y Drive. Cada fase empieza desde el modelo base.
No abrir el benchmark oficial durante pilot/development.

Orden: `pilot` (160/40) → revisión matemática → `development` (840/210)
→ congelar → `final` (1050) → notebook de evaluación con protocolo original.
Las generaciones de validación comparan las mismas diez entradas antes/después.
El loss assistant-only y las longitudes se verifican antes de cargar la GPU.
''', 'markdown')
add('%pip -q install "transformers==4.51.3" "datasets==3.5.0" "peft==0.15.2" "accelerate==1.6.0" "bitsandbytes==0.45.5"')
add('''
from google.colab import drive
drive.mount('/content/drive')
from pathlib import Path
import json, hashlib, zipfile, subprocess, sys, platform, math, time, gc
import importlib.metadata as metadata
from collections import Counter, defaultdict
import torch
from transformers import set_seed
from huggingface_hub import HfApi

PROJECT_DIR = Path('/content/drive/MyDrive/IA/qwen25_qlora_or_v2')
ZIP_PATH = Path('/content/drive/MyDrive/IA/or_sft_dataset_v1_2_final.zip')
RUN_MODE = 'pilot'  # pilot | development | final
RUN_TAG = 'run01'   # nuevo tag si cambia configuración; nunca sobrescribir otro ensayo
SEED = 42
set_seed(SEED)
assert RUN_MODE in {'pilot','development','final'}
assert torch.cuda.is_available(), 'Seleccione un runtime GPU antes de continuar.'
assert ZIP_PATH.is_file(), f'No existe {ZIP_PATH}'
PROJECT_DIR.mkdir(parents=True,exist_ok=True)
RUN_DIR = PROJECT_DIR / RUN_MODE / RUN_TAG
RUN_DIR.mkdir(parents=True,exist_ok=True)
CHECKPOINT_DIR = RUN_DIR / 'checkpoints'
FINAL_ADAPTER_DIR = RUN_DIR / 'final_adapter'
CHECKPOINT_DIR.mkdir(exist_ok=True)

def write_json(path, obj):
    path = Path(path)
    tmp = path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    tmp.replace(path)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

gpu_info = subprocess.check_output(['nvidia-smi'],text=True)
print(gpu_info)
if 'T4' not in torch.cuda.get_device_name(0):
    print('AVISO: hardware distinto de T4; debe declararse en el reporte.')
(RUN_DIR/'nvidia-smi.txt').write_text(gpu_info,encoding='utf-8')
BASE_MODEL_ID = 'Qwen/Qwen2.5-1.5B-Instruct'
revision_file = PROJECT_DIR/'model_revision.json'
if not revision_file.exists():
    write_json(revision_file, {'model_id':BASE_MODEL_ID,'revision':HfApi().model_info(BASE_MODEL_ID).sha})
model_reference = json.loads(revision_file.read_text())
assert model_reference['model_id'] == BASE_MODEL_ID
MODEL_REVISION = model_reference['revision']
DATA_SHA = sha(ZIP_PATH)
LOCAL_DATA_DIR = Path('/content/or_sft_'+DATA_SHA[:12])
LOCAL_DATA_DIR.mkdir(exist_ok=True)
with zipfile.ZipFile(ZIP_PATH) as z:
    for name in z.namelist():
        target = (LOCAL_DATA_DIR/name).resolve()
        assert target.is_relative_to(LOCAL_DATA_DIR.resolve()), 'Ruta ZIP inválida'
    z.extractall(LOCAL_DATA_DIR)
for line in (LOCAL_DATA_DIR/'SHA256SUMS.txt').read_text().splitlines():
    expected, name = line.split(maxsplit=1)
    assert sha(LOCAL_DATA_DIR/name.strip()) == expected, name

LORA_R, LORA_ALPHA, LORA_DROPOUT = 16, 32, 0.05
LEARNING_RATE, GRAD_ACCUM = 2e-4, 8
NUM_EPOCHS = 1 if RUN_MODE=='pilot' else 2
MAX_NEW_TOKENS = 1200  # presupuesto del baseline original, también en validación
if RUN_MODE == 'development':
    decision = json.loads((PROJECT_DIR/'pilot_approved.json').read_text())
    assert decision['approved'] is True and decision['dataset_sha256']==DATA_SHA
    assert decision['mathematical_review'].strip()
if RUN_MODE == 'final':
    frozen = json.loads((PROJECT_DIR/'frozen_config.json').read_text())
    assert frozen['dataset_sha256']==DATA_SHA and frozen['revision']==MODEL_REVISION
    assert frozen['mathematical_review'].strip()
    LORA_R, LORA_ALPHA, LORA_DROPOUT = frozen['lora_r'], frozen['lora_alpha'], frozen['lora_dropout']
    LEARNING_RATE, GRAD_ACCUM, NUM_EPOCHS = frozen['learning_rate'], frozen['grad_accum'], frozen['epochs']
    SEED = frozen['seed']
    set_seed(SEED)
''')
add(old(6))
add('''
assert len(train840)==840 and len(val210)==210 and len(all1050)==1050
assert len({r['id'] for r in all1050})==1050
assert {r['id'] for r in train840}.isdisjoint({r['id'] for r in val210})
assert {r['id'] for r in train840+val210} == {r['id'] for r in all1050}
by_id = {r['id']:r for r in all1050}
for row in train840+val210:
    assert row['messages']==by_id[row['id']]['messages']
systems = {r['messages'][0]['content'] for r in all1050}
assert len(systems)==1
SYSTEM_PROMPT = next(iter(systems))
sample_rows = first_n_per_family(eval_rows,1) if eval_rows else []
assert not sample_rows or len(sample_rows)==len({r['family_id'] for r in sample_rows})==10
''')
source = old(7)
source = source.replace('use_fast=True,', 'use_fast=True,\n    revision=MODEL_REVISION,')
source = source[:source.index('train_lengths =')] + '''
all_lengths = [full_token_length(x) for x in all1050]
MAX_LENGTH = max(1024, int(math.ceil(max(all_lengths)/128)*128))
assert MAX_LENGTH <= 2048, f'Máximo medido {max(all_lengths)}: revisar memoria antes de entrenar.'
if RUN_MODE == 'final':
    assert MAX_LENGTH == frozen['max_length']
train_lengths = [full_token_length(x) for x in train_rows]
eval_lengths = [full_token_length(x) for x in eval_rows]
length_summary = {'n':len(all_lengths), 'mean':float(np.mean(all_lengths)),
    'p95':float(np.percentile(all_lengths,95)), 'p99':float(np.percentile(all_lengths,99)),
    'max':max(all_lengths), 'max_length':MAX_LENGTH, 'truncated':sum(n>MAX_LENGTH for n in all_lengths)}
print(length_summary)
write_json(RUN_DIR/'token_lengths.json',length_summary)
'''
add(source)
source = old(8)
start = source.index('    common = 0')
end = source.index('    # --------------------------------------------------------\n    # 4)',start)
source = source[:start]+'''    if full_ids[:len(prefix_ids)] != prefix_ids:
        raise RuntimeError(f"{row['id']}: frontera assistant no coincide exactamente; revisar tokenizer.")
    assistant_start = len(prefix_ids)
    assert len(full_ids) <= MAX_LENGTH, f"{row['id']}: prohibido truncar targets"

'''+source[end:]
source = source.replace('for row, x in zip(train_rows, train_tokenized):','for row, x in zip(train_rows + eval_rows, train_tokenized + eval_tokenized):')
source += '''
write_json(RUN_DIR/'masking_audit.json', {
    'train_supervised_min':int(train_sup.min()),'train_supervised_mean':float(train_sup.mean()),
    'train_truncated':sum(x['was_truncated'] for x in train_tokenized),
    'eval_truncated':sum(x['was_truncated'] for x in eval_tokenized),
    'strict_prefix_equality':True,
    'decoded_supervised_example':tokenizer.decode([t for t in train_tokenized[0]['labels'] if t!=-100])})
'''
add(source)
add(old(9)); add(old(10))
add('''
versions = {p:metadata.version(p) for p in ['torch','transformers','peft','datasets','accelerate','bitsandbytes','huggingface-hub']}
manifest = {'mode':RUN_MODE,'tag':RUN_TAG,'model_id':BASE_MODEL_ID,'revision':MODEL_REVISION,
    'dataset_sha256':DATA_SHA,'seed':SEED,'epochs':NUM_EPOCHS,'max_length':MAX_LENGTH,
    'learning_rate':LEARNING_RATE,'grad_accum':GRAD_ACCUM,'lora_r':LORA_R,
    'lora_alpha':LORA_ALPHA,'lora_dropout':LORA_DROPOUT,'versions':versions,
    'train_ids':[r['id'] for r in train_rows],'eval_ids':[r['id'] for r in eval_rows],
    'gpu':torch.cuda.get_device_name(0), 'cuda':torch.version.cuda,
    'system_prompt':SYSTEM_PROMPT,'development_generation':{'messages':'user_only','do_sample':False,'max_new_tokens':MAX_NEW_TOKENS,'repetition_penalty':1.0}}
manifest_path = RUN_DIR/'manifest.json'
if manifest_path.exists():
    assert json.loads(manifest_path.read_text()) == manifest, 'Config diferente: use otro RUN_TAG.'
else:
    write_json(manifest_path,manifest)
(RUN_DIR/'requirements-runtime.txt').write_text(subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True),encoding='utf-8')
torch.cuda.reset_peak_memory_stats()
''')
source = old(11).replace('quantization_config=bnb_config,','quantization_config=bnb_config,\n    revision=MODEL_REVISION,\n    attn_implementation="sdpa",')
add(source)
add('''
from transformers import TrainingArguments, Trainer
from transformers.trainer_utils import get_last_checkpoint
from transformers import TrainerCallback

class PersistentLog(TrainerCallback):
    def on_log(self,args,state,control,logs=None,**kwargs):
        if logs:
            with (RUN_DIR/'training_log.jsonl').open('a',encoding='utf-8') as f:
                f.write(json.dumps({'step':state.global_step, 'epoch':state.epoch, **logs},ensure_ascii=False)+'\\n')

training_args = TrainingArguments(
    output_dir=str(CHECKPOINT_DIR),num_train_epochs=NUM_EPOCHS,
    per_device_train_batch_size=1,per_device_eval_batch_size=1,
    gradient_accumulation_steps=GRAD_ACCUM,learning_rate=LEARNING_RATE,
    warmup_ratio=0.05,lr_scheduler_type='cosine',fp16=True,bf16=False,
    optim='paged_adamw_8bit',logging_steps=5,
    eval_strategy='epoch' if eval_ds is not None else 'no',
    save_strategy='epoch' if RUN_MODE=='development' else 'steps',
    save_steps=10 if RUN_MODE=='pilot' else 25,save_total_limit=3,
    load_best_model_at_end=RUN_MODE=='development',metric_for_best_model='eval_loss',greater_is_better=False,
    report_to='none',remove_unused_columns=False,seed=SEED,data_seed=SEED,
    dataloader_num_workers=0,prediction_loss_only=True,label_names=['labels'],
)
trainer = Trainer(model=model,args=training_args,train_dataset=train_ds,eval_dataset=eval_ds,
                  data_collator=data_collator,callbacks=[PersistentLog()])
last_checkpoint = get_last_checkpoint(str(CHECKPOINT_DIR))
print('Checkpoint para reanudar:',last_checkpoint)

@torch.inference_mode()
def generate_validation(stage):
    destination = RUN_DIR/f'validation_{stage}_no_gold.jsonl'
    if destination.exists():
        stored = read_jsonl(destination)
        assert [r['id'] for r in stored]==[r['id'] for r in sample_rows]
        return stored
    model.eval()
    model.gradient_checkpointing_disable()
    model.config.use_cache=True
    outputs=[]
    for row in sample_rows:
        # Mismo mensaje user-only del baseline; nunca pasar el assistant al generador.
        prompt = tokenizer.apply_chat_template([row['messages'][1]],tokenize=False,add_generation_prompt=True)
        batch = tokenizer(prompt,return_tensors='pt',add_special_tokens=False).to(model.device)
        torch.cuda.synchronize(); start=time.perf_counter()
        out=model.generate(**batch,max_new_tokens=MAX_NEW_TOKENS,do_sample=False,
                           repetition_penalty=1.0,pad_token_id=tokenizer.pad_token_id,
                           eos_token_id=tokenizer.eos_token_id)
        torch.cuda.synchronize()
        token_ids=out[0,batch['input_ids'].shape[1]:].tolist()
        text=tokenizer.decode(token_ids,skip_special_tokens=True).strip()
        lines=[line.strip() for line in text.splitlines() if len(line.strip())>15]
        outputs.append({'id':row['id'],'family_id':row['family_id'],'problem':row['messages'][1]['content'],
            'candidate':text,'tokens':len(token_ids),'seconds':time.perf_counter()-start,
            'truncated':len(token_ids)==MAX_NEW_TOKENS and token_ids[-1]!=tokenizer.eos_token_id,
            'repeated_long_lines':len(lines)-len(set(lines))})
        print(row['id'],text,sep='\\n')
    destination.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\\n' for r in outputs),encoding='utf-8')
    model.config.use_cache=False
    model.gradient_checkpointing_enable()
    return outputs

# Este modelo está recién inicializado: LoRA aún es identidad. En una reanudación,
# Trainer cargará el checkpoint después de esta celda.
if eval_ds is not None:
    if not (RUN_DIR/'base_eval_metrics.json').exists():
        base_metrics=trainer.evaluate(metric_key_prefix='base_eval')
        write_json(RUN_DIR/'base_eval_metrics.json',base_metrics)
    base_generations=generate_validation('base')
''')
add('''
# Si ya existe completed.json, no repetir entrenamiento en el mismo RUN_TAG.
assert not (RUN_DIR/'completed.json').exists(), 'Fase ya completada: revisar evidencia guardada.'
model.train()
torch.cuda.reset_peak_memory_stats()
started=time.perf_counter()
train_result=trainer.train(resume_from_checkpoint=last_checkpoint)
trainer.save_model(str(FINAL_ADAPTER_DIR))
tokenizer.save_pretrained(FINAL_ADAPTER_DIR)
trainer.save_state()
metrics=dict(train_result.metrics)
metrics.update(wall_seconds_this_session=time.perf_counter()-started,
    peak_allocated_gib=torch.cuda.max_memory_allocated()/1024**3,
    peak_reserved_gib=torch.cuda.max_memory_reserved()/1024**3,
    global_step=trainer.state.global_step,best_checkpoint=trainer.state.best_model_checkpoint)
write_json(RUN_DIR/'train_metrics.json',metrics)
write_json(RUN_DIR/'trainer_log_history.json',trainer.state.log_history)
if eval_ds is not None:
    eval_metrics=trainer.evaluate()
    assert math.isfinite(eval_metrics['eval_loss'])
    write_json(RUN_DIR/'eval_metrics.json',eval_metrics)
    adapted_generations=generate_validation('adapted')
    before=json.loads((RUN_DIR/'base_eval_metrics.json').read_text())['base_eval_loss']
    diagnostic={'base_eval_loss':before,'adapted_eval_loss':eval_metrics['eval_loss'],
        'loss_delta':eval_metrics['eval_loss']-before,
        'base_truncated':sum(r['truncated'] for r in base_generations),
        'adapted_truncated':sum(r['truncated'] for r in adapted_generations),
        'base_repeated_lines':sum(r['repeated_long_lines'] for r in base_generations),
        'adapted_repeated_lines':sum(r['repeated_long_lines'] for r in adapted_generations),
        'n_generation_pairs':len(adapted_generations),
        'mathematical_success':'requires manual review; these diagnostics are not FOM-5'}
    write_json(RUN_DIR/'validation_comparison.json',diagnostic)
    print(diagnostic)
adapter_hashes={p.name:sha(p) for p in FINAL_ADAPTER_DIR.iterdir() if p.is_file()}
write_json(RUN_DIR/'completed.json',{'manifest_sha256':sha(manifest_path),'adapter_hashes':adapter_hashes,
    'global_step':trainer.state.global_step,'status':'training_complete_not_benchmark_evaluated'})
''')
add('''
## Revisión y transición

Revisar las diez parejas de validación contra las referencias **solo para evaluación**.
Examinar dominios, ponderaciones, vinculación, balances, precedencias y completitud.
Contar títulos o una caída del loss no certifica corrección matemática.

La siguiente celda no aprueba automáticamente el piloto. Complete una justificación
basada en las salidas. Tras aprobar, cambiar `RUN_MODE`, usar una sesión limpia o
liberar el modelo anterior y ejecutar desde el inicio; no continuar pesos del piloto.
''','markdown')
add('''
APPROVE_PHASE = False
MATHEMATICAL_REVIEW = ''
if APPROVE_PHASE:
    assert eval_rows and MATHEMATICAL_REVIEW.strip()
    assert (RUN_DIR/'completed.json').exists()
    if RUN_MODE=='pilot':
        write_json(PROJECT_DIR/'pilot_approved.json', {'approved':True,'dataset_sha256':DATA_SHA,
            'source_run':str(RUN_DIR),'mathematical_review':MATHEMATICAL_REVIEW})
    elif RUN_MODE=='development':
        evaluations=[x for x in trainer.state.log_history if 'eval_loss' in x]
        best_step=int(Path(trainer.state.best_model_checkpoint).name.rsplit('-',1)[1])
        best=next(x for x in evaluations if x['step']==best_step)
        # El adapter guardado corresponde al mejor checkpoint por loss.
        chosen_epoch=int(round(best['epoch']))
        assert chosen_epoch in (1,2)
        frozen_config={k:manifest[k] for k in ['dataset_sha256','revision','lora_r','lora_alpha','lora_dropout',
                       'learning_rate','grad_accum','max_length','seed']}
        frozen_config.update(epochs=chosen_epoch,source_run=str(RUN_DIR),
                             mathematical_review=MATHEMATICAL_REVIEW,selected_eval_loss=best['eval_loss'])
        write_json(PROJECT_DIR/'frozen_config.json',frozen_config)
        print('Configuración congelada:',frozen_config)
else:
    print('Sin aprobación: completar revisión antes de avanzar a la fase siguiente.')
''')
add('''
## Después de final

Guardar el adapter, el manifest y `completed.json`. Recuperar los 30 problemas y el
caso original de Entrega 1 con su texto exacto, la configuración baseline y el
evaluador FOM-5 v2 original. Generar sin gold/requirements, después evaluar.
El benchmark aún no está incluido en este notebook. No reconstruir sus resultados.
''','markdown')

notebook={'cells':cells,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},
    'language_info':{'name':'python'},'accelerator':'GPU','colab':{'provenance':[]}},'nbformat':4,'nbformat_minor':5}
for index,cell in enumerate(cells):
    cell['id']=f'or-qlora-{index:02d}'
destination=ROOT/'notebooks/01_qlora_experimento_controlado.ipynb'
destination.parent.mkdir(exist_ok=True)
destination.write_text(json.dumps(notebook,ensure_ascii=False,indent=1),encoding='utf-8')
print(destination)
