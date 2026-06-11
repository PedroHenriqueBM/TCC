import asyncio
import shutil
import os
import time
from pathlib import Path
from PIL import Image
import imageio.v3 as iio
import cv2
from playwright.async_api import async_playwright

# Silenciar logs chatos de sistema
os.environ["OPENCV_LOG_LEVEL"] = "OFF"
os.environ["IMAGEIO_FFMPEG_LOG_LEVEL"] = "quiet"

try:
    from playwright_stealth import stealth_async as apply_stealth
except ImportError:
    try:
        from playwright_stealth import stealth as apply_stealth
    except ImportError:
        apply_stealth = None

def _process_videos_in_exact_order(output_dir: Path, ordered_video_names: list, functionality_id: str, every_seconds: float = 0.2) -> str:
    """Processa a lista exata de vídeos capturados na ordem da operação."""
    all_frames = []
    MAX_RES = (1280, 1280) 

    print(f"-> Consolidando {len(ordered_video_names)} vídeos na ordem da operação...")

    for video_name in ordered_video_names:
        video_path = output_dir / video_name
        # Aguarda o arquivo aparecer ou ter tamanho se necessário (retry rápido)
        for _ in range(5):
            if video_path.exists() and video_path.stat().st_size > 0:
                break
            time.sleep(1)

        if not video_path.exists() or video_path.stat().st_size == 0:
            print(f"   ! Aviso: Vídeo {video_name} não encontrado ou vazio. Pulando...")
            continue
            
        video_abs_path = os.path.abspath(str(video_path))
        print(f"   - Extraindo frames da aba: {video_name}")
        
        try:
            for i, frame in enumerate(iio.imiter(video_abs_path, plugin="pyav")):
                if i % 6 == 0: 
                    img = Image.fromarray(frame).convert("RGB")
                    img.thumbnail(MAX_RES, Image.Resampling.LANCZOS)
                    all_frames.append(img)
        except Exception:
            try:
                cap = cv2.VideoCapture(video_abs_path)
                fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
                step = max(1, int(fps * every_seconds))
                count = 0
                while True:
                    ret, frame = cap.read()
                    if not ret: break
                    if count % step == 0 and frame is not None:
                        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).convert("RGB")
                        img.thumbnail(MAX_RES, Image.Resampling.LANCZOS)
                        all_frames.append(img)
                    count += 1
                cap.release()
            except Exception: pass

    if not all_frames:
        raise ValueError("Nenhum frame extraído. Verifique se as janelas foram gravadas.")

    pdf_name = f"execuction_recording_{functionality_id}.pdf"
    pdf_path = output_dir / pdf_name
    
    print(f"-> Gerando PDF: {pdf_name} ({len(all_frames)} páginas)")
    all_frames[0].save(
        str(pdf_path),
        save_all=True,
        append_images=all_frames[1:],
        resolution=100.0,
        quality=75
    )
    return str(pdf_path)

async def record_video(path_to_save_video: str, url_to_search: str, functionality_id: str):
    output_dir = Path(path_to_save_video).resolve()
    script_name = f"execuction_recording_{functionality_id}.py"
    
    if output_dir.exists():
        shutil.rmtree(output_dir, ignore_errors=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    video_filenames_in_order = []
    last_url_recorded = ""

    actions_log = [
        "import asyncio", "from playwright.async_api import async_playwright",
        "try: from playwright_stealth import stealth_async", "except: stealth_async = None",
        "", "async def run():", "    async with async_playwright() as p:",
        "        user_data = './browser_session_reproduction'",
        "        context = await p.chromium.launch_persistent_context(",
        "            user_data, headless=False, slow_mo=150,",
        "            args=['--disable-blink-features=AutomationControlled']",
        "        )",
        "        page = context.pages[0] if context.pages else await context.new_page()",
        "        if stealth_async: await stealth_async(page)",
        f"        await page.goto('{url_to_search}', wait_until='load')"
    ]

    async with async_playwright() as p:
        user_data_dir = output_dir / "browser_session"
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=False,
            slow_mo=150,
            args=["--disable-blink-features=AutomationControlled"],
            record_video_dir=str(output_dir),
            record_video_size={"width": 1280, "height": 720}
        )

        async def track_video(page_obj):
            """Registra o vídeo da página na lista global."""
            if page_obj.video:
                v_path = await page_obj.video.path()
                v_name = Path(v_path).name
                if v_name not in video_filenames_in_order:
                    video_filenames_in_order.append(v_name)

        async def setup_page(page_obj):
            nonlocal last_url_recorded
            # Tenta pegar o vídeo imediatamente e agenda nova tentativa no fechamento
            await track_video(page_obj)
            page_obj.on("close", lambda p: asyncio.create_task(track_video(p)))

            if apply_stealth and callable(apply_stealth):
                await apply_stealth(page_obj)
            await page_obj.add_init_script("delete navigator.__proto__.webdriver")

            async def on_nav(frame):
                nonlocal last_url_recorded
                url = frame.url
                if frame == page_obj.main_frame and url.startswith("http") and url != last_url_recorded:
                    actions_log.append(f"        await page.goto('{url}', wait_until='load')")
                    last_url_recorded = url
            page_obj.on("framenavigated", on_nav)

        context.on("page", setup_page)
        main_page = context.pages[0] if context.pages else await context.new_page()
        await setup_page(main_page)

        try:
            await main_page.goto(url_to_search, wait_until="load")
            print("\n" + "="*40 + "\n   GRAVAÇÃO EM ORDEM ATIVA\n   Feche o navegador para processar\n" + "="*40 + "\n")
            
            while any(not pg.is_closed() for pg in context.pages):
                # Mantém varredura ativa para garantir que pegamos abas rápidas
                for pg in context.pages:
                    await track_video(pg)
                await asyncio.sleep(1)
            
        except Exception: pass
        finally:
            # Força o registro de vídeos das páginas antes de fechar o contexto
            for pg in context.pages:
                await track_video(pg)
                try: await pg.close()
                except: pass
            await asyncio.sleep(2) # Buffer para o Playwright salvar o último webm
            try: await context.close()
            except: pass

    # Salva o script
    actions_log.extend(["", "        await context.close()", "asyncio.run(run())"])
    with open(output_dir / script_name, "w") as f:
        f.write("\n".join(actions_log))

    try:
        # Pausa maior para o SO liberar os descritores de arquivo
        time.sleep(10) 
        final_pdf_path = _process_videos_in_exact_order(output_dir, video_filenames_in_order, functionality_id)
        
        # Faxina Final
        for item in output_dir.iterdir():
            if item.name not in [Path(final_pdf_path).name, script_name]:
                if item.is_file(): item.unlink()
                elif item.is_dir(): shutil.rmtree(item, ignore_errors=True)
                
        return str(final_pdf_path)
    except Exception as e:
        print(f"-> Erro final: {e}")
        return None
