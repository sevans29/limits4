class ProductNode:
    def __init__(self, level, name, limit, tenor):
        self.level = level
        self.name = name
        self.limit = limit
        self.tenor = tenor
        self.children = []
        self.transactions = []

    def add_child(self, child_node):
        self.children.append(child_node)

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def get_total_transactions(self):
        total = sum(txn['amount'] for txn in self.transactions)
        for child in self.children:
            total += child.get_total_transactions()
        return total

    def get_max_transaction_tenor(self):
        tenors = [txn['tenor'] for txn in self.transactions]
        for child in self.children:
            tenors.append(child.get_max_transaction_tenor())
        return max(tenors) if tenors else 0

    def validate_limits(self):
        errors = []
        total = self.get_total_transactions()
        max_tenor = self.get_max_transaction_tenor()

        if total > self.limit:
            errors.append(f"[LIMIT BREACH] {self.name} (Level {self.level}) - {total} > {self.limit}")
        if max_tenor > self.tenor:
            errors.append(f"[TENOR BREACH] {self.name} (Level {self.level}) - {max_tenor} > {self.tenor}")
        for child in self.children:
            errors.extend(child.validate_limits())
        return errors

    def print_structure(self, indent=0):
        print("  " * indent + f"{self.name} (Level {self.level}): Limit={self.limit}, Tenor={self.tenor}")
        for child in self.children:
            child.print_structure(indent + 1)

# Sample Transaction File (in-memory)
transactions = [
    {"path": ["Level 1", "Product 1", "Product 1A"], "amount": 1_000, "tenor": 10},
    # {"path": ["Level 1", "Product 1", "Product 1A"], "amount": 500_000, "tenor": 10},
    {"path": ["Level 1", "Product 1", "Product 1B"], "amount": 200_000, "tenor": 11},
    {"path": ["Level 1", "Product 1", "Product 1C"], "amount": 225_000, "tenor": 18},
    {"path": ["Level 1", "Product 2", "Product 2A"], "amount": 200_000, "tenor": 6},
    {"path": ["Level 1", "Product 2", "Product 2B"], "amount": 100_000, "tenor": 6},
    {"path": ["Level 1", "Product 2", "Product 2C"], "amount": 199_000, "tenor": 18},
]

# Build hierarchy
def build_sample_hierarchy():
    root = ProductNode(1, "Level 1", 1_000_000, 24)

    p1 = ProductNode(2, "Product 1", 600_000, 18)
    p1.add_child(ProductNode(3, "Product 1A", 200_000, 12))
    p1.add_child(ProductNode(3, "Product 1B", 250_000, 12))
    p1.add_child(ProductNode(3, "Product 1C", 250_000, 18))

    p2 = ProductNode(2, "Product 2", 500_000, 24)
    p2.add_child(ProductNode(3, "Product 2A", 200_000, 24))
    p2.add_child(ProductNode(3, "Product 2B", 150_000, 6))
    p2.add_child(ProductNode(3, "Product 2C", 220_000, 18))

    root.add_child(p1)
    root.add_child(p2)

    return root

# Assign transactions to hierarchy
def assign_transactions(root, transactions):
    def find_node(node, path):
        if node.name == path[0]:
            if len(path) == 1:
                return node
            for child in node.children:
                result = find_node(child, path[1:])
                if result:
                    return result
        return None

    for txn in transactions:
        node = find_node(root, txn["path"])
        if node:
            node.add_transaction(txn)
        else:
            print(f"Transaction path not found: {txn['path']}")

# UI
def main():
    root = build_sample_hierarchy()
    assign_transactions(root, transactions)

    print("Financial Product Structure:")
    print("                            ")
    root.print_structure()

    print("\n           Validation Results:")
    errors = root.validate_limits()
    if errors:
        for err in errors:
            print(" -", err)
    else:
        print("           No breaches found.")

if __name__ == "__main__":
    main()
