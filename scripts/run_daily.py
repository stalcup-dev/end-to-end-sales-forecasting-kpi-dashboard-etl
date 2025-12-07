# scripts/run_daily.py
import subprocess, sys, time, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]  # repo root
PY = sys.executable  # current venv interpreter
LOG = ROOT / "logs"
LOG.mkdir(exist_ok=True)

def run(cmd, cwd=None):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] RUN: {cmd}")
    proc = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    (LOG / "run_daily.log").open("a", encoding="utf-8").write(
        f"\n\n==== {ts} :: {cmd} ====\n{proc.stdout}\n{proc.stderr}\n"
    )
    if proc.returncode != 0:
        raise SystemExit(f"FAILED: {cmd}\n{proc.stderr}")

if __name__ == "__main__":
    # 1) dbt transformations (materialize mart + views)
    run("dbt deps", cwd=ROOT / "vitamarkets_dbt" / "vitamarkets")
    run("dbt run",  cwd=ROOT / "vitamarkets_dbt" / "vitamarkets")

    # 2) Export mart_sales_summary to CSV (for Power BI or archive)
    run(f'{PY} etl/refresh_actuals.py', cwd=ROOT)

    # 3) Build Prophet forecasts & write table public.simple_prophet_forecast
    run(f'{PY} prophet_improved.py', cwd=ROOT)

    # 4) Optional: quick data quality snapshot
    run(f'{PY} checkcsv.py', cwd=ROOT)

    print("✅ Daily job completed.")
