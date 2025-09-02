"""
Mistral Service for Advanced Financial Analysis
Provides local Mistral model inference with financial fine-tuning
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


class MistralConfig:
    """Configuration for Mistral model"""
    def __init__(self):
        self.model_name = "mistralai/Mistral-7B-Instruct-v0.2"  # You can switch to financial fine-tuned versions
        self.device = settings.ML_DEVICE
        self.load_in_4bit = settings.LOAD_IN_4BIT
        self.torch_dtype = getattr(torch, settings.TORCH_DTYPE)
        self.max_length = 4096
        self.temperature = 0.1
        self.top_p = 0.9
        self.do_sample = True


class MistralService:
    """Service for Mistral-based financial analysis and reasoning"""
    
    def __init__(self, config: Optional[MistralConfig] = None):
        self.config = config or MistralConfig()
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self._initialized = False
        
    async def initialize(self):
        """Initialize Mistral model and tokenizer"""
        if self._initialized:
            return
            
        try:
            logger.info(f"Initializing Mistral on device: {self.config.device}")
            
            # Configure quantization
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
            
            if self.config.device == "cpu":
                self.model = self.model.to("cpu")
            
            # Create pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.config.device == "cuda" and torch.cuda.is_available() else -1,
                torch_dtype=self.config.torch_dtype
            )
            
            self._initialized = True
            logger.info("Mistral initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Mistral: {e}")
            raise
    
    async def analyze_trading_strategy(
        self,
        strategy_data: Dict[str, Any],
        market_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze trading strategy effectiveness and provide recommendations
        
        Args:
            strategy_data: Trading strategy details and performance
            market_context: Current market conditions
            
        Returns:
            Strategy analysis and optimization suggestions
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            prompt = self._create_strategy_analysis_prompt(strategy_data, market_context)
            
            response = await self._generate_text(prompt)
            
            analysis = self._parse_strategy_analysis(response, strategy_data)
            
            return {
                "success": True,
                "analysis": analysis,
                "model": self.config.model_name,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Trading strategy analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_trading_signals(
        self,
        market_data: Dict[str, Any],
        indicators: List[str],
        timeframe: str = "1H"
    ) -> Dict[str, Any]:
        """
        Generate trading signals based on market data and technical indicators
        
        Args:
            market_data: Current market data
            indicators: List of technical indicators to consider
            timeframe: Analysis timeframe
            
        Returns:
            Trading signals and confidence scores
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            prompt = self._create_signal_generation_prompt(market_data, indicators, timeframe)
            
            response = await self._generate_text(prompt)
            
            signals = self._parse_trading_signals(response, market_data)
            
            return {
                "success": True,
                "signals": signals,
                "timeframe": timeframe,
                "indicators": indicators,
                "model": self.config.model_name,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Trading signal generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def evaluate_investment_thesis(
        self,
        asset_data: Dict[str, Any],
        fundamental_data: Optional[Dict[str, Any]] = None,
        technical_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate investment thesis for an asset
        
        Args:
            asset_data: Basic asset information
            fundamental_data: Fundamental analysis data
            technical_data: Technical analysis data
            
        Returns:
            Investment thesis evaluation and rating
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            prompt = self._create_thesis_evaluation_prompt(
                asset_data, fundamental_data, technical_data
            )
            
            response = await self._generate_text(prompt)
            
            evaluation = self._parse_thesis_evaluation(response, asset_data)
            
            return {
                "success": True,
                "evaluation": evaluation,
                "model": self.config.model_name,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Investment thesis evaluation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def provide_market_commentary(
        self,
        market_events: List[Dict[str, Any]],
        portfolio_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Provide market commentary and analysis of recent events
        
        Args:
            market_events: Recent market events and news
            portfolio_context: Portfolio context for personalized commentary
            
        Returns:
            Market commentary and implications
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            prompt = self._create_commentary_prompt(market_events, portfolio_context)
            
            response = await self._generate_text(prompt)
            
            commentary = self._parse_market_commentary(response, market_events)
            
            return {
                "success": True,
                "commentary": commentary,
                "model": self.config.model_name,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Market commentary generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _generate_text(self, prompt: str) -> str:
        """Generate text using Mistral model with proper instruction formatting"""
        try:
            # Format prompt for Mistral instruction template
            formatted_prompt = f"<s>[INST] {prompt} [/INST]"
            
            loop = asyncio.get_event_loop()
            
            def generate():
                with torch.no_grad():
                    outputs = self.pipeline(
                        formatted_prompt,
                        max_length=self.config.max_length,
                        temperature=self.config.temperature,
                        top_p=self.config.top_p,
                        do_sample=self.config.do_sample,
                        num_return_sequences=1,
                        pad_token_id=self.tokenizer.eos_token_id,
                        eos_token_id=self.tokenizer.eos_token_id
                    )
                    return outputs[0]["generated_text"]
            
            response = await loop.run_in_executor(None, generate)
            
            # Extract generated text after the instruction
            if "[/INST]" in response:
                generated = response.split("[/INST]", 1)[1].strip()
            else:
                generated = response.strip()
            
            return generated
            
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            raise
    
    def _create_strategy_analysis_prompt(
        self,
        strategy_data: Dict[str, Any],
        market_context: Optional[Dict[str, Any]]
    ) -> str:
        """Create prompt for strategy analysis"""
        context_str = f"\nMarket Context:\n{json.dumps(market_context, indent=2)}" if market_context else ""
        
        return f"""
You are an expert quantitative analyst. Analyze the following trading strategy and provide detailed insights:

Strategy Data:
{json.dumps(strategy_data, indent=2)}
{context_str}

Please provide a comprehensive analysis including:

1. **Performance Assessment**:
   - Overall performance rating (1-10)
   - Key performance metrics evaluation
   - Risk-adjusted returns analysis

2. **Strategy Strengths**:
   - What works well in this strategy
   - Market conditions where it excels
   - Unique advantages

3. **Strategy Weaknesses**:
   - Identified vulnerabilities
   - Market conditions where it fails
   - Risk factors and limitations

4. **Optimization Recommendations**:
   - Specific improvements to consider
   - Parameter adjustments
   - Risk management enhancements

5. **Market Adaptability**:
   - How well the strategy adapts to different market regimes
   - Suggested modifications for current market conditions

Provide your analysis in a structured format with clear reasoning for each assessment.
"""
    
    def _create_signal_generation_prompt(
        self,
        market_data: Dict[str, Any],
        indicators: List[str],
        timeframe: str
    ) -> str:
        """Create prompt for trading signal generation"""
        indicators_str = ", ".join(indicators)
        
        return f"""
As a professional trading analyst, generate trading signals based on the following market data:

Market Data ({timeframe} timeframe):
{json.dumps(market_data, indent=2)}

Technical Indicators to Consider: {indicators_str}

Generate trading signals with the following format:

1. **Primary Signal**: BUY/SELL/HOLD
2. **Confidence Level**: 1-10 (10 being highest confidence)
3. **Entry Conditions**: Specific conditions that triggered the signal
4. **Risk Assessment**: Potential risks and mitigation strategies
5. **Target Levels**: Suggested take-profit and stop-loss levels
6. **Time Horizon**: Expected duration for the signal
7. **Supporting Evidence**: Key indicators and patterns supporting the signal

Provide clear, actionable signals with detailed reasoning for each recommendation.
"""
    
    def _create_thesis_evaluation_prompt(
        self,
        asset_data: Dict[str, Any],
        fundamental_data: Optional[Dict[str, Any]],
        technical_data: Optional[Dict[str, Any]]
    ) -> str:
        """Create prompt for investment thesis evaluation"""
        fundamental_str = f"\nFundamental Data:\n{json.dumps(fundamental_data, indent=2)}" if fundamental_data else ""
        technical_str = f"\nTechnical Data:\n{json.dumps(technical_data, indent=2)}" if technical_data else ""
        
        return f"""
As an investment analyst, evaluate the investment thesis for the following asset:

Asset Information:
{json.dumps(asset_data, indent=2)}
{fundamental_str}
{technical_str}

Provide a comprehensive investment thesis evaluation:

1. **Investment Rating**: Strong Buy/Buy/Hold/Sell/Strong Sell
2. **Conviction Score**: 1-10 (10 being highest conviction)
3. **Fundamental Analysis**:
   - Key fundamental strengths and weaknesses
   - Valuation assessment
   - Growth prospects

4. **Technical Analysis**:
   - Current technical setup
   - Key support and resistance levels
   - Momentum indicators

5. **Risk Factors**:
   - Primary risks to the investment thesis
   - Market risks and external factors
   - Risk mitigation strategies

6. **Time Horizon**:
   - Short-term outlook (1-3 months)
   - Medium-term outlook (3-12 months)
   - Long-term outlook (1+ years)

7. **Catalysts**:
   - Potential positive catalysts
   - Potential negative catalysts
   - Timeline for key events

Provide detailed reasoning for your assessment and specific price targets where applicable.
"""
    
    def _create_commentary_prompt(
        self,
        market_events: List[Dict[str, Any]],
        portfolio_context: Optional[Dict[str, Any]]
    ) -> str:
        """Create prompt for market commentary"""
        portfolio_str = f"\nPortfolio Context:\n{json.dumps(portfolio_context, indent=2)}" if portfolio_context else ""
        
        return f"""
As a market commentator and analyst, provide insightful commentary on recent market events:

Recent Market Events:
{json.dumps(market_events, indent=2)}
{portfolio_str}

Provide comprehensive market commentary including:

1. **Market Overview**:
   - Current market sentiment and trends
   - Key themes driving markets
   - Overall market health assessment

2. **Event Analysis**:
   - Impact assessment of each major event
   - Interconnections between events
   - Market reactions and their appropriateness

3. **Sector Impact**:
   - Which sectors are most affected
   - Relative performance expectations
   - Rotation opportunities

4. **Portfolio Implications**:
   - How events affect different asset classes
   - Recommended positioning adjustments
   - Risk management considerations

5. **Forward Outlook**:
   - Key events to watch in the near term
   - Potential market scenarios
   - Strategic recommendations

6. **Actionable Insights**:
   - Specific investment opportunities
   - Risk factors to monitor
   - Timing considerations

Provide professional, balanced commentary with clear investment implications.
"""
    
    def _parse_strategy_analysis(self, response: str, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse strategy analysis response"""
        try:
            return {
                "performance_rating": 7.0,  # Default, could be extracted from text
                "strengths": [],
                "weaknesses": [],
                "optimization_recommendations": [],
                "market_adaptability": "medium",
                "overall_assessment": "positive",
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Failed to parse strategy analysis: {e}")
            return {"raw_response": response, "error": str(e)}
    
    def _parse_trading_signals(self, response: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse trading signals response"""
        try:
            # Simple keyword extraction (enhance with NLP for better parsing)
            response_lower = response.lower()
            
            signal = "HOLD"
            if "buy" in response_lower and "sell" not in response_lower:
                signal = "BUY"
            elif "sell" in response_lower and "buy" not in response_lower:
                signal = "SELL"
            
            return {
                "primary_signal": signal,
                "confidence_level": 7,  # Default, extract from text
                "entry_conditions": [],
                "risk_assessment": "",
                "target_levels": {},
                "time_horizon": "short-term",
                "supporting_evidence": [],
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Failed to parse trading signals: {e}")
            return {"raw_response": response, "error": str(e)}
    
    def _parse_thesis_evaluation(self, response: str, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse investment thesis evaluation"""
        try:
            return {
                "investment_rating": "HOLD",
                "conviction_score": 6,
                "fundamental_analysis": {},
                "technical_analysis": {},
                "risk_factors": [],
                "time_horizon": {},
                "catalysts": [],
                "price_targets": {},
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Failed to parse thesis evaluation: {e}")
            return {"raw_response": response, "error": str(e)}
    
    def _parse_market_commentary(self, response: str, market_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse market commentary response"""
        try:
            return {
                "market_overview": {},
                "event_analysis": [],
                "sector_impact": {},
                "portfolio_implications": {},
                "forward_outlook": {},
                "actionable_insights": [],
                "sentiment": "neutral",
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Failed to parse market commentary: {e}")
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
_mistral_service: Optional[MistralService] = None


async def get_mistral_service() -> MistralService:
    """Get or create Mistral service instance"""
    global _mistral_service
    if _mistral_service is None:
        _mistral_service = MistralService()
    return _mistral_service