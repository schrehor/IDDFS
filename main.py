from itertools import count


# vlastny sposob hashovania stavov
def hash_layout(layouts):
    hash = ""
    for layout in layouts:
        hash += layout.color[:1]
        hash += str(layout.y)
        hash += str(layout.x)
    return hash


class Layout:
    def __init__(self, color, size, y, x, direction):
        self.color = color
        self.size = size
        self.y = y
        self.x = x
        self.direction = direction

    # skopiruje hodnoty jedneho stavu do druheho na principe copy by value
    def copy_layout(self, y, x):
        return Layout(self.color, self.size, y, x, self.direction)


class Node:
    def __init__(self, layout, last_layout, last_operator, depth):
        self.depth = depth
        self.last_operator = last_operator
        self.last_layout = last_layout
        self.layout = layout

    # pretvori stavy na dvojrozmerne pole, volne miesta su reprezentovane 0, vozidla 1
    def make_map(self, node):
        map = [[0 for column in range(6)] for row in range(6)]
        return self.mark_vehicles(map, node)

    # do 2d pola vlozi vozidla tym, ze zmeni 0 na 1
    def mark_vehicles(self, map, node):
        for layout in node.layout:
            x = layout.x - 1
            y = layout.y - 1
            if layout.direction == "v":
                map[y][x] = 1
                map[layout.y][x] = 1
                if layout.size == 3:
                    map[layout.y + 1][x] = 1
            elif layout.direction == "h":
                map[y][x] = 1
                map[y][layout.x] = 1
                if layout.size == 3:
                    map[y][layout.x + 1] = 1
        return map

    # zisti ci bol dany stav uz navstiveny
    def check_visited(self, new_node, visited):
        hash = hash_layout(new_node.layout)
        if hash in visited:
            if visited[hash].depth <= new_node.depth:
                return False
            else:
                return True
        else:
            return True

    # skopiruje pole stavov do noveho pola stavov na principe copy by value
    def copy_layouts_list(self, new_layout, list_layouts, layout):
        new_layouts = list_layouts[:]
        new_layouts[list_layouts.index(layout)] = new_layout
        return new_layouts

    # skontroluje ci sa vozidlo moze pohnut dolava, ak ano, tak prida nove stavy do stacku
    def check_left(self, layout, map, visited):
        layouts = self.layout[:]
        move_list = []
        x = layout.x - 1
        y = layout.y - 1

        for counter in range(1, 5):
            if x - counter >= 0 and map[y][x - counter] == 0:
                new_layout = layout.copy_layout(layout.y, layout.x - counter)
                new_layouts = self.copy_layouts_list(new_layout, layouts, layout)
                new_node = Node(new_layouts, self, "Left " + new_layout.color + " " + str(counter), self.depth + 1)
                if self.check_visited(new_node, visited):
                    move_list.append(new_node)
            else:
                break

        return move_list

    # skontroluje ci sa vozidlo moze pohnut doprava, ak ano, tak prida nove stavy do stacku
    def check_right(self, layout, map, visited):
        layouts = self.layout[:]
        move_list = []
        x = layout.x - 1
        y = layout.y - 1

        for counter in range(1, 5):
            if x + layout.size + counter - 1 <= 5 and map[y][x + layout.size + counter - 1] == 0:
                new_layout = layout.copy_layout(layout.y, layout.x + counter)
                new_layouts = self.copy_layouts_list(new_layout, layouts, layout)
                new_node = Node(new_layouts, self, "Right " + new_layout.color + " " + str(counter), self.depth + 1)
                if self.check_visited(new_node, visited):
                    move_list.append(new_node)
            else:
                break

        return move_list

    # skontroluje ci sa vozidlo moze pohnut hore, ak ano, tak prida nove stavy do stacku
    def check_up(self, layout, map, visited):
        layouts = self.layout[:]
        move_list = []
        x = layout.x - 1
        y = layout.y - 1

        for counter in range(1, 5):
            if y - counter >= 0 and map[y - counter][x] == 0:
                new_layout = layout.copy_layout(layout.y - counter, layout.x)
                new_layouts = self.copy_layouts_list(new_layout, layouts, layout)
                new_node = Node(new_layouts, self, "Up " + new_layout.color + " " + str(counter), self.depth + 1)
                if self.check_visited(new_node, visited):
                    move_list.append(new_node)
            else:
                break

        return move_list

    # skontroluje ci sa vozidlo moze pohnut dole, ak ano, tak prida nove stavy do stacku
    def check_down(self, layout, map, visited):
        layouts = self.layout[:]
        move_list = []
        x = layout.x - 1
        y = layout.y - 1

        for counter in range(1, 5):
            if y + layout.size + counter - 1 <= 5 and map[y + layout.size + counter - 1][x] == 0:
                new_layout = layout.copy_layout(layout.y + counter, layout.x)
                new_layouts = self.copy_layouts_list(new_layout, layouts, layout)
                new_node = Node(new_layouts, self, "Down " + new_layout.color + " " + str(counter), self.depth + 1)
                if self.check_visited(new_node, visited):
                    move_list.append(new_node)
            else:
                break

        return move_list

    # skusi pohnut vozidlom do vsetkych moznych stran, ak sa podari prida stavy do stacku
    def move(self, visited):
        layouts = self.layout
        map = self.make_map(self)
        new_node = []

        for vehicle in layouts:
            if vehicle.direction == "h":
                new_node.extend(self.check_left(vehicle, map, visited))
                new_node.extend(self.check_right(vehicle, map, visited))
            elif vehicle.direction == "v":
                new_node.extend(self.check_up(vehicle, map, visited))
                new_node.extend(self.check_down(vehicle, map, visited))

        return new_node

    # funkcia zisti ci ide o finalny stav
    def success(self):
        if self.layout[0].size == 2 and self.layout[0].x == 5:
            return True
        elif self.layout[0].size == 3 and self.layout[0].x == 4:
            return True

        return False


