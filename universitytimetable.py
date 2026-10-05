# University Timetable Room Minimizer
# Approach: Conflict Graph Construction + Greedy Graph Coloring


class UniversityTimetableScheduler:
    def __init__(self):
        # List of class sessions: each session is a dict
        self.classes: list[dict] = []
        # Adjacency list representation of the conflict graph
        self.graph: dict[int, list[int]] = {}

    def add_class(self, class_id, course_name, instructor, batch, timeslot):
        """Adds a scheduled class session to the system."""
        self.classes.append({
            "id": class_id,
            "course": course_name,
            "instructor": instructor,
            "batch": batch,
            "timeslot": timeslot,
        })

    def validate_no_hard_conflicts(self):
        """
        Ensures no instructor or student batch is scheduled
        in two different classes at the exact same timeslot.
        """
        n = len(self.classes)
        for i in range(n):
            for j in range(i + 1, n):
                c1 = self.classes[i]
                c2 = self.classes[j]
                if c1["timeslot"] == c2["timeslot"]:
                    if c1["instructor"] == c2["instructor"]:
                        raise ValueError(
                            f"Instructor Clash: {c1['instructor']} is assigned to both "
                            f"\"{c1['course']}\" and \"{c2['course']}\" at {c1['timeslot']}."
                        )
                    if c1["batch"] == c2["batch"]:
                        raise ValueError(
                            f"Batch Clash: Batch {c1['batch']} has concurrent classes "
                            f"\"{c1['course']}\" and \"{c2['course']}\" at {c1['timeslot']}."
                        )

    def build_conflict_graph(self):
        """
        Builds a graph where:
        - Vertices = Classes
        - Edge = Exists if two classes run during the SAME timeslot
                 (meaning they cannot share the same classroom).
        """
        self.graph = {c["id"]: [] for c in self.classes}
        n = len(self.classes)

        for i in range(n):
            for j in range(i + 1, n):
                c1 = self.classes[i]
                c2 = self.classes[j]
                # If two classes overlap in time, add an undirected conflict edge
                if c1["timeslot"] == c2["timeslot"]:
                    self.graph[c1["id"]].append(c2["id"])
                    self.graph[c2["id"]].append(c1["id"])

    def allocate_rooms_greedy(self):
        """
        Applies Greedy Graph Coloring to allocate classrooms.
        Colors represent individual Room numbers (Room 1, Room 2, ...).
        """
        # Dictionary to store assigned room (color) for each class
        # -1 means unassigned
        room_assignment = {c["id"]: -1 for c in self.classes}

        # Order nodes by degree descending (Welsh-Powell heuristic)
        # to achieve a more compact room allocation
        ordered_classes = sorted(
            self.classes,
            key=lambda c: len(self.graph[c["id"]]),
            reverse=True,
        )

        for current_class in ordered_classes:
            class_id = current_class["id"]

            # Find all rooms currently used by conflicting neighbors
            neighbor_rooms = set()
            for neighbor_id in self.graph[class_id]:
                assigned_room = room_assignment[neighbor_id]
                if assigned_room != -1:
                    neighbor_rooms.add(assigned_room)

            # Assign the lowest available room index starting from 1
            room_num = 1
            while room_num in neighbor_rooms:
                room_num += 1

            room_assignment[class_id] = room_num

        return room_assignment

    def display_schedule(self, room_assignment):
        """Formats and displays the final allocation table."""
        total_rooms = max(room_assignment.values()) if room_assignment else 0
        print("=" * 80)
        print("                OPTIMIZED UNIVERSITY TIMETABLE & ROOM ALLOCATION")
        print("=" * 80)
        print(f"{'Class ID':<10}{'Course':<18}{'Instructor':<16}{'Batch':<12}{'Timeslot':<14}{'Room':<10}")
        print("-" * 80)

        for c in sorted(self.classes, key=lambda x: (x["timeslot"], room_assignment[x["id"]])):
            cid = c["id"]
            room_name = f"Room-{room_assignment[cid]}"
            print(f"{cid:<10}{c['course']:<18}{c['instructor']:<16}{c['batch']:<12}{c['timeslot']:<14}{room_name:<10}")

        print("-" * 80)
        print(f"Minimum Practical Classrooms Required: {total_rooms}")
        print("=" * 80)


# --- Driver Code for Demonstration ---
if __name__ == "__main__":
    scheduler = UniversityTimetableScheduler()

    # Sample university workload with multiple batches and instructors
    sample_classes = [
        (101, "DAA", "PRATHEEK", "DS-B", "Mon 09:00-10:00"),
        (102, "BWT", "ADITHYA", "DS-B", "Mon 09:00-10:00"),
        (103, "DE", "AKSHAJ", "DS-C", "Mon 09:00-10:00"),
        (104, "P&S", "TEJAS", "DS-B", "Mon 10:00-11:00"),
        (105, "LR", "VIGNESH", "DS-C", "Mon 10:00-11:00"),
        (106, "ACS", "GANESH", "DS-A", "Mon 10:00-11:00"),
        (107, "COI", "DANNY", "DS-A", "Mon 11:00-12:00"),
        (108, "GEN AI", "HARSHITH", "DS-B", "Mon 11:00-12:00"),
    ]

    for item in sample_classes:
        scheduler.add_class(item[0], item[1], item[2], item[3], item[4])

    try:
        # Step 1: Check for double-booked professors or student batches
        scheduler.validate_no_hard_conflicts()

        # Step 2: Build the interference/conflict graph
        scheduler.build_conflict_graph()

        # Step 3: Run Greedy Coloring to minimize classrooms
        allocations = scheduler.allocate_rooms_greedy()

        # Step 4: Display Output
        scheduler.display_schedule(allocations)

    except ValueError as err:
        print(f"Scheduling Error: {err}")