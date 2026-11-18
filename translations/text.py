from difflib import SequenceMatcher

from translations.ai import translate_texts
from vas3k_blog.exceptions import TranslationError


def changed_ranges(previous, current):
    for group in SequenceMatcher(a=previous, b=current, autojunk=False).get_grouped_opcodes(n=2):
        changes = [change for change in group if change[0] != "equal"]
        if all(operation == "delete" for operation, *positions in changes):
            for operation, start, end, new_start, new_end in changes:
                yield start, end, new_start, new_end
        else:
            yield group[0][1], group[-1][2], group[0][3], group[-1][4]


def update_post_text(previous_source, current_source, previous_target, current_target, language):
    result = dict(current_target)
    baseline = dict(previous_target)
    chunks = []
    replacements = []
    context = {"title": current_source.get("title"), "changes": []}

    for field, current in current_source.items():
        previous = previous_source[field]
        if previous == current:
            continue

        source_lines = (previous or "").splitlines(keepends=True)
        new_lines = (current or "").splitlines(keepends=True)
        target_lines = (previous_target[field] or "").splitlines(keepends=True)
        edited_lines = (current_target[field] or "").splitlines(keepends=True)
        equal_ranges = [
            (start, end, new_start)
            for operation, start, end, new_start, new_end in SequenceMatcher(
                a=target_lines, b=edited_lines, autojunk=False,
            ).get_opcodes() if operation == "equal"
        ]
        if not target_lines and not edited_lines:
            equal_ranges = [(0, 0, 0)]

        for start, end, new_start, new_end in changed_ranges(source_lines, new_lines):
            old_text = "".join(source_lines[start:end])
            new_text = "".join(new_lines[new_start:new_end])
            changed_characters = sum(
                max(right - left, new_right - new_left)
                for operation, left, right, new_left, new_right in SequenceMatcher(
                    a=old_text, b=new_text, autojunk=False,
                ).get_opcodes() if operation != "equal"
            )
            if changed_characters <= 2 and source_lines[start:end] and end - start == new_end - new_start:
                continue

            positions = {
                (offset + start - left, offset + end - left)
                for left, right, offset in equal_ranges if left <= start <= end <= right
            }
            if len(positions) != 1:
                raise TranslationError(f"Manual edits overlap a Russian change in {field}; review before updating.")

            target_start, target_end = positions.pop()
            replacements.append((field, start, end, target_start, target_end))
            chunks.append(new_text)
            context["changes"].append({
                "previous_source": old_text,
                "previous_translation": "".join(target_lines[start:end]),
                "before": "".join(new_lines[max(0, new_start - 3):new_start]),
                "after": "".join(new_lines[new_end:new_end + 3]),
            })

    translated = translate_texts(chunks, language, context=context)

    for (field, start, end, target_start, target_end), replacement in reversed(list(zip(replacements, translated))):
        target_lines = (result[field] or "").splitlines(keepends=True)
        baseline_lines = (baseline[field] or "").splitlines(keepends=True)
        target_lines[target_start:target_end] = [replacement]
        baseline_lines[start:end] = [replacement]
        result[field] = "".join(target_lines) or (None if current_source[field] is None else "")
        baseline[field] = "".join(baseline_lines) or (None if current_source[field] is None else "")

    return result, baseline
