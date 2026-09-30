"""Create a controlled user-only training variant from the reviewed notebook."""
from pathlib import Path
import ast
import json

root=Path(__file__).resolve().parents[1]
source=root/'notebooks/01_qlora_experimento_controlado.ipynb'
notebook=json.loads(source.read_text(encoding='utf-8'))
cells=notebook['cells']

def modify(index, old, new):
    text=''.join(cells[index]['source'])
    assert old in text, (index,old)
    text=text.replace(old,new)
    ast.parse(text)
    cells[index]['source']=text.splitlines(keepends=True)

cells[0]['source']=(
    '# Variante de piloto: entrada user-only\n\n'
    'Entrena con el mismo template de entrada que usa el baseline y la inferencia final. '
    'Conserva exactamente los targets, splits, hiperparámetros y evaluación del notebook 01. '
    'Se usa un RUN_TAG separado y se comparan las mismas diez familias.\n').splitlines(keepends=True)
modify(2,"RUN_TAG = 'run01'", "RUN_TAG = 'user_only_run01'")
modify(5,'row["messages"],\n            add_generation_prompt=False,',
       'row["messages"][1:],\n            add_generation_prompt=False,')
modify(6,'messages[:2],\n        tokenize=False,\n        add_generation_prompt=True,',
       '[messages[1]],\n        tokenize=False,\n        add_generation_prompt=True,')
modify(6,'        messages,\n        tokenize=False,\n        add_generation_prompt=False,',
       '        messages[1:],\n        tokenize=False,\n        add_generation_prompt=False,')
modify(9,"'system_prompt':SYSTEM_PROMPT,'development_generation'", 
       "'system_prompt':SYSTEM_PROMPT,'training_messages':'user_only','development_generation'")
for index,cell in enumerate(cells):
    cell['id']=f'or-user-only-{index:02d}'
destination=root/'notebooks/04_qlora_user_only_controlado.ipynb'
destination.write_text(json.dumps(notebook,ensure_ascii=False,indent=1),encoding='utf-8')
print(destination)
