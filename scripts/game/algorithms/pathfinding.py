from __future__ import annotations

import heapq  # For priority queue
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Tuple, List


class Node:
    def __init__(self,
                 position: Tuple[int, int],
                 parent: Optional[Node] = None) -> None:
        """
        Args:
            position:
                A tuple representing the (x, y) position of the node.
            parent:
                The parent node of this node. Used for pathfinding to trace the route back to the start.
        """
        self.position = position  # (x, y)
        self.parent = parent  # The parent node
        self.g = 0  # Cost from start to this node
        self.h = 0  # Heuristic cost from this node to end
        self.f = 0  # Total cost

    def __eq__(self, other: Node) -> bool:
        """
        Args:
            other: The object to compare with.

        Returns:
            bool: True if both objects have the same position, else False.
        """
        return self.position == other.position

    def __lt__(self, other: Node) -> bool:
        """
        Args:
            other: An object to be compared with the current instance.

        Returns:
            bool: True if the 'f' attribute of the current instance
                  is less than the 'f' attribute of the 'other' object,
                  else False.
        """
        return self.f < other.f

    def __hash__(self) -> int:
        """
        Generates a hash value for the node's position attribute.

        Returns:
            int: The hash value computed from the position attribute of the node.
        """
        return hash(self.position)


def heuristic(a: Tuple[int, int], b: Tuple[int, int], enemy_positions_list) -> float:
    """
    Calculates the heuristic value using the Diagonal Distance formula.

    Args:
        enemy_positions_list: A list of the enemies positions.
        a: Tuple[int, int] representing the coordinates of the first point.
        b: Tuple[int, int] representing the coordinates of the second point.

    Returns:
        An integer representing the heuristic value.
    """
    # Calculate the differences in x and y coordinates
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    D_orthogonal = 1  # Cost for orthogonal movement
    D_diagonal = 1.414  # Cost for diagonal movement

    # Diagonal distance heuristic
    base_cost = D_orthogonal * (dx + dy) + (D_diagonal - 2 * D_orthogonal) * min(dx, dy)

    # Additional cost for enemy avoidance
    enemy_avoidance_cost = 0
    danger_radius = 10
    for enemy_pos in enemy_positions_list:
        # Calculate the Manhattan distance to the enemy's position
        dist_to_enemy = abs(a[0] - enemy_pos[0]) + abs(a[1] - enemy_pos[1])

        # If the tile is within the danger zone, add a penalty
        if dist_to_enemy <= danger_radius:
            enemy_avoidance_cost += danger_radius - dist_to_enemy  # The closer, the higher the penalty

    # Diagonal distance heuristic
    return base_cost + enemy_avoidance_cost


def calculate_costs(neighbour_node: Node,
                    open_set: List,
                    potential_g: int,
                    end_node: Node, enemy_positions_list) -> None:
    """
    Calculates the costs for the neighbour node.

    Args:
        enemy_positions_list: A list of the enemies positions.
        neighbour_node (Node): The neighboring node being evaluated.
        open_set (list[Node]): The list of nodes pending evaluation.
        potential_g (float): The potential 'g' value (cost from the start node).
        end_node (Node): The target node for the pathfinding algorithm
    """

    # Check if the neighbor node is not already in the open set
    # or if a shorter path to it has been found
    if neighbour_node not in open_set or potential_g < neighbour_node.g:
        # Updates the 'g' value (cost from start to the current node)
        neighbour_node.g = potential_g
        # Calculate the heuristic cost (estimated cost to the end node)
        neighbour_node.h = heuristic(neighbour_node.position, end_node.position, enemy_positions_list)
        # Calculate the total cost 'f' (sum of 'g' and 'h')
        neighbour_node.f = neighbour_node.g + neighbour_node.h
        # If the neighbor node is not in the open set, add it to the priority queue
        if neighbour_node not in open_set:
            heapq.heappush(open_set, neighbour_node)


