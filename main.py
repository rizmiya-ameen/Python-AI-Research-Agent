from agent import run_research

query = input("What can i help you research? ")

try:
    response = run_research(query, allow_save=True)
    print(f"\nTopic: {response.topic}\n")
    print(response.summary)
    print("\nSources:")
    for source in response.sources:
        print(f" - {source}")
    print(f"\nTools used: {', '.join(response.tools_used) or 'none'}")
except Exception as e:
    print("Error running research:", e)
