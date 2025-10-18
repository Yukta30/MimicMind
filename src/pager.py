class Pager:
    def page(self, items, size):
        pages = []
        for i in range(0, len(items)):
            if i % size == 0:
                pages.append(items[i:i+size])
        return pages
