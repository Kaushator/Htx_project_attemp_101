"""
FinGPT Service for Financial LLM Integration
Provides local FinGPT model inference with hardware optimization
"""

import logging
import torch
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json
import asyncio
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    BitsAndBytesConfig, pipeline
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class FinGPTConfig:
    """Configuration for FinGPT model"""
    def __init__(self):
        self.model_name = "AI4Finance-Foundation/FinGPT-v3.1_A16Z-FinTech"
        self.device = settings.ML_DEVICE  # "cuda" or "cpu"
        self.load_in_4bit = settings.LOAD_IN_4BIT
        self.torch_dtype = getattr(torch, settings.TORCH_DTYPE)
        self.max_length = 2048
        self.temperature = 0.1
        self.top_p = 0.9
        self.do_sample = True


class FinGPTService:
    """Service for FinGPT-based financial analysis"""
    
    def __init__(self, config: Optional[FinGPTConfig] = None):
        self.config = config or FinGPTConfig()
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self._initialized = False
        
    async def initialize(self):
        """Initialize FinGPT model and tokenizer"""
        if self._initialized:
            return
            
        try:
            logger.info(f"Initializing FinGPT on device: {self.config.device}")
            
            # Configure quantization for memory efficiency
            quantization_config = None
            if self.config.load_in_4bit and self.config.device == "cuda":
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=self.config.torch_dtype,
                    bnb_4bit_use_double_quant=True
                )
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_name,
                trust_remote_code=True
            )
            
            # Set pad token if not exists
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            model_kwargs = {
                "trust_remote_code": True,
                "torch_dtype": self.config.torch_dtype,
                "device_map": "auto" if self.config.device == "cuda" else None
            }
            
            if quantization_config:
                model_kwargs["quantization_config"] = quantization_config
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.model_name,
                **model_kwargs
            )
            
            # Move to device if CPU
            if self.config.device == "cpu":
                self.model = self.model.to("cpu")
            
            # Create text generation pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.config.device == "cuda" and torch.cuda.is_available() else -1,
                torch_dtype=self.config.torch_dtype
            )
            
            self._initialized = True
            logger.info("FinGPT initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize FinGPT: {e}")
            raise
    
    async def analyze_trade_sentiment(
        self,
        trade_data: Dict[str, Any],
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze sentiment and implications of trade data
        
        Args:
            trade_data: Trade information to analyze
            context: Additional context for analysis
            
        Returns:
            Sentiment analysis and trading insights
        """
        if not self._initialized:
            await self.initialize()
            
        if self.pipeline is None or self.tokenizer is None:
            return {
                "success": False,
                "error": "FinGPT service not properly initialized"
            }
            
        try:
            # Prepare prompt for financial analysis
            prompt = self._create_trade_analysis_prompt(trade_data, context)
            
            # Generate analysis
            response = await self._generate_text(prompt)
            
            # Parse and structure the response
            analysis = self._parse_trade_analysis(response, trade_data)
            
            return {
                "success": True,
                "analysis": analysis,
                "model": self.config.model_name,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Trade sentiment analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_market_insights(
        self,
        market_data: Dict[str, Any],
        timeframe: str = "1D"
    ) -> Dict[str, Any]:
        """
        Generate market insights and predictions
        
        Args:
            market_data: Market data for analysis
            timeframe: Analysis timeframe
            
        Returns:
            Market insights and predictions
        """
        if not self._initialized:
            await self.initialize()
            
        if self.pipeline is None or self.tokenizer is None:
            return {
                "success": False,
                "error": "FinGPT service not properly initialized"
            }
            
        try:
            prompt = self._create_market_insights_prompt(market_data, timeframe)
            
            response = await self._generate_text(prompt)
            
            insights = self._parse_market_insights(response, market_data)
            
            return {
                "success": True,
                "insights": insights,
                "timeframe": timeframe,
                "model": self.config.model_name,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Market insights generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def assess_portfolio_risk(
        self,
        portfolio_data: Dict[str, Any],
        market_conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Assess portfolio risk using FinGPT
        
        Args:
            portfolio_data: Portfolio composition and metrics
            market_conditions: Current market conditions
            
        Returns:
            Risk assessment and recommendations
        """
        if not self._initialized:
            await self.initialize()
            
        if self.pipeline is None or self.tokenizer is None:
            return {
                "success": False,
                "error": "FinGPT service not properly initialized"
            }
            
        try:
            prompt = self._create_risk_assessment_prompt(portfolio_data, market_conditions)
            
            response = await self._generate_text(prompt)
            
            risk_assessment = self._parse_risk_assessment(response, portfolio_data)
            
            return {
                "success": True,
                "risk_assessment": risk_assessment,
                "model": self.config.model_name,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Portfolio risk assessment failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _generate_text(self, prompt: str) -> str:
        """Generate text using FinGPT model"""
        if not self._initialized or self.pipeline is None or self.tokenizer is None:
            raise RuntimeError("FinGPT service not properly initialized")
            
        try:
            # Run in thread pool for async compatibility
            loop = asyncio.get_event_loop()
            
            # Capture references to avoid None access in nested function
            pipeline = self.pipeline
            tokenizer = self.tokenizer
            
            def generate():
                with torch.no_grad():
                    outputs = pipeline(
                        prompt,
                        max_length=self.config.max_length,
                        temperature=self.config.temperature,
                        top_p=self.config.top_p,
                        do_sample=self.config.do_sample,
                        num_return_sequences=1,
                        pad_token_id=tokenizer.eos_token_id
                    )
                    return outputs[0]["generated_text"]
            
            response = await loop.run_in_executor(None, generate)
            
            # Extract only the generated part (remove prompt)
            if prompt in response:
                generated = response[len(prompt):].strip()
            else:
                generated = response.strip()
            
            return generated
            
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            raise
    
    def _create_trade_analysis_prompt(self, trade_data: Dict[str, Any], context: Optional[str]) -> str:
        """Create prompt for trade analysis"""
        context_str = f"\nMarket Context: {context}" if context else ""
        
        return f"""
As a financial analyst, analyze the following trade data and provide insights:

Trade Information:
- Symbol: {trade_data.get('symbol', 'N/A')}
- Side: {trade_data.get('side', 'N/A')} 
- Amount: {trade_data.get('amount', 'N/A')}
- Price: {trade_data.get('price', 'N/A')}
- Time: {trade_data.get('time', 'N/A')}
- Fee: {trade_data.get('fee', 'N/A')}
{context_str}

Please provide:
1. Sentiment analysis (bullish/bearish/neutral)
2. Market timing assessment
3. Risk factors
4. Potential implications
5. Strategic recommendations

Analysis:
"""
    
    def _create_market_insights_prompt(self, market_data: Dict[str, Any], timeframe: str) -> str:
        """Create prompt for market insights"""
        return f"""
As a cryptocurrency market analyst, analyze the following market data for {timeframe} timeframe:

Market Data:
{json.dumps(market_data, indent=2)}

Provide insights on:
1. Market trend direction
2. Support and resistance levels
3. Volume analysis
4. Key drivers and catalysts
5. Short-term predictions
6. Risk factors

Market Analysis:
"""
    
    def _create_risk_assessment_prompt(self, portfolio_data: Dict[str, Any], market_conditions: Optional[Dict[str, Any]]) -> str:
        """Create prompt for risk assessment"""
        conditions_str = f"\nMarket Conditions:\n{json.dumps(market_conditions, indent=2)}" if market_conditions else ""
        
        return f"""
As a risk management specialist, assess the following portfolio:

Portfolio Data:
{json.dumps(portfolio_data, indent=2)}
{conditions_str}

Please evaluate:
1. Overall risk level (Low/Medium/High)
2. Diversification analysis
3. Concentration risks
4. Market exposure
5. Liquidity risks
6. Recommended risk mitigation strategies

Risk Assessment:
"""
    
    def _parse_trade_analysis(self, response: str, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse trade analysis response"""
        try:
            # Extract key information from response
            lines = response.split('\n')
            analysis = {
                "sentiment": "neutral",
                "timing_assessment": "unknown",
                "risk_factors": [],
                "implications": [],
                "recommendations": [],
                "raw_response": response
            }
            
            # Simple keyword-based parsing (could be enhanced with NLP)
            response_lower = response.lower()
            
            if any(word in response_lower for word in ["bullish", "positive", "buy", "uptrend"]):
                analysis["sentiment"] = "bullish"
            elif any(word in response_lower for word in ["bearish", "negative", "sell", "downtrend"]):
                analysis["sentiment"] = "bearish"
            
            if any(word in response_lower for word in ["good timing", "optimal", "favorable"]):
                analysis["timing_assessment"] = "favorable"
            elif any(word in response_lower for word in ["poor timing", "unfavorable", "risky"]):
                analysis["timing_assessment"] = "unfavorable"
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to parse trade analysis: {e}")
            return {"raw_response": response, "error": str(e)}
    
    def _parse_market_insights(self, response: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse market insights response"""
        try:
            return {
                "trend_direction": "unknown",
                "support_levels": [],
                "resistance_levels": [],
                "volume_analysis": "normal",
                "key_drivers": [],
                "predictions": [],
                "risks": [],
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Failed to parse market insights: {e}")
            return {"raw_response": response, "error": str(e)}
    
    def _parse_risk_assessment(self, response: str, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse risk assessment response"""
        try:
            return {
                "overall_risk": "medium",
                "diversification_score": 0.5,
                "concentration_risks": [],
                "market_exposure": {},
                "liquidity_risks": [],
                "mitigation_strategies": [],
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Failed to parse risk assessment: {e}")
            return {"raw_response": response, "error": str(e)}
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_name": self.config.model_name,
            "device": self.config.device,
            "load_in_4bit": self.config.load_in_4bit,
            "torch_dtype": str(self.config.torch_dtype),
            "initialized": self._initialized,
            "cuda_available": torch.cuda.is_available(),
            "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0
        }


# Global service instance
_fingpt_service: Optional[FinGPTService] = None


async def get_fingpt_service() -> FinGPTService:
    """Get or create FinGPT service instance"""
    global _fingpt_service
    if _fingpt_service is None:
        _fingpt_service = FinGPTService()
    return _fingpt_service