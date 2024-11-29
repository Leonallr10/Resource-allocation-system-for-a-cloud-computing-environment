import hashlib
from queue import PriorityQueue
import networkx as nx
import matplotlib.pyplot as plt


class Resource:
    def __init__(self, id, priority):
        self.id = id
        self.priority = priority

    def __lt__(self, other):
        return self.priority < other.priority

    def __repr__(self):
        return f"Resource(id={self.id}, priority={self.priority})"


class MerkleNode:
    def __init__(self, left=None, right=None, value=None):
        self.left = left
        self.right = right
        self.value = value

    def __repr__(self):
        return f"MerkleNode(value={self.value})"


class MerkleTree:
    def __init__(self):
        self.root = None
        self.graph = nx.DiGraph()

    def construct_tree(self, resources):
        print("Constructing Merkle Tree...")
        nodes = [MerkleNode(value=r.id) for r in resources]
        while len(nodes) > 1:
            new_level = []
            for i in range(0, len(nodes), 2):
                left = nodes[i]
                right = nodes[i + 1] if i + 1 < len(nodes) else left
                combined_hash = self._combine_hashes(left.value, right.value)
                parent = MerkleNode(left=left, right=right, value=combined_hash)
                new_level.append(parent)

                # Add to graph for visualization
                self.graph.add_edge(parent.value, left.value, label="Left")
                self.graph.add_edge(parent.value, right.value, label="Right")
            nodes = new_level
        self.root = nodes[0]
        print("Merkle Tree construction complete.")

    def _combine_hashes(self, hash1, hash2):
        combined_hash = hash1 + hash2
        return hashlib.sha256(combined_hash.encode()).hexdigest()

    def plot_tree(self):
        print("\nVisualizing Merkle Tree with Enhanced Labels...")
        pos = nx.spring_layout(self.graph)
        node_colors = [
            "lightgreen" if node == self.root.value else "skyblue" if "VM" in node else "lightcoral"
            for node in self.graph.nodes()
        ]
        labels = {node: f"Root\n{node}" if node == self.root.value else node for node in self.graph.nodes()}
        
        nx.draw(
            self.graph,
            pos,
            with_labels=True,
            labels=labels,
            node_size=3000,
            node_color=node_colors,
            font_size=9,
        )
        nx.draw_networkx_edge_labels(
            self.graph,
            pos,
            edge_labels={(u, v): d["label"] for u, v, d in self.graph.edges(data=True)},
        )
        plt.title("Merkle Tree Structure")
        plt.show()


class ResourceAllocator:
    def __init__(self):
        self.priority_queue = PriorityQueue()
        self.merkle_tree = MerkleTree()
        self.resources = []

    def initialize_resources(self, resource_list):
        print("\nInitializing Resources...")
        self.resources = resource_list
        for resource in resource_list:
            self.priority_queue.put(resource)
            print(f"Added {resource} to Priority Queue.")
        self.merkle_tree.construct_tree(resource_list)

    def allocate_resource(self, allocation_request):
        print(f"\nAllocating resource based on request: {allocation_request}")
        if self.priority_queue.empty():
            raise Exception("No resources available")
        allocated_resource = self.priority_queue.get()
        print(f"Allocated Resource: {allocated_resource}")
        self.resources.remove(allocated_resource)
        self.merkle_tree.construct_tree(self.resources)
        return allocated_resource

    def deallocate_resource(self, allocated_resource):
        print(f"\nDeallocating Resource: {allocated_resource}")
        self.priority_queue.put(allocated_resource)
        self.resources.append(allocated_resource)
        self.merkle_tree.construct_tree(self.resources)

    def verify_merkle_tree_integrity(self):
        print("\nVerifying Merkle Tree Integrity...")
        if self.merkle_tree.root:
            print(f"Root hash is {self.merkle_tree.root.value}")
            return True
        return False


# Example usage
resource_allocator = ResourceAllocator()

# Initialize resources
resource_list = [
    Resource("VM1", 2),
    Resource("VM2", 1),
    Resource("VM3", 3)
]
resource_allocator.initialize_resources(resource_list)

# Allocate resources
allocation_request = "High-priority task"
allocated_resource = resource_allocator.allocate_resource(allocation_request)

# Deallocate resource
resource_allocator.deallocate_resource(allocated_resource)

# Verify Merkle tree integrity
is_integrity_verified = resource_allocator.verify_merkle_tree_integrity()
print(f"\nMerkle Tree Integrity Verified: {is_integrity_verified}")

# Plot the Merkle Tree
resource_allocator.merkle_tree.plot_tree()
