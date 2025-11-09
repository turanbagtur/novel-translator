"""
Cost Tracking Service - Token counting and cost estimation
"""
from typing import Dict
import tiktoken


class CostTracker:
    """Track translation costs and token usage"""
    
    # Token pricing per 1K tokens (as of 2025)
    PRICING = {
        # AI Models
        'gemini': {
            'input': 0.00025,  # $0.25 per 1M tokens
            'output': 0.00075,  # $0.75 per 1M tokens
        },
        'openai': {
            'gpt-4o': {
                'input': 0.0025,  # $2.50 per 1M tokens (2025 fiyat)
                'output': 0.01,   # $10 per 1M tokens
            },
            'gpt-4-turbo': {
                'input': 0.01,  # $10 per 1M tokens
                'output': 0.03,  # $30 per 1M tokens
            },
            'gpt-3.5-turbo': {
                'input': 0.0005,  # $0.50 per 1M tokens
                'output': 0.0015,  # $1.50 per 1M tokens
            }
        },
        'claude': {
            'claude-3-sonnet': {
                'input': 0.003,  # $3 per 1M tokens
                'output': 0.015,  # $15 per 1M tokens
            },
            'claude-3-haiku': {
                'input': 0.00025,  # $0.25 per 1M tokens
                'output': 0.00125,  # $1.25 per 1M tokens
            }
        },
        'groq': {
            'input': 0.0,  # FREE!
            'output': 0.0,
        },
        'deepseek': {
            'input': 0.00014,
            'output': 0.00028,
        },
        'perplexity': {
            'input': 0.001,
            'output': 0.002,
        },
        # Professional Translation APIs (character-based, converted to token estimate)
        'deepl': {
            'input': 0.000006,  # ~$25 per 1M characters ≈ $6 per 1M tokens (2025)
            'output': 0.0,
        },
        'google-translate': {
            'input': 0.00002,  # $20 per 1M characters
            'output': 0.0,
        },
        'microsoft-translator': {
            'input': 0.00001,  # $10 per 1M characters
            'output': 0.0,
        },
        'yandex': {
            'input': 0.000015,  # ~$15 per 1M characters
            'output': 0.0,
        },
        # Free/Open Source
        'libretranslate': {
            'input': 0.0,  # FREE (self-hosted or public)
            'output': 0.0,
        },
        'mymemory': {
            'input': 0.0,  # FREE (limited)
            'output': 0.0,
        }
    }
    
    def __init__(self):
        try:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        except:
            self.encoding = None
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.encoding:
            return len(self.encoding.encode(text))
        else:
            # Fallback: rough estimation (1 token ≈ 4 characters)
            return len(text) // 4
    
    def estimate_cost(self, provider: str, model: str, input_tokens: int, 
                     output_tokens: int) -> Dict[str, float]:
        """Estimate cost for translation"""
        
        # Get pricing
        pricing = self._get_pricing(provider, model)
        
        if not pricing:
            return {
                'input_cost': 0.0,
                'output_cost': 0.0,
                'total_cost': 0.0,
                'currency': 'USD'
            }
        
        # Calculate costs (pricing is per 1K tokens)
        input_cost = (input_tokens / 1000) * pricing['input']
        output_cost = (output_tokens / 1000) * pricing['output']
        total_cost = input_cost + output_cost
        
        return {
            'input_cost': round(input_cost, 6),
            'output_cost': round(output_cost, 6),
            'total_cost': round(total_cost, 6),
            'currency': 'USD',
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': input_tokens + output_tokens
        }
    
    def _get_pricing(self, provider: str, model: str = None) -> Dict[str, float]:
        """Get pricing for provider/model"""
        provider = provider.lower()
        
        if provider not in self.PRICING:
            return None
        
        pricing_data = self.PRICING[provider]
        
        # If provider has multiple models
        if isinstance(pricing_data, dict) and 'input' not in pricing_data:
            if model:
                model = model.lower()
                for key in pricing_data.keys():
                    if key in model:
                        return pricing_data[key]
            # Return first model's pricing as default
            return list(pricing_data.values())[0]
        
        return pricing_data
    
    def estimate_chapter_cost(self, provider: str, model: str, 
                             original_text: str, estimated_output_ratio: float = 1.2) -> Dict:
        """Estimate cost for translating a chapter"""
        input_tokens = self.count_tokens(original_text)
        estimated_output_tokens = int(input_tokens * estimated_output_ratio)
        
        cost_info = self.estimate_cost(provider, model, input_tokens, estimated_output_tokens)
        cost_info['is_estimate'] = True
        
        return cost_info
    
    def format_cost_report(self, cost_data: Dict) -> str:
        """Format cost report as string"""
        lines = [
            f"💰 Maliyet Raporu",
            f"{'=' * 40}",
            f"Input Tokens:  {cost_data.get('input_tokens', 0):,}",
            f"Output Tokens: {cost_data.get('output_tokens', 0):,}",
            f"Total Tokens:  {cost_data.get('total_tokens', 0):,}",
            f"",
            f"Input Cost:    ${cost_data.get('input_cost', 0):.6f}",
            f"Output Cost:   ${cost_data.get('output_cost', 0):.6f}",
            f"Total Cost:    ${cost_data.get('total_cost', 0):.6f} {cost_data.get('currency', 'USD')}",
        ]
        
        return '\n'.join(lines)

