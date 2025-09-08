# Hardware Setup Guide for HTX ML Services

## Overview
This guide covers hardware configuration for the HTX trading platform's ML components, including OpenAI integration, local LLMs (FinGPT, Mistral), and vector search.

## System Requirements

### Minimum Requirements
- **CPU**: Intel i5 or AMD Ryzen 5 (4 cores)
- **RAM**: 16GB DDR4
- **Storage**: 50GB free SSD space
- **Network**: Stable internet for OpenAI API calls

### Recommended for Local LLM Inference
- **CPU**: Intel i7/i9 or AMD Ryzen 7/9 (8+ cores)
- **RAM**: 32GB+ DDR4/DDR5
- **GPU**: NVIDIA RTX 4060/4070 (12GB+ VRAM) or RTX 3080/3090
- **Storage**: 200GB+ NVMe SSD
- **Network**: High-speed internet (100+ Mbps)

### Optimal for Production
- **CPU**: Intel Xeon or AMD EPYC (16+ cores)
- **RAM**: 64GB+ ECC memory
- **GPU**: NVIDIA A4000/A5000 or RTX 4090 (24GB+ VRAM)
- **Storage**: 1TB+ NVMe SSD in RAID configuration
- **Network**: Dedicated connection with low latency

## Configuration Options

### Device Selection
The platform automatically detects available hardware and configures services accordingly:

```python
# In settings (backend/app/core/config.py)
ML_DEVICE = "cuda"  # Options: "cuda", "cpu"
LOAD_IN_4BIT = True  # Enable 4-bit quantization for memory efficiency
TORCH_DTYPE = "float16"  # Options: "float32", "float16"
```

### GPU Configuration (CUDA)
When `ML_DEVICE="cuda"` and NVIDIA GPU is available:
- **Memory Optimization**: 4-bit quantization reduces VRAM usage by ~75%
- **Performance**: 3-10x faster inference vs CPU
- **Models**: Can run FinGPT-7B, Mistral-7B simultaneously on 12GB+ VRAM

### CPU Configuration  
When `ML_DEVICE="cpu"` or no GPU available:
- **Memory Usage**: Higher RAM requirements (8-16GB per model)
- **Performance**: Slower inference (10-60 seconds per request)
- **Compatibility**: Works on any x86_64 system

## Service Configuration

### OpenAI Integration
Requires API key configuration:

```bash
# Environment variables (.env file)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

Features:
- **JSON Mode**: Structured responses for ML planning
- **Batch Processing**: Efficient labeling of large datasets
- **Embeddings**: High-quality vector representations
- **Rate Limiting**: Built-in request throttling

### Local LLM Services

#### FinGPT Service
- **Model**: AI4Finance-Foundation/FinGPT-v3.1_A16Z-FinTech
- **Size**: ~7B parameters
- **Specialization**: Financial analysis, trading insights
- **Use Cases**: Trade sentiment, market commentary, risk assessment

#### Mistral Service  
- **Model**: mistralai/Mistral-7B-Instruct-v0.2
- **Size**: ~7B parameters
- **Specialization**: General reasoning, strategy analysis
- **Use Cases**: Trading signals, investment thesis, strategy optimization

### Vector Search (Embeddings)
Supports both PostgreSQL with pgvector and SQLite fallback:

```python
# PostgreSQL with pgvector (recommended)
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/htx_db"

# SQLite fallback
DATABASE_URL = "sqlite+aiosqlite:///./data/app.db"
```

## Performance Optimization

### Memory Management
1. **4-bit Quantization**: Reduces model size by 75%
2. **Gradient Checkpointing**: Saves memory during inference
3. **Model Offloading**: Automatically manages GPU/CPU memory

### Inference Optimization
1. **Batch Processing**: Groups requests for efficiency
2. **Caching**: Stores frequently used embeddings
3. **Async Operations**: Non-blocking request handling

### Hardware Monitoring
Monitor system resources during operation:
- **GPU Memory**: Use `nvidia-smi` to check VRAM usage
- **CPU Load**: Monitor with `htop` or Task Manager  
- **RAM Usage**: Ensure sufficient memory for models
- **Storage I/O**: Fast storage improves model loading

## Deployment Scenarios

### Development (Local)
- Single machine with moderate specs
- CPU inference for testing
- SQLite database
- OpenAI API for production features

### Production (Cloud)
- GPU-enabled instance (AWS p3/p4, GCP A100)
- PostgreSQL with pgvector
- Load balancer for multiple API instances
- Redis for caching and task queues

### Hybrid Setup
- OpenAI for complex reasoning tasks
- Local LLMs for high-frequency operations
- Edge deployment for low-latency requirements

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   - Enable 4-bit quantization: `LOAD_IN_4BIT=True`
   - Reduce batch size in requests
   - Use CPU fallback: `ML_DEVICE="cpu"`

2. **Slow CPU Inference**
   - Increase batch size for better throughput
   - Consider GPU upgrade or cloud instance
   - Use OpenAI API for critical operations

3. **Model Loading Errors**
   - Check internet connection for model downloads
   - Verify sufficient storage space
   - Ensure PyTorch/transformers compatibility

4. **API Timeouts**
   - Increase request timeout settings
   - Monitor OpenAI rate limits
   - Implement request retry logic

### Performance Metrics

Expected performance benchmarks:

#### GPU (RTX 4070, 12GB VRAM)
- **FinGPT/Mistral**: 2-5 seconds per request
- **Batch Processing**: 50-100 items/minute
- **Memory Usage**: 6-8GB VRAM per model

#### CPU (Ryzen 7, 32GB RAM)  
- **FinGPT/Mistral**: 15-45 seconds per request
- **Batch Processing**: 10-20 items/minute
- **Memory Usage**: 8-12GB RAM per model

## Security Considerations

1. **API Keys**: Store securely, never commit to repositories
2. **Model Access**: Restrict file system access for model storage
3. **Network**: Use HTTPS for all API communications
4. **Data Privacy**: Local LLMs keep data on-premises
5. **Resource Limits**: Set memory and CPU limits to prevent abuse

## Future Enhancements

1. **Multi-GPU Support**: Distribute models across multiple GPUs
2. **Model Quantization**: INT8/INT4 for further optimization
3. **Edge Deployment**: ARM-based processors for mobile/IoT
4. **Custom Fine-tuning**: Domain-specific model adaptation
5. **Distributed Inference**: Kubernetes-based model serving

This hardware setup enables the HTX platform to provide advanced ML capabilities while maintaining flexibility for different deployment scenarios and resource constraints.