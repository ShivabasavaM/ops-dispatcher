# Fine-Tuned Llama-3-8B: Cost-Optimized Agentic Router

## Problem Statement

Automated infrastructure remediation relies on parsing chaotic system logs into structured commands. Using generalized frontier models for high-frequency alert triage introduces three major challenges:
1. **Compounding API Costs**
   - Processing thousands of daily infrastructure alerts creates unpredictable and expensive API bills.

2. **Schema Hallucinations**
   - Unconstrained language models may generate conversational text or malformed JSON, causing downstream automation failures.

3. **Network Latency**
   - Dependence on external APIs introduces delays during critical production incidents where rapid response is essential.

---

## Solution Overview

**Ops Dispatcher** is a specialized, locally hosted incident routing engine designed for deterministic infrastructure triage.

The system fine-tunes **Meta-Llama-3.1-8B** using **LoRA** to transform the model into a dedicated MLOps routing agent capable of:

- Parsing raw incident descriptions
- Identifying likely infrastructure bottlenecks
- Classifying incident severity
- Predicting remediation workflows
- Generating strict machine-readable JSON outputs

The resulting system eliminates external API dependencies while providing predictable latency and schema-safe responses for automation platforms.

---

## Architecture

The project follows a **Hybrid Decoupled Architecture** consisting of three layers.

### 1. Inference Layer

- Meta-Llama-3.1-8B
- LoRA Fine-Tuning
- 4-bit Quantization
- GPU-accelerated inference

The model is loaded directly into GPU VRAM for low-latency execution.

### 2. Middleware Layer

Built using FastAPI to:

- Handle incoming requests
- Enforce output schema validation
- Clean malformed generations
- Sanitize model responses
- Manage asynchronous request processing

### 3. Presentation Layer

A lightweight Streamlit application provides an interface for submitting incidents and viewing routing decisions.

Communication between the UI and backend occurs through an Ngrok tunnel, enabling cloud-hosted GPU inference while keeping the frontend lightweight.

### Volume Decoupling

To reduce deployment size:

- Model checkpoints are excluded from the Docker image
- Weights are mounted dynamically at runtime
- Container size remains under 1 GB
- CI/CD build times remain fast

---

## Tech Stack

### Foundation Model

- Meta-Llama-3.1-8B

### Fine-Tuning

- Unsloth
- LoRA
- 4-bit Quantization

### Backend

- FastAPI
- Uvicorn

### Frontend

- Streamlit

### Deployment

- Docker
- Ngrok

### Infrastructure

- NVIDIA T4 GPU
- CUDA 12.1+

---

## Results & Metrics

Evaluation was conducted on an unseen test dataset.

| Metric | Baseline | Fine-Tuned Model |
|----------|----------|----------|
| API Schema Compliance | 5.0% | 100.0% |
| Risk Classification Accuracy | Baseline | 100.0% |
| Exact Tool-Chain Match | Baseline | 80.0% |
| Average Inference Latency | - | < 3 seconds |

### Key Improvements

- 100% JSON schema compliance
- Perfect risk-level classification
- Accurate multi-step remediation planning
- Low-latency local inference

---

## Features

### Deterministic Execution

The model is configured with:

- Temperature = 0.0
- Custom Hugging Face `StoppingCriteria`
- `<|eot_id|>` termination token

This eliminates generation variance and ensures consistent outputs.

### Defensive Parsing Middleware

The middleware:

- Removes markdown artifacts
- Validates JSON structure
- Performs bracket matching
- Sanitizes malformed generations

### Dynamic Tool Chaining

The model predicts ordered remediation workflows.

Example:

```json
[
  "fetch_network_logs",
  "restart_ec2_node",
  "page_oncall"
]
```

---

## Installation & Setup

### Prerequisites

- Docker Engine
- NVIDIA GPU with CUDA 12.1+
- Downloaded `mlops_router_model` directory

---

### Clone Repository

```bash
git clone https://github.com/YourUsername/ops-dispatcher.git
cd ops-dispatcher
```

### Build Docker Image

```bash
docker build -t ops-dispatcher-backend .
```

### Run Container

```bash
docker run -d \
  --gpus all \
  -p 8000:8000 \
  -v $(pwd)/mlops_router_model:/app/mlops_router_model \
  ops-dispatcher-backend
```

---

## API Usage

### Request

```bash
curl -X POST "http://127.0.0.1:8000/route" \
     -H "Content-Type: application/json" \
     -d '{
           "incident": "CRITICAL ALERT: Kafka consumer lag on order-processing-v2 has exceeded 1,200,000 messages. EC2 instance reporting 99% CPU utilization."
         }'
```

### Response

```json
{
  "tools_to_call": [
    "fetch_network_logs",
    "restart_ec2_node",
    "page_oncall"
  ],
  "predicted_bottleneck": "Resource exhaustion and message broker lag leading to CPU thrashing.",
  "risk_level": "high"
}
```

---

## Performance & Reliability

### Cost Efficiency

- Eliminates recurring LLM API costs
- Inference cost is limited to infrastructure hosting expenses

### Reliability

Schema validation guarantees that downstream integrations such as:

- ServiceNow
- PagerDuty
- Internal Automation Systems

receive valid machine-readable payloads.

---

## Design Trade-Offs

### Specialization vs Generalization

The model has been aggressively fine-tuned for MLOps incident routing.

Benefits:

- High routing accuracy
- Deterministic outputs
- Domain specialization

Trade-off:

- Significant reduction in general-purpose reasoning capabilities

---

### Container Size vs Deployment Complexity

Benefits:

- Small Docker image
- Faster builds
- Improved CI/CD performance

Trade-off:

- Additional orchestration required for model volume mounting

---

## Limitations

### Context Window Constraints

Large incident reports and lengthy stack traces may exceed available context length.

Current approach:

- Summarize logs before inference

### Hardware Dependency

Current deployment relies on:

- CUDA
- NVIDIA GPUs

---

## Future Work

### Apple Silicon Support

Convert model weights to GGUF format and deploy using:

- llama.cpp
- Metal Acceleration

Benefits:

- Native Apple Silicon support
- Elimination of cloud GPU dependency
- Improved portability

### Expanded Context Handling

- Long-context fine-tuning
- Hierarchical log summarization
- Multi-document incident ingestion

---

## References

- Unsloth Documentation
- Meta Llama 3.1 Model Card
- FastAPI Documentation
- Hugging Face Transformers Documentation

---
