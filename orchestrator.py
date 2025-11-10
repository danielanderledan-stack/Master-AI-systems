"""
Master AI Orchestration System
Main orchestrator engine that executes JSON-configured workflows
"""

import json
import time
import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import httpx
from datetime import datetime
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class WorkflowState:
    """Manages state and variables across workflow execution"""
    variables: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def set_variable(self, name: str, value: Any):
        """Set a workflow variable"""
        self.variables[name] = value
        logger.info(f"Set variable '{name}'")

    def get_variable(self, name: str) -> Any:
        """Get a workflow variable"""
        return self.variables.get(name)

    def replace_variables(self, text: str) -> str:
        """Replace {variable_name} references in text with actual values"""
        def replacer(match):
            var_name = match.group(1)
            value = self.get_variable(var_name)
            if value is None:
                logger.warning(f"Variable '{var_name}' not found")
                return match.group(0)
            return str(value)

        return re.sub(r'\{([^}]+)\}', replacer, text)


class TokenBucket:
    """Token bucket algorithm for rate limiting"""

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()

    def consume(self, tokens_required: int = 1) -> bool:
        """Try to consume tokens, return True if successful"""
        self._refill()
        if self.tokens >= tokens_required:
            self.tokens -= tokens_required
            return True
        return False

    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now


