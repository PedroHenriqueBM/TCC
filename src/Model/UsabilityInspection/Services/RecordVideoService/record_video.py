import subprocess
import sys
import shutil
import os
import re
import time
from pathlib import Path
from PIL import Image

os.environ["OPENCV_LOG_LEVEL"] = "OFF"
os.environ["IMAGEIO_FFMPEG_LOG_LEVEL"] = "quiet"


def _inject_video_recording(content: str, video_dir: str) -> str:
    """Inject record_video_dir into browser.new_context() calls in generated script."""
    vd = video_dir.replace("\\", "/")
    size = '{"width": 1280, "height": 720}'

    # Make headless for automated replay
    content = re.sub(r"headless\s*=\s*False", "headless=True", content)
    # Speed up replay
    content = re.sub(r"slow_mo\s*=\s*\d+", "slow_mo=0", content)

    # Pattern 1: empty new_context()
    content = re.sub(
        r"await\s+browser\.new_context\(\s*\)",
        f'await browser.new_context(record_video_dir=r"{vd}", record_video_size={size})',
        content,
    )

    # Pattern 2: new_context( with existing args — inject at start
    # Negative lookahead avoids double-injection from Pattern 1
    content = re.sub(
        r"await\s+browser\.new_context\((?!record_video_dir)",
        f'await browser.new_context(record_video_dir=r"{vd}", record_video_size={size}, ',
        content,
    )

    return content


def _process_videos_to_pdf(output_dir: Path, video_files: list, functionality_id: str) -> str:
    """Extract frames from WebM files and save as PDF."""
    try:
        import imageio.v3 as iio
    except ImportError:
        iio = None
    try:
        import cv2
    except ImportError:
        cv2 = None

    all_frames = []
    MAX_RES = (1280, 1280)
    print(f"  -> Consolidando {len(video_files)} vídeos em PDF...")

    for video_path in video_files:
        video_abs = str(video_path.resolve())
        print(f"     - {video_path.name}")
        extracted = False

        if iio is not None:
            try:
                for i, frame in enumerate(iio.imiter(video_abs, plugin="pyav")):
                    if i % 6 == 0:
                        img = Image.fromarray(frame).convert("RGB")
                        img.thumbnail(MAX_RES, Image.Resampling.LANCZOS)
                        all_frames.append(img)
                extracted = True
            except Exception:
                pass

        if not extracted and cv2 is not None:
            try:
                cap = cv2.VideoCapture(video_abs)
                fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
                step = max(1, int(fps * 0.2))
                count = 0
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    if count % step == 0:
                        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).convert("RGB")
                        img.thumbnail(MAX_RES, Image.Resampling.LANCZOS)
                        all_frames.append(img)
                    count += 1
                cap.release()
            except Exception:
                pass

    if not all_frames:
        raise ValueError("Nenhum frame extraído dos vídeos.")

    pdf_name = f"execuction_recording_{functionality_id}.pdf"
    pdf_path = output_dir / pdf_name
    print(f"  -> Gerando PDF: {pdf_name} ({len(all_frames)} frames)")
    all_frames[0].save(
        str(pdf_path),
        save_all=True,
        append_images=all_frames[1:],
        resolution=100.0,
        quality=75,
    )
    return str(pdf_path)


def record_video(path_to_save_video: str, url_to_search: str, functionality_id: str) -> str | None:
    """
    Two-phase recording:

    Phase 1 — playwright codegen: opens a browser where the user performs the
    functionality naturally. Every interaction (click, fill, keyboard, navigation)
    is captured and saved as a Python-async Playwright script.

    Phase 2 — automated replay: the generated script is executed headlessly with
    record_video_dir injected. The recorded WebM is converted to PDF frames for
    the usability inspection agent.
    """
    output_dir = Path(path_to_save_video).resolve()
    script_name = f"execuction_recording_{functionality_id}.py"
    script_path = output_dir / script_name

    shutil.rmtree(output_dir, ignore_errors=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Phase 1: capture all interactions with playwright codegen ─────────────
    print("\n" + "=" * 50)
    print("   GRAVAÇÃO ATIVA")
    print("   Realize a funcionalidade no navegador.")
    print("   Feche a janela para finalizar.")
    print("=" * 50 + "\n")

    subprocess.run(
        [
            sys.executable, "-m", "playwright", "codegen",
            "--browser=chromium",
            "--target=python-async",
            f"--output={script_path}",
            url_to_search,
        ],
        check=False,
    )

    if not script_path.exists() or script_path.stat().st_size == 0:
        raise ValueError("Gravação cancelada — nenhum script foi gerado.")

    print("  -> Script de interações gerado com sucesso.")

    # ── Phase 2: replay with video recording → PDF ────────────────────────────
    print("  -> Gerando PDF de usabilidade (reprodução automática)...")

    video_dir = output_dir / "_replay_video"
    video_dir.mkdir(exist_ok=True)

    script_content = script_path.read_text(encoding="utf-8")
    replay_content = _inject_video_recording(script_content, str(video_dir))

    replay_path = output_dir / "_replay.py"
    replay_path.write_text(replay_content, encoding="utf-8")

    try:
        result = subprocess.run(
            [sys.executable, str(replay_path)],
            timeout=180,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0 and result.stderr:
            print(f"  -> Aviso no replay: {result.stderr[:300]}")
    except subprocess.TimeoutExpired:
        print("  -> Timeout no replay — processando frames disponíveis")
    except Exception as e:
        print(f"  -> Erro no replay: {e}")

    time.sleep(5)  # wait for Playwright to flush WebM files

    video_files = sorted(video_dir.glob("*.webm"))

    pdf_path = None
    if video_files:
        try:
            pdf_path = _process_videos_to_pdf(output_dir, video_files, functionality_id)
        except Exception as e:
            print(f"  -> Erro ao gerar PDF: {e}")
    else:
        print("  -> Nenhum vídeo capturado no replay — PDF não gerado.")

    # Cleanup temporary replay artefacts
    shutil.rmtree(video_dir, ignore_errors=True)
    replay_path.unlink(missing_ok=True)

    return pdf_path
