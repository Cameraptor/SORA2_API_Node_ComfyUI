# =============================================================================
# 🦖 Sora2 by Cameraptor
# Author: Voogie
# Credit: Cameraptor
# Website: https://cameraptor.com/voogie
#
# Версия 7.4: Remix Input Fix
# - Исправлена критическая ошибка при подключенном image_input в режиме Remix
# - Единая нода для Generate и Remix
# - Автоматический ресайз Img2Vid
# - Автоматическое использование последнего video_id для Remix
# - Извлечение аудио для Video Combine
# - Надежная обработка ошибок
# =============================================================================
import requests, torch, numpy as np, time, os, io, re
from PIL import Image
import folder_paths

# Глобальное хранилище для ID последнего сгенерированного видео
_LAST_VIDEO_ID_STORAGE = {"video_id": None, "duration": None, "size": None, "model": None}

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    print("⚠️ Sora2 Node: OpenCV not found. Frame loading will be limited.")
    OPENCV_AVAILABLE = False

try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    print("⚠️ Sora2 Node: moviepy not found. Audio extraction will be disabled.")
    print("   To enable audio, run in your ComfyUI folder: .\\python_embeded\\python.exe -m pip install moviepy")
    MOVIEPY_AVAILABLE = False

# =============================================================================
# КЛАСС-ПОМОЩНИК ДЛЯ РАБОТЫ С API
# =============================================================================
class SoraAPI_Utils:
    
    def get_profile_details(self, profile, orientation):
        is_landscape = (orientation == "Landscape")
        if profile == "Sora 2 (720p)": return "sora-2", "1280x720" if is_landscape else "720x1280"
        elif profile == "Sora 2 Pro (720p)": return "sora-2-pro", "1280x720" if is_landscape else "720x1280"
        elif profile == "Sora 2 Pro (HD 1080p)": return "sora-2-pro", "1792x1024" if is_landscape else "1024x1792"
        else: return "sora-2", "1280x720"

    def get_video_metadata(self, api_key, video_id):
        url = f"https://api.openai.com/v1/videos/{video_id}"
        headers = {"Authorization": f"Bearer {api_key}"}
        try:
            response = requests.get(url, headers=headers, timeout=30); response.raise_for_status()
            result = response.json()
            duration, size, model = result.get('seconds', '8'), result.get('size', '1280x720'), result.get('model', 'sora-2')
            print(f"📊 Sora2 Node: Video metadata retrieved for {video_id}")
            return duration, size, model
        except Exception as e:
            print(f"⚠️ Sora2 Node: Could not fetch video metadata: {e}. Using defaults.")
            return "8", "1280x720", "sora-2"

    def calculate_cost(self, model, duration_str, size):
        duration = float(duration_str)
        cost_per_sec = 0.10
        if "sora-2-pro" in model:
            cost_per_sec = 0.30
            if size and ("1792" in size or "1024" in size):
                cost_per_sec = 0.50
        return duration * cost_per_sec
    
    def smart_resize_image(self, image_tensor, target_size_str):
        target_w, target_h = map(int, target_size_str.split('x'))
        img_array = (image_tensor.cpu().numpy().squeeze(0) * 255).astype(np.uint8)
        pil_image = Image.fromarray(img_array)
        original_w, original_h = pil_image.size
        if original_w == target_w and original_h == target_h: return pil_image
        print(f"📐 Sora2 Node: Resizing input image from {original_w}x{original_h} to {target_w}x{target_h}")
        original_aspect, target_aspect = original_w / original_h, target_w / target_h
        if abs(original_aspect - target_aspect) < 0.01:
            resized = pil_image.resize((target_w, target_h), Image.LANCZOS)
        else:
            if original_aspect > target_aspect: new_w, new_h = target_w, int(target_w / original_aspect)
            else: new_h, new_w = target_h, int(target_h * original_aspect)
            resized_content = pil_image.resize((new_w, new_h), Image.LANCZOS)
            resized = Image.new('RGB', (target_w, target_h), (0, 0, 0))
            paste_x, paste_y = (target_w - new_w) // 2, (target_h - new_h) // 2
            resized.paste(resized_content, (paste_x, paste_y))
        return resized

    def create_video_job(self, api_key, prompt, size, duration, model, image_input):
        payload = {"model": (None, model), "prompt": (None, prompt), "size": (None, size), "seconds": (None, str(duration))}
        if image_input is not None:
            try:
                print("🖼️ Sora2 Node: Image-to-Video mode detected")
                pil_image = self.smart_resize_image(image_input, size)
                img_buffer = io.BytesIO(); pil_image.save(img_buffer, format='PNG'); img_buffer.seek(0)
                payload['input_reference'] = ('image.png', img_buffer, 'image/png')
            except Exception as e: raise Exception(f"Failed to process input image: {e}")
        return self._post_request("https://api.openai.com/v1/videos", {"Authorization": f"Bearer {api_key}"}, files=payload)

    def create_remix_job(self, api_key, original_video_id, remix_prompt):
        url = f"https://api.openai.com/v1/videos/{original_video_id}/remix"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        data = {"prompt": remix_prompt}
        return self._post_request(url, headers, json_data=data)

    def _post_request(self, url, headers, files=None, json_data=None):
        try:
            if json_data: response = requests.post(url, headers=headers, json=json_data, timeout=60)
            else: response = requests.post(url, headers=headers, files=files, timeout=60)
            if not response.ok:
                try: error_data = response.json(); error_message = error_data.get('error', {}).get('message', str(error_data))
                except: error_message = response.text
                raise Exception(f"API Error {response.status_code}: {error_message}")
            response.raise_for_status()
        except requests.exceptions.RequestException as e: raise Exception(f"Network error: {e}")
        result = response.json()
        if 'id' not in result: raise Exception(f"Invalid API response: {result}")
        return result['id']

    def poll_video_status(self, api_key, video_id, p_interval, p_max_time, show_progress, p_prefix):
        url = f"https://api.openai.com/v1/videos/{video_id}"; headers = {"Authorization": f"Bearer {api_key}"}
        print(f"{p_prefix} Polling status for {video_id}...")
        start_time = time.time(); last_progress = -1
        while True:
            elapsed = time.time() - start_time
            if elapsed > p_max_time: raise Exception(f"Polling timeout after {elapsed:.1f}s")
            try:
                response = requests.get(url, headers=headers, timeout=30); response.raise_for_status(); result = response.json()
            except requests.exceptions.RequestException as e:
                print(f"  ⚠️ Sora2 Node: Polling failed ({e}), retrying..."); time.sleep(p_interval); continue
            status = result.get('status', 'unknown')
            if show_progress:
                progress = result.get('progress', 0)
                if progress != last_progress: print(f"  {p_prefix} Progress: {progress}% | Status: {status}"); last_progress = progress
            if status == 'completed': print(f"  {p_prefix} Generation completed!"); return
            elif status == 'failed':
                error_obj = result.get('error')
                error_message = str(error_obj) if not isinstance(error_obj, dict) else error_obj.get('message', "No details provided.")
                raise Exception(f"Video generation failed: {error_message}")
            elif status in ['queued', 'in_progress']: time.sleep(p_interval)
            else: print(f"  ⚠️ Sora2 Node: Unknown status: {status}, continuing..."); time.sleep(p_interval)

    def download_video(self, api_key, video_id, save_path, filename_prefix, p_prefix):
        url = f"https://api.openai.com/v1/videos/{video_id}/content"; headers = {"Authorization": f"Bearer {api_key}"}
        print(f"{p_prefix} Downloading video...")
        try:
            with requests.get(url, headers=headers, stream=True, timeout=300) as r:
                r.raise_for_status(); os.makedirs(save_path, exist_ok=True)
                final_filepath = os.path.join(save_path, f"{filename_prefix}.mp4"); counter = 1
                while os.path.exists(final_filepath):
                    final_filepath = os.path.join(save_path, f"{filename_prefix}_{counter:05d}.mp4"); counter += 1
                with open(final_filepath, 'wb') as f:
                    total_size = 0
                    for chunk in r.iter_content(chunk_size=8192): f.write(chunk); total_size += len(chunk)
        except requests.exceptions.RequestException as e: raise Exception(f"Download failed: {e}")
        final_filename = os.path.basename(final_filepath)
        print(f"{p_prefix} Video saved to: {final_filepath} ({total_size / 1024 / 1024:.2f} MB)")
        subfolder = ""
        try:
            output_dir = folder_paths.get_output_directory()
            if os.path.commonpath([save_path, output_dir]) == output_dir:
                subfolder = os.path.relpath(save_path, output_dir)
        except ValueError: pass
        return final_filepath, final_filename, subfolder

    def extract_audio(self, video_path):
        if not MOVIEPY_AVAILABLE: return lambda: (None, None)
        try:
            print(f"🔊 Sora2 Node: Extracting audio...")
            with VideoFileClip(video_path) as video_clip:
                if video_clip.audio is None:
                    print("⚠️ Sora2 Node: Video has no audio track."); return lambda: (None, None)
                audio_array = video_clip.audio.to_soundarray(fps=44100)
                sample_rate = int(video_clip.audio.fps)
            audio_tensor = torch.from_numpy(audio_array.T).float().unsqueeze(0)
            print(f"✅ Sora2 Node: Audio extracted. Shape: {audio_tensor.shape}")
            return lambda: (audio_tensor, sample_rate)
        except Exception as e:
            print(f"💥 Sora2 Node: Error extracting audio: {e}"); return lambda: (None, None)

    def load_frames(self, video_path):
        if not OPENCV_AVAILABLE: return self._create_dummy_tensor()
        try:
            video_cap = cv2.VideoCapture(video_path); frames = []
            while True:
                ret, frame = video_cap.read()
                if not ret: break
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb.astype(np.float32) / 255.0)
            video_cap.release()
            if not frames: raise Exception("No frames were loaded from video.")
            print(f"✅ Sora2 Node: Loaded {len(frames)} frames into a tensor.")
            return torch.from_numpy(np.stack(frames, axis=0))
        except Exception as e:
            print(f"💥 Sora2 Node: Error loading video frames: {e}"); return self._create_dummy_tensor()

    def _create_dummy_tensor(self):
        return torch.zeros((1, 64, 64, 3), dtype=torch.float32)

