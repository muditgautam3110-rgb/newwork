"""Orderly — report computation module.

This is a brownfield project: some functions are complete, some are
TODO-marked gaps, and one has a planted bug. Work through TASKS.md.
"""

from __future__ import annotations

import csv
import logging
import os
import time

logger = logging.getLogger("orderly.reports")


# --------------------------------------------------------------------------
# Task T1 — planted bug (see TASKS.md)
# --------------------------------------------------------------------------
def monthly_revenue(conn):
    """Return [(month, revenue), ...] sorted ascending by month.

    Revenue = SUM(qty * unit_price) over order items whose order status is
    'completed'. Month is 'YYYY-MM' taken from the order date.

    TODO(T1): this currently counts cancelled and returned orders as well.
    It must count 'completed' orders only.
    """
    rows = conn.execute(
        """
        SELECT strftime('%Y-%m', o.order_date) AS month,
               SUM(oi.qty * oi.unit_price) AS revenue
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.id
        Where o.status = 'completed'
        GROUP BY month
        ORDER BY month
        """
    ).fetchall()
    return [(m, round(r, 2)) for m, r in rows]


# --------------------------------------------------------------------------
# Task T2 — TODO gaps
# --------------------------------------------------------------------------
def monthly_running_total(conn):
    """Return [(month, revenue, running_total), ...] sorted by month.
    Build on monthly_revenue(); do not re-query the database here.
    """
    monthly_revenue_data = monthly_revenue(conn)
    running_total = 0
    result = []
    for month, revenue in monthly_revenue_data:
        running_total += revenue
        result.append((month, revenue, round(running_total, 2)))
    return result 

def top_customers(conn, limit=5):
    """Return [(name, city, revenue), ...] for the top `limit` customers by
    total revenue (completed orders only), highest revenue first.
    """
    rows = conn.execute(
        """
        SELECT c.name, c.city, SUM(oi.qty * oi.unit_price) AS revenue
        FROM customers c
        JOIN orders o ON o.customer_id = c.id
        JOIN order_items oi ON oi.order_id = o.id
        WHERE o.status = 'completed'                        
        GROUP BY c.id
        ORDER BY revenue DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [(name, city, round(revenue, 2)) for name, city, revenue in rows]
    
    raise NotImplementedError("TODO(T2b): top_customers")


def iter_completed_items(conn):
    """Yield one dict per order item belonging to a completed order.

    Keys: order_id, month, product, category, qty, unit_price, amount.
    Must be a generator (use yield).
    """
    row = conn.execute(
        """
        SELECT o.id AS order_id,
               strftime('%Y-%m', o.order_date) AS month,
               p.name AS product,
               p.category AS category,
               oi.qty AS qty,
               oi.unit_price AS unit_price,
               (oi.qty * oi.unit_price) AS amount
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.id
        JOIN products p ON p.id = oi.product_id
        WHERE o.status = 'completed'
        """
    )
    for order_id, month, product, category, qty, unit_price, amount in row:
        yield {
            "order_id": order_id,
            "month": month,
            "product": product,
            "category": category,
            "qty": qty,
            "unit_price": unit_price,
            "amount": amount,
        }
    
    #raise NotImplementedError("TODO(T2c): iter_completed_items")


class SalesSummary:
    """A small container for monthly revenue rows.

    TODO(T2d): implement this class.
      - constructor takes a list of (month, revenue) tuples
      - len(summary)            -> number of months
      - repr(summary)           -> "SalesSummary(months=4, total=12345.67)"
      - summary.total_revenue   -> property, sum of revenues (2 decimals)
      - summary.best_month()    -> (month, revenue) of the best month
    """
    
    def __init__(self, rows):
        self.rows = rows

    def __len__(self):
        return len(self.rows)

    @property
    def total_revenue(self):
        return round(sum(revenue for month, revenue in self.rows), 2)

    def best_month(self):
        if not self.rows:
            return None
        return max(self.rows, key=lambda row: row[1])

    def __repr__(self):
        return f"SalesSummary(months={len(self)}, total={self.total_revenue:.2f})"


def timed(func):
    """Decorator: log "<funcname> took <ms> ms" at INFO level and return the
    wrapped function's result unchanged.

    TODO(T2e): implement. Use the module logger and time.perf_counter().
    """
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info("%s took %.2f ms", func.__name__, elapsed_ms)
        return result
    return wrapper
    # TODO(T2e): implement the decorator.
    raise NotImplementedError("TODO(T2e): timed")


def write_report(rows, out_path, header):
    """Write `rows` (a list of tuples) to `out_path` as CSV with `header`.

    TODO(T2f): implement.
      - create the parent directory if it does not exist
      - raise ValueError("no rows to write") when rows is empty
      - use a context manager for the file and newline=""
      - log how many rows were written (INFO level)
      - return the path written (as str)
    """
    if not rows:
        raise ValueError("no rows to write")

    out_path = str(out_path)
    parent = os.path.dirname(out_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(rows)

    logger.info("Wrote %s rows to %s", len(rows), out_path)
    return out_path
        
    # TODO(T2f): implement write_report.
    raise NotImplementedError("TODO(T2f): write_report")


# --------------------------------------------------------------------------
# Completed reference code (do not edit)
# --------------------------------------------------------------------------
def revenue_by_category(conn):
    """Return [(category, revenue), ...] for completed orders, highest first."""
    rows = conn.execute(
        """
        SELECT p.category, SUM(oi.qty * oi.unit_price) AS revenue
        FROM order_items oi
        JOIN orders   o ON o.id = oi.order_id
        JOIN products p ON p.id = oi.product_id
        WHERE o.status = 'completed'
        GROUP BY p.category
        ORDER BY revenue DESC
        """
    ).fetchall()
    return [(c, round(r, 2)) for c, r in rows]
