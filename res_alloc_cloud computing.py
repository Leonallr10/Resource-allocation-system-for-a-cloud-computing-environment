import hashlib
from queue import PriorityQueue


class Resource:
    def __init__(self, id, priority):
        self.id = id
        self.priority = priority


class MerkleTree:
    def __init__(self):
        self.root = None

    def construct_tree(self, resources):
        self.root = self._construct_tree_recursive(resources)

    def _construct_tree_recursive(self, resources):
        if len(resources) == 1:
            return resources[0]
        else:
            left_child = self._construct_tree_recursive(resources[:len(resources) // 2])
            right_child = self._construct_tree_recursive(resources[len(resources) // 2:])
            combined_hash = self._combine_hashes(left_child, right_child)
            return Resource(combined_hash, 0)  # Create a new Resource with the combined hash

    def _combine_hashes(self, hash1, hash2):
        combined_hash = str(hash1) + str(hash2)
        return hashlib.sha256(combined_hash.encode()).hexdigest()

    def update_tree(self, allocated_resource):
        resource_list = self._get_resource_list()
        resource_list.append(allocated_resource)
        self.construct_tree(resource_list)

    def verify_integrity(self):
        resource_list = self._get_resource_list()
        computed_hash = self._compute_hash(resource_list)
        return computed_hash == self.root.id

    def _get_resource_list(self):
        resource_list = []
        self._traverse_tree(self.root, resource_list)
        return resource_list

    def _traverse_tree(self, node, resource_list):
        if node is not None:
            if isinstance(node, Resource):
                resource_list.append(node)
            else:
                self._traverse_tree(node.left, resource_list)
                self._traverse_tree(node.right, resource_list)

    def _compute_hash(self, resources):
        hash_input = ''.join([resource.id + str(resource.priority) for resource in resources])
        return hashlib.sha256(hash_input.encode()).hexdigest()


class ResourceAllocator:
    def __init__(self):
        self.priority_queue = PriorityQueue()
        self.merkle_tree = MerkleTree()

    def initialize_resources(self, resource_list):
        for resource in resource_list:
            self.priority_queue.add_resource(resource)
        self.merkle_tree.construct_tree(resource_list)

    def allocate_resource(self, allocation_request):
        allocated_resource = self.priority_queue.get_highest_priority_resource()
        self.priority_queue.remove_resource(allocated_resource)
        self.merkle_tree.update_tree(allocated_resource)
        return allocated_resource

    def deallocate_resource(self, allocated_resource):
        self.priority_queue.add_resource(allocated_resource)
        self.merkle_tree.update_tree(allocated_resource)

    def verify_merkle_tree_integrity(self):
        return self.merkle_tree.verify_integrity()


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
allocation_request = "Some criteria for resource allocation"
allocated_resource = resource_allocator.allocate_resource(allocation_request)
print("Allocated Resource:", allocated_resource.id)

# Deallocate resource
resource_allocator.deallocate_resource(allocated_resource)

# Verify Merkle tree integrity
is_integrity_verified = resource_allocator.verify_merkle_tree_integrity()
print("Merkle Tree Integrity Verified:", is_integrity_verified)
