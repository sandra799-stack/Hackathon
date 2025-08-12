from agent import GCPAIAgent
from config import AgentConfig

def main():
    config = AgentConfig()
    agent = GCPAIAgent(config)

    examples = [
        "Rank the top customers by sales in the last month",
        "Send a notification about our new product launch to the marketing team",
        "Create a marketing strategy for millennials to increase engagement",
    ]

    for i, example in enumerate(examples, 1):
        print(f"\nExample {i}: {example}")
        print(agent.chat(example))

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == 'quit':
            break
        print("Agent:", agent.chat(user_input))

if __name__ == "__main__":
    main()
