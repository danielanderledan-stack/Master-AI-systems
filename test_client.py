"""
Test client for Master AI Orchestration System
Run this to test the orchestration API
"""

import httpx
import asyncio
import json
from typing import Dict, Any


class OrchestrationClient:
    """Client for interacting with the orchestration API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=300.0)
        self.session_id = None

    async def health_check(self) -> Dict[str, Any]:
        """Check if the API is healthy"""
        response = await self.client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    async def chat(self, message: str, context_tokens: int = 0) -> Dict[str, Any]:
        """Send a chat message"""
        payload = {
            "message": message,
            "context_tokens": context_tokens
        }

        if self.session_id:
            payload["session_id"] = self.session_id

        response = await self.client.post(f"{self.base_url}/chat", json=payload)
        response.raise_for_status()

        result = response.json()
        self.session_id = result.get("session_id")
        return result

    async def execute_workflow(self, workflow: list, variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a custom workflow"""
        payload = {
            "workflow": workflow,
            "variables": variables or {}
        }

        response = await self.client.post(f"{self.base_url}/workflow", json=payload)
        response.raise_for_status()
        return response.json()

    async def execute_template(self, template_name: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow template"""
        response = await self.client.post(
            f"{self.base_url}/template/{template_name}",
            json=variables
        )
        response.raise_for_status()
        return response.json()

    async def list_models(self) -> Dict[str, Any]:
        """List available AI models"""
        response = await self.client.get(f"{self.base_url}/models")
        response.raise_for_status()
        return response.json()

    async def list_addons(self) -> Dict[str, Any]:
        """List available prompt addons"""
        response = await self.client.get(f"{self.base_url}/addons")
        response.raise_for_status()
        return response.json()

    async def list_templates(self) -> Dict[str, Any]:
        """List available workflow templates"""
        response = await self.client.get(f"{self.base_url}/templates")
        response.raise_for_status()
        return response.json()

    async def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        response = await self.client.get(f"{self.base_url}/stats")
        response.raise_for_status()
        return response.json()

    async def close(self):
        """Close the client"""
        await self.client.aclose()


async def test_basic_functionality():
    """Test basic API functionality"""
    print("="*80)
    print("TESTING BASIC FUNCTIONALITY")
    print("="*80)

    client = OrchestrationClient()

    try:
        # 1. Health check
        print("\n1. Health Check...")
        health = await client.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Models available: {health['models_available']}")

        # 2. List models
        print("\n2. Listing Available Models...")
        models = await client.list_models()
        print(f"   Total models: {models['count']}")
        for model in models['models'][:5]:
            print(f"   - {model['name']}: {model['purpose']}")

        # 3. List addons
        print("\n3. Listing Prompt Addons...")
        addons = await client.list_addons()
        print(f"   Total addons: {addons['count']}")
        print(f"   Sample addons: {', '.join(addons['addons'][:10])}")

        # 4. List templates
        print("\n4. Listing Workflow Templates...")
        templates = await client.list_templates()
        print(f"   Total templates: {templates['count']}")
        for template in templates['templates']:
            print(f"   - {template['name']}: {template['description']}")

        print("\n✅ Basic functionality tests passed!")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

    finally:
        await client.close()


async def test_simple_query():
    """Test a simple query (should be category M)"""
    print("\n" + "="*80)
    print("TESTING SIMPLE QUERY (Category M)")
    print("="*80)

    client = OrchestrationClient()

    try:
        query = "What are the main benefits of renewable energy?"
        print(f"\nQuery: {query}")

        response = await client.chat(query)

        print(f"\nResponse:")
        print(f"  Session ID: {response['session_id']}")
        print(f"  Category: {response.get('category', 'N/A')}")
        print(f"  Response: {response['response'][:500]}...")

        print("\n✅ Simple query test passed!")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

    finally:
        await client.close()


async def test_complex_task():
    """Test a complex task (should be category H)"""
    print("\n" + "="*80)
    print("TESTING COMPLEX TASK (Category H)")
    print("="*80)

    client = OrchestrationClient()

    try:
        query = """Create a brief marketing plan for an eco-friendly water bottle company.
        Include target audience analysis and 2 marketing channel recommendations."""

        print(f"\nQuery: {query}")

        response = await client.chat(query)

        print(f"\nResponse:")
        print(f"  Session ID: {response['session_id']}")
        print(f"  Category: {response.get('category', 'N/A')}")
        print(f"  Response: {response['response'][:1000]}...")

        print("\n✅ Complex task test passed!")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

    finally:
        await client.close()


async def test_custom_workflow():
    """Test custom workflow execution"""
    print("\n" + "="*80)
    print("TESTING CUSTOM WORKFLOW")
    print("="*80)

    client = OrchestrationClient()

    try:
        # Simple 2-step workflow
        workflow = [
            {
                "type": "inline",
                "tasks": [
                    {
                        "model": "thinking_ai",
                        "prompt": "List 3 key benefits of {topic}",
                        "output_variable": "benefits",
                        "config": {
                            "temperature": 0.7,
                            "max_tokens": 500
                        }
                    }
                ]
            },
            {
                "type": "inline",
                "tasks": [
                    {
                        "model": "thinking_ai",
                        "prompt": "Based on these benefits: {benefits}\n\nWrite a short paragraph explaining why {topic} is important.",
                        "output_variable": "summary",
                        "config": {
                            "temperature": 0.7,
                            "max_tokens": 500
                        }
                    }
                ]
            }
        ]

        variables = {
            "topic": "artificial intelligence"
        }

        print(f"\nExecuting workflow with topic: {variables['topic']}")

        response = await client.execute_workflow(workflow, variables)

        print(f"\nWorkflow Results:")
        print(f"  Status: {response['status']}")
        print(f"  Execution time: {response['execution_time']:.2f}s")
        print(f"\n  Benefits:\n{response['result'].get('benefits', 'N/A')}")
        print(f"\n  Summary:\n{response['result'].get('summary', 'N/A')}")

        print("\n✅ Custom workflow test passed!")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

    finally:
        await client.close()


async def test_workflow_template():
    """Test workflow template execution"""
    print("\n" + "="*80)
    print("TESTING WORKFLOW TEMPLATE")
    print("="*80)

    client = OrchestrationClient()

    try:
        # Use research_report template
        variables = {
            "topic": "electric vehicles"
        }

        print(f"\nExecuting research_report template with topic: {variables['topic']}")

        response = await client.execute_template("research_report", variables)

        print(f"\nTemplate Execution Results:")
        print(f"  Status: {response['status']}")
        print(f"  Execution time: {response['execution_time']:.2f}s")
        print(f"\n  Variables in result: {list(response['result'].keys())}")

        # Show snippet of each result
        for key, value in response['result'].items():
            if isinstance(value, str):
                print(f"\n  {key}: {value[:200]}...")

        print("\n✅ Workflow template test passed!")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

    finally:
        await client.close()


async def interactive_mode():
    """Interactive chat mode"""
    print("\n" + "="*80)
    print("INTERACTIVE MODE")
    print("="*80)
    print("Type 'quit' to exit, 'stats' for statistics, 'models' to list models")
    print("="*80)

    client = OrchestrationClient()

    try:
        while True:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            if user_input.lower() == 'quit':
                break

            if user_input.lower() == 'stats':
                stats = await client.get_stats()
                print(f"\nStats: {json.dumps(stats, indent=2)}")
                continue

            if user_input.lower() == 'models':
                models = await client.list_models()
                print(f"\nAvailable Models ({models['count']}):")
                for model in models['models']:
                    print(f"  - {model['name']}: {model['purpose']}")
                continue

            # Send chat message
            print("\nAI: Thinking...")
            response = await client.chat(user_input)
            print(f"\nAI: {response['response']}")

    except KeyboardInterrupt:
        print("\n\nExiting...")

    finally:
        await client.close()


async def main():
    """Main test runner"""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                  Master AI Orchestration System                            ║
║                         Test Client v1.0                                   ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

    print("\nSelect test mode:")
    print("1. Run all automated tests")
    print("2. Test basic functionality")
    print("3. Test simple query")
    print("4. Test complex task")
    print("5. Test custom workflow")
    print("6. Test workflow template")
    print("7. Interactive chat mode")
    print("0. Exit")

    choice = input("\nEnter choice (1-7): ").strip()

    if choice == "1":
        await test_basic_functionality()
        await test_simple_query()
        await test_complex_task()
        await test_custom_workflow()
        # await test_workflow_template()  # Uncomment if you want to test this too
    elif choice == "2":
        await test_basic_functionality()
    elif choice == "3":
        await test_simple_query()
    elif choice == "4":
        await test_complex_task()
    elif choice == "5":
        await test_custom_workflow()
    elif choice == "6":
        await test_workflow_template()
    elif choice == "7":
        await interactive_mode()
    elif choice == "0":
        print("Goodbye!")
        return
    else:
        print("Invalid choice!")

    print("\n" + "="*80)
    print("Testing Complete!")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
