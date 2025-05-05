import time, random 
import matplotlib.pyplot as plt

class Recommender:
    def __init__(self, content_features):
        self.user_profiles = {}
        self.content_features = content_features

    def record_interaction(self, user_id: str, tag: str, score: float = 1.0):
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {}
        if tag not in self.user_profiles[user_id]:
            self.user_profiles[user_id][tag] = 0
        self.user_profiles[user_id][tag] += score

class ListRecommender:
    def __init__(self, content_features):
        self.user_profiles = []
        self.content_features = list(content_features.items())

    def record_interaction(self, user_id: str, tag: str, score: float = 1.0):
        for uid, profile in self.user_profiles:
            if uid == user_id:
                break
        else:
            profile = {}
            self.user_profiles.append([user_id, profile])
        if tag not in profile:
            profile[tag] = 0
        profile[tag] += score


def simulate_interactions(num_interactions, content_features, user_ids=None):
    if user_ids is None:
        user_ids = [f"user{i}" for i in range(1, 1001)]
    tags = list({tag for feats in content_features.values() for tag in feats})
    interactions = []
    for _ in range(num_interactions):
        user = random.choice(user_ids)
        tag = random.choice(tags)
        score = random.random()
        interactions.append((user, tag, score))
    return interactions


def benchmark(recommender, interactions):
    start_rec = time.perf_counter()
    for user_id, tag, score in interactions:
        recommender.record_interaction(user_id, tag, score)
    elapsed_rec = time.perf_counter() - start_rec
    return elapsed_rec


def compare_growth(content_features, interaction_sizes):
    implementations = [
        ("Dict", Recommender),
        ("List", ListRecommender)
    ]
    times = {name: [] for name, _ in implementations}
    for name, Impl in implementations:
        for n in interaction_sizes:
            rec = Impl(content_features)
            interactions = simulate_interactions(n, content_features)
            t_rec = benchmark(rec, interactions)
            times[name].append(t_rec)
            print(f"{name} - Interactions: {n:>5}, Record: {t_rec:.4f}s")
    print("\nComparison Summary:")
    for i, n in enumerate(interaction_sizes):
        line = f"{n:>5}: "
        for name, _ in implementations:
            line += f"{name} {times[name][i]:.8f}s; "
        print(line)
    xs = interaction_sizes
    for name, _ in implementations:
        plt.plot(xs, times[name], marker='o', label=f'{name}')
    plt.xlabel('Number of interactions')
    plt.ylabel('Time (s)')
    plt.title('Insertions Growth: Dict vs List')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    content = {
        "video1": {"sports": 2, "news": 1},
        "video2": {"cats": 3},
        "video3": {"sports": 1, "cats": 1},
        "video4": {"news": 2, "technology": 2},
    }
    interaction_sizes = list(range(100, 10001, 100))
    compare_growth(content, interaction_sizes)
