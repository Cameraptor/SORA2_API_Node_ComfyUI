\# 🦖 Sora2 Node for ComfyUI by Cameraptor



This is a universal node for ComfyUI that provides direct access to the full capabilities of the \*\*OpenAI Sora API\*\*. Create videos from text, animate your images, and generate sequential remixes all within a single, convenient interface.



Author: \*\*Voogie\*\* | Project: \*\*Cameraptor\*\* | \[cameraptor.com/voogie](https://cameraptor.com/voogie)



!\[Workflow Example](https://i.imgur.com/your\_image\_link.png) <!-- REPLACE THIS LINK WITH A SCREENSHOT OF YOUR WORKFLOW -->



---



\### ✨ Key Features



\*   \*\*Unified Interface:\*\* A single node for all modes (`Generate` and `Remix`).

\*   \*\*Auto-Remix:\*\* The node automatically uses the ID of the last generated video for remixing. No more cyclical dependencies in your workflow!

\*   \*\*Audio Extraction:\*\* Automatically extracts the audio track for direct use with nodes like `VHS Video Combine` (\*requires `moviepy`\*).

\*   \*\*Smart Resize (Img2Vid):\*\* Automatically resizes your input image to match Sora API's requirements while preserving aspect ratio (using letterboxing/pillarboxing).

\*   \*\*Accurate Cost Estimation:\*\* Calculates the approximate cost for both `Generate` and `Remix` jobs.

\*   \*\*Bulletproof Error Handling:\*\* The node won't crash or break the queue if the OpenAI API returns an error.



---



\### 🚀 Installation



Installation is designed to be as simple and automatic as possible.



\#### Method 1: Via ComfyUI Manager (Recommended)



1\.  Launch ComfyUI and open the \*\*Manager\*\*.

2\.  Click on the \*\*Install via Git URL\*\* button.

3\.  Paste this repository's URL into the field: `https://github.com/Cameraptor/SORA2\_API\_Node\_ComfyUI`

4\.  Click \*\*Install\*\*. ComfyUI Manager will automatically download the node and install all required dependencies (`opencv-python`, `moviepy`, etc.).

5\.  \*\*Completely restart ComfyUI.\*\*



\#### Method 2: Manual Installation



1\.  Navigate to your `ComfyUI/custom\_nodes/` directory.

2\.  Open a terminal (command prompt) in this folder and run the command:

&nbsp;   ```bash

&nbsp;   git clone https://github.com/Cameraptor/SORA2\_API\_Node\_ComfyUI

&nbsp;   ```

3\.  After the download is complete, navigate into the new directory:

&nbsp;   ```bash

&nbsp;   cd SORA2\_API\_Node\_ComfyUI

&nbsp;   ```

4\.  Install the dependencies. \*\*Important:\*\* Use the Python environment embedded with your ComfyUI. For Windows, the command is:

&nbsp;   ```bash

&nbsp;   ..\\..\\python\_embeded\\python.exe -m pip install -r requirements.txt

&nbsp;   ```

5\.  \*\*Completely restart ComfyUI.\*\*



---



\### 🔑 How to Get an OpenAI API Key (Required!)



Sora is a paid service. To use this node, you need an OpenAI account with a positive credit balance and an API key.



\#### Step 1: Sign Up on the OpenAI Platform



\*   Go to \[platform.openai.com](https://platform.openai.com/).

\*   Sign up for a new account or log in to your existing one.



\#### Step 2: Verification and Adding Credits (IMPORTANT!)



\*   \*\*Verification:\*\* OpenAI will require you to verify your account, usually with a phone number. Complete this process.

\*   \*\*Credits:\*\* Unlike ChatGPT, the API operates on a pre-paid basis.

&nbsp;   \*   In the left-hand menu, navigate to \*\*Settings\*\* -> \*\*Billing\*\*.

&nbsp;   \*   Click \*\*Add payment details\*\* and add your credit card.

&nbsp;   \*   After adding a card, click \*\*Add to credit balance\*\* and add funds (e.g., $10). \*The API will not work without credits.\*



\#### Step 3: Create an API Key



\*   In the left-hand menu, navigate to \*\*API Keys\*\*.

\*   Click the \*\*Create new secret key\*\* button.

\*   Give the key a name (e.g., `ComfyUI-Sora`).

\*   Click \*\*Create secret key\*\*.

\*   \*\*ATTENTION!\*\* This key will be shown \*\*only once\*\*. Copy it immediately and save it in a secure place. If you close the window, you will never be able to see it again.



\#### Step 4: Use the Key in ComfyUI



\*   Paste the copied key into the `openai\_api\_key` field in the `🦖 Sora2` node.



---



\### 🕹️ How to Use \& Parameters Explained



Find the `🦖 Sora2` node in the `🦖Cameraptor` menu. After configuring the parameters, click \*\*"Queue Prompt"\*\* and \*\*watch the console (the black command window) to see the generation progress!\*\*



---



\#### Main Parameters



\##### `mode`

\*   \*\*`Generate`\*\*: Creates a brand new video from a text prompt or an image.

\*   \*\*`Remix`\*\*: Modifies a previously generated video based on a new prompt.



\##### `openai\_api\_key`

\*   Your secret API key from the OpenAI Platform. This is required.



\##### `prompt`

\*   The main text description for your video.

\*   In `Generate` mode, it describes the scene you want to create.

\*   In `Remix` mode, it describes the \*changes\* you want to make to the source video.

\*   For best results, check out the \[Official Sora Prompting Guide](https://cookbook.openai.com/examples/sora/sora2\_prompting\_guide).



\##### `save\_path`

\*   The directory where the final video file will be saved. Defaults to the ComfyUI `output` folder.



\##### `filename\_prefix`

\*   The base name for your saved video file. A unique number will be automatically appended to prevent overwriting (e.g., `Sora\_Video\_00001.mp4`).



---

\#### `Generate` Mode Parameters



\*These are only active when `mode` is set to `Generate`.\*



\##### `profile`

\*   Selects the model and quality tier. "Pro" versions offer higher visual fidelity at a higher cost.



\##### `orientation`

\*   Sets the aspect ratio of the video (`Landscape` or `Portrait`).



\##### `duration`

\*   The length of the video in seconds. Longer durations cost more and take more time.



\##### `image\_input` (Optional Socket)

\*   Connect an image to enable \*\*Image-to-Video\*\* mode. The node will automatically resize the image to fit the target resolution. If nothing is connected, the node runs in \*\*Text-to-Video\*\* mode.



---

\#### `Remix` Mode Parameters



\*These are only active when `mode` is set to `Remix`.\*



\##### `source\_video\_id`

\*   The ID of the video you want to remix (e.g., `video\_...`).

\*   \*\*Automatic Mode (Recommended):\*\* Leave this field \*\*empty\*\*. The node will automatically use the ID of the last video generated in the current session. This is the easiest way to create a sequence of remixes.

\*   \*\*Manual Mode:\*\* Paste a specific `video\_id` here to remix an older video. This will take priority over the automatic mode.



---

\#### General Parameters



\*These are active in both modes.\*



\##### `polling\_interval`

\*   How often (in seconds) the node checks with OpenAI to see if the video is ready.



\##### `max\_polling\_time`

\*   The maximum time (in seconds) the node will wait for a video to be completed. If the generation takes longer than this, the node will time out. Increase this for longer or higher-quality videos.



\##### `show\_progress`

\*   If enabled, prints the generation progress percentage (`0%... 100%`) in the console.



---



Load the `workflow\_example.json` file to see a complete working example!

