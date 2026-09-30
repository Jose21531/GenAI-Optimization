# Adapter QLoRA final

`adapter_qlora_qwen25_final.zip` contiene `adapter_model.safetensors` y `adapter_config.json` de la corrida final `user_only_run01` sobre 1050 ejemplos. SHA-256 del ZIP: `68583e9dffa6647a5c0b89a74168363264daf246e4337ef1ae0c644243391151`. Tamaño: 68 549 293 bytes. Los pesos del modelo base y su tokenizador se descargan desde `Qwen/Qwen2.5-1.5B-Instruct`, revisión `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`.

El adapter fue exportado del `final_adapter` guardado tras 131 pasos de una época QLoRA en Colab T4. `evidence/training_manifest.json` y `evidence/training_completed.json` identifican la corrida. El notebook principal verifica el ZIP antes de extraerlo y ejecuta baseline y modelo ajustado sin acceso al Drive del equipo.
