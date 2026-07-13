import concurrent.futures
import time
import urllib.request

BASE_URL = "http://localhost:8000"
TOTAL_REQUESTS = 80
WORKERS = 10


def request_home(_):
    inicio = time.perf_counter()
    with urllib.request.urlopen(BASE_URL, timeout=10) as response:
        response.read()
        status = response.status
    return status, time.perf_counter() - inicio


def main():
    inicio = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        resultados = list(executor.map(request_home, range(TOTAL_REQUESTS)))

    duracao = time.perf_counter() - inicio
    falhas = [status for status, _ in resultados if status >= 400]
    tempos = [tempo for _, tempo in resultados]
    print(f"Requisições: {TOTAL_REQUESTS}")
    print(f"Concorrência: {WORKERS}")
    print(f"Falhas HTTP: {len(falhas)}")
    print(f"Tempo total: {duracao:.2f}s")
    print(f"Tempo médio: {(sum(tempos) / len(tempos)):.3f}s")
    print(f"Maior tempo: {max(tempos):.3f}s")
    if falhas:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