def a_star(maze:  List[List[int]],
           start: Tuple[int, int],
           end:   Tuple[int, int], temp_list) -> List[Tuple[int, int]]:

    """
    Runs the A* search algorithm to find a path from start to end in a maze.

    Args:
        maze : The maze represented as a 2D list of integers.
        start : The starting coordinates (x, y).
        end : The ending coordinates (x, y).

    Returns:
        return: List[Tuple[int, int]]
            The resulting path from start to end.

    """

    # The starting position node (where the A* search algorithm starts)
    start_node = Node(start)
    # The ending position node (where the A* search algorithm ends)
    end_node = Node(end)
    # The open set of nodes to be evaluated
    open_set = []
    # The closed set of nodes that have been evaluated
    closed_set = set()

    # Push the start node to the open set
    heapq.heappush(open_set, start_node)

    while open_set:
        # Gets the current node
        current_node = heapq.heappop(open_set)
        # Adds the current node to the closed set
        closed_set.add(current_node)

        # Checks whether the current node is the end node
        if current_node == end_node:
            # Returns the path - a list of x and y coordinates
            return reconstruct_path(current_node)

        # A list of neighbour node x and y coordinates
        neighbours = get_neighbours(current_node.position, maze)

        # Loops through the x and y coordinates in neighbours
        for position in neighbours:
            # Creates a Node for the neighbours position
            neighbour_node = Node(position, current_node)

            # If the neighbour node has already been visited
            if neighbour_node in closed_set:
                # Skip this node and continue with the next iteration
                continue

            # Calculate costs
            potential_g = current_node.g + 1  # Assuming uniform cost for movement
            calculate_costs(neighbour_node, open_set, potential_g, end_node, temp_list)

    return []  # Return empty if no path is found

def get_neighbours(position, maze):
    # Empty neighbours list
    neighbours = []
    # Current x and y position in the maze
    x, y = position

    # Directions: right, left, down, up
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1)]

    # loops through the change in x and y directions
    for dx, dy in directions:
        # neighbour nodes x and y position
        nx, ny = x + dx, y + dy
        # Check if the new position is within the bounds of the maze and not a wall
        if 0 <= nx < len(maze) and 0 <= ny < len(maze[0]) and maze[nx][ny] != 1:
            # If the direction is diagonal
            if (dx, dy) in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                adj_cells = [(x + dx, y), (x, y + dy)]
                # Checks whether there is a corner of a wall between the diagonal path
                if any(0 <= adj_x < len(maze) and 0 <= adj_y < len(maze[0]) and maze[adj_x][adj_y] == 1 for adj_x, adj_y
                       in adj_cells):
                    # Don't add this node
                    continue
            # Add the neighbour node to the list of nodes
            neighbours.append((nx, ny))

    # Return the neighbour nodes
    return neighbours


def reconstruct_path(node):
    # Empty path list
    path = []
    while node is not None:
        # Adds the nodes position to the path
        path.append(node.position)
        # Gets the parent node (next node in path)
        node = node.parent
    # Return reversed path
    return path[::-1]


def adjust_path(maze, current_path: List[Tuple[int, int]], start: Tuple[int, int], end: Tuple[int, int]) -> List[
    Tuple[int, int]]:
    """
    Adjusts the path based on the current path and new obstacles.

    Args:
        maze : The maze represented as a 2D list.
        current_path : The previous path that needs adjustment.
        start : The starting coordinates (x, y).
        end : The ending coordinates (x, y).

    Returns:
        A new path list with adjusted or updated segments.
    """
    # Check if the last path segment is still valid
    last_valid_node = current_path[-1]  # Check from the last valid node
    # If the end is blocked, replan from the last valid node
    if maze[last_valid_node[0]][last_valid_node[1]] == 1:  # Wall check
        new_path = a_star(maze, last_valid_node, end)
        return current_path[:-1] + new_path  # Combine old valid path with new segment

    # Check if start position has changed
    if start != current_path[0]:
        new_start_path = a_star(maze, start, current_path[0])
        # Combine the new start path with the rest of the current path
        return new_start_path + current_path[len(new_start_path):]

    return current_path  # If no change, return the original path


