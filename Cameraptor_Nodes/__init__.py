# =============================================================================
# 🦖 Sora2 by Cameraptor - Node Registration
# Author: Voogie
# Website: https://cameraptor.com/voogie
# =============================================================================

# Импортируем нашу единственную ноду
from .sora2_node import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# Сообщаем ComfyUI о наших нодах
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

print("✅ 🦖 Sora2 Node by Cameraptor: Loaded successfully!")