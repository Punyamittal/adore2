import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
from threading import Lock

from fastapi import HTTPException
from rapidfuzz import fuzz


def _task_to_dict(task) -> dict:
    return {
        "id": task.id,
        "name": task.name,
        "description": task.description,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "priority": task.priority,
        "status": task.status,
        "parent_id": task.parent_id,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "duration": task.duration,
    }


def question2(tasks):
    groups: dict = defaultdict(list)
    for t in tasks:
        groups[t.parent_id].append(t)
    for pid in groups:
        groups[pid].sort(
            key=lambda x: x.created_at or datetime.min.replace(tzinfo=None),
            reverse=True,
        )
    ordered_keys = sorted(groups.keys(), key=lambda k: (k is None, k if k is not None else 0))
    return [
        {"parent_id": k, "tasks": [_task_to_dict(t) for t in groups[k]]}
        for k in ordered_keys
    ]


def question3(tasks):
    today = date.today()
    tomorrow = today + timedelta(days=1)
    out = []
    for t in tasks:
        if t.priority != 1 or t.due_date is None:
            continue
        d = t.due_date.date() if isinstance(t.due_date, datetime) else t.due_date
        if d in (today, tomorrow):
            out.append(t)
    return [_task_to_dict(t) for t in out]


def question4(tasks):
    """Kept for API symmetry; question 4 is solved via SQL in main.py."""
    by_parent = defaultdict(list)
    for t in tasks:
        if t.parent_id is not None:
            by_parent[t.parent_id].append(t)
    parents_with_children = set(by_parent.keys())
    leaf_tasks = [t for t in tasks if t.id not in parents_with_children]
    return [_task_to_dict(t) for t in leaf_tasks]


def question5(tasks, task_id: int):
    target = next((t for t in tasks if t.id == task_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail="Task not found")
    pid = target.parent_id
    siblings = [t for t in tasks if t.parent_id == pid and t.id != task_id]
    return {"count": len(siblings), "sibling_ids": [t.id for t in siblings]}


def question6(tasks, query: str):
    if not query:
        return []
    q = query.strip().lower()
    scored = [(t, fuzz.token_sort_ratio(q, (t.name or "").lower())) for t in tasks]
    scored.sort(key=lambda x: x[1], reverse=True)
    threshold = 55
    return [_task_to_dict(t) for t, s in scored if s >= threshold]


def _is_ancestor_of(ancestor_id: int, descendant_id: int, by_id: dict) -> bool:
    current = descendant_id
    seen = set()
    while current is not None and current not in seen:
        seen.add(current)
        t = by_id.get(current)
        if t is None or t.parent_id is None:
            break
        if t.parent_id == ancestor_id:
            return True
        current = t.parent_id
    return False


def question7(tasks, task_id_a: int, task_id_b: int):
    by_id = {t.id: t for t in tasks}
    if task_id_a not in by_id or task_id_b not in by_id:
        raise HTTPException(status_code=404, detail="One or both tasks not found")
    if task_id_a == task_id_b:
        return "NONE"
    if _is_ancestor_of(task_id_a, task_id_b, by_id):
        return {
            "subtask_of_other": task_id_b,
            "ancestor": task_id_a,
            "detail": f"Task {task_id_b} is a subtask of task {task_id_a} (directly or indirectly).",
        }
    if _is_ancestor_of(task_id_b, task_id_a, by_id):
        return {
            "subtask_of_other": task_id_a,
            "ancestor": task_id_b,
            "detail": f"Task {task_id_a} is a subtask of task {task_id_b} (directly or indirectly).",
        }
    return "NONE"


def question8(tasks, criteria: dict, sort_by: str):
    raise HTTPException(
        status_code=501,
        detail="Question 8 is implemented as raw SQL/SQLAlchemy in main.py only.",
    )


def question9(tasks, worker_threads: int):
    if worker_threads < 1:
        raise HTTPException(status_code=400, detail="worker_threads must be at least 1")

    lock = Lock()
    results: list = []

    def run_one(task):
        seconds = max((task.duration or 0), 0) / 10.0
        if seconds > 0:
            time.sleep(seconds)
        rec = {"id": task.id, "name": task.name, "simulated_duration_seconds": seconds}
        with lock:
            results.append(rec)
        return rec

    with ThreadPoolExecutor(max_workers=worker_threads) as pool:
        futures = [pool.submit(run_one, t) for t in tasks]
        for f in as_completed(futures):
            f.result()

    return {
        "worker_threads": worker_threads,
        "tasks_processed": len(results),
        "executions": sorted(results, key=lambda x: x["id"]),
    }
