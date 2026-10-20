from huggingface_hub import model_info

model_id = "Qwen/Qwen2.5-7B-Instruct-1M"

info = model_info(
    model_id,
    expand="inferenceProviderMapping"
)

print(info.inference_provider_mapping)