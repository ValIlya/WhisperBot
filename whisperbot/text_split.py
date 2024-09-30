from typing import Iterator, List


def split(text: str, limit: int = 4096) -> List[str]:
    splits = list(iterate_splits([text], "\n", limit))
    splits = list(iterate_splits(splits, ".", limit))
    splits = list(iterate_splits(splits, " ", limit))
    return splits


def iterate_splits(splits: Iterator[str], sep: str, limit: int) -> Iterator:
    for split in splits:
        if len(split) < limit:
            yield split
        else:
            yield from split_text_by_sep(split, sep=sep, limit=limit)


def split_text_by_sep(text: str, sep: str, limit: int) -> List[str]:
    pieces = text.split(sep)
    splits = []
    current_split = ""

    for piece in pieces:
        if piece.strip() == "":
            continue
        if len(current_split) == 0:
            current_split += piece + sep
        elif len(current_split) + len(piece) + len(sep) < limit:
            current_split += piece + sep
        else:
            splits.append(current_split.strip())
            current_split = piece + sep

    current_split = current_split.strip()
    if current_split:
        splits.append(current_split)

    return splits
