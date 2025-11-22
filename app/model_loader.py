"""
Local LLM Model Loader
Handles loading and inference using HuggingFace Transformers
"""
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocalLLM:
    """Manages local LLM loading and inference"""
    
    def __init__(self, model_name: str = "deepseek-ai/deepseek-coder-1.3b-base"):
        """
        Initialize the local LLM
        
        Args:
            model_name: HuggingFace model identifier
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None
        logger.info(f"Initializing LocalLLM with {model_name} on {self.device}")
        
    def load_model(self):
        """Load the model and tokenizer"""
        try:
            logger.info(f"Loading tokenizer from {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            logger.info(f"Loading model from {self.model_name}...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            # Set padding token if not set
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            logger.info("Model and tokenizer loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
    
    def generate_fix(self, prompt: str, max_new_tokens: int = 512) -> Tuple[str, Dict[str, int]]:
        """
        Generate code fix using the local LLM
        
        Args:
            prompt: The formatted prompt with context
            max_new_tokens: Maximum tokens to generate
            
        Returns:
            Tuple of (generated_text, token_usage_dict)
        """
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=2048
            ).to(self.device)
            
            input_token_count = inputs['input_ids'].shape[1]
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=0.2,
                    do_sample=True,
                    top_p=0.95,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode output
            generated_text = self.tokenizer.decode(
                outputs[0][input_token_count:],
                skip_special_tokens=True
            )
            
            output_token_count = outputs[0].shape[0] - input_token_count
            
            token_usage = {
                "input_tokens": input_token_count,
                "output_tokens": output_token_count
            }
            
            return generated_text.strip(), token_usage
            
        except Exception as e:
            logger.error(f"Generation failed: {str(e)}")
            raise
    
    def get_model_name(self) -> str:
        """Return the model name"""
        return self.model_name.split('/')[-1] if '/' in self.model_name else self.model_name


# Singleton instance
_llm_instance = None


def get_llm_instance(model_name: str = None) -> LocalLLM:
    """Get or create the LLM singleton instance"""
    global _llm_instance
    
    if _llm_instance is None:
        if model_name is None:
            # Default to a small model for faster inference
            model_name = "deepseek-ai/deepseek-coder-1.3b-base"
        _llm_instance = LocalLLM(model_name)
        _llm_instance.load_model()
    
    return _llm_instance