class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance"""

    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout_seconds:
                self.state = "half_open"
                logger.info("Circuit breaker entering half-open state")
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            if self.state == "half_open":
                self.state = "closed"
                self.failures = 0
                logger.info("Circuit breaker closed")
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()

            if self.failures >= self.failure_threshold:
                self.state = "open"
                logger.error(f"Circuit breaker opened after {self.failures} failures")

            raise e


class MasterOrchestrator:
    """Main orchestration engine"""

    def __init__(self, config_path: str = "orchestration_config.json"):
        """Initialize orchestrator with configuration"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.rate_limiters = self._initialize_rate_limiters()
        self.circuit_breakers = {}
        self.client = httpx.AsyncClient(timeout=300.0)

        logger.info("Master Orchestrator initialized")

    def _initialize_rate_limiters(self) -> Dict[str, TokenBucket]:
        """Initialize rate limiters for each provider"""
        limiters = {}

        for provider, limits in self.config.get('rate_limiting', {}).items():
            rpm = limits.get('requests_per_minute', 60)
            limiters[provider] = TokenBucket(
                capacity=rpm,
                refill_rate=rpm / 60.0  # tokens per second
            )

        return limiters

    def _get_circuit_breaker(self, model_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for a model"""
        if model_name not in self.circuit_breakers:
            cb_config = self.config['error_handling']['circuit_breaker']
            self.circuit_breakers[model_name] = CircuitBreaker(
                failure_threshold=cb_config['failure_threshold'],
                timeout_seconds=cb_config['timeout_seconds']
            )
        return self.circuit_breakers[model_name]

    async def _retry_with_backoff(self, func, max_retries: int = 3, error_type: str = "transient"):
        """Execute function with exponential backoff retry"""
        retry_config = self.config['error_handling']['retry_config']
        base_delay = retry_config['base_delay_ms'] / 1000.0
        max_delay = retry_config['max_delay_ms'] / 1000.0
        exponential_base = retry_config['exponential_base']
        jitter_enabled = retry_config['jitter_enabled']

        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e

                # Calculate delay with exponential backoff
                delay = min(base_delay * (exponential_base ** attempt), max_delay)

                # Add jitter if enabled
                if jitter_enabled:
                    import random
                    delay = delay * (0.5 + random.random())

                logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay:.2f}s: {str(e)}")
                await asyncio.sleep(delay)

    async def call_ai_model(self, model_name: str, prompt: str, config: Dict = None,
                           system_prompt: str = None) -> str:
        """Call an AI model with retry and fallback logic"""
        model_config = self.config['ai_models'].get(model_name)
        if not model_config:
            raise ValueError(f"Unknown model: {model_name}")

        provider = model_config['provider']
        model = model_config['model']

        # Apply addons if specified
        full_system_prompt = system_prompt or self.config['base_ai_prompts'].get(model_name, {}).get('system_prompt', '')

        if config and 'addons' in config:
            addon_texts = []
            for addon_name in config['addons']:
                addon_text = self.config['prompt_addons'].get(addon_name, '')
                if addon_text:
                    addon_texts.append(f"[{addon_name.upper()} ADDON]: {addon_text}")

            if addon_texts:
                full_system_prompt += "\n\n" + "\n\n".join(addon_texts)

        # Merge model config with task config
        final_config = {**model_config.get('config', {}), **(config or {})}

        async def _make_request():
            # Check rate limiter
            rate_limiter = self.rate_limiters.get(provider)
            if rate_limiter:
                while not rate_limiter.consume():
                    await asyncio.sleep(0.1)

            # Make API call based on provider
            if provider == "openrouter":
                return await self._call_openrouter(model, prompt, full_system_prompt, final_config)
            elif provider == "google_ai":
                return await self._call_google_ai(model, prompt, final_config)
            else:
                raise ValueError(f"Unknown provider: {provider}")

        try:
            # Use circuit breaker
            circuit_breaker = self._get_circuit_breaker(model_name)

            # Retry with backoff
            return await self._retry_with_backoff(_make_request, max_retries=3)

        except Exception as e:
            logger.error(f"Error calling {model_name}: {str(e)}")

            # Try fallbacks
            fallbacks = self.config.get('model_fallbacks', {}).get(model_name, [])
            for fallback_model in fallbacks:
                try:
                    logger.info(f"Trying fallback model: {fallback_model}")
                    return await self.call_ai_model(fallback_model, prompt, config, system_prompt)
                except Exception as fallback_error:
                    logger.error(f"Fallback {fallback_model} also failed: {str(fallback_error)}")

            raise e

    async def _call_openrouter(self, model: str, prompt: str, system_prompt: str, config: Dict) -> str:
        """Call OpenRouter API"""
        url = self.config['api_endpoints']['openrouter']
        api_key = self.config['api_keys']['openrouter']

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": config.get('temperature', 0.7),
            "max_tokens": config.get('max_tokens', 2000),
            "top_p": config.get('top_p', 0.95),
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        response = await self.client.post(url, json=payload, headers=headers)
        response.raise_for_status()

        result = response.json()
        return result['choices'][0]['message']['content']

    async def _call_google_ai(self, model: str, prompt: str, config: Dict) -> str:
        """Call Google AI API (Imagen/Veo)"""
        api_key = self.config['api_keys']['google_ai']

        if 'imagen' in model.lower():
            url = self.config['api_endpoints']['google_imagen']
            payload = {
                "prompt": prompt,
                "aspectRatio": config.get('aspect_ratio', '1:1'),
                "negativePrompt": config.get('negative_prompt', ''),
                "numberOfImages": config.get('num_images', 1),
            }
        elif 'veo' in model.lower():
            url = self.config['api_endpoints']['google_veo']
            payload = {
                "prompt": prompt,
                "duration": config.get('duration', 8),
                "aspectRatio": config.get('aspect_ratio', '16:9'),
                "resolution": config.get('resolution', '1080p'),
                "generateAudio": config.get('generate_audio', True),
            }
        else:
            raise ValueError(f"Unknown Google AI model: {model}")

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }

        response = await self.client.post(url, json=payload, headers=headers)
        response.raise_for_status()

        result = response.json()
        # Return image/video URL or base64 data
        return json.dumps(result)

    async def categorize_request(self, user_message: str, context_tokens: int = 0) -> str:
        """Categorize user request as L, M, or H"""

        # Check context limits first
        limits = self.config['request_flow']['context_limits']
        if context_tokens > limits['deny_request']:
            raise ValueError("Request exceeds maximum token limit")
        elif context_tokens > limits['force_gemini_pro']:
            return "L"  # Force to thinking AI
        elif context_tokens > limits['force_thinking_ai']:
            return "L"  # Force to thinking AI

        # Check for image
        if self._contains_image(user_message):
            return "L"  # Use image model

        # Use categorizer AI
        category = await self.call_ai_model(
            'categorizer_ai',
            user_message,
            {'temperature': 0.3}
        )

        # Extract L, M, or H from response
        category = category.strip().upper()
        if category not in ['L', 'M', 'H']:
            logger.warning(f"Invalid category '{category}', defaulting to H")
            category = 'H'

        logger.info(f"Request categorized as: {category}")
        return category

    def _contains_image(self, message: str) -> bool:
        """Check if message contains image reference"""
        # Simple check - can be enhanced
        return 'image:' in message.lower() or 'img:' in message.lower()

    async def execute_workflow(self, workflow_definition: List[Dict], state: WorkflowState) -> WorkflowState:
        """Execute a workflow with linear and inline task queues"""

        for step_index, step in enumerate(workflow_definition):
            step_type = step.get('type', 'inline')
            tasks = step.get('tasks', [])

            logger.info(f"Executing step {step_index + 1}/{len(workflow_definition)} (type: {step_type})")

            if step_type == 'linear':
                # Execute tasks in parallel
                results = await asyncio.gather(
                    *[self._execute_task(task, state) for task in tasks],
                    return_exceptions=True
                )

                # Check for errors
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"Task {i} failed: {str(result)}")
                        raise result

            elif step_type == 'inline':
                # Execute tasks sequentially
                for task in tasks:
                    await self._execute_task(task, state)

            else:
                raise ValueError(f"Unknown step type: {step_type}")

        return state

    async def _execute_task(self, task: Dict, state: WorkflowState) -> Any:
        """Execute a single task"""
        model_name = task['model']
        prompt_template = task['prompt']
        output_variable = task.get('output_variable')
        config = task.get('config', {})

        # Replace variables in prompt
        prompt = state.replace_variables(prompt_template)

        logger.info(f"Executing task with model: {model_name}")

        try:
            # Call the AI model
            result = await self.call_ai_model(model_name, prompt, config)

            # Store result in state
            if output_variable:
                state.set_variable(output_variable, result)

            return result

        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}")

            # Use AI Workers Failed AI to communicate error
            try:
                error_message = await self.call_ai_model(
                    'ai_workers_failed_ai',
                    f"Task failed: {str(e)}. Model: {model_name}. Prompt: {prompt[:200]}...",
                    {'temperature': 0.7}
                )
                logger.info(f"Error message generated: {error_message}")
                return error_message
            except Exception as error_comm_failed:
                logger.error(f"Failed to generate error message: {str(error_comm_failed)}")
                raise e

    async def process_request(self, user_message: str, context_tokens: int = 0) -> str:
        """Main entry point for processing user requests"""

        logger.info(f"Processing request: {user_message[:100]}...")

        # Categorize the request
        category = await self.categorize_request(user_message, context_tokens)

        # Get routing configuration
        routing = self.config['request_flow']['categorization'][category]

        if category == 'L':
            # Low complexity - direct to Thinking AI
            result = await self.call_ai_model(
                routing['model'],
                user_message,
                {'temperature': 0.7}
            )
            return result

        elif category == 'M':
            # Medium complexity - use Medium AI
            result = await self.call_ai_model(
                routing['model'],
                user_message,
                {'temperature': 0.7}
            )
            return result

        elif category == 'H':
            # High complexity - use orchestration

            # Send fast response
            fast_response = await self.call_ai_model(
                routing['fast_response_model'],
                f"User requested: {user_message}. Acknowledge that you're working on it.",
                {'temperature': 0.7}
            )

            logger.info(f"Fast response: {fast_response}")

            # Get workflow from Master AI
            workflow_prompt = f"""User request: {user_message}

Create a JSON workflow to fulfill this request. Output ONLY valid JSON in the format specified in your system prompt."""

            workflow_json_str = await self.call_ai_model(
                routing['model'],
                workflow_prompt,
                {'temperature': 0.7}
            )

            # Extract JSON from response
            workflow_json_str = self._extract_json(workflow_json_str)

            try:
                workflow_definition = json.loads(workflow_json_str)
                workflow_steps = workflow_definition.get('workflow', [])
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse workflow JSON: {str(e)}")
                return f"Error: Could not create workflow. {fast_response}"

            # Execute the workflow
            state = WorkflowState()
            state.set_variable('user_message', user_message)

            try:
                final_state = await self.execute_workflow(workflow_steps, state)

                # Get completion message
                completion_msg = final_state.get_variable('completion_message')
                if completion_msg:
                    return f"{fast_response}\n\n{completion_msg}"
                else:
                    # Return all results
                    results = {k: v for k, v in final_state.variables.items() if k != 'user_message'}
                    return f"{fast_response}\n\nResults:\n{json.dumps(results, indent=2)}"

            except Exception as e:
                logger.error(f"Workflow execution failed: {str(e)}")
                return f"{fast_response}\n\nError during execution: {str(e)}"

        else:
            return f"Unknown category: {category}"

    def _extract_json(self, text: str) -> str:
        """Extract JSON from text that may contain markdown code blocks"""
        # Try to find JSON in code blocks
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, text, re.DOTALL)
        if match:
            return match.group(1)

        # Try to find raw JSON
        json_pattern = r'\{.*\}'
        match = re.search(json_pattern, text, re.DOTALL)
        if match:
            return match.group(0)

        return text

    async def close(self):
        """Clean up resources"""
        await self.client.aclose()


# Example usage
async def main():
    """Example main function"""
    orchestrator = MasterOrchestrator()

    # Example requests
    test_requests = [
        "What is the capital of France?",  # Should be M
        "Write a 2000 word article about climate change",  # Should be L
        "Create a complete marketing campaign for eco-friendly water bottles with images and videos",  # Should be H
    ]

    for request in test_requests:
        print(f"\n{'='*80}")
        print(f"REQUEST: {request}")
        print(f"{'='*80}")

        try:
            response = await orchestrator.process_request(request)
            print(f"\nRESPONSE:\n{response}")
        except Exception as e:
            print(f"\nERROR: {str(e)}")

    await orchestrator.close()


if __name__ == "__main__":
    asyncio.run(main())
