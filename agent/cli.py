from __future__ import annotations

from agent.graph_builder import build_graph


def run_cli() -> None:
    graph = build_graph()

    print("=" * 60)
    print("TravelBuddy - Trợ lý Du lịch Thông minh")
    print("Gõ 'quit' để thoát")
    print("=" * 60)

    messages = []
    while True:
        user_input = input("\nBạn: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break

        print("\nTravelBuddy đang suy nghĩ...")
        messages.append(("human", user_input))

        result = graph.invoke({"messages": messages})
        final = result["messages"][-1]

        messages.append(("assistant", final.content))
        if hasattr(final, "content") and final.content:
            print(f"\nTravelBuddy: {final.content}")
        else:
            print("\nTravelBuddy: (Không có phản hồi)")


if __name__ == "__main__":
    run_cli()