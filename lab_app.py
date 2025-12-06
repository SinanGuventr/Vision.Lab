import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

DATA_FILE = Path("lab_data.json")


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


@dataclass
class Sample:
    id: int
    name: str
    category: str
    owner: str
    created_at: str


@dataclass
class Experiment:
    id: int
    name: str
    description: str
    lead: str
    scheduled_for: Optional[str]
    created_at: str


@dataclass
class Result:
    experiment_id: int
    sample_id: int
    status: str
    notes: str
    recorded_at: str


def load_db(path: Path) -> Dict[str, List[Dict]]:
    if path.exists():
        return json.loads(path.read_text())
    return {"samples": [], "experiments": [], "results": [], "counters": {"sample": 0, "experiment": 0}}


def save_db(path: Path, data: Dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def init_database(args: argparse.Namespace) -> None:
    data = {"samples": [], "experiments": [], "results": [], "counters": {"sample": 0, "experiment": 0}}
    save_db(args.path, data)
    print(f"Veri dosyası oluşturuldu: {args.path}")


def add_sample(args: argparse.Namespace) -> None:
    data = load_db(args.path)
    data["counters"]["sample"] += 1
    sample = Sample(
        id=data["counters"]["sample"],
        name=args.name,
        category=args.category,
        owner=args.owner,
        created_at=_now_iso(),
    )
    data["samples"].append(asdict(sample))
    save_db(args.path, data)
    print(f"Numune eklendi: {sample.id} - {sample.name}")


def add_experiment(args: argparse.Namespace) -> None:
    data = load_db(args.path)
    data["counters"]["experiment"] += 1
    experiment = Experiment(
        id=data["counters"]["experiment"],
        name=args.name,
        description=args.description,
        lead=args.lead,
        scheduled_for=args.scheduled_for,
        created_at=_now_iso(),
    )
    data["experiments"].append(asdict(experiment))
    save_db(args.path, data)
    print(f"Deney eklendi: {experiment.id} - {experiment.name}")


def record_result(args: argparse.Namespace) -> None:
    data = load_db(args.path)
    sample_ids = {item["id"] for item in data.get("samples", [])}
    experiment_ids = {item["id"] for item in data.get("experiments", [])}
    if args.sample_id not in sample_ids:
        raise SystemExit(f"Numune bulunamadı: {args.sample_id}")
    if args.experiment_id not in experiment_ids:
        raise SystemExit(f"Deney bulunamadı: {args.experiment_id}")
    result = Result(
        experiment_id=args.experiment_id,
        sample_id=args.sample_id,
        status=args.status,
        notes=args.notes,
        recorded_at=_now_iso(),
    )
    data.setdefault("results", []).append(asdict(result))
    save_db(args.path, data)
    print("Sonuç kaydedildi")


def list_samples(args: argparse.Namespace) -> None:
    data = load_db(args.path)
    samples = data.get("samples", [])
    if not samples:
        print("Henüz numune yok.")
        return
    print("ID | İsim | Kategori | Sorumlu | Oluşturulma")
    for item in samples:
        print(f"{item['id']:>2} | {item['name']} | {item['category']} | {item['owner']} | {item['created_at']}")


def list_experiments(args: argparse.Namespace) -> None:
    data = load_db(args.path)
    experiments = data.get("experiments", [])
    if args.lead:
        experiments = [exp for exp in experiments if exp["lead"].lower() == args.lead.lower()]
    if not experiments:
        print("Henüz deney yok.")
        return
    print("ID | İsim | Sorumlu | Tarih | Açıklama")
    for item in experiments:
        scheduled = item["scheduled_for"] or "-"
        print(f"{item['id']:>2} | {item['name']} | {item['lead']} | {scheduled} | {item['description']}")


def list_results(args: argparse.Namespace) -> None:
    data = load_db(args.path)
    results = data.get("results", [])
    if args.status:
        results = [res for res in results if res["status"].lower() == args.status.lower()]
    if not results:
        print("Henüz sonuç yok.")
        return
    print("DeneyID | NumuneID | Durum | Notlar | Kayıt Tarihi")
    for item in results:
        print(
            f"{item['experiment_id']:>7} | {item['sample_id']:>8} | "
            f"{item['status']} | {item['notes']} | {item['recorded_at']}"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Basit laboratuvar takip programı")
    parser.add_argument("--path", type=Path, default=DATA_FILE, help="Veri dosyası yolu (varsayılan: lab_data.json)")

    subparsers = parser.add_subparsers(dest="command", required=True)

    init_cmd = subparsers.add_parser("init", help="Yeni veri dosyası oluştur")
    init_cmd.set_defaults(func=init_database)

    sample_cmd = subparsers.add_parser("add-sample", help="Numune ekle")
    sample_cmd.add_argument("name", help="Numune adı")
    sample_cmd.add_argument("category", help="Kategori")
    sample_cmd.add_argument("owner", help="Sorumlu kişi")
    sample_cmd.set_defaults(func=add_sample)

    experiment_cmd = subparsers.add_parser("add-experiment", help="Deney ekle")
    experiment_cmd.add_argument("name", help="Deney adı")
    experiment_cmd.add_argument("description", help="Açıklama")
    experiment_cmd.add_argument("lead", help="Sorumlu kişi")
    experiment_cmd.add_argument("--scheduled-for", help="Planlanan tarih (örn. 2024-05-01 10:00)")
    experiment_cmd.set_defaults(func=add_experiment)

    result_cmd = subparsers.add_parser("record-result", help="Sonuç kaydet")
    result_cmd.add_argument("experiment_id", type=int, help="Deney ID")
    result_cmd.add_argument("sample_id", type=int, help="Numune ID")
    result_cmd.add_argument("status", help="Durum (örn. başarı, başarısız, beklemede)")
    result_cmd.add_argument("notes", help="Notlar")
    result_cmd.set_defaults(func=record_result)

    list_samples_cmd = subparsers.add_parser("list-samples", help="Numuneleri listele")
    list_samples_cmd.set_defaults(func=list_samples)

    list_experiments_cmd = subparsers.add_parser("list-experiments", help="Deneyleri listele")
    list_experiments_cmd.add_argument("--lead", help="Sorumlu kişiye göre filtrele")
    list_experiments_cmd.set_defaults(func=list_experiments)

    list_results_cmd = subparsers.add_parser("list-results", help="Sonuçları listele")
    list_results_cmd.add_argument("--status", help="Duruma göre filtrele")
    list_results_cmd.set_defaults(func=list_results)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