# =============================================================================
# ОСНОВНАЯ UNIFIED НОДА
# =============================================================================
class Sora2:
    OUTPUT_NODE = True
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mode": (["Generate", "Remix"], {"default": "Generate"}),
                "openai_api_key": ("STRING", {"default": os.environ.get("OPENAI_API_KEY", "")}),
                "prompt": ("STRING", {"multiline": True, "default": "A cinematic shot of a woman walking through neon-lit Tokyo streets at night"}),
                "save_path": ("STRING", {"default": folder_paths.get_output_directory()}),
                "filename_prefix": ("STRING", {"default": "Sora_Video"}),
            },
            "optional": {
                "profile": (["Sora 2 (720p)", "Sora 2 Pro (720p)", "Sora 2 Pro (HD 1080p)"], {"default": "Sora 2 Pro (720p)"}),
                "orientation": (["Landscape", "Portrait"], {"default": "Landscape"}),
                "duration": (["4", "8", "12"], {"default": "8"}),
                "image_input": ("IMAGE",),
                "source_video_id": ("STRING", {"default": ""}),
                "polling_interval": ("INT", {"default": 15, "min": 5, "max": 60}),
                "max_polling_time": ("INT", {"default": 1200, "min": 60, "max": 1800}),
                "show_progress": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "AUDIO", "STRING", "STRING", "IMAGE", "STRING")
    RETURN_NAMES = ("frames", "audio", "video_path", "info", "first_frame_preview", "video_id")
    FUNCTION = "execute"
    CATEGORY = "🦖Cameraptor"
    
    def execute(self, mode, openai_api_key, prompt, save_path, filename_prefix, **kwargs):
        shared = SoraAPI_Utils()
        if not openai_api_key: raise Exception("OpenAI API key is required!")
        
        try:
            start_time = time.time()
            
            if mode == "Generate":
                prefix = "🎬 [Sora2 Generate]"
                print(f"\n{prefix} Starting...")
                profile, orient, dur = kwargs.get("profile"), kwargs.get("orientation"), kwargs.get("duration")
                model, size = shared.get_profile_details(profile, orient)
                cost = shared.calculate_cost(model, dur, size)
                print(f"   Est. Cost: ${cost:.2f}")
                video_id = shared.create_video_job(openai_api_key, prompt, size, dur, model, kwargs.get("image_input"))
                info_template = (f"✅ Done in {{time:.1f}}s | {size} | {dur}s | ${cost:.2f} | {model} | ID: {video_id}")
            else: # Remix
                prefix = "🎭 [Sora2 Remix]"
                print(f"\n{prefix} Starting...")
                # [ИСПРАВЛЕНО] Безопасная проверка на наличие, а не на содержимое
                if "image_input" in kwargs: 
                    print("⚠️ Sora2 Node: Note: image_input is ignored in Remix mode")

                source_id = kwargs.get("source_video_id", "").strip()
                if not source_id:
                    source_id = _LAST_VIDEO_ID_STORAGE.get("video_id")
                    if source_id: print(f"💾 Sora2 Node: Using last generated video_id from storage: {source_id}")
                    else: raise Exception("No source video ID found! Manually enter a 'source_video_id' or generate a video first.")
                
                duration, size, model = shared.get_video_metadata(openai_api_key, source_id)
                cost = shared.calculate_cost(model, duration, size)
                print(f"   Source: {source_id} | Est. Remix Cost: ${cost:.2f}")
                video_id = shared.create_remix_job(openai_api_key, source_id, prompt)
                info_template = (f"✅ Remix done in {{time:.1f}}s | {size} | {duration}s | ${cost:.2f} | Original ID: {source_id} | New ID: {video_id}")
            
            print(f"✅ Sora2 Node: Job created: {video_id}")
            shared.poll_video_status(openai_api_key, video_id, kwargs.get("polling_interval", 15), kwargs.get("max_polling_time", 1200), kwargs.get("show_progress", True), prefix)
            
            video_path, filename, subfolder = shared.download_video(openai_api_key, video_id, save_path, filename_prefix, prefix)
            
            frames = shared.load_frames(video_path)
            audio = shared.extract_audio(video_path)
            final_info = info_template.format(time=time.time() - start_time)
            
            _LAST_VIDEO_ID_STORAGE.update({"video_id": video_id, "duration": duration if 'duration' in locals() else dur, "size": size, "model": model})
            print(f"💾 Sora2 Node: Saved video_id '{video_id}' for next Remix.")

            if frames.shape[0] == 0: raise Exception("Failed to load any frames from the generated video.")
            
            preview = {"filename": filename, "subfolder": subfolder, "type": "output", "format": "video/mp4"}
            return {"ui": {"previews": [preview]}, "result": (frames, audio, video_path, final_info, frames[0].unsqueeze(0), video_id)}
        
        except Exception as e:
            error = f"💥 Sora2 Node Error: {e}"
            print(f"\n{'='*60}\n{error}\n{'='*60}\n")
            dummy_tensor, safe_audio = shared._create_dummy_tensor(), lambda: (None, None)
            return {"ui": {"text": [error]}, "result": (dummy_tensor, safe_audio, "ERROR", error, dummy_tensor, "ERROR")}

# =============================================================================
# РЕГИСТРАЦИЯ НОДЫ
# =============================================================================
NODE_CLASS_MAPPINGS = {"Sora2": Sora2}
NODE_DISPLAY_NAME_MAPPINGS = {"Sora2": "🦖 Sora2"}