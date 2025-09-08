# Hardware Setup and Deployment Considerations

This document summarises how to leverage your personal hardware — **NVIDIA RTX 4060 (8 GB VRAM)**, **AMD Ryzen 5600X** and **80 GB system RAM** — when integrating advanced AI models (FinGPT and Mistral) into the HTX project.  It also outlines adjustments to the project configuration so that inference and training tasks run efficiently on your machine.

## 1 Hardware overview

| Component        | Specification                                 | Notes |
|------------------|-----------------------------------------------|------|
| GPU             | NVIDIA RTX 4060 (8 GB VRAM)                   | Supports CUDA; memory is limited to 8 GB, which affects model sizes. |
| CPU             | AMD Ryzen 5 5600X                              | 6‑core CPU; adequate for inference or data preprocessing. |
| System memory    | 80 GB RAM                                      | Ample for running preprocessing or loading quantised models. |

## 2 Running large language models on limited VRAM

Large language models (LLMs) such as Mistral 7B require significant GPU memory.  Without compression techniques, models can need 24 GB or more of VRAM【956454828609477†L80-L93】.  Fortunately, **quantisation** reduces memory requirements: quantising weights to 4‑bit or 8‑bit makes it possible to run 7B and even 13B models on GPUs with 8 GB of VRAM【956454828609477†L80-L93】.  Useful tools include:

* **bitsandbytes** – a CUDA‑accelerated library that lets you load models with 4‑bit precision; the memory savings are substantial【956454828609477†L107-L121】.  In your inference code, you can set `load_in_4bit=True` via `BitsAndBytesConfig`:

  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  from bitsandbytes import BitsAndBytesConfig

  bnb_config = BitsAndBytesConfig(load_in_4bit=True)
  model = AutoModelForCausalLM.from_pretrained(
      "mistral-7b-instruct",
      quantization_config=bnb_config,
      device_map="auto"
  )
  ```

* **LLama.cpp / GGUF models** – for CPU‑only inference, the `llama.cpp` project and its Python bindings (`llama‑cpp‑python`) run quantised models extremely efficiently.  You can clone the repository, compile it and run Mistral 7B using a pre‑quantised GGUF file.  Launching with the `-ngl 0` flag disables GPU usage and runs everything on the CPU【283579564806087†L95-L104】.

* **NF4 quantisation with bitsandbytes** – when using Hugging Face `transformers`, configure NF4 4‑bit quantisation to fit Mistral 7B into 8 GB of VRAM【235484315400863†L166-L168】.

## 3 Configuring your project for GPU/CPU selection

Your project should detect the available device at runtime and fall back to the CPU if no CUDA device is found.  Use the following pattern (shown in the Mistral quick‑start guide) to check for a GPU:

```python
import torch

# Determine if CUDA is available
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

if DEVICE == "cuda":
    print(torch.cuda.get_device_name(0))  # prints the GPU model【235484315400863†L147-L159】
```

If you encounter issues loading CUDA, install the matching CUDA toolkit via Conda as suggested in the guide【235484315400863†L161-L164】.

## 4 Local FinGPT considerations

FinGPT is built to train and fine‑tune financial language models.  The authors note that running FinGPT locally can be complex because every user’s environment differs, and there is no single recipe for local installation【813095132946273†L52-L62】.  To make it work on your hardware:

1. **Isolate dependencies** – create a dedicated Conda or virtual‑env environment (`python=3.11`) and install required libraries (PyTorch, Transformers, Datasets, LoRA toolkits, etc.).
2. **Use pre‑trained weights** – whenever possible, rely on pre‑trained FinGPT models published on Hugging Face to avoid lengthy training.
3. **Fine‑tuning** – for personalised strategies, fine‑tune using low‑rank adaptation (LoRA) to reduce memory consumption.  The FinGPT training guide uses LoRA with ChatGLM2‑6B and emphasises cleaning and formatting data sets before training【813095132946273†L64-L82】.

## 5 Updates to project configuration

To incorporate your hardware into the deployment pipeline:

* **Update configuration files** – add new fields to `config.yaml` or environment variables reflecting hardware options (e.g., `device: cuda` or `cpu`; `load_in_4bit: true`).  This allows services like `pnl_service` or your AI modules to pick the appropriate device automatically.
* **Devcontainer/Docker settings** – if using Docker or Codespaces, enable GPU support by specifying the NVIDIA runtime and installing CUDA libraries.  For example, in `docker-compose.yml`, add:

  ```yaml
  runtime: nvidia
  environment:
    - CUDA_VISIBLE_DEVICES=0
  ```

* **Documentation** – include this hardware setup document in the `docs/` directory and reference it from your README or integration guide so that other developers understand how to run the AI components locally.

By codifying your RTX 4060/5600X setup and adopting quantisation techniques, the HTX project can run sophisticated models like FinGPT and Mistral without expensive cloud GPUs and without exceeding your 8 GB VRAM limit.
