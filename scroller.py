import cv2
import pyautogui
import time
import sys

# ลอง Import MediaPipe ด้วยวิธีที่ทนทานต่อปัญหาบน Windows
try:
    import mediapipe as mp
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    print("MediaPipe imported successfully using standard method.")
except AttributeError:
    try:
        from mediapipe.python.solutions import hands as mp_hands
        from mediapipe.python.solutions import drawing_utils as mp_draw
        print("MediaPipe imported successfully using fallback method.")
    except ImportError:
        print("Error: Could not import MediaPipe. Please run: pip install mediapipe")
        sys.exit()

# ตั้งค่ากล้อง
# หากเลข 0 ไม่ติด ให้ลองเปลี่ยนเป็น 1 หรือ 2
cap = cv2.VideoCapture(0)

# ตั้งค่าเครื่องมือตรวจจับมือ
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# ตัวแปรสำหรับคุมการเลื่อน
prev_y = 0
dy = 0
scroll_threshold = 50  # ปรับความไวในการปัด (ค่าน้อย = ไว)
cooldown = 1.0         # เวลารอระหว่างการปัด (วินาที)
last_scroll_time = time.time()

print("---------------------------------------")
print("AI Hand Scroller ทำงานแล้ว!")
print("- ปัดมือขึ้น: เลื่อนคลิปถัดไป (Next)")
print("- ปัดมือลง: เลื่อนคลิปก่อนหน้า (Prev)")
print("- กด 'q' หรือ 'ESC' เพื่อปิด")
print("---------------------------------------")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("ไม่สามารถอ่านข้อมูลจากกล้องได้")
        break

    # กลับด้านภาพและแปลงสี
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # ตรวจหาตำแหน่งมือ
    results = hands.process(image_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # วาดจุดเชื่อมต่อบนมือ
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # ตำแหน่งศูนย์กลางฝ่ามือ (Landmark 9)
            cy = int(hand_landmarks.landmark[9].y * h)

            current_time = time.time()
            if prev_y != 0:
                dy = cy - prev_y
                
                # ตรวจสอบการปัดเมื่อพ้นระยะ Cooldown
                if current_time - last_scroll_time > cooldown:
                    if dy < -scroll_threshold:
                        print(">> Swipe UP Detected -> Next Video")
                        pyautogui.press('down')
                        last_scroll_time = current_time
                    elif dy > scroll_threshold:
                        print("<< Swipe DOWN Detected -> Previous Video")
                        pyautogui.press('up')
                        last_scroll_time = current_time

            prev_y = cy
    else:
        # ถ้าไม่เห็นมือ ให้รีเซ็ตตำแหน่งอ้างอิง
        prev_y = 0

    # แสดงผลข้อความบนหน้าจอ
    cv2.putText(frame, "TikTok AI Control", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # หากมีการเลื่อนเมื่อครู่ ให้แสดงสถานะ
    if time.time() - last_scroll_time < 0.5:
        cv2.putText(frame, "SCROLLED!", (int(w/2)-50, int(h/2)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    cv2.imshow('Camera Feed', frame)

    # กด q หรือ ESC เพื่อออก
    key = cv2.waitKey(1)
    if key == ord('q') or key == 27:
        break

cap.release()
cv2.destroyAllWindows()
print("ปิดโปรแกรมเรียบร้อย")
