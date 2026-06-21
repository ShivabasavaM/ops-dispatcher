import json
import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from unsloth import FastLanguageModel
from transformers import StoppingCriteria, StoppingCriteriaList

app = FastAPI(title="MLOps Specialized Agentic Router")

# Persistent configuration (Update this path to your downloaded model folder)
MODEL_PATH = "./mlops_router_model"
MAX_SEQ_LENGTH = 2048

print("Loading model into memory...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_PATH,
    max_seq_length=MAX_SEQ_LENGTH,
    dtype=None,
    load_in_4bit=True,
)
FastLanguageModel.for_inference(model)
print("Model loaded successfully!")

class IncidentRequest(BaseModel):
    incident: str

class RouterResponse(BaseModel):
    tools_to_call: list[str]
    predicted_bottleneck: str
    risk_level: str

class StopOnToken(StoppingCriteria):
    def __init__(self, stop_token_id):
        self.stop_token_id = stop_token_id
    def __call__(self, input_ids, scores, **kwargs):
        return input_ids[0, -1] == self.stop_token_id

eot_token_id = tokenizer.convert_tokens_to_ids("<|eot_id|>")
stopping_criteria = StoppingCriteriaList([StopOnToken(eot_token_id)])

@app.post("/route", response_model=RouterResponse)
async def route_incident(request: IncidentRequest):
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are an expert MLOps router. Output strictly valid JSON.
Given an incident description, determine the tools to call, bottleneck, and risk level.
Allowed tools: ["query_servicenow_db", "fetch_network_logs", "restart_ec2_node", "trigger_anomaly_detection", "page_oncall"]<|eot_id|><|start_header_id|>user<|end_header_id|>
Incident: {request.incident}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""

    inputs = tokenizer([prompt], return_tensors="pt").to("cuda")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            temperature=0.0,
            do_sample=False,
            use_cache=True,
            stopping_criteria=stopping_criteria,
            pad_token_id=tokenizer.eos_token_id
        )
    
    # Slice tensor to grab ONLY the newly generated tokens
    input_length = inputs['input_ids'].shape[1]
    generated_tokens = outputs[0][input_length:]
    raw_output = tokenizer.decode(generated_tokens, skip_special_tokens=True)
    
    # Defensive Bracket-Matching Parser
    cleaned_output = raw_output.replace("```json", "").replace("```", "").strip()
    start_idx = cleaned_output.find('{')
    end_idx = cleaned_output.rfind('}')
    
    if start_idx == -1 or end_idx == -1:
        raise HTTPException(status_code=500, detail="Model failed to generate structured JSON segment.")
        
    json_str = cleaned_output[start_idx:end_idx+1]
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Extracted segment was invalid JSON.")

if __name__ == "__main__":
    # Standard production execution
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)