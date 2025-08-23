import os
import shutil
from pathlib import Path
import csv
from collections import defaultdict

import torch
from ultralytics import YOLO
from tqdm import tqdm

img_path = "classify"
out_path = "classify_result"
weight_path = "best.pt"

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}

# 폴더 내에 있는 이미지들을 반환합니다.
def iter_images(root: Path, recursive: bool):
    images = []
    if recursive:
        for p in root.rglob("*"):
            if p.suffix.lower() in IMG_EXTS:
                images.append(p)
    else:
        for p in root.iterdir():
            if p.suffix.lower() in IMG_EXTS:
                images.append(p)
    return images


if __name__ == "__main__":
    src = Path(img_path)
    outdir = Path(out_path)
    outdir.mkdir(parents=True, exist_ok=True)

    # Load model
    try:
        model = YOLO(weight_path)
    except Exception as e:
        print(f"Error loading model from {weight_path}: {e}")
        raise SystemExit(1)
    try:
        device = "0" if torch.cuda.is_available() else "cpu"
    except Exception:
        device = "cpu"

    # Collect images
    images = iter_images(src, recursive=True)
    if not images:
        print(f"No images found in {src} (recursive=True).")
        raise SystemExit(0)

    # Predict (streaming)
    results = model.predict(
        source=[str(p) for p in images],
        imgsz=320,
        device=device
    )

    # CSV (per-image)
    csv_path = outdir / "args.csv"
    fcsv = open(csv_path, "w", newline="", encoding="utf-8")
    writer = csv.writer(fcsv)
    writer.writerow(["filename", "pred_class", "confidence", "dest_path"])

    pbar = tqdm(zip(images, results), total=len(images), desc="Classifying")

    # ---- 추가: 클래스별 통계 집계 ----
    count_by_class = defaultdict(int)
    sum_conf_by_class = defaultdict(float)
    min_conf_by_class = defaultdict(lambda: 1.0)
    max_conf_by_class = defaultdict(lambda: 0.0)

    n_ok, n_low, n_err = 0, 0, 0
    for img_p, res in pbar:
        try:
            probs = res.probs
            names = res.names  # dict: {idx: class_name}
            if probs is None:
                pred_name = "unknown"
                conf = 0.0
            else:
                scores = probs.data.cpu().numpy()
                top_idx = scores.argmax()
                conf = float(scores[top_idx])
                pred_name = names[top_idx] if conf >= 0.8 else "unknown"

            # Save file to its class folder
            dest_dir = outdir / pred_name
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_path = dest_dir / img_p.name

            if dest_path.exists():
                stem, suf = dest_path.stem, dest_path.suffix
                k = 1
                while True:
                    cand = dest_dir / f"{stem}_{k}{suf}"
                    if not cand.exists():
                        dest_path = cand
                        break
                    k += 1

            shutil.copy2(str(img_p), str(dest_path))
            writer.writerow([str(img_p), pred_name, f"{conf:.4f}", str(dest_path)])

            # ---- 추가: 통계 업데이트 ----
            count_by_class[pred_name] += 1
            sum_conf_by_class[pred_name] += conf
            if conf < min_conf_by_class[pred_name]:
                min_conf_by_class[pred_name] = conf
            if conf > max_conf_by_class[pred_name]:
                max_conf_by_class[pred_name] = conf

            if pred_name == "unknown":
                n_low += 1
            else:
                n_ok += 1

        except Exception as e:
            n_err += 1
            writer.writerow([str(img_p), "ERROR", "0.0", f"{e}"])

    fcsv.close()

    # ---- 추가: 요약 CSV/출력 ----
    summary_path = outdir / "class_summary.csv"
    with open(summary_path, "w", newline="", encoding="utf-8") as fs:
        sw = csv.writer(fs)
        sw.writerow(["class", "count", "mean_conf", "min_conf", "max_conf"])
        for cls_name in sorted(count_by_class.keys()):
            cnt = count_by_class[cls_name]
            mean_conf = (sum_conf_by_class[cls_name] / cnt) if cnt > 0 else 0.0
            min_conf = min_conf_by_class[cls_name] if cnt > 0 else 0.0
            max_conf = max_conf_by_class[cls_name] if cnt > 0 else 0.0
            sw.writerow([cls_name, cnt, f"{mean_conf:.4f}", f"{min_conf:.4f}", f"{max_conf:.4f}"])

    # 콘솔 출력
    print("\n=== Classification Summary ===")
    for cls_name in sorted(count_by_class.keys()):
        cnt = count_by_class[cls_name]
        mean_conf = (sum_conf_by_class[cls_name] / cnt) if cnt > 0 else 0.0
        print(f"- {cls_name:12s}: {cnt:5d} (mean_conf={mean_conf:.4f})")

    print(f"\nDone. Saved results to: {outdir}")
    print(f" - Classified (>= 0.8): {n_ok}")
    print(f" - Low-confidence  (< 0.8 → 'unknown'): {n_low}")
    print(f" - Errors: {n_err}")
    print(f" - Per-image CSV: {csv_path}")
    print(f" - Class summary CSV: {summary_path}")
