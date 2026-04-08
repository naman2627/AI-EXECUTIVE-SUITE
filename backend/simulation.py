class SimulationRunner:
    def run_simulation(self, steps=5):
        results = []

        revenue = 1000
        cash = 5000
        bugs = 50

        for step in range(steps):
            revenue += 200 + (step * 50)
            cash += revenue - 1500
            bugs = max(0, bugs - 5)

            results.append({
                "ceo": {"state": {"revenue": revenue}},
                "cfo": {"state": {"cash": cash}},
                "cto": {"state": {"bug_count": bugs}},
            })

        return results