class Tree:
    def __init__(self, node):
        self.node = node

    # pre kazdu hlbku skusi vyhladavanie do hlbky, ak je uspesne, tak vypise cestu
    def iddfs(self):
        memory = 0
        for depth in count(0):
            node, visited = self.dfs(depth)
            if node is not None:
                self.path(node)
                break
            elif memory == visited:
                print("Neexistuje riesenie")
                break
            memory = visited

    # prehladavanie do hlbky s tym, ze je ohranicene maximalnou hlbkou
    def dfs(self, depth):
        stack = [self.node]
        higher_depth = []
        visited = {}

        while stack:
            current_node = stack.pop()
            hash = hash_layout(current_node.layout)
            visited[hash] = current_node

            if depth >= current_node.depth:
                if current_node.success():
                    return current_node, len(visited)
                stack.extend(current_node.move(visited))
            else:
                continue

            higher_depth.extend([item for item in stack if item.depth > depth])
            stack = [item for item in stack if item.depth <= depth]

        return None, len(visited)

    # vypise cestu akou sa vozidla museli posunut
    def path(self, node):
        path = []
        depth = node.depth

        while node.last_operator is not None:
            path.append(node.last_operator)
            node = node.last_layout

        print("Celkova dlzka cesty je: ", depth)
        print("Postup krokov:")

        path.reverse()
        for item in path:
            print(item)


# ma riesenie

layout_assignment = [Layout("red", 2, 3, 2, "h"), Layout("orange", 2, 1, 1, "h"), Layout("yellow", 3, 2, 1, "v"),
                     Layout("purple", 2, 5, 1, "v"), Layout("green", 3, 2, 4, "v"), Layout("blue", 3, 6, 3, "h"),
                     Layout("grey", 2, 5, 5, "h"), Layout("white", 3, 1, 6, "v")]

layout8 = [Layout("red", 2, 3, 3, "h"), Layout("orange", 3, 1, 5, "v"), Layout("yellow", 2, 6, 5, "h"),
           Layout("purple", 2, 2, 2, "h"), Layout("green", 3, 4, 3, "v"), Layout("blue", 3, 2, 6, "v"),
           Layout("white", 2, 2, 1, "v")]

layout9 = [Layout("red", 2, 1, 1, "h"), Layout("orange", 2, 1, 3, "v"), Layout("yellow", 2, 1, 5, "v"),
           Layout("purple", 2, 2, 2, "v"), Layout("green", 3, 3, 3, "h"), Layout("blue", 3, 4, 1, "h"),
           Layout("grey", 2, 4, 4, "v"), Layout("white", 2, 6, 4, "h")]

layout4 = [Layout("red", 2, 3, 2, "h"), Layout("orange", 3, 1, 5, "v"), Layout("yellow", 3, 3, 4, "v"),
           Layout("green", 2, 6, 3, "h")]

layout3 = [Layout("red", 2, 3, 2, "h"), Layout("orange", 3, 1, 6, "v"), Layout("yellow", 3, 3, 5, "v")]

layout6 = [Layout("red", 2, 2, 2, "h"), Layout("orange", 3, 1, 5, "v"), Layout("yellow", 3, 1, 6, "v"),
           Layout("purple", 3, 4, 4, "h"), Layout("green", 2, 4, 3, "v"), Layout("blue", 2, 6, 3, "h")]

layout1 = [Layout("red", 2, 3, 4, "h"), Layout("orange", 3, 1, 1, "v"), Layout("yellow", 3, 3, 2, "v")]

layout0 = [Layout("red", 2, 3, 5, "h"), Layout("orange", 3, 1, 1, "v"), Layout("yellow", 3, 3, 2, "v")]

# nema riesenie

layoutN1 = [Layout("red", 2, 3, 2, "h"), Layout("orange", 2, 1, 1, "h"), Layout("yellow", 3, 2, 1, "v"),
            Layout("purple", 2, 5, 1, "v"), Layout("green", 3, 4, 6, "v"), Layout("blue", 3, 6, 3, "h"),
            Layout("grey", 2, 5, 4, "h"), Layout("white", 3, 1, 6, "v")]

layoutN2 = [Layout("red", 2, 3, 1, "h"), Layout("orange", 3, 1, 6, "v"), Layout("yellow", 3, 4, 6, "v")]

layoutN3 = [Layout("red", 2, 3, 1, "h"), Layout("orange", 3, 2, 6, "v"), Layout("yellow", 2, 5, 6, "v")]


start_node = Node(layoutN1, None, None, 0)
tree = Tree(start_node)
tree.iddfs()