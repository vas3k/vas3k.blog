def parse_classes(value):
    return [
        klass for klass in str(value or "").split(".") if klass and not klass.startswith("#")
    ]


def parse_ids(value):
    return [
        klass[1:] for klass in str(value or "").split(".") if klass and klass.startswith("#")
    ]


def parse_classes_and_ids(value):
    classes = parse_classes(value)
    ids = parse_ids(value)
    return classes, ids
