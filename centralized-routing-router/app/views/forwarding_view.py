class ForwardingView:
    """
    View responsible for printing forwarding decisions.
    """

    @staticmethod
    def display(result):
        """
        Print a forwarding simulation result.
        """
        router_id = result.get("router_id", "UNKNOWN")
        decision = result.get("decision", {})

        print("")
        print(f"Forwarding simulation at router {router_id}")
        print("-" * 72)

        action = decision.get("action")

        if action == "FORWARD":
            print(f"Destination: {decision.get('destination')}")
            print(f"Action:      FORWARD")
            print(f"Next hop:    {decision.get('next_hop')}")
            print(f"Match:       {decision.get('matched_prefix')}/{decision.get('prefix_length')}")
            print(f"Cost:        {decision.get('cost')}")
            print(f"Path:        {' -> '.join(decision.get('path', []))}")

        elif action == "DROP":
            print(f"Destination: {decision.get('destination')}")
            print(f"Action:      DROP")
            print(f"Reason:      {decision.get('reason')}")

        else:
            print("Unknown forwarding decision.")

        print("-" * 72)