def run_a_star_thread(maze: List[List[int]],
                      start: Tuple[int, int],
                      end: Tuple[int, int]) -> List[Tuple[int, int]]:

    """
    Runs the A* algorithm to find a path from start to end in a maze.

    Args:
        maze : The maze represented as a 2D list of integers.
        start : The starting coordinates (x, y).
        end : The ending coordinates (x, y).

    Returns:
        return: List[Tuple[int, int]]
            The resulting path from start to end.


    """
    return a_star(maze, start, end)


def a_star_multithreaded(maze: List[List[int]], start, end) -> List[Tuple[int, int]]:
    """


    """
    with ThreadPoolExecutor(max_workers=10) as executor:
        future = executor.submit(run_a_star_thread, maze, start, end)
        return future.result()

# import pytmx
# def load_tmx_to_array(file_path):
#     """
#     Load a TMX file and convert the tile layers to a 2D array.
#
#     Args:
#         file_path (str): Path to the TMX file.
#
#     Returns:
#         list of int: 2D array representing the tile map.
#     """
#     tmx_data = pytmx.TiledMap(file_path)
#
#     # Assuming you want to convert the first tile layer to a 2D array
#     layer = tmx_data.layers[0]
#     if isinstance(layer, pytmx.TiledTileLayer):
#         map_array = []
#         for y in range(layer.height):
#             row = []
#             for x in range(layer.width):
#                 gid = layer.data[y][x]  # Accessing via [y][x] to prevent index issues
#                 # Check if there's a tile at this location
#                 if gid != 0:
#                     row.append(1)
#                 else:
#                     row.append(0)
#             map_array.append(row)
#         return map_array
#     else:
#         raise TypeError("The selected layer is not a Tile Layer")

# def main():
#     import pygame
#     import sys
#     screen = pygame.display.set_mode((800, 640))
#     maze1 = [[1,1,1,1,1,1,1,1,1,1],
#              [1,0,0,0,0,0,1,0,0,1],
#              [1,0,0,0,0,0,1,1,0,1],
#              [1,0,0,1,1,0,0,0,0,1],
#              [1,1,0,0,0,0,0,1,1,1],
#              [1,0,0,0,1,1,0,0,0,1],
#              [1,0,0,0,1,0,0,0,0,1],
#              [1,1,1,0,1,0,0,1,0,1],
#              [1,0,1,0,0,0,0,1,0,1],
#              [1,1,1,1,1,1,1,1,1,1]]
#     maze1 = load_tmx_to_array(r"C:\Users\Daniel\My Drive\ComputerScienceCourseWork\scripts\game\levels\level1_simple.tmx")
#     print(maze1)
#     path1 = a_star(maze1, (1, 1), (38, 45))
#     path2 = a_star(maze1, (2, 2), (38, 43))
#     while True:
#         # Handles events in the Pygame window
#         for event in pygame.event.get():
#             # Checks if the QUIT event is triggered
#             if event.type == pygame.QUIT:
#                 # Quitting Pygame
#                 pygame.quit()
#                 # Closing the program
#                 sys.exit()
#
#         # Get the number of rows (outer list length)
#         rows = len(maze1)
#
#         # Get the number of columns (inner list length, assuming all rows have the same number of columns)
#         columns = len(maze1[0]) if rows > 0 else 0
#         print("Rows: ", rows, "Columns: ", columns)
#         for x, y in [(x, y) for x in range(40) for y in range(50)]:  # Draw the maze
#             if maze1[x][y] == 1:
#                 pygame.draw.rect(screen, (0, 0, 0), (y * 16, x * 16, 16, 16))
#             else:
#                 pygame.draw.rect(screen, (255, 255, 255), (y * 16, x * 16, 16, 16))
#
#
#         for node in path1:
#             pygame.draw.rect(screen, (0, 200, 0), (node[1] * 16, node[0] * 16, 16, 16))
#         for node in path2:
#             pygame.draw.rect(screen, (0, 200, 200), (node[1] * 16, node[0] * 16, 16, 16))
#         # Iterate through the common elements of path1 and path2
#         for value in [v for v in path1 if v in path2]:
#             pygame.draw.rect(screen, (200, 200, 0), (value[1] * 16, value[0] * 16, 16, 16))
#         pygame.display.flip()
#
# main()