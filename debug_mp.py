import mediapipe
print("MediaPipe version:", getattr(mediapipe, "__version__", "unknown"))
print("MediaPipe file:", mediapipe.__file__)
try:
    from mediapipe.solutions import hands
    print("Successfully imported mediapipe.solutions.hands")
except Exception as e:
    print("Error importing hands:", e)

import sys
print("Python executable:", sys.executable)
print("Sys Path:", sys.path)
