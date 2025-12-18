# Complete Examples

## 1. Multi-Node PyTorch Training (DDP)

```python
import kubetorch as kt
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import os

# Define a simple model
class ToyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Linear(10, 10)

    def forward(self, x):
        return self.net(x)

def train_epoch(rank, world_size):
    # Setup DDP
    torch.distributed.init_process_group("nccl")
    
    # Create model on correct GPU
    device = rank % torch.cuda.device_count()
    model = ToyModel().to(device)
    ddp_model = nn.parallel.DistributedDataParallel(model, device_ids=[device])
    
    # Dummy data
    dataset = TensorDataset(torch.randn(100, 10), torch.randn(100, 10))
    sampler = torch.utils.data.distributed.DistributedSampler(dataset)
    loader = DataLoader(dataset, batch_size=20, sampler=sampler)
    
    optimizer = optim.SGD(ddp_model.parameters(), lr=0.001)
    
    # Training loop
    for batch_idx, (data, target) in enumerate(loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = ddp_model(data)
        loss = nn.MSELoss()(output, target)
        loss.backward()
        optimizer.step()
        
    return f"Rank {rank} finished"

def train_main():
    rank = int(os.environ["RANK"])
    world_size = int(os.environ["WORLD_SIZE"])
    return train_epoch(rank, world_size)

if __name__ == "__main__":
    # 4 Nodes x 8 GPUs = 32 GPUs total
    compute = kt.Compute(
        gpus=8,
        memory="512Gi",
        gpu_type="A100",
        image=kt.images.pytorch("24.08-py3")
    ).distribute(
        framework="pytorch",
        workers=4
    )
    
    remote_train = kt.fn(train_main).to(compute)
    results = remote_train()
    print(results)
```

## 2. LLM Inference API with Autoscaling

```python
import kubetorch as kt

class LLMService:
    def __init__(self):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = "meta-llama/Llama-2-7b-chat-hf"
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name, 
            torch_dtype=torch.float16,
            device_map="auto"
        )
    
    def generate(self, prompt: str, max_length: int = 100):
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(**inputs, max_length=max_length)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

if __name__ == "__main__":
    # HuggingFace token secret
    hf_secret = kt.Secret.from_provider("huggingface")
    
    # Compute: 1 GPU, scale 0-5 replicas
    compute = kt.Compute(
        gpus=1,
        memory="24Gi",
        secrets=[hf_secret],
        env_vars={"HF_HOME": "/cache"}
    )
    
    # Autoscale configuration
    # Keep 1 warm for low latency, scale up on load
    service = kt.cls(LLMService).to(compute).autoscale(
        min_replicas=1,
        max_replicas=5,
        target_concurrency=4  # 4 concurrent requests per replica
    )
    
    # Test call
    print(service.generate("What is the capital of France?"))
    
    # Service stays up!
    # Call from other scripts using:
    # service = kt.cls(name="yourname-LLMService").to(compute, get_if_exists=True)
```

## 3. Parameter Sweep (Hyperparameter Optimization)

```python
import kubetorch as kt
import concurrent.futures

def train_model(lr, batch_size):
    # Simulate training
    import time, random
    time.sleep(2)  # Training time
    accuracy = 1.0 - abs(lr - 0.01) - random.random() * 0.05
    return {"lr": lr, "batch_size": batch_size, "accuracy": accuracy}

if __name__ == "__main__":
    # Shared compute resource
    compute = kt.Compute(cpus="1")
    remote_train = kt.fn(train_model, name="hparam-sweep").to(compute)
    
    configs = [
        (lr, bs) 
        for lr in [0.1, 0.01, 0.001] 
        for bs in [32, 64, 128]
    ]
    
    print(f"Running {len(configs)} experiments...")
    
    # Run in parallel using threads (non-blocking HTTP calls)
    with concurrent.futures.ThreadPoolExecutor(max_workers=9) as executor:
        futures = [
            executor.submit(remote_train, lr, bs) 
            for lr, bs in configs
        ]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
    # Find best
    best = max(results, key=lambda x: x["accuracy"])
    print(f"Best config: {best}")
```

