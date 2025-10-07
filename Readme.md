# 🦖 Sora2 Node for ComfyUI

[![GitHub](https://img.shields.io/badge/GitHub-Cameraptor-blue?logo=github)](https://github.com/Cameraptor/SORA2_API_Node_ComfyUI)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Node-orange)](https://github.com/comfyanonymous/ComfyUI)

> **Universal ComfyUI node providing direct access to the full capabilities of the OpenAI Sora API**

Create videos from text, animate your images, and generate sequential remixes all within a single, convenient interface.

**Author:** Voogie | **Project:** Cameraptor | [cameraptor.com/voogie](https://cameraptor.com/voogie)

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🎯 **Unified Interface** | Single node for all modes (Generate and Remix) |
| 🔄 **Auto-Remix** | Automatically uses the ID of the last generated video - no cyclical dependencies! |
| 🔊 **Audio Extraction** | Extracts audio track for direct use with nodes like VHS Video Combine |
| 📐 **Smart Resize** | Auto-resizes input images to match Sora API requirements (preserves aspect ratio) |
| 💰 **Cost Estimation** | Accurate cost calculation for both Generate and Remix jobs |
| 🛡️ **Error Handling** | Bulletproof handling - won't crash or break the queue on API errors |

---

## 🚀 Installation

### Method 1: Via ComfyUI Manager ⭐ (Recommended)

1. Launch ComfyUI and open the **Manager**
2. Click **Install via Git URL**
3. Paste the repository URL:
   ```
   https://github.com/Cameraptor/SORA2_API_Node_ComfyUI
   ```
4. Click **Install** (dependencies will be installed automatically)
5. **Restart ComfyUI completely**

### Method 2: Manual Installation

1. Navigate to your `ComfyUI/custom_nodes/` directory

2. Clone the repository:
   ```bash
   git clone https://github.com/Cameraptor/SORA2_API_Node_ComfyUI
   ```

3. Enter the directory:
   ```bash
   cd SORA2_API_Node_ComfyUI
   ```

4. Install dependencies using ComfyUI's Python:
   
   **Windows:**
   ```bash
   ..\..\python_embeded\python.exe -m pip install -r requirements.txt
   ```
   
   **Linux/Mac:**
   ```bash
   ../../python/bin/python -m pip install -r requirements.txt
   ```

5. **Restart ComfyUI completely**

---

## 🔑 Getting Your OpenAI API Key

> ⚠️ **Important:** Sora is a paid service. You need an OpenAI account with credits and an API key.

### Step 1: Create an Account

Go to [platform.openai.com](https://platform.openai.com/) and sign up or log in.

### Step 2: Verification & Add Credits

1. **Verify your account** (usually requires phone number)
2. Navigate to **Settings** → **Billing**
3. Click **Add payment details** and add your credit card
4. Click **Add to credit balance** and add funds (minimum $10 recommended)

> 💡 **Note:** The API operates on a pre-paid basis and won't work without credits.

### Step 3: Create API Key

1. Navigate to **API Keys** in the left menu
2. Click **Create new secret key**
3. Give it a name (e.g., `ComfyUI-Sora`)
4. Click **Create secret key**

> ⚠️ **Warning:** The key is shown only once! Copy it immediately and store it securely.

### Step 4: Use in ComfyUI

Paste your API key into the `openai_api_key` field in the 🦖 Sora2 node.

---

## 🕹️ Usage Guide

Find the **🦖 Sora2** node in the **🦖Cameraptor** menu. Configure parameters and click **Queue Prompt**.

> 💡 **Tip:** Watch the console (command window) to monitor generation progress!

---

## 📋 Parameters Reference

### Core Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `mode` | Dropdown | **Generate**: Create new video from text/image<br>**Remix**: Modify existing video |
| `openai_api_key` | String | Your OpenAI API secret key (required) |
| `prompt` | Text | Video description or modification instructions |
| `save_path` | String | Output directory (defaults to ComfyUI output folder) |
| `filename_prefix` | String | Base filename (unique number appended automatically) |

---

### Generate Mode Parameters

*Active only when `mode = Generate`*

| Parameter | Options | Description |
|-----------|---------|-------------|
| `profile` | Standard/Pro | Model quality tier (Pro = higher fidelity, higher cost) |
| `orientation` | Landscape/Portrait | Video aspect ratio |
| `duration` | Seconds | Video length (longer = more cost) |
| `image_input` | Socket (Optional) | Connect image for **Image-to-Video** mode<br>Empty = **Text-to-Video** mode |

> 📐 **Auto-Resize:** Connected images are automatically resized with letterboxing/pillarboxing to match Sora requirements.

---

### Remix Mode Parameters

*Active only when `mode = Remix`*

| Parameter | Description |
|-----------|-------------|
| `source_video_id` | **Auto Mode (Recommended):** Leave empty - uses last generated video ID<br>**Manual Mode:** Enter specific `video_...` ID to remix older videos |

> 🔄 **Pro Tip:** Leave `source_video_id` empty for automatic sequential remixing!

---

### General Parameters

*Active in both modes*

| Parameter | Default | Description |
|-----------|---------|-------------|
| `polling_interval` | 5s | How often to check if video is ready |
| `max_polling_time` | 600s | Maximum wait time before timeout |
| `show_progress` | True | Display generation progress (0-100%) in console |

---

## 📖 Best Practices

### Prompting Tips

For optimal results, check the [Official Sora Prompting Guide](https://cookbook.openai.com/examples/sora/sora2_prompting_guide).

**Generate Mode:**
- Describe the complete scene you want to create
- Include details about camera movement, lighting, mood

**Remix Mode:**
- Describe only the changes you want to make
- Reference elements from the source video

### Workflow Optimization

1. Use **Auto-Remix** by leaving `source_video_id` empty
2. Increase `max_polling_time` for longer/higher-quality videos
3. Enable `show_progress` to monitor generation status
4. Check console output for detailed information

---

## 📦 Example Workflow

Load `workflow_example.json` to see a complete working setup!

---

## 🛠️ Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Node not appearing | Restart ComfyUI completely after installation |
| API Error | Verify API key and check credit balance |
| Timeout | Increase `max_polling_time` value |
| Image size error | Node auto-resizes, but check source image isn't corrupted |

---

## 📝 Requirements

- **ComfyUI** (latest version recommended)
- **Python packages:** opencv-python, moviepy (auto-installed)
- **OpenAI API key** with credits

---

## 🤝 Support

- **Issues:** [GitHub Issues](https://github.com/Cameraptor/SORA2_API_Node_ComfyUI/issues)
- **Website:** [cameraptor.com/voogie](https://cameraptor.com/voogie)

---

## 📄 License

MIT License - See LICENSE file for details

---

<div align="center">

**Made with ❤️ by Voogie | Cameraptor**

⭐ Star this repo if you find it useful!

</div>
