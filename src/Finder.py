from thefuzz import process


class Finder:
    def __init__(self):
        pass

    @staticmethod
    def get_best_match_for_each_entry(data: dict, query: str) -> list:
        best_matches = []
        for key, entry in data.items():
            best_match = process.extractOne(query, entry["values"])
            best_matches.append((key, best_match[0], best_match[1]))
        return best_matches

    @staticmethod
    def fuzzy_search(data: dict, query: str, top_n=5) -> list:
        best_matches = Finder.get_best_match_for_each_entry(data, query)
        best_matches.sort(key=lambda x: x[2], reverse=True)
        return best_matches[:top_n]


if __name__ == "__main__":
    find = Finder()
